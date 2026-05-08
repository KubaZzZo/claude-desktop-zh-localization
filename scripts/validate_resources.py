import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = [
    ROOT / 'locales' / 'root-zh-CN.json',
    ROOT / 'locales' / 'ion-zh-CN.json',
    ROOT / 'locales' / 'ion-zh-CN.overrides.json',
    ROOT / 'locales' / 'statsig' / 'zh-CN.json',
    ROOT / 'patches' / 'main-ui-patches.json',
    ROOT / 'scripts' / 'reference' / 'patch_windowsapps_json_only.py',
    ROOT / 'scripts' / 'reference' / 'patch_chunks_zh_cn.py',
    ROOT / 'scripts' / 'reference' / 'restore_claude_zh_cn_windowsapps.py',
]


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    for path in FILES:
        if not path.exists():
            print(f'SKIP missing optional file: {path.relative_to(ROOT)}')
            continue
        if path.suffix == '.json':
            data = load_json(path)
            if not isinstance(data, (dict, list)):
                raise SystemExit(f'Expected JSON object or array at: {path}')
            print(f'OK {path.relative_to(ROOT)}: {len(data)} top-level entries')
        else:
            compile(path.read_text(encoding='utf-8-sig'), str(path), 'exec')
            print(f'OK {path.relative_to(ROOT)}: syntax')
    print('All resource files validated.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
