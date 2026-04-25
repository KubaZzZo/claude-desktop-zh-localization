import json
import os
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
ION_OVERRIDES_SRC = PROJECT_ROOT / 'locales' / 'ion-zh-CN.overrides.json'
ION_OVERRIDES_DST = Path(CONFIG.get('optionalTargets', {}).get('ionOverrides', '')) if CONFIG.get('optionalTargets', {}).get('ionOverrides') else None
STATSIG_SRC_DIR = PROJECT_ROOT / 'locales' / 'statsig'
STATSIG_DST_DIR = Path(CONFIG.get('optionalTargets', {}).get('statsigDir', '')) if CONFIG.get('optionalTargets', {}).get('statsigDir') else None
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


def expand_path(value: str) -> Path:
    return Path(os.path.expandvars(value))


def find_existing_paths(candidates: list[str]) -> list[Path]:
    paths = []
    for candidate in candidates:
        path = expand_path(candidate)
        if path.exists():
            paths.append(path)
    return paths


def detect_optional_resources() -> dict[str, object]:
    overrides_exists = bool(ION_OVERRIDES_DST and ION_OVERRIDES_DST.exists())
    statsig_exists = bool(STATSIG_DST_DIR and STATSIG_DST_DIR.exists() and STATSIG_DST_DIR.is_dir())
    statsig_files = sorted(STATSIG_DST_DIR.glob('*.json')) if statsig_exists else []
    return {
        'availableInstallRoots': [str(path) for path in find_existing_paths(CONFIG.get('installCandidates', []))],
        'ionOverrides': {
            'configured': bool(ION_OVERRIDES_DST),
            'exists': overrides_exists,
            'sourceExists': ION_OVERRIDES_SRC.exists(),
            'target': str(ION_OVERRIDES_DST) if ION_OVERRIDES_DST else None,
        },
        'statsig': {
            'configured': bool(STATSIG_DST_DIR),
            'exists': statsig_exists,
            'sourceExists': STATSIG_SRC_DIR.exists(),
            'target': str(STATSIG_DST_DIR) if STATSIG_DST_DIR else None,
            'targetFiles': [str(path) for path in statsig_files],
        },
    }


def backup_file(src: Path, backup_dir: Path) -> None:
    ensure_dir(backup_dir)
    if src.exists():
        shutil.copy2(src, backup_dir / src.name)


def backup_tree(src_dir: Path, backup_dir: Path) -> list[str]:
    ensure_dir(backup_dir)
    copied: list[str] = []
    if not src_dir.exists() or not src_dir.is_dir():
        return copied
    for item in sorted(src_dir.glob('*.json')):
        shutil.copy2(item, backup_dir / item.name)
        copied.append(str(item))
    return copied


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


def sync_optional_resources(run_dir: Path) -> dict[str, object]:
    optional_report = detect_optional_resources()

    if optional_report['ionOverrides']['exists'] and ION_OVERRIDES_DST:
        backup_file(ION_OVERRIDES_DST, run_dir / 'ion-overrides')
        if ION_OVERRIDES_SRC.exists():
            shutil.copy2(ION_OVERRIDES_SRC, ION_OVERRIDES_DST)
            optional_report['ionOverrides']['synced'] = True
        else:
            optional_report['ionOverrides']['synced'] = False
    else:
        optional_report['ionOverrides']['synced'] = False

    if optional_report['statsig']['exists'] and STATSIG_DST_DIR:
        optional_report['statsig']['backedUpFiles'] = backup_tree(STATSIG_DST_DIR, run_dir / 'statsig')
        if STATSIG_SRC_DIR.exists():
            copied_files: list[str] = []
            for src_file in sorted(STATSIG_SRC_DIR.glob('*.json')):
                shutil.copy2(src_file, STATSIG_DST_DIR / src_file.name)
                copied_files.append(str(src_file))
            optional_report['statsig']['synced'] = True
            optional_report['statsig']['copiedFiles'] = copied_files
        else:
            optional_report['statsig']['synced'] = False
            optional_report['statsig']['copiedFiles'] = []
    else:
        optional_report['statsig']['synced'] = False
        optional_report['statsig']['copiedFiles'] = []
        optional_report['statsig']['backedUpFiles'] = []

    return optional_report


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
    optional_report = sync_optional_resources(run_dir)

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
        'optionalResources': optional_report,
        'copiedLocales': {
            'rootLocale': str(ROOT_LOCALE_DST),
            'ionLocale': str(ION_LOCALE_DST),
        },
    }

    report_path = run_dir / 'apply-report.json'
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding=ENCODING)
    print(f'Applied localization. Backup saved at: {run_dir}')
    print(f"Patched files: {report['summary']['patchedFiles']}")
    print(f"Matched patches: {report['summary']['matchedPatches']}/{report['summary']['totalPatches']}")
    print(f"Already patched: {report['summary']['alreadyPatchedPatches']}")
    print(f"Unmatched patches: {report['summary']['unmatchedPatches']}")
    if optional_report['ionOverrides']['exists']:
        print(f"Overrides synced: {optional_report['ionOverrides']['synced']}")
    if optional_report['statsig']['exists']:
        print(f"Statsig synced: {optional_report['statsig']['synced']}")


if __name__ == '__main__':
    main()
