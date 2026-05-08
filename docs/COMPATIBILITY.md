# 兼容能力说明

当前项目吸收了参考项目里更适合分发和跨版本使用的做法，同时保留原有配置化补丁、备份、报告和校验流程。

## 自动发现 Claude 安装目录

```bat
apply.bat --auto-detect
verify.bat --auto-detect
rollback.bat --auto-detect
```

这些命令会从 `C:\Program Files\WindowsApps` 中查找最新的 `Claude_*_x64__...\app` 目录，并基于该目录派生资源路径。

## 手动指定 app 目录

```bat
apply.bat --app-dir "D:\Claude\app"
verify.bat --app-dir "D:\Claude\app"
rollback.bat --app-dir "D:\Claude\app"
```

`--app-dir` 需要指向 Claude 的 `app` 目录，而不是 `resources` 目录。

## 资源校验

```bat
python scripts\validate_resources.py
```

该命令会检查 `locales/` 和 `patches/` 中维护的 JSON 文件是否可解析，适合在维护翻译资源后先跑一遍。
