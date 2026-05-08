# Claude Desktop 中文本地化工具

这个仓库用于维护 Claude Desktop 的简体中文本地化资源和自动应用脚本。它不是一次性的手工改文件记录，而是一套可重复执行的本地化流程：同步中文语言包、修补运行时硬编码文案、备份原始资源、验证结果、恢复英文、回滚最近一次应用。

当前项目重点面向 Windows 版 Claude Desktop，尤其是 Microsoft Store/WindowsApps 安装结构。脚本会优先尝试自动发现当前机器上最新的 Claude 安装目录，因此 Claude Desktop 升级版本后通常不需要手动改路径。

## 主要能力

- 自动定位 Claude Desktop 安装目录。
- 同步 `zh-CN.json`、`ion-dist/i18n/zh-CN.json`、Statsig 等中文资源。
- 对语言包覆盖不到的打包 JS 硬编码英文做运行时补丁。
- 每次应用前自动备份目标资源，便于回滚。
- 支持恢复英文资源后重新汉化。
- 检测缺失的 `defaultMessage id`，并生成维护文档。
- 检测 mojibake 乱码和 `??`、`???` 问号占位翻译。
- 提供完整验证命令和 pytest 测试。

## 当前覆盖状态

最近一次维护后，已确认：

- `defaultMessage id` 剩余数量为 `0`。
- `billing`、`claude-code`、`general` 分组均已补齐。
- mojibake 检测结果为 `0`。
- 已修复设置页头像等 `??` 问号占位文案。
- 已补 Projects 页面硬编码文案，例如 `Projects`、`New project`。
- 已补计划任务页面硬编码文案，例如 `Run tasks on a schedule...`、`No scheduled tasks yet.`。
- `pytest scripts -q` 在本地项目中通过。

仍需注意：Claude Desktop 每次升级都可能改变前端打包文件名和硬编码文本位置。如果升级后发现新英文残留，应按“维护新翻译”的流程继续补丁。

## 快速开始

在项目根目录执行：

```bat
auto-localize.bat
```

或直接执行：

```bat
py -3 scripts\auto_localize.py --report backups\auto-localize-next.json
```

`auto_localize.py` 会按顺序执行：

1. 同步设置页专项翻译。
2. 自动定位 Claude Desktop 安装目录。
3. 应用中文语言包和运行时补丁。
4. 修复可检测的 mojibake 资源。
5. 运行应用结果验证。
6. 输出报告到 `backups/auto-localize-next.json`。

执行完成后，完全退出并重新打开 Claude Desktop。Electron 应用可能缓存旧 JS 资源，只刷新页面不一定能看到最新效果。

## 常用命令

### 一键应用并验证

```bat
auto-localize.bat
```

适合日常使用。它比单独运行 `apply.bat` 更完整，因为它会自动处理设置页专项翻译、mojibake 检查和报告输出。

### 只应用中文资源

```bat
apply.bat --auto-detect
```

或：

```bat
py -3 scripts\apply_localization.py --auto-detect
```

该命令会备份当前安装目录中的资源，然后复制项目维护的中文资源，并按 `patches/main-ui-patches.json` 修补打包 JS 中的硬编码英文。

### 验证已安装资源

```bat
verify.bat --auto-detect
```

或：

```bat
py -3 scripts\verify_localization.py --auto-detect
```

用于确认关键中文条目和运行时补丁是否已经应用。

### 恢复英文

```bat
restore-english.bat --auto-detect
```

或：

```bat
python scripts\restore_reference_localization.py --auto-detect
```

恢复英文后，可以再次运行 `auto-localize.bat` 重新汉化。

### 回滚最近一次应用

```bat
rollback.bat
```

回滚使用 `backups/` 中最近一次 apply 生成的备份。它适合撤销最近一次本项目造成的资源变更。

### 检查资源文件

```bat
python scripts\validate_resources.py
```

该命令会检查：

- `locales/` 和 `patches/` 下 JSON 是否可解析。
- 参考脚本是否有语法错误。
- JSON 字符串中是否存在 `??`、`???` 这类问号占位翻译。

### 重新提取缺失翻译 ID

```bat
py -3 scripts\extract_missing_locale_ids.py
```

输出：

- `docs/missing-locale-ids.json`
- `docs/missing-locale-ids.md`

如果结果不是 `missing ids: 0`，说明还有 `defaultMessage` 对应的中文条目缺失，需要继续维护 `locales/ion-zh-CN.json` 或 `locales/root-zh-CN.json`。

### 检查 mojibake

```bat
py -3 scripts\repair_mojibake_assets.py --auto-detect --check
```

结果应为：

```text
mojibake asset files: 0
```

### 运行测试

```bat
pytest scripts -q
```

维护脚本或资源结构后都应运行该命令。

## 推荐验证流程

每次修改翻译或补丁后，建议按以下顺序执行：

```bat
py -3 scripts\apply_settings_translations.py
py -3 scripts\extract_missing_locale_ids.py
python scripts\validate_resources.py
pytest scripts -q
py -3 scripts\auto_localize.py --report backups\auto-localize-next.json
py -3 scripts\repair_mojibake_assets.py --auto-detect --check
```

关键通过标准：

- `missing ids: 0`
- `All resource files validated.`
- `pytest scripts -q` 全部通过
- `Auto-localize status: ok`
- `Missing installed ids: 0`
- `Mojibake after repair: 0`
- `mojibake asset files: 0`

## 项目结构

```text
.
├─ auto-localize.bat
├─ apply.bat
├─ verify.bat
├─ rollback.bat
├─ restore-english.bat
├─ install-complete-zh-cn.bat
├─ config.json
├─ locales/
│  ├─ root-zh-CN.json
│  ├─ ion-zh-CN.json
│  ├─ ion-zh-CN.overrides.json
│  └─ statsig/
│     └─ zh-CN.json
├─ patches/
│  └─ main-ui-patches.json
├─ scripts/
│  ├─ auto_localize.py
│  ├─ apply_localization.py
│  ├─ apply_settings_translations.py
│  ├─ extract_missing_locale_ids.py
│  ├─ repair_mojibake_assets.py
│  ├─ restore_reference_localization.py
│  ├─ rollback_localization.py
│  ├─ validate_resources.py
│  ├─ verify_localization.py
│  └─ test_*.py
├─ docs/
│  ├─ missing-locale-ids.json
│  ├─ missing-locale-ids.md
│  ├─ USAGE.md
│  └─ COMPATIBILITY.md
└─ backups/
```

`backups/` 是运行产物，不应提交到仓库。

## 核心文件说明

### `locales/root-zh-CN.json`

Claude Desktop 根级中文语言资源，主要覆盖顶层菜单、基础设置、桌面端原生相关文案。

### `locales/ion-zh-CN.json`

Claude Desktop 前端主界面的中文语言资源。大部分界面文案都在这里维护，包括通用界面、设置页、项目、账单、Claude Code、插件、隐私等内容。

### `locales/ion-zh-CN.overrides.json`

可选覆盖资源。目标安装目录存在对应文件时会被同步；不存在时自动跳过。

### `locales/statsig/zh-CN.json`

Statsig 相关中文资源。目标安装目录存在 statsig 语言目录时会同步。

### `patches/main-ui-patches.json`

运行时 JS 补丁表。它用于处理语言包覆盖不到的硬编码英文，例如：

- 打包 JS 中直接写死的按钮文案。
- 某些页面的标题、副标题和空状态。
- 版本升级后没有进入 locale JSON 的 fallback 字符串。

补丁项一般包含：

```json
{
  "description": "human readable description",
  "filePattern": "index-*.js",
  "find": "English string or minified JS fragment",
  "replace": "Chinese string or patched JS fragment"
}
```

如果只想扫描某个文件前缀，可以设置 `filePattern`。如果不设置，默认扫描所有 `*.js`。

### `docs/missing-locale-ids.json`

由 `scripts/extract_missing_locale_ids.py` 生成，用于追踪安装资源中仍缺失的 `defaultMessage id`。

### `docs/missing-locale-ids.md`

同一份缺失 ID 的 Markdown 报告，便于人工查看和分组维护。

## 脚本说明

### `scripts/auto_localize.py`

推荐的一键流程脚本。它串联设置页翻译同步、应用中文资源、mojibake 修复、安装结果验证和报告输出。

### `scripts/apply_localization.py`

负责把项目中的中文资源应用到 Claude Desktop 安装目录。

它会：

1. 解析目标路径。
2. 备份 root locale、ion locale、可选资源和命中的 JS 文件。
3. 复制中文 JSON。
4. 应用 `main-ui-patches.json` 中的运行时补丁。
5. 生成 `backups/<timestamp>/apply-report.json`。

### `scripts/apply_settings_translations.py`

维护设置页中一些容易遗漏或曾出现问号占位的翻译。它会把专项翻译同步到 locale 和 patch 数据中。

### `scripts/extract_missing_locale_ids.py`

从当前安装资源和项目资源中提取 `defaultMessage`，对比中文 locale，生成缺失 ID 报告。

### `scripts/repair_mojibake_assets.py`

检测或修复安装资源中可识别的 mojibake 乱码。

常用检查命令：

```bat
py -3 scripts\repair_mojibake_assets.py --auto-detect --check
```

### `scripts/validate_resources.py`

资源质量门禁。它会检查 JSON 结构、参考脚本语法和问号占位翻译。

### `scripts/verify_localization.py`

验证已安装 Claude Desktop 资源是否包含关键中文条目，以及关键运行时补丁是否仍有效。

### `scripts/rollback_localization.py`

把最近一次备份恢复到安装目录。

## 自动检测安装目录

多数命令支持：

```bat
--auto-detect
```

自动检测会在 WindowsApps 等常见位置中寻找最新的 Claude Desktop 安装目录。对于 Microsoft Store 版 Claude，这通常比手动维护 `config.json` 中的旧版本号更可靠。

也可以手动指定 Claude 的 `app` 目录：

```bat
py -3 scripts\apply_localization.py --app-dir "D:\Claude\app"
```

注意：`--app-dir` 指向的是 Claude 的 `app` 目录，不是 `resources` 目录。

## 备份和报告

每次应用都会创建：

```text
backups/YYYYMMDD-HHMMSS/
```

其中通常包含：

- 原始 root locale 备份。
- 原始 ion locale 备份。
- 命中的 JS 资源备份。
- 可选 statsig/overrides 资源备份。
- `apply-report.json`。

`apply-report.json` 会记录：

- 总补丁数量。
- 本次命中的补丁数量。
- 已经处于补丁后状态的补丁数量。
- 未命中的补丁数量。
- 实际修改了哪些 JS 文件。
- 可选资源是否存在并已同步。

如果 `Matched patches: 0`，不一定代表失败。若目标资源已经被补丁过，再次运行时可能显示为 `Already patched`。

## 维护新翻译

### 1. 处理 locale 缺失

运行：

```bat
py -3 scripts\extract_missing_locale_ids.py
```

查看：

```text
docs/missing-locale-ids.md
docs/missing-locale-ids.json
```

把缺失 ID 补到对应 locale 文件：

- root 相关补 `locales/root-zh-CN.json`
- 主前端相关补 `locales/ion-zh-CN.json`

要求：

- 不要写“本地化文本”这类占位翻译。
- 保留 ICU 占位符，例如 `{count}`、`{provider}`。
- 保留 HTML tag，例如 `<link>`、`<b>`、`<learnMoreLink>`。
- 保留变量名和结构，不要改 key。

### 2. 处理硬编码英文

如果 `missing ids: 0`，但界面仍有英文，通常说明该文案没有走 locale，而是打包 JS 里的硬编码字符串。

处理方法：

1. 在安装目录的 `ion-dist/assets/v1/*.js` 中搜索英文原文。
2. 找到稳定的最小 JS 片段。
3. 在 `patches/main-ui-patches.json` 添加 `find`/`replace`。
4. 运行 `python scripts\validate_resources.py`。
5. 运行 `py -3 scripts\apply_localization.py --auto-detect`。
6. 再次搜索安装 JS，确认英文消失、中文写入。

示例场景：

- Projects 页面中的 `Projects`、`New project`。
- 计划任务页面中的 `Run tasks on a schedule...`、`No scheduled tasks yet.`。

### 3. 每批维护后验证

建议每补一批都运行：

```bat
py -3 scripts\apply_settings_translations.py
py -3 scripts\extract_missing_locale_ids.py
python scripts\validate_resources.py
pytest scripts -q
```

最后运行：

```bat
py -3 scripts\auto_localize.py --report backups\auto-localize-next.json
py -3 scripts\repair_mojibake_assets.py --auto-detect --check
```

## 常见问题

### 为什么 `missing ids: 0` 但界面还有英文？

因为并非所有界面文案都来自 locale JSON。有些文案是前端打包 JS 中的硬编码字符串，需要在 `patches/main-ui-patches.json` 中维护运行时补丁。

### 为什么修改后界面还是旧英文？

通常是 Claude Desktop 仍在运行或缓存了旧资源。请完全退出 Claude Desktop，再重新打开。

### 为什么出现 `??` 或 `????`？

这通常是编码写入错误或占位翻译。当前 `validate_resources.py` 会拒绝这类问号占位，避免它们进入资源文件。

### 为什么 README 或旧文档里有乱码？

早期文件可能经历过错误编码读写。当前 README 已按 UTF-8 重写。后续编辑时应使用 UTF-8，并避免通过非 UTF-8 控制台直接写中文。

### 可以删除 `_patch_*.py` 这类脚本吗？

可以。这些是历史一次性补丁脚本，真正生效的翻译已经沉淀到 `locales/` 或 `patches/` 中。当前正式流程不依赖它们。

### Claude Desktop 升级后怎么办？

先运行：

```bat
py -3 scripts\auto_localize.py --report backups\auto-localize-next.json
```

然后查看报告中的：

- `Missing installed ids`
- `Mojibake after repair`
- `Matched patches`
- `Already patched`
- `Unmatched patches`

如果有新增英文残留，再按“维护新翻译”继续补。

## 发布和提交建议

提交前至少运行：

```bat
python scripts\validate_resources.py
pytest scripts -q
```

如果改了真实汉化内容，还应运行：

```bat
py -3 scripts\auto_localize.py --report backups\auto-localize-next.json
py -3 scripts\repair_mojibake_assets.py --auto-detect --check
```

不要提交：

- `backups/`
- `__pycache__/`
- `.pytest_cache/`
- 临时日志
- 本地安装资源副本
- 个人 token 或凭据

## 当前仓库状态说明

这个项目主要维护 Claude Desktop 中文化资源和脚本，不修改 Claude Desktop 程序源码。所有变更都通过复制 JSON 资源和替换打包 JS 文本片段完成。

如果你发现某个界面还有英文，最有用的信息是：

1. 截图。
2. 英文原文。
3. 所在页面或操作路径。
4. 当前 Claude Desktop 版本。

拿到这些信息后，通常可以通过 locale 补齐或 runtime patch 继续完善。
