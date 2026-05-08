import argparse
import json
import re
from pathlib import Path

from common import ENCODING, ION_LOCALE_SRC, resolve_apply_targets


DEFAULT_MESSAGE_PATTERNS = [
    re.compile(r'defaultMessage:"(?P<msg>(?:\\.|[^"\\]){1,500})",id:"(?P<id>[^"]+)"'),
    re.compile(r'id:"(?P<id>[^"]+)",defaultMessage:"(?P<msg>(?:\\.|[^"\\]){1,500})"'),
]

EXACT_TRANSLATIONS = {
    "Which organization is this about?": "这是关于哪个组织？",
    "I'd like help sizing a plan for {orgName}.": "我想请你帮忙为 {orgName} 选择合适的套餐规模。",
    "(internal override) Looking at org {uuid}.": "（内部覆盖）正在查看组织 {uuid}。",
    "Org UUID (internal override)": "组织 UUID（内部覆盖）",
    "Your quote": "你的报价",
    "Est. annual": "预计年费",
    "Answer a few questions and your recommended plan will appear here.": "回答几个问题后，推荐套餐会显示在这里。",
    "Continue to checkout": "继续结账",
    "Claude Sales": "Claude 销售",
    "Hi {name}! Which of your organizations can I help with?": "你好，{name}！我可以帮你处理哪个组织？",
    "Hi! Which of your organizations can I help with?": "你好！我可以帮你处理哪个组织？",
    "Choose an organization to start": "选择一个组织开始",
    "Ask about pricing, security, or what plan fits": "询问价格、安全性或适合的套餐",
    "Ready to check out": "准备结账",
    "Your request has been sent to our sales team.": "你的请求已发送给我们的销售团队。",
    "Based on what you've described, a smaller plan is the better fit.": "根据你的描述，较小的套餐更适合。",
    "This isn't something I can help with here.": "这个问题我无法在这里帮助处理。",
    "Back to plans": "返回套餐",
    "Use a different card": "使用其他银行卡",
    "For your security, please re-enter the security code (CVC) for your saved card.": "为保障安全，请重新输入已保存银行卡的安全码（CVC）。",
    "Confirm payment": "确认付款",
    "Every plan includes Claude Code, unlimited projects, and access to our latest models.": "每个套餐都包含 Claude Code、不限数量的项目，以及最新模型访问权限。",
    "Gift purchases aren't available for your account at this time.": "你的账号目前无法购买礼品。",
    "We'll email {name}'s gift to {toEmail}. <link>Learn more</link>.": "我们会将 {name} 的礼品通过邮件发送给 {toEmail}。<link>了解更多</link>。",
    "Couldn’t save that change": "无法保存该更改",
    "Couldn't save that change": "无法保存该更改",
    "Avatar": "头像",
    "Clear avatar": "清除头像",
    "Instructions can't be changed because one of your orgs has an encryption key configured.": "由于你的某个组织配置了加密密钥，无法更改说明。",
    "Instructions for Claude": "给 Claude 的说明",
    "Preferences": "偏好设置",
    "Couldn’t update that setting": "无法更新该设置",
    "Couldn't update that setting": "无法更新该设置",
    "Get notified when Claude has finished a response. Useful for long-running tasks.": "Claude 完成回复时通知你。适合耗时较长的任务。",
    "Code notifications": "代码通知",
    "Claude can choose to notify you about important updates from a Code session.": "Claude 可以选择通知你代码会话中的重要更新。",
    "Code permission requests": "代码权限请求",
    "Get a push notification when Claude needs your approval to run a command in a Code session.": "当 Claude 在代码会话中需要你批准运行命令时，发送推送通知。",
    "Security scan emails": "安全扫描邮件",
    "Get an email when a Claude Code security scan finishes.": "Claude Code 安全扫描完成时发送邮件。",
    "Legacy": "旧版",
    "Previous-generation model. May be removed in a future update.": "上一代模型。可能会在未来更新中移除。",
    "Settings default model not recognized": "无法识别设置中的默认模型",
    "Setting up plugins...": "正在设置插件...",
    "Error details copied to clipboard. Paste in Slack (⌘V), then drag the zip from Finder into the message.": "错误详情已复制到剪贴板。粘贴到 Slack（⌘V），然后将 Finder 中的 zip 文件拖入消息。",
    "Get logs and open Slack": "获取日志并打开 Slack",
    "Image copied to clipboard": "图片已复制到剪贴板",
    "Couldn't copy image.": "无法复制图片。",
    "Couldn't save image.": "无法保存图片。",
    "Save image": "保存图片",
    "Ran skill": "已运行技能",
    "Running skill": "正在运行技能",
    "Sent": "已发送",
    "Sending": "正在发送",
    "Dreaming": "正在构思",
    "Rewind to an earlier message or clear the session to continue.": "回退到更早的消息，或清空会话后继续。",
    "This image is too large to send. Rewind to remove it and try again.": "这张图片太大，无法发送。请回退并移除后重试。",
    "Try sending your message again.": "请尝试重新发送消息。",
    "View attached image {n}": "查看附件图片 {n}",
    "Attached image": "附件图片",
    "Running — click to cancel": "正在运行 - 点击取消",
    "Message from session {name}": "来自会话 {name} 的消息",
    "Message from teammate {name}": "来自队友 {name} 的消息",
    "Channel message": "频道消息",
    "Remove queued message": "移除排队消息",
    "Start free Claude Code trial": "开始 Claude Code 免费试用",
    "Ready for review": "可供审核",
    "Start on {host}": "在 {host} 上开始",
    "Dismiss error": "关闭错误",
    "Edit link": "编辑链接",
    "Remove link": "移除链接",
    "Load all{serverTotal, number}invites": "加载全部 {serverTotal, number} 个邀请",
    "Load all {serverTotal, number} invites": "加载全部 {serverTotal, number} 个邀请",
    "Continue to Claude": "继续使用 Claude",
    "You just got access to Claude Code": "你刚刚获得了 Claude Code 访问权限",
    "Give the gift of Claude": "赠送 Claude 礼品会员",
    "What is a Claude gift membership?": "什么是 Claude 礼品会员？",
    "What should Claude call you?": "Claude 应该怎么称呼你？",
    "View on Google Maps": "在 Google 地图中查看",
    "Total tokens": "Token 总量",
    "Daily tokens by model": "按模型统计的每日 Token",
    "Hook re-prompted Claude": "钩子重新提示了 Claude",
    "Install Git": "安装 Git",
}

WORD_TRANSLATIONS = {
    "Cancel": "取消",
    "Close": "关闭",
    "Delete": "删除",
    "Dismiss": "关闭",
    "Back": "返回",
    "Continue": "继续",
    "Name": "名称",
    "Save": "保存",
    "Try again": "重试",
    "Connect": "连接",
    "Connectors": "连接器",
    "Download": "下载",
    "Copied": "已复制",
    "Done": "完成",
    "Install": "安装",
    "More options": "更多选项",
    "Skip": "跳过",
    "Settings": "设置",
    "Upgrade": "升级",
    "Copy": "复制",
    "Preview": "预览",
    "Show more": "显示更多",
    "Skills": "技能",
    "Plugins": "插件",
    "Untitled": "无标题",
    "Archive": "归档",
    "Deny": "拒绝",
    "Edit": "编辑",
    "Learn more": "了解更多",
    "Next": "下一步",
    "Custom": "自定义",
    "Manage": "管理",
    "Retry": "重试",
    "Remove": "移除",
    "Show less": "显示更少",
    "Active": "活跃",
    "All": "全部",
    "Create": "创建",
    "New": "新建",
    "Submit": "提交",
    "Enable": "启用",
    "Instructions": "说明",
    "Open": "打开",
    "Share": "分享",
    "Status": "状态",
    "Update": "更新",
    "Copy link": "复制链接",
    "Refresh": "刷新",
    "Save changes": "保存更改",
    "Untitled session": "未命名会话",
    "Description": "描述",
    "Rename": "重命名",
    "Go back": "返回",
    "Running": "正在运行",
    "Add": "添加",
    "Allow": "允许",
    "Scheduled": "已安排",
    "Chats": "聊天",
    "Error": "错误",
    "Disable": "禁用",
    "Disconnect": "断开连接",
    "Local": "本地",
    "Manage connectors": "管理连接器",
    "Not now": "暂不",
    "Open sidebar": "打开侧边栏",
    "Search": "搜索",
    "Select": "选择",
    "Show in Folder": "在文件夹中显示",
    "Uninstall": "卸载",
    "Connected": "已连接",
    "Customize": "自定义",
    "Folder instructions": "文件夹说明",
    "Global instructions": "全局说明",
    "Later": "稍后",
    "Manual": "手动",
    "Other": "其他",
    "Shared": "已共享",
    "Turn on": "开启",
    "Archived": "已归档",
    "Back to Login": "返回登录",
    "Daily": "每日",
    "Details": "详情",
    "General": "通用",
    "Hourly": "每小时",
    "Reconnect": "重新连接",
    "Unpin": "取消固定",
    "Weekly": "每周",
    "Clear storage": "清除存储",
    "Close sidebar": "关闭侧边栏",
    "Contact sales": "联系销售",
    "Disabled": "已禁用",
    "Failed": "失败",
    "Memory": "记忆",
    "New session": "新建会话",
    "Request": "请求",
    "Something went wrong": "出了点问题",
    "Unlimited": "不限量",
    "Upgrade to try": "升级以试用",
    "Use a different email": "使用其他邮箱",
    "Add plugin": "添加插件",
    "Awaiting input": "等待输入",
    "Completed": "已完成",
    "Environment": "环境",
    "Get started": "开始使用",
    "I have my own topic": "我有自己的主题",
    "Model": "模型",
    "New task": "新建任务",
    "Organization": "组织",
    "Pin": "固定",
    "Published": "已发布",
    "Schedule": "计划",
    "Stop": "停止",
    "Weekdays": "工作日",
    "Actions": "操作",
    "Always allow": "始终允许",
    "Branch": "分支",
    "Close panel": "关闭面板",
    "Enabled": "已启用",
    "Hide": "隐藏",
    "Home": "首页",
    "In progress": "进行中",
    "Incognito chat": "隐身聊天",
    "Log out": "退出登录",
    "Members": "成员",
    "Output": "输出",
    "Previous page": "上一页",
    "Private": "私有",
    "Used a tool": "使用了工具",
    "Add repository": "添加仓库",
    "Browse plugins": "浏览插件",
    "Buy extra usage": "购买额外用量",
    "Copy path": "复制路径",
    "Default": "默认",
    "Disconnected": "已断开连接",
}

MIXED_REPLACEMENTS = {
    "继续Claude": "继续使用 Claude",
    "继续 Claude": "继续使用 Claude",
    "安装Git": "安装 Git",
    "Token 总数": "Token 总量",
    "每日Token": "每日 Token",
    "Claude应该": "Claude 应该",
    "送给Claude的礼物": "赠送 Claude 礼品会员",
    "去找Claude": "前往 Claude",
    "Claude码": "Claude Code",
    "胡克重新提示Claude": "钩子重新提示了 Claude",
    "在Google Maps上查看": "在 Google 地图中查看",
    "Load all{serverTotal, number}invites": "加载全部 {serverTotal, number} 个邀请",
    "Load all{serverTotal, number}成员": "加载全部 {serverTotal, number} 个成员",
    "Load all {serverTotal, number} members": "加载全部 {serverTotal, number} 个成员",
    "Load all{serverTotal, number}members": "加载全部 {serverTotal, number} 个成员",
    "ANTHROPIC_ API_KEY": "ANTHROPIC_API_KEY",
}

PLACEHOLDER_RE = re.compile(r"(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}|<[^>]+>|</[^>]+>)")
LATIN_RE = re.compile(r"[A-Za-z]")


def js_unescape(value: str) -> str:
    return bytes(value, "utf-8").decode("unicode_escape")


def extract_default_messages(text: str) -> dict[str, str]:
    messages: dict[str, str] = {}
    for pattern in DEFAULT_MESSAGE_PATTERNS:
        for match in pattern.finditer(text):
            messages.setdefault(match.group("id"), js_unescape(match.group("msg")))
    return messages


def extract_default_messages_from_assets(assets_dir: Path) -> dict[str, str]:
    messages: dict[str, str] = {}
    for path in sorted(assets_dir.glob("*.js")):
        try:
            text = path.read_text(encoding=ENCODING)
        except OSError:
            continue
        messages.update(extract_default_messages(text))
    return messages


def _translate_segment(segment: str) -> str | None:
    if not segment:
        return segment
    stripped = segment.strip()
    if not stripped:
        return segment
    if stripped in EXACT_TRANSLATIONS:
        return segment.replace(stripped, EXACT_TRANSLATIONS[stripped])
    if stripped in WORD_TRANSLATIONS:
        return segment.replace(stripped, WORD_TRANSLATIONS[stripped])

    translated = stripped
    for english in sorted(WORD_TRANSLATIONS, key=len, reverse=True):
        translated = re.sub(rf"\b{re.escape(english)}\b", WORD_TRANSLATIONS[english], translated)

    if LATIN_RE.search(translated):
        return None

    return segment.replace(stripped, translated)


def translate_default_message(message: str) -> str | None:
    if message in EXACT_TRANSLATIONS:
        return EXACT_TRANSLATIONS[message]

    parts = PLACEHOLDER_RE.split(message)
    translated = []
    for part in parts:
        if not part:
            continue
        if PLACEHOLDER_RE.fullmatch(part):
            translated.append(part)
        else:
            segment = _translate_segment(part)
            if segment is None:
                return None
            translated.append(segment)
    value = "".join(translated)
    return fix_common_mixed_text(value)


def backfill_locale(locale: dict[str, str], messages: dict[str, str]) -> int:
    added = 0
    for key, message in sorted(messages.items()):
        if key not in locale:
            translated = translate_default_message(message)
            if translated is None:
                continue
            locale[key] = translated
            added += 1
    return added


def fix_common_mixed_text(value: str) -> str:
    fixed = value
    for old, new in MIXED_REPLACEMENTS.items():
        fixed = fixed.replace(old, new)
    fixed = re.sub(r"([^\s])Claude", r"\1 Claude", fixed)
    fixed = re.sub(r"Claude([^\s，。！？、）)])", r"Claude \1", fixed)
    fixed = re.sub(r"([^\s])GitHub", r"\1 GitHub", fixed)
    fixed = re.sub(r"([^\s])Git", r"\1 Git", fixed)
    fixed = re.sub(r"([^\s])URL", r"\1 URL", fixed)
    fixed = re.sub(r"([^\s])API", r"\1 API", fixed)
    fixed = re.sub(r"([^\s])Token", r"\1 Token", fixed)
    fixed = re.sub(r"([A-Za-z])（", r"\1 （", fixed)
    fixed = re.sub(r"\s+([，。！？；：])", r"\1", fixed)
    fixed = fixed.replace("URL。", "URL。")
    return fixed


def fix_common_mixed_values(locale: dict[str, str]) -> int:
    changed = 0
    for key, value in list(locale.items()):
        if not isinstance(value, str):
            continue
        fixed = fix_common_mixed_text(value)
        if fixed != value:
            locale[key] = fixed
            changed += 1
    return changed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backfill zh-CN locale entries from Claude Desktop JS defaultMessage ids.")
    parser.add_argument("--auto-detect", action="store_true", help="Auto-detect current Claude Desktop app package.")
    parser.add_argument("--locale", type=Path, default=ION_LOCALE_SRC, help="Locale JSON file to update.")
    parser.add_argument("--assets-dir", type=Path, help="Claude ion-dist assets directory.")
    parser.add_argument("--check", action="store_true", help="Report missing entries without writing.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    targets = resolve_apply_targets(auto_detect=args.auto_detect)
    assets_dir = args.assets_dir or targets.assets_dir
    messages = extract_default_messages_from_assets(assets_dir)
    locale = json.loads(args.locale.read_text(encoding=ENCODING))

    missing = {key: value for key, value in messages.items() if key not in locale}
    if args.check:
        print(f"defaultMessage ids: {len(messages)}")
        print(f"missing locale ids: {len(missing)}")
        return 1 if missing else 0

    added = backfill_locale(locale, messages)
    fixed = fix_common_mixed_values(locale)
    args.locale.write_text(json.dumps(locale, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding=ENCODING)
    print(f"defaultMessage ids: {len(messages)}")
    print(f"added locale ids: {added}")
    print(f"fixed mixed values: {fixed}")
    print(f"updated: {args.locale}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
