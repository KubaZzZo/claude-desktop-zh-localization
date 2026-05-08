import argparse
from datetime import datetime
from pathlib import Path

from common import (
    BACKUP_ROOT, CONFIG, ENCODING, ION_LOCALE_SRC, ION_OVERRIDES_SRC, PATCHES,
    ROOT_LOCALE_SRC, STATSIG_SRC_DIR, ApplyTargets, copy2_best_effort,
    decode_patch_text, ensure_assets_dir, ensure_dir, ensure_file_exists,
    expand_path, find_claude_package, patch_file_pattern, resolve_apply_targets,
    write_text_best_effort,
)


def timestamp() -> str:
    return datetime.now().strftime('%Y%m%d-%H%M%S')


def backup_file(src: Path, backup_dir: Path) -> None:
    ensure_dir(backup_dir)
    if src.exists():
        copy2_best_effort(src, backup_dir / src.name, 'backup file')


def backup_tree(src_dir: Path, backup_dir: Path) -> list[str]:
    ensure_dir(backup_dir)
    copied: list[str] = []
    if not src_dir.exists() or not src_dir.is_dir():
        return copied
    for item in sorted(src_dir.glob('*.json')):
        copy2_best_effort(item, backup_dir / item.name, 'backup tree file')
        copied.append(str(item))
    return copied


def find_existing_paths(candidates: list[str]) -> list[Path]:
    return [p for c in candidates if (p := expand_path(c)).exists()]


def detect_optional_resources(targets: ApplyTargets) -> dict:
    overrides_exists = bool(targets.ion_overrides and targets.ion_overrides.exists())
    statsig_exists = bool(targets.statsig_dir and targets.statsig_dir.exists() and targets.statsig_dir.is_dir())
    return {
        'availableInstallRoots': [str(p) for p in find_existing_paths(CONFIG.get('installCandidates', []))],
        'ionOverrides': {
            'configured': bool(targets.ion_overrides),
            'exists': overrides_exists,
            'sourceExists': ION_OVERRIDES_SRC.exists(),
            'target': str(targets.ion_overrides) if targets.ion_overrides else None,
        },
        'statsig': {
            'configured': bool(targets.statsig_dir),
            'exists': statsig_exists,
            'sourceExists': STATSIG_SRC_DIR.exists(),
            'target': str(targets.statsig_dir) if targets.statsig_dir else None,
            'targetFiles': [str(p) for p in sorted(targets.statsig_dir.glob('*.json'))] if statsig_exists else [],
        },
    }


def analyze_patch_hits(assets_dir: Path) -> list[dict]:
    results = []
    for item in PATCHES:
        find = decode_patch_text(item['find'])
        replace = decode_patch_text(item['replace'])
        matched, replaced = [], []
        paths = sorted(assets_dir.glob(patch_file_pattern(item)))
        for path in paths:
            try:
                text = path.read_text(encoding=ENCODING)
            except Exception:
                continue
            if c := text.count(find):
                matched.append({'file': str(path), 'count': c})
            if c := text.count(replace):
                replaced.append({'file': str(path), 'count': c})
        results.append({
            'description': item['description'],
            'find': item['find'],
            'replace': item['replace'],
            'matched': bool(matched),
            'alreadyPatched': not matched and bool(replaced),
            'totalHits': sum(f['count'] for f in matched),
            'totalReplacedHits': sum(f['count'] for f in replaced),
            'files': matched,
            'replacedFiles': replaced,
        })
    return results


def apply_patches_to_file(path: Path) -> list[tuple[str, int]]:
    text = path.read_text(encoding=ENCODING)
    changed, counts = False, []
    for item in PATCHES:
        find = decode_patch_text(item['find'])
        replace = decode_patch_text(item['replace'])
        if find == replace:
            continue
        if count := text.count(find):
            text = text.replace(find, replace)
            changed = True
            counts.append((item['description'], count))
    if changed:
        write_text_best_effort(path, text, 'asset patch')
    return counts


def sync_optional_resources(run_dir: Path, targets: ApplyTargets) -> dict:
    report = detect_optional_resources(targets)

    if report['ionOverrides']['exists'] and targets.ion_overrides:
        backup_file(targets.ion_overrides, run_dir / 'ion-overrides')
        if ION_OVERRIDES_SRC.exists():
            copy2_best_effort(ION_OVERRIDES_SRC, targets.ion_overrides, 'ion overrides')
            report['ionOverrides']['synced'] = True
        else:
            report['ionOverrides']['synced'] = False
    else:
        report['ionOverrides']['synced'] = False

    if report['statsig']['exists'] and targets.statsig_dir:
        report['statsig']['backedUpFiles'] = backup_tree(targets.statsig_dir, run_dir / 'statsig')
        if STATSIG_SRC_DIR.exists():
            copied = []
            for src_file in sorted(STATSIG_SRC_DIR.glob('*.json')):
                copy2_best_effort(src_file, targets.statsig_dir / src_file.name, 'statsig resource')
                copied.append(str(src_file))
            report['statsig']['synced'] = True
            report['statsig']['copiedFiles'] = copied
        else:
            report['statsig'].update({'synced': False, 'copiedFiles': []})
    else:
        report['statsig'].update({'synced': False, 'copiedFiles': [], 'backedUpFiles': []})

    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Apply Claude Desktop zh-CN localization')
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

    run_dir = BACKUP_ROOT / timestamp()
    ensure_dir(run_dir)
    backup_file(targets.root_locale, run_dir / 'root')
    backup_file(targets.ion_locale, run_dir / 'ion')

    assets_paths = sorted(targets.assets_dir.glob('*.js'))
    patch_analysis = analyze_patch_hits(targets.assets_dir)
    patch_targets = [
        p for p in assets_paths
        if any(f['file'] == str(p) for r in patch_analysis for f in r['files'])
    ]

    for path in patch_targets:
        backup_file(path, run_dir / 'assets')

    copy2_best_effort(ROOT_LOCALE_SRC, targets.root_locale, 'root locale')
    copy2_best_effort(ION_LOCALE_SRC, targets.ion_locale, 'ion locale')
    optional_report = sync_optional_resources(run_dir, targets)

    file_report = []
    for path in patch_targets:
        if counts := apply_patches_to_file(path):
            file_report.append({'file': str(path), 'changes': [{'description': d, 'count': c} for d, c in counts]})

    report = {
        'summary': {
            'totalPatches': len(PATCHES),
            'matchedPatches': sum(1 for r in patch_analysis if r['matched']),
            'alreadyPatchedPatches': sum(1 for r in patch_analysis if r['alreadyPatched']),
            'unmatchedPatches': sum(1 for r in patch_analysis if not r['matched'] and not r['alreadyPatched']),
            'patchedFiles': len(file_report),
        },
        'patches': patch_analysis,
        'files': file_report,
        'optionalResources': optional_report,
        'copiedLocales': {'rootLocale': str(targets.root_locale), 'ionLocale': str(targets.ion_locale)},
    }

    report_path = run_dir / 'apply-report.json'
    report_path.write_text(__import__('json').dumps(report, ensure_ascii=False, indent=2), encoding=ENCODING)
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
