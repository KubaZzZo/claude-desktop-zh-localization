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


def timestamp() -> str:
    return datetime.now().strftime('%Y%m%d-%H%M%S')


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def ensure_file_exists(path: Path, description: str) -> None:
    if not path.exists():
        raise SystemExit(f'{description} not found or inaccessible: {path}')


def ensure_assets_dir(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f'Assets directory not found or inaccessible: {path}')
    if not path.is_dir():
        raise SystemExit(f'Assets path is not a directory: {path}')


def backup_file(src: Path, backup_dir: Path) -> None:
    ensure_dir(backup_dir)
    if src.exists():
        shutil.copy2(src, backup_dir / src.name)


def decode_patch_text(value: str) -> str:
    return value.encode('utf-8').decode('unicode_escape')


def analyze_patch_hits(paths: list[Path]) -> list[dict[str, object]]:
    patch_results: list[dict[str, object]] = []
    for item in PATCHES:
        find = decode_patch_text(item['find'])
        replace = decode_patch_text(item['replace'])
        matched_files: list[dict[str, object]] = []
        replaced_files: list[dict[str, object]] = []
        total_hits = 0
        total_replaced_hits = 0
        for path in paths:
            try:
                text = path.read_text(encoding=ENCODING)
            except Exception:
                continue
            count = text.count(find)
            replaced_count = text.count(replace)
            if count:
                matched_files.append({'file': str(path), 'count': count})
                total_hits += count
            if replaced_count:
                replaced_files.append({'file': str(path), 'count': replaced_count})
                total_replaced_hits += replaced_count
        patch_results.append(
            {
                'description': item['description'],
                'find': item['find'],
                'replace': item['replace'],
                'matched': total_hits > 0,
                'alreadyPatched': total_hits == 0 and total_replaced_hits > 0,
                'totalHits': total_hits,
                'totalReplacedHits': total_replaced_hits,
                'files': matched_files,
                'replacedFiles': replaced_files,
            }
        )
    return patch_results


def apply_patches_to_file(path: Path) -> list[tuple[str, int]]:
    text = path.read_text(encoding=ENCODING)
    changed = False
    counts: list[tuple[str, int]] = []
    for item in PATCHES:
        find = decode_patch_text(item['find'])
        replace = decode_patch_text(item['replace'])
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


def main() -> None:
    ensure_file_exists(ROOT_LOCALE_DST, 'Target root locale')
    ensure_file_exists(ION_LOCALE_DST, 'Target ion locale')
    ensure_assets_dir(ASSETS_DIR)

    run_dir = BACKUP_ROOT / timestamp()
    ensure_dir(run_dir)
    backup_file(ROOT_LOCALE_DST, run_dir / 'root')
    backup_file(ION_LOCALE_DST, run_dir / 'ion')

    assets_paths = sorted(ASSETS_DIR.glob('*.js'))
    patch_analysis = analyze_patch_hits(assets_paths)
    patch_targets = [
        path
        for path in assets_paths
        if any(file_info['file'] == str(path) for result in patch_analysis for file_info in result['files'])
    ]

    for path in patch_targets:
        backup_file(path, run_dir / 'assets')

    shutil.copy2(ROOT_LOCALE_SRC, ROOT_LOCALE_DST)
    shutil.copy2(ION_LOCALE_SRC, ION_LOCALE_DST)

    file_report: list[dict[str, object]] = []
    for path in patch_targets:
        counts = apply_patches_to_file(path)
        if counts:
            file_report.append(
                {
                    'file': str(path),
                    'changes': [{'description': d, 'count': c} for d, c in counts],
                }
            )

    report = {
        'summary': {
            'totalPatches': len(PATCHES),
            'matchedPatches': sum(1 for item in patch_analysis if item['matched']),
            'alreadyPatchedPatches': sum(1 for item in patch_analysis if item['alreadyPatched']),
            'unmatchedPatches': sum(1 for item in patch_analysis if not item['matched'] and not item['alreadyPatched']),
            'patchedFiles': len(file_report),
        },
        'patches': patch_analysis,
        'files': file_report,
    }

    report_path = run_dir / 'apply-report.json'
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding=ENCODING)
    print(f'Applied localization. Backup saved at: {run_dir}')
    print(f"Patched files: {report['summary']['patchedFiles']}")
    print(f"Matched patches: {report['summary']['matchedPatches']}/{report['summary']['totalPatches']}")
    print(f"Already patched: {report['summary']['alreadyPatchedPatches']}")
    print(f"Unmatched patches: {report['summary']['unmatchedPatches']}")


if __name__ == '__main__':
    main()
