# 汉化质量验收清单

每次发布或大规模改词典前，建议至少按本清单走一遍。

## 页面覆盖

请至少检查以下区域：

- Agent Manager 首页
- Settings 页面
- Agents 页面
- Workspace / Conversation 历史
- MCP / Knowledge 页面
- 配额 / AI 额度 / Marketplace 相关区域

## 检查维度

### 1. 漏翻

- 是否仍有明显英文按钮、标题、菜单
- 是否有长说明文案完全未翻译
- 是否有动态文本只翻了一半

### 2. 文案自然度

- 是否存在明显机翻腔
- 是否像真实中文产品界面
- 是否有过长、过硬、难读的说明

### 3. 术语一致性

重点确认以下术语不要混用：

- 智能体
- 工作区
- 会话
- 交付件
- 模型
- 模型配额
- AI 额度
- 使用数据

### 4. 误翻风险

- 品牌名是否被误翻
- 模型名是否被误翻
- 文件名、路径、命令是否被误翻
- 代码区域、日志区域是否被错误替换

## 提交前命令

```bash
python AntigravityHanHua_GongJu.py --check-dicts
python -m py_compile AntigravityHanHua_GongJu.py
python -m py_compile tools/generate_translation_candidates.py
```

## 通过标准

至少满足：

- 高频页面没有明显大面积英文残留
- 核心设置页没有明显生硬机翻腔
- 动态文本翻译不影响原始功能
- 词典检查通过
- 脚本语法检查通过
