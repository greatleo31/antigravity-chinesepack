# Contributing

感谢你帮助改进 Antigravity 中文语言包。

## 优先贡献方向

- 未翻译文本补充
- 不自然文案润色
- 术语统一
- 长文案漏翻修复
- 不同版本 Antigravity 的兼容性修复

## 提交前建议

1. 修改后运行：

```bash
python "AntigravityHanHua_GongJu.py" --check-dicts
```

2. 保持术语一致，例如：
   - Agent → 智能体
   - Workspace → 工作区
   - Conversation → 会话
   - Artifact → 交付件

3. 避免以下问题：
   - 机翻腔太重
   - 同一词多种译法混用
   - 模型名、产品名被误翻
   - 长文案只在单一空格/换行情况下才能命中

## 建议提交流程

- 小改动：直接提 PR
- 文案建议：提 Issue
- 大范围重构：建议先开 Issue 讨论
