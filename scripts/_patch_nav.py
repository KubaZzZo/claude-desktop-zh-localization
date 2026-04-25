import json
from pathlib import Path

path = Path(__file__).resolve().parent.parent / 'locales' / 'ion-zh-CN.json'
data = json.loads(path.read_text(encoding='utf-8'))

# 侧边栏/任务栏/导航常见标签
translations = {
    # 导航
    'ZT0z9z6v6s': '询问',
    'rEBc+0T8zS': '扮演 Claude',
    'KsA5dxbgQZ': '询问 Claude',
    'XfP/HbNKQz': '询问 Claude 任何问题',
    'AEustq5R+6': '由 Claude 自动整理',
    # 状态
    '3cdAZ366W5': '（需要关注）',
    '8P2GX1fsW6': '（不再可见）',
    'fy+VEx/YUC': '（不再可见）',
    'MCSWQARMox': '（空）',
    'vg7ixeSm+z': '（未安装）',
    'N01HT5JT7d': '（已编辑）',
    'yKEwi7f1HL': '（已取消）',
    # 计费（简单的）
    'yRs7NosnRw': '（含税）',
    'dvptwJGqul': '（如适用）',
    '1pfSshF491': '（不含用量）',
    'H/9uGFjKzR': '+ 税',
    # 常见操作
    'VMIM8/fAKn': '分析',
    'HJv0iTm4zI': '分析',
    'bF46uAWl+6': '按字母排序',
    'ISly67nSyK': '同意',
    'gC6HyzeGoV': '同意并部署',
    '2C6TrW95uE': '年付',
    'ZSCbZACJ+n': '按年计费',
    'osyYBn10tk': '年度总计',
    'IzYUCGlYL9': '归档中...',
    'nc7BrwYVL+': '参数',
    'pgaCSv2/6H': '参数',
    'iHN12uxiqf': '管理员',
    'QGVI63s1dJ': '智能体',
    'GBnvl1JpeB': '智能体',
    'bC9979Pv0w': '即将完成...',
    'xvEaun0GGh': '始终显示最新版本',
    '3VG8rbxa4v': '发生未知错误',
    'FFJy9Pgt4P': '认证过程中发生未知错误。',
    'tM90hqjWj0': '等待输入',
    '5kfntb9RKU': '取消',
    'AHk/hh2tts': '取消中...',
    '90evMzS2tV': '取消中...',
    '3wsVWFbC1x': '已取消',
    'U/my45Rm4s': '已列入黑名单',
    'lxjxGdlvau': '错误率',
    'FFFScMMBYY': '错误率（30天）',
    '1rMFg0JQMQ': '审计日志',
    '57VhQbitLE': '认证错误',
    'Fh0QP1M2C8': '认证成功',
    'sHRXIdTx3F': '自动重载',
    'Fvcg75HZwF': '自动重载已禁用',
    'JTSyIVn+xw': '自动重载已启用',
    'unT/B/rqrN': '自动重载已关闭',
    'C0IHaxOPo4': '余额不足时自动重载',
    'qQHsVqEort': '自动化浏览器任务',
    'nFa1MsHw4R': '审批',
    'WCaf5CZSTt': '批准',
    'qbXbBIixhT': '自动批准',
    'm/7+82LTth': '自动批准（即时）',
    'Ln8ciHiZMb': '自动批准未来请求',
    '6XFO/Cw7Ld': '已批准',
    'Z/DKbn2gfH': '请求权限',
    'GkOEztGVgI': '关联会话',
}

updated = 0
for k, v in translations.items():
    if k in data:
        data[k] = v
        updated += 1

path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Updated {updated} entries')
