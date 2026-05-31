# 当前阶段聚焦

现在项目的重点不再是继续补一层包装脚本，而是把汉化质量做成一套能持续迭代的流程。

## 本轮新增的核心能力

1. **术语统一**
   - 新增 `dicts/glossary.json`
   - 用于固定 Agent / Workspace / Conversation / Artifact / Model 等核心译法

2. **风格统一**
   - 新增 `TRANSLATION_STYLE_GUIDE.md`
   - 统一按钮、设置项、长说明文案的中文表达方式

3. **漏翻收集闭环**
   - 新增 `UNTRANSLATED_REVIEW.md`
   - 把“发现漏翻 → 收集 → 分类 → 回补词典”的流程固定下来

4. **质量验收清单**
   - 新增 `QA_CHECKLIST.md`
   - 发布前可以快速检查漏翻、术语一致性和误翻风险

5. **AI 候选翻译辅助脚本**
   - 新增 `tools/generate_translation_candidates.py`
   - 定位是“AI 先给候选，人再定终稿”，避免直接机翻覆盖词典

## 接下来最值得继续做的事

1. 先跑一轮真实界面漏翻收集
2. 优先根据实际导出的未翻译文本继续补 `patterns.json` 和页面词典
3. 再把 AI 候选翻译能力用于长文案批量润色

如果目标是“先把本地效果做扎实，再谈商店”，这条路线是可执行且可持续的。
