import argparse
import json
from pathlib import Path

from common import (
    CONFIG, ENCODING, ION_OVERRIDES_SRC, PATCHES, STATSIG_SRC_DIR, ApplyTargets,
    decode_patch_text, ensure_assets_dir, ensure_file_exists, find_claude_package,
    patch_file_pattern, resolve_apply_targets,
)


def verify_locales(targets: ApplyTargets) -> list[str]:
    issues = []
    root_data = json.loads(targets.root_locale.read_text(encoding=ENCODING))
    ion_data = json.loads(targets.ion_locale.read_text(encoding=ENCODING))
    for entry in CONFIG.get('verifyEntries', []):
        data = root_data if entry.get('file') == 'root' else ion_data
        if data.get(entry['key']) != entry['value']:
            issues.append(entry['message'])
    return issues


def verify_optional_resources(targets: ApplyTargets) -> list[str]:
    issues = []
    if targets.ion_overrides and targets.ion_overrides.exists() and ION_OVERRIDES_SRC.exists():
        if targets.ion_overrides.read_text(encoding=ENCODING) != ION_OVERRIDES_SRC.read_text(encoding=ENCODING):
            issues.append('ion overrides file is not synced with project copy')
    if targets.statsig_dir and targets.statsig_dir.exists() and STATSIG_SRC_DIR.exists():
        for src in sorted(STATSIG_SRC_DIR.glob('*.json')):
            dst = targets.statsig_dir / src.name
            if not dst.exists():
                issues.append(f'statsig target file missing: {src.name}')
            elif dst.read_text(encoding=ENCODING) != src.read_text(encoding=ENCODING):
                issues.append(f'statsig file is not synced: {src.name}')
    return issues


def verify_assets(targets: ApplyTargets) -> list[str]:
    issues = []
    for patch in PATCHES:
        old = decode_patch_text(patch['find'])
        for path in targets.assets_dir.glob(patch_file_pattern(patch)):
            try:
                if old in path.read_text(encoding=ENCODING):
                    issues.append(f"English fallback remains: {patch['description']} -> {path.name}")
            except Exception:
                continue
    return issues


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Verify Claude Desktop zh-CN localization')
    parser.add_argument('--app-dir', help='Claude app directory. Auto-detected when omitted if configured paths are missing.')
    parser.add_argument('--auto-detect', action='store_true', help='Force WindowsApps package auto-detection.')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    app_dir = Path(args.app_dir) if args.app_dir else None
    targets = resolve_apply_targets(app_dir, auto_detect=True)

    ensure_file_exists(targets.root_locale, 'Target root locale')
    ensure_file_exists(targets.ion_locale, 'Target ion locale')
    ensure_assets_dir(targets.assets_dir)

    issues = verify_locales(targets) + verify_optional_resources(targets) + verify_assets(targets)
    if issues:
        print('VERIFY FAILED')
        for item in issues:
            print(item)
        raise SystemExit(1)
    print('VERIFY OK')


if __name__ == '__main__':
    main()
