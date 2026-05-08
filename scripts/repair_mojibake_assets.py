import argparse
import re
from pathlib import Path

from common import ENCODING, resolve_apply_targets


MOJIBAKE_RUN = re.compile(r"[\x80-\xff]{2,}")
CJK = re.compile(r"[\u3400-\u9fff]")


def repair_mojibake_text(text: str) -> tuple[str, int]:
    repairs = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal repairs
        value = match.group(0)
        try:
            fixed = value.encode("latin-1").decode("utf-8")
        except UnicodeError:
            return value
        if fixed != value and CJK.search(fixed):
            repairs += 1
            return fixed
        return value

    return MOJIBAKE_RUN.sub(replace, text), repairs


def repair_assets(assets_dir: Path) -> dict[str, int]:
    changed: dict[str, int] = {}
    for path in sorted(assets_dir.glob("*.js")):
        try:
            text = path.read_text(encoding=ENCODING)
        except OSError:
            continue
        fixed, repairs = repair_mojibake_text(text)
        if repairs:
            path.write_text(fixed, encoding=ENCODING)
            changed[path.name] = repairs
    return changed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Repair UTF-8 Chinese text that was written as Latin-1 mojibake in JS assets.")
    parser.add_argument("--auto-detect", action="store_true", help="Auto-detect current Claude Desktop app package.")
    parser.add_argument("--assets-dir", type=Path, help="Claude ion-dist assets directory.")
    parser.add_argument("--check", action="store_true", help="Only report files that would change.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    targets = resolve_apply_targets(auto_detect=args.auto_detect)
    assets_dir = args.assets_dir or targets.assets_dir
    changed: dict[str, int] = {}
    for path in sorted(assets_dir.glob("*.js")):
        try:
            text = path.read_text(encoding=ENCODING)
        except OSError:
            continue
        _, repairs = repair_mojibake_text(text)
        if repairs:
            changed[path.name] = repairs
    if args.check:
        print(f"mojibake asset files: {len(changed)}")
        for name, count in changed.items():
            print(f"{name}: {count}")
        return 1 if changed else 0
    changed = repair_assets(assets_dir)
    print(f"repaired asset files: {len(changed)}")
    for name, count in changed.items():
        print(f"{name}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
