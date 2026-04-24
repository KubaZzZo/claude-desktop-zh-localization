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
5. 本轮已纳入自动补丁的运行时选项包括：Recommended、Something else、Test setup instructions；执行 apply.bat 时会一并同步。
6. verify.bat 现在会额外校验“其他选项”“测试安装说明”等关键运行时文案是否已写入 ion 语言包。
