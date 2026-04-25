import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((PROJECT_ROOT / 'config.json').read_text(encoding='utf-8'))
PATCHES = json.loads((PROJECT_ROOT / 'patches' / 'main-ui-patches.json').read_text(encoding='utf-8'))
ENCODING = CONFIG.get('encoding', 'utf-8')

ROOT_LOCALE_DST = Path(CONFIG['applyTargets']['rootLocale'])
ION_LOCALE_DST = Path(CONFIG['applyTargets']['ionLocale'])
ASSETS_DIR = Path(CONFIG['applyTargets']['assetsDir'])


def decode_patch_text(value: str) -> str:
    return value.encode('utf-8').decode('unicode_escape')


def ensure_file_exists(path: Path, description: str) -> None:
    if not path.exists():
        raise SystemExit(f'{description} not found or inaccessible: {path}')


def ensure_assets_dir(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f'Assets directory not found or inaccessible: {path}')
    if not path.is_dir():
        raise SystemExit(f'Assets path is not a directory: {path}')


def verify_locales() -> list[str]:
    issues: list[str] = []
    root_text = ROOT_LOCALE_DST.read_text(encoding=ENCODING)
    ion_text = ION_LOCALE_DST.read_text(encoding=ENCODING)
    expected_entries = [
        ('"wVu1FLTwAn": "开始吧"', 'ion zh-CN 缺少开始吧'),
        ('"CJsWpnmYD4": "开始处理你的待办事项"', 'ion zh-CN 缺少首页标题翻译'),
        ('"EfdnINFnIz": "文件"', 'root zh-CN 缺少顶层菜单翻译'),
        ('"qm/eL5Y8Fl": "其他选项"', 'ion zh-CN 缺少其他选项翻译'),
        ('"qmzHEfH73H": "测试安装说明"', 'ion zh-CN 缺少安装说明翻译'),
    ]
    for expected, message in expected_entries:
        target_text = root_text if 'root zh-CN' in message else ion_text
        if expected not in target_text:
            issues.append(message)
    return issues


def verify_assets() -> list[str]:
    issues: list[str] = []
    for patch in PATCHES:
        old = decode_patch_text(patch['find'])
        for path in ASSETS_DIR.glob('*.js'):
            try:
                text = path.read_text(encoding=ENCODING)
            except Exception:
                continue
            if old in text:
                issues.append(f"仍有英文回退残留: {patch['description']} -> {path.name}")
    return issues


def main() -> None:
    ensure_file_exists(ROOT_LOCALE_DST, 'Target root locale')
    ensure_file_exists(ION_LOCALE_DST, 'Target ion locale')
    ensure_assets_dir(ASSETS_DIR)

    issues: list[str] = []
    issues.extend(verify_locales())
    issues.extend(verify_assets())
    if issues:
        print('VERIFY FAILED')
        for item in issues:
            print(item)
        raise SystemExit(1)
    print('VERIFY OK')


if __name__ == '__main__':
    main()
