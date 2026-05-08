import json
import re
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


def iter_string_values(data, prefix=''):
    if isinstance(data, dict):
        for key, value in data.items():
            path = f'{prefix}.{key}' if prefix else str(key)
            yield from iter_string_values(value, path)
    elif isinstance(data, list):
        for index, value in enumerate(data):
            path = f'{prefix}[{index}]'
            yield from iter_string_values(value, path)
    elif isinstance(data, str):
        yield prefix, data


def is_question_mark_placeholder(value: str) -> bool:
    stripped = value.strip()
    return bool(re.fullmatch(r'\?+', stripped) or re.search(r'\?\?\?+', stripped))


def validate_no_placeholder_values(data, path: Path) -> None:
    bad = [
        f'{key}={value!r}'
        for key, value in iter_string_values(data)
        if is_question_mark_placeholder(value)
    ]
    if bad:
        sample = '; '.join(bad[:10])
        raise SystemExit(f'Placeholder question-mark translations in {path}: {sample}')


def main() -> int:
    for path in FILES:
        if not path.exists():
            print(f'SKIP missing optional file: {path.relative_to(ROOT)}')
            continue
        if path.suffix == '.json':
            data = load_json(path)
            if not isinstance(data, (dict, list)):
                raise SystemExit(f'Expected JSON object or array at: {path}')
            validate_no_placeholder_values(data, path.relative_to(ROOT))
            print(f'OK {path.relative_to(ROOT)}: {len(data)} top-level entries')
        else:
            compile(path.read_text(encoding='utf-8-sig'), str(path), 'exec')
            print(f'OK {path.relative_to(ROOT)}: syntax')
    print('All resource files validated.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
