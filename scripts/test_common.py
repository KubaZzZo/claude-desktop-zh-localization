import sys
import json
import shutil
import pytest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

_mock_config = {
    'targetResourceRoot': '/fake',
    'applyTargets': {
        'rootLocale': '/fake/zh-CN.json',
        'ionLocale': '/fake/ion/zh-CN.json',
        'assetsDir': '/fake/assets',
    },
    'backupDirName': 'backups',
    'encoding': 'utf-8',
    'verifyEntries': [
        {'file': 'ion', 'expected': '"key1": "中文"', 'message': '缺少 key1'},
    ],
}
_mock_patches = [
    {'description': 'targeted patch', 'filePattern': 'index-*.js', 'find': 'Code', 'replace': '代码'},
    {'description': 'test patch', 'find': 'Hello', 'replace': '你好'},
]

with patch('builtins.open'), \
     patch('pathlib.Path.read_text', side_effect=[
         json.dumps(_mock_config), json.dumps(_mock_patches)
     ]):
    sys.modules.pop('common', None)
    import common

# 使用项目内临时目录，避免 AppData/Temp 权限问题
_TEST_TMP = Path(__file__).parent.parent / '.test_tmp'


@pytest.fixture(autouse=True)
def tmp_dir():
    _TEST_TMP.mkdir(exist_ok=True)
    yield _TEST_TMP
    shutil.rmtree(_TEST_TMP, ignore_errors=True)


def tmp(name: str) -> Path:
    return _TEST_TMP / name


# --- decode_patch_text ---

def test_decode_patch_text_plain():
    assert common.decode_patch_text('Hello') == 'Hello'


def test_decode_patch_text_escape():
    assert common.decode_patch_text('\\u4e2d\\u6587') == '中文'


def test_decode_patch_text_preserves_utf8_chinese():
    assert common.decode_patch_text('协作') == '协作'


# --- ensure_file_exists ---

def test_ensure_file_exists_raises_when_missing():
    with pytest.raises(SystemExit):
        common.ensure_file_exists(tmp('missing.txt'), 'test file')


def test_ensure_file_exists_passes_when_present():
    f = tmp('exists.txt')
    f.write_text('ok')
    common.ensure_file_exists(f, 'test file')


# --- ensure_assets_dir ---

def test_ensure_assets_dir_raises_when_missing():
    with pytest.raises(SystemExit):
        common.ensure_assets_dir(tmp('no_dir'))


def test_ensure_assets_dir_raises_when_file():
    f = tmp('file.txt')
    f.write_text('x')
    with pytest.raises(SystemExit):
        common.ensure_assets_dir(f)


def test_ensure_assets_dir_passes_for_dir():
    d = tmp('assets')
    d.mkdir()
    common.ensure_assets_dir(d)


# --- ensure_dir ---

def test_ensure_dir_creates_directory():
    new_dir = tmp('new/nested')
    common.ensure_dir(new_dir)
    assert new_dir.exists()


def test_ensure_dir_raises_with_description_when_missing():
    with pytest.raises(SystemExit):
        common.ensure_dir(tmp('missing'), 'required dir')


# --- expand_path ---

def test_expand_path_returns_path():
    assert isinstance(common.expand_path('/some/path'), Path)


# --- resolve_apply_targets ---

def test_resolve_apply_targets_uses_config_when_no_app_dir():
    targets = common.resolve_apply_targets()

    assert targets.root_locale == Path('/fake/zh-CN.json')
    assert targets.ion_locale == Path('/fake/ion/zh-CN.json')
    assert targets.assets_dir == Path('/fake/assets')


def test_resolve_apply_targets_auto_detects_latest_when_enabled():
    app_dir = tmp('Claude/app')

    with patch('common.find_claude_package', return_value=app_dir):
        targets = common.resolve_apply_targets(auto_detect=True)

    assert targets.resource_root == app_dir / 'resources'
    assert targets.root_locale == app_dir / 'resources' / 'zh-CN.json'
    assert targets.ion_locale == app_dir / 'resources' / 'ion-dist' / 'i18n' / 'zh-CN.json'
    assert targets.assets_dir == app_dir / 'resources' / 'ion-dist' / 'assets' / 'v1'


def test_resolve_apply_targets_derives_paths_from_app_dir():
    app_dir = tmp('Claude/app')

    targets = common.resolve_apply_targets(app_dir)

    assert targets.resource_root == app_dir / 'resources'
    assert targets.root_locale == app_dir / 'resources' / 'zh-CN.json'
    assert targets.ion_locale == app_dir / 'resources' / 'ion-dist' / 'i18n' / 'zh-CN.json'
    assert targets.assets_dir == app_dir / 'resources' / 'ion-dist' / 'assets' / 'v1'
    assert targets.ion_overrides == app_dir / 'resources' / 'ion-dist' / 'i18n' / 'zh-CN.overrides.json'
    assert targets.statsig_dir == app_dir / 'resources' / 'ion-dist' / 'i18n' / 'statsig'


def test_find_claude_package_returns_latest_app_dir():
    base = tmp('windowsapps')
    older = base / 'Claude_1.0.0.0_x64__pzs8sxrjxfjjc' / 'app' / 'resources'
    newer = base / 'Claude_2.0.0.0_x64__pzs8sxrjxfjjc' / 'app' / 'resources'
    older.mkdir(parents=True)
    newer.mkdir(parents=True)
    (older / 'en-US.json').write_text('{}')
    (newer / 'en-US.json').write_text('{}')

    assert common.find_claude_package(base) == newer.parent


def test_patch_file_pattern_defaults_to_all_js():
    assert common.patch_file_pattern({'find': 'Hello', 'replace': '你好'}) == '*.js'


def test_patch_file_pattern_scans_all_assets_by_default():
    assert common.patch_file_pattern({'filePattern': 'index-*.js'}) == '*.js'


def test_patch_file_pattern_can_use_configured_pattern():
    assert common.patch_file_pattern({'scanAllAssets': False, 'filePattern': 'index-*.js'}) == 'index-*.js'


def test_patch_file_pattern_wildcards_hashed_chunk_names():
    item = {'scanAllAssets': False, 'filePattern': 'cbc59a8af-DbOQVv5S.js'}

    assert common.patch_file_pattern(item) == 'cbc59a8af-*.js'
