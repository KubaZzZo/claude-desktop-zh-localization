import json
from pathlib import Path

path = Path(r"C:\Users\liukun\Desktop\chineseTwo\locales\ion-zh-CN.json")
data = json.loads(path.read_text(encoding="utf-8"))

updates = {
    "1kdnAB9Eoo": "哪项最符合你的工作？",
    "AfwYGfa3bH": "选择工作职能",
    "uVGZFvhDkp": "选择你的工作职能",
    "sjfw113DWS": "Claude 应该怎么称呼你？",
    "Pfo7emYvVg": "你的偏好将应用于所有聊天，并遵循 <aupLink>Anthropic 的准则</aupLink>。",
    "wUQeP+0qJE": "你的偏好将应用于所有对话，并遵循 <aupLink>Anthropic 的准则</aupLink>。",
    "wwxeIp0xi9": "例如：在给出详细回答前先询问澄清问题",
    "9rL+46Sd/5": "回复完成通知",
    "QjtUOSSv3b": "当 Claude 完成回复时通知我。对于工具调用、研究等耗时较长的任务最有用。",
    "SR19nKO/BD": "桌面应用",
    "XFievosQFD": "能力",
    "BHnMOtM/i0": "要运行代码，请在 设置 > 能力 中启用代码执行和文件创建。",
    "NNApjhmYjK": "桌面端似乎处于离线状态。",
    "DnyceeZdfx": "使用桌面应用，Claude 可以编写代码、处理你的文件，并在你专注于其他工作时自动执行任务。",
    "DycFq0NrtR": "通过桌面应用更充分地使用 Claude",
    "Fp23m9EF1v": "在桌面应用中使用 Claude 编写代码，并在本地运行编码会话。",
    "GAxpg9+rLr": "此浏览器登录的账号与 Claude Desktop 中使用的账号不同。请退出登录，并使用你在 Claude Desktop 中使用的同一账号重新登录，然后再尝试连接。",
    "H/tJ47E9to": "拆解大型任务，并在需要时询问澄清问题。",
    "IALmokeZ+k": "拉取请求创建功能不可用。你可以尝试更新桌面应用。",
    "J6H1cmpYwA": "Claude 桌面应用有一个待安装更新存在已知问题，可能导致崩溃。请改为下载最新版本。",
    "Jh4bqqtwlT": "正在重定向到桌面应用…",
    "KRp72IewWp": "你需要哪些缺失的功能或能力？",
    "KYEZbypo5l": "更新桌面应用以访问代码功能并处理编码任务。",
    "KnGIr1KELi": "更新桌面应用以启用记忆。",
    "KodPa0kb+n": "更新桌面应用以访问 Cowork，并开始交接更长时间的任务。",
    "KztcpqBs9Q": "SSH 浏览需要桌面应用。",
    "NWi9kdlynt": "安装桌面应用，或选择你想从哪里开始。",
    "NuIZMe7zck": "正在编辑的计划任务不可用。请重启桌面应用以启用此功能。",
    "R/j+ofEyrg": "浏览插件需要网络访问权限以连接插件市场。请在 <link>能力设置</link> 中启用网络出口，以浏览和安装插件。",
    "VH2ERZ3Ola": "获取桌面应用",
    "X6AvQomsP7": "Claude 桌面应用的企业部署",
    "aME9ORDmiY": "自定义插件仅在桌面应用中可用。",
    "aRKJtgnmU8": "打开桌面应用",
    "aZ1Z6Z/Fgn": "可以浏览插件，但插件仅可在桌面应用中使用。<link>下载 Claude Desktop</link>",
    "bL5xSAmnhm": "更新桌面应用，以便从手机启动 Cowork 任务。",
    "ccWa9UuF17": "{featureName} 需要最新版桌面应用",
    "dLNfKXUmWM": "读写能力",
    "dhGMfPeh7+": "桌面应用应已自动下载。如果没有，你可以<link>手动下载</link>。",
    "i0tMkvUahu": "此功能需要较新版本的桌面应用。",
    "jAILCM0znC": "全局说明只能在桌面应用中编辑。",
    "jFMy00zVQ3": "访问 {hostname} 的网络已被出口设置阻止。此市场中的插件将无法接收更新。请更新<link>能力设置</link>。",
    "kdPSYW0PZP": "Cowork 由桌面应用提供支持",
    "o/NOFEuWmE": "以下 {count, plural, one {格式} other {格式}} 的文件需要“代码执行和文件创建”。请前往 设置 > 能力 启用：{formats}",
    "o2sXW/MXlq": "重新安装桌面应用以访问 {featureName}，并开始交接更长时间的任务。",
    "p9soKJ+jhS": "随时监控进度、在需要你时收到通知，并审查变更。",
    "qSEmqaxK/a": "下载桌面应用",
    "ueE0OPRyIL": "{currentModelName} 的安全过滤器标记了此聊天。由于 {currentModelName} 具备更高级的能力，因此有额外安全措施，偶尔会暂停正常、安全的聊天。我们正在改进这一点。你可以使用 {fallbackModelName} 继续聊天、<feedback>发送反馈</feedback>，或<learnMore>了解更多</learnMore>。",
    "v8YR2us4Y6": "你只需执行一次。Claude 中任何现有 Google Drive 能力仍会继续工作。",
    "xEK5IfPUXv": "浏览插件需要网络访问权限以连接插件市场。请让组织所有者在能力设置中启用网络出口。",
    "zAJRXPKbOG": "允许 Claude <b>使用</b>这些能力吗？",
}

updated = 0
for key, value in updates.items():
    if key in data:
        data[key] = value
        updated += 1

path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"updated {updated} of {len(updates)}")
