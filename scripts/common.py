import json
import os
import shutil
import stat
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((PROJECT_ROOT / 'config.json').read_text(encoding='utf-8'))
PATCHES = json.loads((PROJECT_ROOT / 'patches' / 'main-ui-patches.json').read_text(encoding='utf-8'))

ENCODING = CONFIG.get('encoding', 'utf-8')
BACKUP_ROOT = PROJECT_ROOT / CONFIG['backupDirName']
ROOT_LOCALE_SRC = PROJECT_ROOT / 'locales' / 'root-zh-CN.json'
ION_LOCALE_SRC = PROJECT_ROOT / 'locales' / 'ion-zh-CN.json'
ROOT_LOCALE_DST = Path(CONFIG['applyTargets']['rootLocale'])
ION_LOCALE_DST = Path(CONFIG['applyTargets']['ionLocale'])
ASSETS_DIR = Path(CONFIG['applyTargets']['assetsDir'])

_optional = CONFIG.get('optionalTargets', {})
ION_OVERRIDES_SRC = PROJECT_ROOT / 'locales' / 'ion-zh-CN.overrides.json'
ION_OVERRIDES_DST = Path(_optional['ionOverrides']) if _optional.get('ionOverrides') else None
STATSIG_SRC_DIR = PROJECT_ROOT / 'locales' / 'statsig'
STATSIG_DST_DIR = Path(_optional['statsigDir']) if _optional.get('statsigDir') else None


@dataclass(frozen=True)
class ApplyTargets:
    resource_root: Path
    root_locale: Path
    ion_locale: Path
    assets_dir: Path
    ion_overrides: Path | None
    statsig_dir: Path | None


def decode_patch_text(value: str) -> str:
    if '\\' not in value:
        return value
    return value.encode('utf-8').decode('unicode_escape')


def ensure_file_exists(path: Path, description: str) -> None:
    if not path.exists():
        raise SystemExit(f'{description} not found or inaccessible: {path}')


def ensure_assets_dir(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f'Assets directory not found or inaccessible: {path}')
    if not path.is_dir():
        raise SystemExit(f'Assets path is not a directory: {path}')


def ensure_dir(path: Path, description: str = '') -> None:
    if description and not path.exists():
        raise SystemExit(f'{description} not found: {path}')
    path.mkdir(parents=True, exist_ok=True)


def expand_path(value: str) -> Path:
    return Path(os.path.expandvars(value))


def patch_file_pattern(item: dict) -> str:
    if item.get('scanAllAssets', True):
        return '*.js'
    pattern = item.get('filePattern') or item.get('file') or '*.js'
    if pattern.endswith('.js') and '-' in pattern and '*' not in pattern:
        return pattern.split('-', 1)[0] + '-*.js'
    return pattern


def find_claude_package(base: Path = Path(r'C:\Program Files\WindowsApps')) -> Path | None:
    if not base.exists():
        return None
    candidates = sorted(base.glob('Claude_*_x64__*/app/resources/en-US.json'), reverse=True)
    if not candidates:
        return None
    return candidates[0].parent.parent


def resolve_apply_targets(app_dir: Path | str | None = None, auto_detect: bool = False) -> ApplyTargets:
    if auto_detect and not app_dir:
        app_dir = find_claude_package()
    if app_dir:
        resource_root = Path(app_dir) / 'resources'
        i18n_dir = resource_root / 'ion-dist' / 'i18n'
        return ApplyTargets(
            resource_root=resource_root,
            root_locale=resource_root / 'zh-CN.json',
            ion_locale=i18n_dir / 'zh-CN.json',
            assets_dir=resource_root / 'ion-dist' / 'assets' / 'v1',
            ion_overrides=i18n_dir / 'zh-CN.overrides.json',
            statsig_dir=i18n_dir / 'statsig',
        )
    return ApplyTargets(
        resource_root=Path(CONFIG['targetResourceRoot']),
        root_locale=ROOT_LOCALE_DST,
        ion_locale=ION_LOCALE_DST,
        assets_dir=ASSETS_DIR,
        ion_overrides=ION_OVERRIDES_DST,
        statsig_dir=STATSIG_DST_DIR,
    )


def copy2_best_effort(src: Path, dst: Path, context: str) -> bool:
    try:
        shutil.copy2(src, dst)
        return True
    except PermissionError:
        if dst.exists():
            try:
                dst.chmod(dst.stat().st_mode | stat.S_IWRITE)
            except OSError:
                pass
        try:
            shutil.copy2(src, dst)
            return True
        except OSError as error:
            print(f'Warning: cannot copy {context} from {src} to {dst}: {error}; skipping')
            return False
    except OSError as error:
        print(f'Warning: cannot copy {context} from {src} to {dst}: {error}; skipping')
        return False


def write_text_best_effort(path: Path, text: str, context: str, encoding: str = ENCODING) -> bool:
    try:
        path.write_text(text, encoding=encoding)
        return True
    except PermissionError:
        try:
            path.chmod(path.stat().st_mode | stat.S_IWRITE)
        except OSError:
            pass
        try:
            path.write_text(text, encoding=encoding)
            return True
        except OSError as error:
            print(f'Warning: cannot write {context} at {path}: {error}; skipping')
            return False
    except OSError as error:
        print(f'Warning: cannot write {context} at {path}: {error}; skipping')
        return False
