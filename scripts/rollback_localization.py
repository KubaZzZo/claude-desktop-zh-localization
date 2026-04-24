import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKUP_ROOT = PROJECT_ROOT / 'backups'
CONFIG_PATH = PROJECT_ROOT / 'config.json'


def latest_backup_dir() -> Path:
    backups = sorted([p for p in BACKUP_ROOT.iterdir() if p.is_dir()])
    if not backups:
        raise SystemExit('No backups found.')
    return backups[-1]


def restore_tree(src_dir: Path, dst_dir: Path) -> None:
    for item in src_dir.iterdir():
        target = dst_dir / item.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)


def main() -> None:
    if not CONFIG_PATH.exists():
        raise SystemExit('config.json not found.')

    import json
    config = json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
    target_root = Path(config['targetResourceRoot'])
    backup_dir = latest_backup_dir()

    if (backup_dir / 'root').exists():
        restore_tree(backup_dir / 'root', target_root)
    if (backup_dir / 'ion').exists():
        restore_tree(backup_dir / 'ion', target_root / 'ion-dist' / 'i18n')
    if (backup_dir / 'assets').exists():
        restore_tree(backup_dir / 'assets', target_root / 'ion-dist' / 'assets' / 'v1')

    print(f'Rolled back from backup: {backup_dir}')


if __name__ == '__main__':
    main()
