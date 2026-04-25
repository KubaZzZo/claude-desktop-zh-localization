"""
restore_asar.py
---------------
检测 app.asar 是否损坏（通过 SHA256 校验）。
- 若文件哈希与已知好版本一致 → 直接跳过，继续汉化
- 若文件损坏或哈希不匹配 → 提示用户手动替换后重新运行

已知好版本信息：
  版本：Claude 1.3883.0.0
  SHA256：06b87a63877d6546173924651f69c88b407eadbe1ff6dd6d0c1fb004c79da567
  大小：28839903 bytes (27 MB)

如果 app.asar 损坏，请重新安装 Claude Desktop 或从备份恢复，
然后重新运行 apply.bat。
"""
import hashlib
import sys
from pathlib import Path

ASAR_PATH = Path(r"C:\Program Files\WindowsApps\Claude_1.3883.0.0_x64__pzs8sxrjxfjjc\app\resources\app.asar")
KNOWN_SHA256 = "06b87a63877d6546173924651f69c88b407eadbe1ff6dd6d0c1fb004c79da567"
KNOWN_SIZE = 28839903


def check_asar() -> bool:
    if not ASAR_PATH.exists():
        print(f"[错误] 未找到 app.asar: {ASAR_PATH}")
        print("请确认 Claude Desktop 已安装，路径是否正确。")
        return False

    size = ASAR_PATH.stat().st_size
    if size != KNOWN_SIZE:
        print(f"[警告] app.asar 大小异常: {size} bytes (期望 {KNOWN_SIZE} bytes)")

    print("正在校验 app.asar 完整性...")
    sha256 = hashlib.sha256(ASAR_PATH.read_bytes()).hexdigest()

    if sha256 == KNOWN_SHA256:
        print("[OK] app.asar 完整，可以继续汉化。")
        return True
    else:
        print(f"[错误] app.asar 已损坏！")
        print(f"  当前哈希: {sha256}")
        print(f"  期望哈希: {KNOWN_SHA256}")
        print()
        print("修复方法：")
        print("  1. 重新安装 Claude Desktop（会自动替换 app.asar）")
        print("  2. 或从备份目录恢复：运行 rollback.bat")
        print("  3. 修复后重新运行 apply.bat")
        return False


if __name__ == "__main__":
    ok = check_asar()
    sys.exit(0 if ok else 1)
