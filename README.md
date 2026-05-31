# Antigravity 智能管理器中文语言包

[![GitHub Repo stars](https://img.shields.io/github/stars/greatleo31/antigravity-chinesepack?style=flat-square)](https://github.com/greatleo31/antigravity-chinesepack/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/greatleo31/antigravity-chinesepack?style=flat-square)](https://github.com/greatleo31/antigravity-chinesepack/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/greatleo31/antigravity-chinesepack?style=flat-square)](https://github.com/greatleo31/antigravity-chinesepack/commits/main)
[![Check dictionaries](https://img.shields.io/github/actions/workflow/status/greatleo31/antigravity-chinesepack/check-dicts.yml?branch=main&style=flat-square)](https://github.com/greatleo31/antigravity-chinesepack/actions/workflows/check-dicts.yml)
[![License](https://img.shields.io/github/license/greatleo31/antigravity-chinesepack?style=flat-square)](./LICENSE)

> 适用对象：Antigravity Agent Manager  
> 支持平台：Windows / macOS  
> 方案特点：动态注入、自动备份、一键还原、词典校验、未翻译文本收集
>
> **这是一个面向普通用户也能直接使用的 Antigravity 中文语言包项目。**  
> 目标是：安装更简单、汉化更自然、出错更容易定位、协作更方便。

---

## 快速开始

### Windows

1. 关闭 Antigravity
2. 双击 `ZhuRu_HanHua.bat`
3. 重新打开 Antigravity

> 如果系统里没有 `python` 命令，但安装了 Python Launcher，脚本也会自动尝试使用 `py -3`。

### macOS

1. 关闭 Antigravity
2. 首次执行前先运行：

```bash
chmod +x "ZhuRu_HanHua.command" "QingChu_HanHua.command"
```

3. 然后执行：

```bash
./ZhuRu_HanHua.command
```

4. 重新打开 Antigravity

> 如果系统里没有 `python3` 命令，但存在 `python`，脚本也会自动尝试使用 `python`。

---

## 适用范围与说明

- 适用于 **Antigravity Agent Manager** 界面的中文汉化
- 支持 **Windows / macOS**
- 同时兼容：
  - 旧版 `resources/app` 布局
  - 新版 `app.asar` 布局
- 默认尽量不直接修改核心二进制结构，而是通过可回滚方式注入
- 如果官方更新了前端结构，可能需要重新执行脚本或补充词典
- 本项目主要解决：
  - 界面英文较多、不方便日常使用
  - 长文案漏翻或术语不统一
  - 不同系统、不同安装环境下的安装成功率问题

---

## 项目简介

本项目用于给 Antigravity 的 **Agent Manager** 界面做中文汉化。

它会根据 Antigravity 的安装结构自动选择注入方式：

1. **旧版 `resources/app` 布局**
   - 在 `resources/app/out` 目录生成 `ag_agent_hanhua.js`
   - 向工作台 HTML 注入一行 `<script>` 引用
   - 备份原始 HTML
   - 更新 `product.json` 中对应文件的校验值

2. **新版 `app.asar` 布局**
   - 备份原始 `app.asar`
   - 解包 `app.asar`
   - 自动查找 `preload.js`
   - 向 preload 注入汉化逻辑
   - 重新打包 `app.asar`

这样做的好处是：

- 出问题能回滚
- 官方更新后可重新执行
- 对原始程序结构改动相对可控
- 能兼容旧版 HTML 布局和新版 asar 布局

---

## 功能特性

- **动态扫描翻译**：通过 `MutationObserver` 处理动态渲染内容
- **精确词典翻译**：适合按钮、菜单、标题等稳定文本
- **正则模板翻译**：适合带数字、文件名、路径等变量的文本
- **长句模糊匹配**：对空格、换行差异更稳，减少长文案漏翻
- **忽略词表**：避免误翻模型名、技术名词、文件名等内容
- **双平台支持**：Windows 和 macOS 都能直接执行
- **自动备份**：首次注入时会生成 `.bak` / `.hanhua.bak` 备份文件
- **一键还原**：可恢复到官方原始状态
- **路径自动探测**：支持默认路径探测，也支持手动指定安装目录
- **词典检查**：可检查 JSON、重复 key、空译文和正则模板错误
- **未翻译文本收集**：调试模式下可收集页面中尚未覆盖的英文 UI 文本

---

## 使用前准备

开始前请先确认：

1. 已安装 **Python 3**
2. Antigravity 已完全退出
3. 当前账号对 Antigravity 安装目录有写权限
4. 如果是新版 `app.asar` 布局，需要安装 **Node.js/npm**，脚本会通过 `npx @electron/asar` 解包和打包

---

## 默认安装目录

### Windows

脚本会尝试探测：

- `当前目录`
- `当前目录父级`
- `%LOCALAPPDATA%\Programs\Antigravity`
- `%LOCALAPPDATA%\Programs\antigravity`
- `%ProgramFiles%\Antigravity`

也可以手动指定 Antigravity 根目录、`resources` 目录或 `app.asar` 所在目录。

### macOS

脚本会尝试探测：

- `/Applications/Antigravity.app`
- `~/Applications/Antigravity.app`
- `.app/Contents/Resources`

---

## 安装汉化

### Windows

直接双击：

- `ZhuRu_HanHua.bat`

如果 Antigravity 不在默认目录，也可以手动执行：

```bash
python "AntigravityHanHua_GongJu.py" --install-dir "D:\Antigravity"
```

### macOS

首次使用前，先给脚本执行权限：

```bash
chmod +x "ZhuRu_HanHua.command" "QingChu_HanHua.command"
```

然后执行：

```bash
./ZhuRu_HanHua.command
```

如果需要手动指定路径：

```bash
python3 "AntigravityHanHua_GongJu.py" --install-dir "/Applications/Antigravity.app"
```

执行完成后，重新启动 Antigravity，打开 Agent Manager 即可查看汉化效果。

---

## 还原官方原版

### Windows

直接双击：

- `QingChu_HanHua.bat`

或手动执行：

```bash
python "AntigravityHanHua_GongJu.py" --huifu --install-dir "D:\Antigravity"
```

### macOS

执行：

```bash
./QingChu_HanHua.command
```

如果需要手动指定路径：

```bash
python3 "AntigravityHanHua_GongJu.py" --huifu --install-dir "/Applications/Antigravity.app"
```

还原时会：

- 旧版布局：用 `.bak` 文件恢复原始 HTML，并删除 `ag_agent_hanhua.js`
- 新版布局：用 `.hanhua.bak` 文件恢复原始 `app.asar`

---

## 检查词典

执行：

```bash
python "AntigravityHanHua_GongJu.py" --check-dicts
```

该命令会检查：

- JSON 是否合法
- 是否存在空 key
- 是否存在空译文
- 是否存在重复 key
- 正则模板是否能正常编译

## 环境诊断

如果你不确定脚本识别到了哪个安装目录，或者怀疑 Python / npx 环境有问题，可以执行：

```bash
python "AntigravityHanHua_GongJu.py" --diagnose
```

如果需要手动指定路径一起诊断：

```bash
python "AntigravityHanHua_GongJu.py" --diagnose --install-dir "D:\Antigravity"
```

该命令会输出：

- 当前 Python 路径
- `python` / `python3` / `py` / `npx` 是否可用
- 自动探测到的候选安装目录
- 最终识别出的安装目录与布局类型

---

## 词典结构

当前词典目录：

```text
dicts/
├── common.json
├── menu_nav.json
├── page_agents.json
├── page_mcp_knowledge.json
├── page_settings.json
├── page_workspaces.json
├── patterns.json
└── ignored.json
```

### 普通 JSON 词典

普通词典使用英文原文到中文译文的映射：

```json
{
    "Settings": "设置",
    "Agents": "智能体"
}
```

### `patterns.json`

用于翻译带变量的动态文本：

```json
[
    {
        "pattern": "^([0-9]+) agents? running$",
        "replace": "$1 个智能体正在运行"
    }
]
```

### `ignored.json`

用于避免误翻模型名、技术名词、文件名等内容：

```json
[
    "Claude",
    "Gemini",
    "app.asar"
]
```

---

## 收集未翻译文本

如果发现界面仍有英文，可以打开开发者工具，在控制台执行：

```js
localStorage.setItem('ag-hanhua-debug', '1')
location.reload()
```

使用一段时间后，在控制台执行：

```js
copy(window.__agHanhuaDumpUntranslated())
```

即可复制尚未命中的英文 UI 文本，然后补充到 `dicts/` 词典中。

关闭调试模式：

```js
localStorage.removeItem('ag-hanhua-debug')
location.reload()
```

---

## 常见问题

### 1）提示找不到安装目录

请用 `--install-dir` 指定 Antigravity 安装路径，例如：

```bash
python "AntigravityHanHua_GongJu.py" --install-dir "C:\Users\你的用户名\AppData\Local\Programs\Antigravity"
```

### 2）提示权限不足

- Windows：尝试以管理员身份运行
- macOS：确认当前用户对应用目录有写权限

### 3）新版 app.asar 注入时提示找不到 npx

请先安装 Node.js，然后重新执行脚本。

### 4）Windows 下提示找不到 Python，但你已经装过

请优先尝试重新打开终端或重新登录系统。如果你的环境里只有 Python Launcher，当前脚本也会自动尝试使用 `py -3`。

### 5）更新后汉化失效

官方更新可能覆盖原文件，重新执行一次安装脚本即可。

### 6）只有部分文本被翻译

说明词典还没覆盖全。可以开启未翻译文本收集模式，再把收集到的文本补充到 `dicts/` 目录中。

### 7）想帮项目补翻译或修文案

欢迎直接提交 Issue / PR。优先补充：

- 页面上仍未翻译的英文
- 长文案换行或空格变化导致的漏翻
- 不自然、不像产品界面的中文表述
- 模型名、功能名、按钮文案不一致的问题

### 8）提示 Antigravity 仍在运行

请先完全退出 Antigravity 后再执行安装或还原。若你刚关闭应用仍提示占用，可以稍等几秒后重试。

### 9）想反馈安装或还原失败

建议在提 Issue 时一并附上：

- Antigravity 版本
- 系统平台
- 使用的是安装还是还原脚本
- 完整终端输出
- 如方便，附截图

这样会更容易快速定位问题。

---

## 文件说明

| 文件 | 说明 |
| --- | --- |
| `AntigravityHanHua_GongJu.py` | 核心逻辑：路径解析、备份、注入、还原、词典检查 |
| `ZhuRu_HanHua.bat` | Windows 安装入口 |
| `QingChu_HanHua.bat` | Windows 还原入口 |
| `ZhuRu_HanHua.command` | macOS 安装入口 |
| `QingChu_HanHua.command` | macOS 还原入口 |
| `dicts/` | 翻译词典、正则模板和忽略词表 |
| `CONTRIBUTING.md` | 贡献说明 |
| `SECURITY.md` | 安全问题反馈说明 |
| `.github/` | Issue / PR 模板与词典检查工作流 |
| `LICENSE` | 开源许可证 |
| `CHANGELOG.md` | 更新日志 |

---

## 致谢

本项目基于开源项目 [Cursor_chinese](https://github.com/bjrzs/Cursor_chinese) 制作，感谢原作者的无私奉献。

如果这个项目帮到了你，欢迎：

- 点一个 **Star** 支持项目
- 提交未翻译文本或术语优化建议
- 提交 PR 一起完善汉化质量
- 阅读 `CONTRIBUTING.md` 后参与协作
- 通过 Issue 反馈兼容性问题、功能建议或翻译建议
- 遇到潜在安全问题时，优先参考 `SECURITY.md`

如果你只是想快速判断这个项目值不值得继续关注，可以优先看：

- `README.md`：安装、诊断、常见问题
- `CHANGELOG.md`：近期更新与演进方向
- `.github/workflows/check-dicts.yml`：当前自动化检查能力

---

## 友情链接

感谢 **LinuxDo** 社区的支持！

[![LinuxDo](https://img.shields.io/badge/社区-LinuxDo-blue?style=for-the-badge)](https://linux.do/)
