import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from common import BACKUP_ROOT, ENCODING, ION_LOCALE_SRC, PROJECT_ROOT, resolve_apply_targets
from locale_backfill import extract_default_messages_from_assets
from repair_mojibake_assets import repair_assets, repair_mojibake_text


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def build_script_command(script_name: str, auto_detect: bool, app_dir: str | None) -> list[str]:
    command = [sys.executable, str(Path("scripts") / script_name)]
    if app_dir:
        command.extend(["--app-dir", app_dir])
    elif auto_detect:
        command.append("--auto-detect")
    return command


def run_command(name: str, command: list[str], required: bool = True) -> dict:
    completed = subprocess.run(command, cwd=PROJECT_ROOT, text=True, capture_output=True)
    return {
        "name": name,
        "required": required,
        "command": command,
        "exitCode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def summarize_missing_locale_ids(messages: dict[str, str], locale: dict, sample_limit: int = 50) -> dict:
    missing = [
        {"id": key, "defaultMessage": messages[key]}
        for key in messages
        if key not in locale
    ]
    return {
        "count": len(missing),
        "samples": missing[:sample_limit],
    }


def scan_missing_locale_ids(assets_dir: Path, locale_path: Path, sample_limit: int = 50) -> dict:
    messages = extract_default_messages_from_assets(assets_dir)
    locale = json.loads(locale_path.read_text(encoding=ENCODING))
    summary = summarize_missing_locale_ids(messages, locale, sample_limit=sample_limit)
    summary["defaultMessageIds"] = len(messages)
    summary["localeEntries"] = len(locale)
    return summary


def scan_mojibake_assets(assets_dir: Path) -> dict:
    files = []
    for path in sorted(assets_dir.glob("*.js")):
        try:
            text = path.read_text(encoding=ENCODING)
        except OSError:
            continue
        _, repairs = repair_mojibake_text(text)
        if repairs:
            files.append({"file": str(path), "repairs": repairs})
    return {"count": len(files), "files": files}


def repair_mojibake_step(assets_dir: Path) -> dict:
    changed = repair_assets(assets_dir)
    return {
        "name": "repair_mojibake_assets",
        "required": False,
        "exitCode": 0,
        "repairedFiles": [{"file": name, "repairs": count} for name, count in changed.items()],
    }


def latest_apply_report() -> Path | None:
    if not BACKUP_ROOT.exists():
        return None
    reports = sorted(BACKUP_ROOT.glob("*/apply-report.json"), key=lambda p: p.parent.name)
    return reports[-1] if reports else None


def report_status(steps: list[dict]) -> str:
    return "failed" if any(step.get("required") and step.get("exitCode") != 0 for step in steps) else "ok"


def write_report(report: dict, explicit_path: Path | None = None) -> Path:
    report_path = explicit_path
    if report_path is None:
        apply_report = latest_apply_report()
        if apply_report:
            report_path = apply_report.parent / "auto-localize-report.json"
        else:
            ensure = BACKUP_ROOT / f"auto-localize-{timestamp()}"
            ensure.mkdir(parents=True, exist_ok=True)
            report_path = ensure / "auto-localize-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding=ENCODING)
    return report_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cross-version Claude Desktop zh-CN auto localization workflow")
    parser.add_argument("--app-dir", help="Claude app directory. Auto-detected when omitted.")
    parser.add_argument("--auto-detect", action="store_true", default=True, help="Auto-detect Claude WindowsApps package.")
    parser.add_argument("--restore-english", action="store_true", help="Restore official English backup before applying localization.")
    parser.add_argument("--skip-apply", action="store_true", help="Only scan/report; do not apply localization.")
    parser.add_argument("--skip-verify", action="store_true", help="Skip verify_localization.py.")
    parser.add_argument("--report", type=Path, help="Optional explicit report path.")
    parser.add_argument("--sample-limit", type=int, default=50, help="Missing id sample count in report.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    steps: list[dict] = []

    settings_step = run_command(
        "sync_project_settings_translations",
        [sys.executable, str(Path("scripts") / "apply_settings_translations.py")],
        required=True,
    )
    steps.append(settings_step)

    if args.restore_english:
        steps.append(run_command(
            "restore_english",
            build_script_command("restore_reference_localization.py", auto_detect=False, app_dir=args.app_dir),
            required=True,
        ))

    if not args.skip_apply:
        steps.append(run_command(
            "apply_localization",
            build_script_command("apply_localization.py", auto_detect=True, app_dir=args.app_dir),
            required=True,
        ))

    targets = resolve_apply_targets(Path(args.app_dir) if args.app_dir else None, auto_detect=True)

    before_repair = scan_mojibake_assets(targets.assets_dir)
    repair_step = repair_mojibake_step(targets.assets_dir)
    steps.append(repair_step)
    after_repair = scan_mojibake_assets(targets.assets_dir)

    if not args.skip_verify:
        steps.append(run_command(
            "verify_localization",
            build_script_command("verify_localization.py", auto_detect=True, app_dir=args.app_dir),
            required=True,
        ))

    missing_installed = scan_missing_locale_ids(targets.assets_dir, targets.ion_locale, args.sample_limit)
    missing_project = scan_missing_locale_ids(targets.assets_dir, ION_LOCALE_SRC, args.sample_limit)

    report = {
        "status": report_status(steps),
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "targets": {
            "resourceRoot": str(targets.resource_root),
            "rootLocale": str(targets.root_locale),
            "ionLocale": str(targets.ion_locale),
            "assetsDir": str(targets.assets_dir),
        },
        "steps": steps,
        "mojibake": {
            "beforeRepair": before_repair,
            "afterRepair": after_repair,
        },
        "missingLocaleIds": {
            "installed": missing_installed,
            "project": missing_project,
            "policy": "Unknown English is reported only. It is not auto-translated.",
        },
    }
    report_path = write_report(report, args.report)

    print(f"Auto-localize status: {report['status']}")
    print(f"Report: {report_path}")
    print(f"Missing installed ids: {missing_installed['count']}")
    print(f"Mojibake after repair: {after_repair['count']}")
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
