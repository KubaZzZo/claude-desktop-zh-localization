"""
patch asar menu labels - 用空格填充保持字节长度一致
"""
import struct, json
from pathlib import Path

ASAR = Path(r'C:/Program Files/WindowsApps/Claude_1.3883.0.0_x64__pzs8sxrjxfjjc/app/resources/app.asar')
BACKUP = ASAR.with_suffix('.asar.bak')

MENU_TRANSLATIONS = {
    'Reload MCP Configuration': '重新加载 MCP 配置',
    'Enable Main Process Debugger': '启用主进程调试器',
    'Record Performance Trace': '记录性能追踪',
    'Write Main Process Heap Snapshot': '写入主进程堆快照',
    'Record Memory Trace (auto-stop)': '记录内存追踪(自动停)',
    'Record Memory Trace': '记录内存追踪',
    'Show Debug Window': '显示调试窗口',
    'Hide Debug Window': '隐藏调试窗口',
    'Computer Use Debug Panel': '计算机调试面板',
    'Main process log': '主进程日志',
    'Cowork VM log': 'Cowork日志',
    'Crash report list': '崩溃报告列表',
    'Inference provider status': '推理提供商状态',
    'Network reachability': '网络可达性',
    'Package managers': '包管理器',
    'Paste and Match Style': '粘贴并匹配样式',
    'Start Cowork VM': '启动CoworkVM',
    'Stop Cowork VM': '停止CoworkVM',
    'Zoom In (numpad)': '放大(数字键盘)',
    'Zoom Out (numpad)': '缩小(数字键盘)',
    'Actual Size (numpad)': '实际大小(数字键盘)',
    'Configuration': '配置',
    'Emulate Support': '模拟支持',
    'Force Disable Host Loop': '强制禁用主机循环',
}

data = bytearray(ASAR.read_bytes())
json_size = struct.unpack_from('<I', data, 12)[0]
header = json.loads(bytes(data[16:16+json_size]).decode('utf-8'))
base_offset = 16 + json_size

vite = header['files']['.vite']['files']['build']['files']['index.js']
file_offset = base_offset + int(vite['offset'])
file_size = vite['size']

raw = bytes(data[file_offset:file_offset+file_size])

replaced = 0
for en, zh in MENU_TRANSLATIONS.items():
    needle = f'label:"{en}"'.encode('utf-8')
    zh_bytes = zh.encode('utf-8')
    # 计算可用空间：needle 长度
    available = len(needle) - len(b'label:"') - len(b'"')
    # 截断或填充中文到恰好 available 字节
    # 先尝试直接替换，若字节数超出则缩短中文
    if len(zh_bytes) <= available:
        # 用空格填充到 available 字节
        padded = zh_bytes + b' ' * (available - len(zh_bytes))
    else:
        # 中文字节超出，跳过
        print(f'SKIP too long: {en} ({len(zh_bytes)} > {available})')
        continue
    replacement = b'label:"' + padded + b'"'
    assert len(replacement) == len(needle), f'{len(replacement)} != {len(needle)}'
    if needle in raw:
        raw = raw.replace(needle, replacement, 1)
        replaced += 1
        print(f'OK: {en} -> {zh}')
    else:
        print(f'NOT FOUND: {en}')

if len(raw) != file_size:
    print(f'ERROR: size changed')
else:
    data[file_offset:file_offset+file_size] = raw
    ASAR.write_bytes(bytes(data))
    print(f'\nDone. Replaced {replaced} labels.')
