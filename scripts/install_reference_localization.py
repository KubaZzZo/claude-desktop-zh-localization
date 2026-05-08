import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REFERENCE = ROOT / 'scripts' / 'reference'


def run_step(script: str, app_dir: str | None) -> None:
    command = [sys.executable, str(REFERENCE / script)]
    if app_dir:
        command.extend(['--app-dir', app_dir])
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description='Install complete Claude Desktop zh-CN localization')
    parser.add_argument('--app-dir', help='Claude app directory. Auto-detected when omitted.')
    args = parser.parse_args()

    run_step('patch_windowsapps_json_only.py', args.app_dir)
    run_step('patch_chunks_zh_cn.py', args.app_dir)
    print('Complete zh-CN localization installed. Restart Claude Desktop.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
