import argparse
from pathlib import Path

from common import (
    BACKUP_ROOT, ApplyTargets, copy2_best_effort, ensure_dir, find_claude_package,
    resolve_apply_targets,
)


def latest_backup_dir() -> Path:
    backups = sorted(p for p in BACKUP_ROOT.iterdir() if p.is_dir())
    if not backups:
        raise SystemExit('No backup found.')
    return backups[-1]


def restore_tree(src_dir: Path, dst_dir: Path) -> list[str]:
    if not src_dir.exists():
        return []
    ensure_dir(dst_dir, 'Restore target directory')
    restored = []
    for item in src_dir.iterdir():
        copy2_best_effort(item, dst_dir / item.name, 'restore file')
        restored.append(str(dst_dir / item.name))
    return restored


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Rollback Claude Desktop zh-CN localization')
    parser.add_argument('--app-dir', help='Claude app directory. Auto-detected when omitted if configured paths are missing.')
    parser.add_argument('--auto-detect', action='store_true', help='Force WindowsApps package auto-detection.')
    return parser.parse_args()


def restore_backup(targets: ApplyTargets) -> None:
    ensure_dir(BACKUP_ROOT, 'Backup directory')
    ensure_dir(targets.root_locale.parent, 'Target root locale directory')
    ensure_dir(targets.ion_locale.parent, 'Target ion locale directory')
    ensure_dir(targets.assets_dir, 'Assets directory')

    backup = latest_backup_dir()
    restored_root = restore_tree(backup / 'root', targets.root_locale.parent)
    restored_ion = restore_tree(backup / 'ion', targets.ion_locale.parent)
    restored_assets = restore_tree(backup / 'assets', targets.assets_dir)

    restored_overrides: list[str] = []
    if targets.ion_overrides:
        ensure_dir(targets.ion_overrides.parent, 'Target ion overrides directory')
        restored_overrides = restore_tree(backup / 'ion-overrides', targets.ion_overrides.parent)

    restored_statsig: list[str] = []
    if targets.statsig_dir:
        ensure_dir(targets.statsig_dir, 'Statsig directory')
        restored_statsig = restore_tree(backup / 'statsig', targets.statsig_dir)

    print(f'Rollback completed from backup: {backup}')
    print(f'Restored root files: {len(restored_root)}')
    print(f'Restored ion files: {len(restored_ion)}')
    print(f'Restored asset files: {len(restored_assets)}')
    if targets.ion_overrides:
        print(f'Restored ion overrides files: {len(restored_overrides)}')
    if targets.statsig_dir:
        print(f'Restored statsig files: {len(restored_statsig)}')


def main() -> None:
    args = parse_args()
    app_dir = Path(args.app_dir) if args.app_dir else (find_claude_package() if args.auto_detect else None)
    restore_backup(resolve_apply_targets(app_dir))


if __name__ == '__main__':
    main()
