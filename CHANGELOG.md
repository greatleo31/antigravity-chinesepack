# Changelog

本文件记录 Antigravity 中文语言包的重要改动。

## Unreleased

### 汉化质量流程
- 新增 `dicts/glossary.json`，用于统一核心术语
- 新增 `TRANSLATION_STYLE_GUIDE.md`，统一汉化文案风格
- 新增 `UNTRANSLATED_REVIEW.md`，固定未翻译文本收集与分类流程
- 新增 `QA_CHECKLIST.md`，作为发布前质量验收清单
- 新增 `tools/generate_translation_candidates.py`，用于生成 AI 候选译文并保留人工审核环节
- 扩展 `dicts/patterns.json`，补充工作区、会话、知识条目、秒级倒计时与配额重置类动态文本规则
- 继续润色 `dicts/page_settings.json` 中多处高频设置说明文案
- 更新中英文 README，进一步强调直接运行主脚本，并补充术语表、收集流程与 AI 辅助翻译说明

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
