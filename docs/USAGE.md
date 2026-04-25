# 使用说明

双击即可执行：
- apply.bat：备份当前资源并应用中文化
- rollback.bat：回滚到最近一次备份
- verify.bat：校验语言文件与主 UI fallback 是否仍有英文残留

说明：
1. 每次执行 apply.bat 都会在 backups/ 下生成一个时间戳备份目录。
2. rollback.bat 默认回滚到最近一次 apply 生成的备份。
3. 如果 Claude Desktop 更新了版本号，需要先修改 config.json 里的目标路径。
4. locales/ 里保存当前维护的中文语言文件副本；patches/ 里保存主 UI 的字符串替换规则。
5. 当前保留的自动运行时补丁只有：`Test setup instructions`；执行 `apply.bat` 时会一并同步。
6. `apply-report.json` 会区分命中补丁、已补丁和未命中补丁，便于判断当前版本还需要保留哪些运行时规则。
