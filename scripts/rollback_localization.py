import json
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((PROJECT_ROOT / 'config.json').read_text(encoding='utf-8'))
BACKUP_ROOT = PROJECT_ROOT / CONFIG['backupDirName']
ROOT_LOCALE_DST = Path(CONFIG['applyTargets']['rootLocale'])
ION_LOCALE_DST = Path(CONFIG['applyTargets']['ionLocale'])
ASSETS_DIR = Path(CONFIG['applyTargets']['assetsDir'])


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


def restore_tree(src_dir: Path, dst_dir: Path) -> None:
    if not src_dir.exists():
        return
    ensure_dir(dst_dir, 'Restore target directory')
    for item in src_dir.iterdir():
        target = dst_dir / item.name
        shutil.copy2(item, target)


def main() -> None:
    ensure_dir(BACKUP_ROOT, 'Backup directory')
    ensure_dir(ROOT_LOCALE_DST.parent, 'Target root locale directory')
    ensure_dir(ION_LOCALE_DST.parent, 'Target ion locale directory')
    ensure_dir(ASSETS_DIR, 'Assets directory')

    backup = latest_backup_dir()
    root_dir = backup / 'root'
    ion_dir = backup / 'ion'
    assets_dir = backup / 'assets'

    restore_tree(root_dir, ROOT_LOCALE_DST.parent)
    restore_tree(ion_dir, ION_LOCALE_DST.parent)
    restore_tree(assets_dir, ASSETS_DIR)

    print(f'Rollback completed from backup: {backup}')


if __name__ == '__main__':
    main()
