# 完整汉化安装器

当前项目已内置 `D:\GitHub\Claude-desktop-hanhua\Claude-desktop-hanhua` 中的完整汉化资源和核心补丁流程。

## 安装中文

双击：

```text
install-complete-zh-cn.bat
```

脚本会请求管理员权限。用户同意后会：

1. 关闭 Claude Desktop
2. 备份原始资源和 JS 文件
3. 写入 `locales/` 中的 zh-CN JSON 资源
4. 执行完整 chunk UI 文案补丁
5. 注入中文字体/可见文本修正运行时

如果自动检测不到 Claude，也可以在管理员命令行中指定 app 目录：

```bat
install-complete-zh-cn.bat --app-dir "D:\Claude\app"
```

## 恢复英文

双击：

```text
restore-english.bat
```

它会请求管理员权限，然后从备份恢复英文资源和 JS 文件。

## 内置来源

- `locales/root-zh-CN.json`
- `locales/ion-zh-CN.json`
- `locales/statsig/zh-CN.json`
- `scripts/reference/patch_windowsapps_json_only.py`
- `scripts/reference/patch_chunks_zh_cn.py`
- `scripts/reference/restore_claude_zh_cn_windowsapps.py`
