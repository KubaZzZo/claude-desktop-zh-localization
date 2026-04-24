import json
import shutil
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((PROJECT_ROOT / 'config.json').read_text(encoding='utf-8'))
PATCHES = json.loads((PROJECT_ROOT / 'patches' / 'main-ui-patches.json').read_text(encoding='utf-8'))

BACKUP_ROOT = PROJECT_ROOT / CONFIG['backupDirName']
ROOT_LOCALE_SRC = PROJECT_ROOT / 'locales' / 'root-zh-CN.json'
ION_LOCALE_SRC = PROJECT_ROOT / 'locales' / 'ion-zh-CN.json'
ROOT_LOCALE_DST = Path(CONFIG['applyTargets']['rootLocale'])
ION_LOCALE_DST = Path(CONFIG['applyTargets']['ionLocale'])
ASSETS_DIR = Path(CONFIG['applyTargets']['assetsDir'])
ENCODING = CONFIG.get('encoding', 'utf-8')


def timestamp():
    return datetime.now().strftime('%Y%m%d-%H%M%S')


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def backup_file(src: Path, backup_dir: Path):
    ensure_dir(backup_dir)
    if src.exists():
        shutil.copy2(src, backup_dir / src.name)


def collect_patch_targets():
    targets = set()
    for item in PATCHES:
        find = item['find']
        for path in ASSETS_DIR.glob('*.js'):
            try:
                text = path.read_text(encoding=ENCODING)
            except Exception:
                continue
            if find in text:
                targets.add(path)
    return sorted(targets)


def apply_patches_to_file(path: Path):
    text = path.read_text(encoding=ENCODING)
    changed = False
    counts = []
    for item in PATCHES:
        find = item['find']
        replace = item['replace']
        if find == replace:
            continue
        count = text.count(find)
        if count:
            text = text.replace(find, replace)
            changed = True
            counts.append((item['description'], count))
    if changed:
        path.write_text(text, encoding=ENCODING)
    return counts


def main():
    run_dir = BACKUP_ROOT / timestamp()
    ensure_dir(run_dir)
    backup_file(ROOT_LOCALE_DST, run_dir / 'root')
    backup_file(ION_LOCALE_DST, run_dir / 'ion')

    patch_targets = collect_patch_targets()
    for path in patch_targets:
        backup_file(path, run_dir / 'assets')

    shutil.copy2(ROOT_LOCALE_SRC, ROOT_LOCALE_DST)
    shutil.copy2(ION_LOCALE_SRC, ION_LOCALE_DST)

    report = []
    for path in patch_targets:
        counts = apply_patches_to_file(path)
        if counts:
            report.append({
                'file': str(path),
                'changes': [{'description': d, 'count': c} for d, c in counts]
            })

    report_path = run_dir / 'apply-report.json'
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding=ENCODING)
    print(f'Applied localization. Backup saved at: {run_dir}')
    print(f'Patched files: {len(report)}')


if __name__ == '__main__':
    main()
