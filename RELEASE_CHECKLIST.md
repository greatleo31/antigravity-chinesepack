# Release checklist

这个清单用于阶段性发布前自查。

## 核心功能

- [ ] `python -m py_compile AntigravityHanHua_GongJu.py` 通过
- [ ] `python AntigravityHanHua_GongJu.py --check-dicts` 通过
- [ ] `python AntigravityHanHua_GongJu.py --diagnose` 可正常输出
- [ ] Windows 安装脚本可用
- [ ] Windows 还原脚本可用
- [ ] macOS 安装脚本可用
- [ ] macOS 还原脚本可用

## 文案与词典

- [ ] 常见页面已覆盖主要翻译
- [ ] 核心术语已统一（智能体 / 工作区 / 会话 / 交付件）
- [ ] 无明显机翻腔或生硬文案残留
- [ ] 长文案在换行 / 空格变化下仍能命中

## 开源协作

- [ ] README 信息完整且可读
- [ ] CONTRIBUTING.md 可指导外部贡献者
- [ ] Issue / PR 模板齐全
- [ ] LICENSE 存在
- [ ] SECURITY.md 存在
- [ ] GitHub Actions 词典检查工作流存在

## 发布前建议

- [ ] 更新 CHANGELOG.md
- [ ] 如有重要变化，补充 README 对应说明
- [ ] 推送前确认当前分支与远程已同步
