import json
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((PROJECT_ROOT / 'config.json').read_text(encoding='utf-8'))
BACKUP_ROOT = PROJECT_ROOT / CONFIG['backupDirName']
ROOT_LOCALE_DST = Path(CONFIG['applyTargets']['rootLocale'])
ION_LOCALE_DST = Path(CONFIG['applyTargets']['ionLocale'])
ASSETS_DIR = Path(CONFIG['applyTargets']['assetsDir'])
ION_OVERRIDES_DST = Path(CONFIG.get('optionalTargets', {}).get('ionOverrides', '')) if CONFIG.get('optionalTargets', {}).get('ionOverrides') else None
STATSIG_DST_DIR = Path(CONFIG.get('optionalTargets', {}).get('statsigDir', '')) if CONFIG.get('optionalTargets', {}).get('statsigDir') else None


def ensure_dir(path: Path, description: str) -> None:
    if not path.exists():
        raise SystemExit(f'{description} not found or inaccessible: {path}')
    if not path.is_dir():
        raise SystemExit(f'{description} is not a directory: {path}')


def latest_backup_dir() -> Path:
    backups = sorted([p for p in BACKUP_ROOT.iterdir() if p.is_dir()])
    if not backups:
        raise SystemExit('No backup found.')
    return backups[-1]


def restore_tree(src_dir: Path, dst_dir: Path) -> list[str]:
    restored: list[str] = []
    if not src_dir.exists():
        return restored
    ensure_dir(dst_dir, 'Restore target directory')
    for item in src_dir.iterdir():
        target = dst_dir / item.name
        shutil.copy2(item, target)
        restored.append(str(target))
    return restored


def main() -> None:
    ensure_dir(BACKUP_ROOT, 'Backup directory')
    ensure_dir(ROOT_LOCALE_DST.parent, 'Target root locale directory')
    ensure_dir(ION_LOCALE_DST.parent, 'Target ion locale directory')
    ensure_dir(ASSETS_DIR, 'Assets directory')

    backup = latest_backup_dir()
    root_dir = backup / 'root'
    ion_dir = backup / 'ion'
    assets_dir = backup / 'assets'
    ion_overrides_dir = backup / 'ion-overrides'
    statsig_dir = backup / 'statsig'

    restored_root = restore_tree(root_dir, ROOT_LOCALE_DST.parent)
    restored_ion = restore_tree(ion_dir, ION_LOCALE_DST.parent)
    restored_assets = restore_tree(assets_dir, ASSETS_DIR)

    restored_overrides: list[str] = []
    if ION_OVERRIDES_DST and ion_overrides_dir.exists():
        ensure_dir(ION_OVERRIDES_DST.parent, 'Target ion overrides directory')
        restored_overrides = restore_tree(ion_overrides_dir, ION_OVERRIDES_DST.parent)

    restored_statsig: list[str] = []
    if STATSIG_DST_DIR and statsig_dir.exists():
        ensure_dir(STATSIG_DST_DIR, 'Statsig directory')
        restored_statsig = restore_tree(statsig_dir, STATSIG_DST_DIR)

    print(f'Rollback completed from backup: {backup}')
    print(f'Restored root files: {len(restored_root)}')
    print(f'Restored ion files: {len(restored_ion)}')
    print(f'Restored asset files: {len(restored_assets)}')
    if ION_OVERRIDES_DST:
        print(f'Restored ion overrides files: {len(restored_overrides)}')
    if STATSIG_DST_DIR:
        print(f'Restored statsig files: {len(restored_statsig)}')


if __name__ == '__main__':
    main()
