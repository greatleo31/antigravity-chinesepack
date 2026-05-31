# 未翻译文本收集与处理流程

本文件用于把“发现漏翻 → 收集 → 分类 → 补词典”的流程固定下来，避免后续靠感觉维护。

## 一次完整流程

### 1. 开启调试模式

在 Antigravity 开发者工具控制台执行：

```js
localStorage.setItem('ag-hanhua-debug', '1')
location.reload()
```

### 2. 真实使用 10~20 分钟

建议优先覆盖：

- Agent Manager 首页
- Settings
- Agents
- Workspace / Conversation 历史
- MCP / Knowledge
- 配额、通知、市场等侧边区域

### 3. 导出未命中文本

在控制台执行：

```js
copy(window.__agHanhuaDumpUntranslated())
```

### 4. 逐条分类

把导出的英文文本按以下四类处理：

- **应进入精确词典**：按钮、标题、菜单、固定说明文案
- **应进入 `patterns.json`**：数字、时间、路径、配额等动态文本
- **应进入 `ignored.json`**：品牌名、模型名、技术缩写、文件名
- **不该翻译**：代码、命令、路径、日志、模型输出

### 5. 人工复审后再写入

- 高频固定文案 → 写入对应页面词典
- 动态文本 → 补 `dicts/patterns.json`
- 术语冲突 → 先核对 `dicts/glossary.json`

## 本轮建议优先关注

- Settings 页中的长说明文案
- Agent 权限、浏览器策略、命令自动执行相关说明
- 配额、时间、额度、倒计时类动态文本
- Workspace / Conversation 列表里的英文残留

## 关闭调试模式

```js
localStorage.removeItem('ag-hanhua-debug')
location.reload()
```
