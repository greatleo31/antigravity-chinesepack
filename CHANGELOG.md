# Changelog

本文件记录 Antigravity 中文语言包的重要改动。

## Unreleased

- 优化安装与还原失败时的诊断信息与协作反馈材料

## 2026-05

### 功能与稳定性
- 增强旧版 `resources/app` 与新版 `app.asar` 的注入兼容性
- 增加长文案模糊匹配，降低空格和换行变化导致的漏翻概率
- 扩展属性翻译覆盖：`placeholder`、`title`、`aria-label`、`aria-description`、`aria-placeholder`、`alt`、`data-tooltip`、`data-title`
- 增强 Windows 下 Python 启动兼容性，支持 `python` 与 `py -3`
- 增强 macOS 启动脚本兼容性，支持 `python3` 与 `python`
- 安装和还原前主动检测 Antigravity 是否仍在运行，减少占用导致的失败

### 词典与文案
- 统一设置页、导航页、智能体页、知识页核心术语
- 清理重复词条，词典检查结果恢复为干净状态
- 优化多处生硬或不自然中文表述

### 开源协作
- 新增 `CONTRIBUTING.md`
- 新增 Issue / PR 模板
- 新增 GitHub Actions 词典检查工作流
- 新增 MIT License
- 优化 README 展示、快速开始与贡献引导
