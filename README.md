# Claude Desktop 中文化项目

本项目用于把 Claude 桌面端的中文本地化过程工程化，目标是提供稳定的：备份、应用补丁、校验、回滚。

目录规划：
- config/：目标路径与版本配置
- locales/：维护后的中文语言文件
- patches/：主 UI fallback 字符串补丁定义
- scripts/：一键应用 / 一键校验 / 一键回滚脚本
- backups/：运行脚本后自动生成的备份
- docs/：说明文档

GitHub 推送准备：
- 已适合初始化为独立仓库
- 建议先补 `.gitignore`，避免把运行时备份直接提交
- 拿到 GitHub 仓库地址后，可直接添加 remote 并推送

当前迭代状态：
- 已同步维护 `ion-dist/i18n/zh-CN.json` 中最新确认的运行时选项翻译
- 已将 `Recommended`、`Something else`、`Test setup instructions` 纳入补丁规则
- 已把“其他选项”“测试安装说明”等关键项加入校验脚本，便于后续版本升级后快速复检
