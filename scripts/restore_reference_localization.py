import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REFERENCE = ROOT / 'scripts' / 'reference'


def main() -> int:
    parser = argparse.ArgumentParser(description='Restore Claude Desktop files from zh-CN backup')
    parser.add_argument('--app-dir', help='Claude app directory. Auto-detected when omitted.')
    args = parser.parse_args()

    command = [sys.executable, str(REFERENCE / 'restore_claude_zh_cn_windowsapps.py')]
    if args.app_dir:
        command.extend(['--app-dir', args.app_dir])
    subprocess.run(command, cwd=ROOT, check=True)
    print('Claude Desktop restored from backup. Restart Claude Desktop.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
