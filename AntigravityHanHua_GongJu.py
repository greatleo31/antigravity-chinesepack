import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INJECTION_START = "// >>> ANTIGRAVITY_HANHUA_INJECTION_START"
INJECTION_END = "// <<< ANTIGRAVITY_HANHUA_INJECTION_END"

LEGACY_TARGET_FILES = [
    ("resources", "app", "out", "vs", "code", "electron-browser", "workbench", "workbench-jetski-agent.html"),
    ("resources", "app", "out", "vs", "code", "electron-browser", "workbench", "workbench.html"),
]

DEFAULT_WINDOWS_CANDIDATES = [
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Antigravity"),
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "antigravity"),
    os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "Antigravity"),
]

DEFAULT_MAC_CANDIDATES = [
    "/Applications/Antigravity.app",
    os.path.expanduser("~/Applications/Antigravity.app"),
]


class DictIssue:
    def __init__(self, level, message):
        self.level = level
        self.message = message

    def __str__(self):
        return f"[{self.level}] {self.message}"


def rel_path(parts):
    return os.path.join(*parts)


def normalize_text(text):
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text).strip()
    return text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')


def iter_json_files(root):
    if not os.path.isdir(root):
        return
    for current, _, files in os.walk(root):
        for filename in sorted(files):
            if filename.endswith(".json"):
                yield os.path.join(current, filename)


def load_json_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_translation_assets(strict=False):
    dicts_dir = os.path.join(SCRIPT_DIR, "dicts")
    exact_map = {}
    patterns = []
    ignored = []
    issues = []
    seen_keys = defaultdict(list)

    if not os.path.isdir(dicts_dir):
        issues.append(DictIssue("WARN", "未找到 dicts 目录。"))
        return exact_map, patterns, ignored, issues

    for path in iter_json_files(dicts_dir):
        rel = os.path.relpath(path, dicts_dir).replace("\\", "/")
        try:
            data = load_json_file(path)
        except Exception as exc:
            issues.append(DictIssue("ERROR", f"{rel} 不是合法 JSON：{exc}"))
            continue

        stem = os.path.splitext(os.path.basename(path))[0].lower()
        parts = rel.lower().split("/")

        if stem == "ignored" or "ignored" in parts:
            if isinstance(data, list):
                ignored.extend(str(x) for x in data if str(x).strip())
            elif isinstance(data, dict):
                ignored.extend(str(k) for k, v in data.items() if v)
            else:
                issues.append(DictIssue("ERROR", f"{rel} 应为数组或对象。"))
            continue

        if stem == "patterns" or "patterns" in parts:
            if not isinstance(data, list):
                issues.append(DictIssue("ERROR", f"{rel} 应为正则规则数组。"))
                continue
            for index, item in enumerate(data):
                if not isinstance(item, dict) or not item.get("pattern") or "replace" not in item:
                    issues.append(DictIssue("ERROR", f"{rel}[{index}] 缺少 pattern/replace。"))
                    continue
                try:
                    re.compile(str(item["pattern"]))
                except re.error as exc:
                    issues.append(DictIssue("ERROR", f"{rel}[{index}] 正则无效：{exc}"))
                    continue
                patterns.append({"pattern": str(item["pattern"]), "replace": str(item["replace"])})
            continue

        if not isinstance(data, dict):
            issues.append(DictIssue("ERROR", f"{rel} 应为对象。"))
            continue

        for key, value in data.items():
            norm_key = normalize_text(str(key))
            if not norm_key:
                issues.append(DictIssue("WARN", f"{rel} 存在空 key。"))
                continue
            if not isinstance(value, str) or not value.strip():
                issues.append(DictIssue("WARN", f"{rel} 的 {key!r} 翻译为空或不是字符串。"))
                continue
            seen_keys[norm_key].append(rel)
            if norm_key in exact_map and exact_map[norm_key] != value:
                issues.append(DictIssue("WARN", f"{norm_key!r} 在多个词典中译文不一致，已采用 {rel} 的版本。"))
            exact_map[norm_key] = value

    for key, files in seen_keys.items():
        unique_files = sorted(set(files))
        if len(files) > 1 and len(unique_files) == 1:
            issues.append(DictIssue("INFO", f"{key!r} 在同一词典中存在归一化后重复条目：{unique_files[0]}"))

    if strict and any(issue.level == "ERROR" for issue in issues):
        raise RuntimeError("词典存在错误，请先执行 --check-dicts 查看详情。")
    return exact_map, patterns, sorted(set(ignored)), issues


def load_dictionary():
    exact_map, _, _, issues = load_translation_assets()
    for issue in issues:
        if issue.level in {"ERROR", "WARN"}:
            print(f"[!] {issue}")
    return exact_map


def build_injection_js():
    full_dict, patterns, ignored, issues = load_translation_assets()
    for issue in issues:
        if issue.level in {"ERROR", "WARN"}:
            print(f"[!] {issue}")

    long_entries = sorted(full_dict.items(), key=lambda x: len(x[0]), reverse=True)
    dict_json = json.dumps(full_dict, ensure_ascii=False)
    entries_json = json.dumps(long_entries, ensure_ascii=False)
    patterns_json = json.dumps(patterns, ensure_ascii=False)
    ignored_json = json.dumps(ignored, ensure_ascii=False)

    return f"""
{INJECTION_START}
(() => {{
    if (window.__antigravityHanhuaInstalled) return;
    window.__antigravityHanhuaInstalled = true;

    const map = new Map(Object.entries({dict_json}));
    const lowerMap = new Map();
    for (const [k, v] of map.entries()) lowerMap.set(k.toLowerCase(), v);
    const longEntries = {entries_json};
    const patternEntries = {patterns_json}.map(item => [new RegExp(item.pattern), item.replace]);
    const ignoredWords = new Set({ignored_json}.map(x => String(x).toLowerCase()));
    const done = new WeakSet();
    const untranslated = new Set();
    window.__agHanhuaUntranslated = untranslated;
    window.__agHanhuaDumpUntranslated = () => Array.from(untranslated).sort();

    const BLOCKED_CLASSES = [
        'monaco-editor', 'editor-container', 'terminal', 'xterm', 'output-view',
        'debug-console', 'code-view', 'artifact-container', 'suggest-widget',
        'notebook', 'codicon', 'inline-chat', 'view-line'
    ];
    const BLOCKED_TAGS = [
        'SCRIPT', 'STYLE', 'CODE', 'PRE', 'INPUT', 'TEXTAREA',
        'SVG', 'CANVAS', 'SYMBOL', 'PATH'
    ];

    function norm(s) {{
        if (!s) return '';
        return String(s).replace(/\\s+/g, ' ')
            .replace(/[‘’]/g, "'")
            .replace(/[“”]/g, '"')
            .trim();
    }}

    function debugEnabled() {{
        try {{
            return Boolean(window.__agHanhuaDebug) || localStorage.getItem('ag-hanhua-debug') === '1';
        }} catch (_) {{
            return Boolean(window.__agHanhuaDebug);
        }}
    }}

    function shouldIgnoreText(text) {{
        const value = norm(text);
        if (!value || value.length < 2) return true;
        if (!/[A-Za-z]/.test(value)) return true;
        if (/^[\\w./:@#-]+$/.test(value) && !value.includes(' ')) return true;
        return ignoredWords.has(value.toLowerCase());
    }}

    function rememberUntranslated(text) {{
        const value = norm(text);
        if (debugEnabled() && !shouldIgnoreText(value)) untranslated.add(value);
    }}

    function isBlocked(node) {{
        let curr = node && node.nodeType === Node.TEXT_NODE ? node.parentElement : node;
        let depth = 0;
        while (curr && depth < 16) {{
            if (curr.nodeType === Node.ELEMENT_NODE) {{
                const tag = curr.tagName && curr.tagName.toUpperCase();
                if (BLOCKED_TAGS.includes(tag)) return true;
                if (curr.getAttribute && curr.getAttribute('contenteditable') === 'true') return true;

                const className = String(curr.className || '').toLowerCase();
                if (BLOCKED_CLASSES.some(cls => className.includes(cls))) return true;
            }}
            curr = curr.parentElement || (curr.parentNode && curr.parentNode.host);
            depth++;
        }}
        return false;
    }}

    function translateText(original) {{
        const text = norm(original);
        if (!text) return original;
        const lower = text.toLowerCase();
        if (map.has(text)) return map.get(text);
        if (lowerMap.has(lower)) return lowerMap.get(lower);

        for (const [pattern, replacement] of patternEntries) {{
            if (pattern.test(text)) return text.replace(pattern, replacement);
        }}

        let next = text;
        for (const [key, translated] of longEntries) {{
            if (key.length > 20 && next.includes(key)) next = next.split(key).join(translated);
        }}
        return next !== text ? next : original;
    }}

    function translateAttr(node, attr) {{
        const value = node.getAttribute && node.getAttribute(attr);
        if (!value) return;
        const next = translateText(value);
        if (next !== value) node.setAttribute(attr, next);
        else rememberUntranslated(value);
    }}

    function translateNode(node) {{
        try {{
            if (!node || done.has(node)) return;

            if (node.nodeType === Node.ELEMENT_NODE || node.nodeType === Node.DOCUMENT_FRAGMENT_NODE) {{
                const tag = node.tagName && node.tagName.toUpperCase();
                if (BLOCKED_TAGS.includes(tag)) return;

                if (!isBlocked(node) && node.nodeType === Node.ELEMENT_NODE) {{
                    for (const attr of ['placeholder', 'title', 'aria-label', 'alt', 'data-tooltip']) translateAttr(node, attr);
                }}

                if (node.shadowRoot) translateNode(node.shadowRoot);
                for (const child of node.childNodes) translateNode(child);
                return;
            }}

            if (node.nodeType !== Node.TEXT_NODE) return;
            const original = node.nodeValue;
            if (!original || original.trim().length < 1 || isBlocked(node)) return;

            const next = translateText(original);
            if (next !== original) {{
                node.nodeValue = next;
                done.add(node);
                setTimeout(() => done.delete(node), 1000);
            }} else {{
                rememberUntranslated(original);
            }}
        }} catch (_) {{}}
    }}

    function boot() {{
        if (!document.body) return;
        const observer = new MutationObserver(mutations => {{
            for (const mutation of mutations) {{
                if (mutation.type === 'childList') {{
                    for (const node of mutation.addedNodes) translateNode(node);
                }} else if (mutation.type === 'characterData') {{
                    translateNode(mutation.target);
                }}
            }}
        }});
        observer.observe(document.body, {{ childList: true, subtree: true, characterData: true }});
        translateNode(document.body);
        setTimeout(() => translateNode(document.body), 1500);
        setTimeout(() => translateNode(document.body), 4000);
        setTimeout(() => translateNode(document.body), 9000);
    }}

    if (document.readyState === 'loading') {{
        window.addEventListener('DOMContentLoaded', boot, {{ once: true }});
    }} else {{
        setTimeout(boot, 0);
    }}
}})();
{INJECTION_END}
"""


def run_command(args):
    completed = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if completed.returncode != 0:
        raise RuntimeError(f"命令失败: {' '.join(args)}\n{completed.stdout}")
    return completed.stdout


def get_npx_command():
    npx = shutil.which("npx.cmd") or shutil.which("npx")
    if not npx:
        raise RuntimeError("未找到 npx。app.asar 修改需要 Node.js/npm，请安装 Node.js 后重试。")
    return npx


def has_install_layout(path):
    return is_legacy_layout(path) or is_asar_layout(path)


def candidate_install_dirs(path=None):
    candidates = []
    if path:
        candidates.append(os.path.abspath(os.path.expanduser(path)))
    candidates.extend([
        SCRIPT_DIR,
        os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir)),
        os.getcwd(),
    ])
    if os.name == "nt":
        candidates.extend(DEFAULT_WINDOWS_CANDIDATES)
    else:
        candidates.extend(DEFAULT_MAC_CANDIDATES)

    expanded = []
    for item in candidates:
        if not item:
            continue
        item = os.path.abspath(os.path.expanduser(item))
        expanded.extend([
            item,
            os.path.join(item, "Contents", "Resources"),
            os.path.join(item, "resources", "app"),
        ])

    seen = set()
    for item in expanded:
        norm = os.path.normcase(os.path.normpath(item))
        if norm not in seen:
            seen.add(norm)
            yield item


def install_dir_from_args(path):
    for candidate in candidate_install_dirs(path):
        if os.path.isdir(candidate) and has_install_layout(candidate):
            return candidate
    if path:
        return os.path.abspath(os.path.expanduser(path))
    return os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir))


def legacy_paths(install_dir):
    product_json = os.path.join(install_dir, "resources", "app", "product.json")
    hanhua_js = os.path.join(install_dir, "resources", "app", "out", "ag_agent_hanhua.js")
    targets = [os.path.join(install_dir, rel_path(parts)) for parts in LEGACY_TARGET_FILES]
    return product_json, hanhua_js, targets


def is_legacy_layout(install_dir):
    _, _, targets = legacy_paths(install_dir)
    return any(os.path.exists(path) for path in targets)


def backup_legacy_files(install_dir):
    _, _, targets = legacy_paths(install_dir)
    for path in targets:
        bak_path = path + ".bak"
        if os.path.exists(path) and not os.path.exists(bak_path):
            shutil.copy2(path, bak_path)
            print(f"[备份] 已创建: {os.path.basename(path)}.bak")


def install_legacy(install_dir):
    product_json, hanhua_js, targets = legacy_paths(install_dir)
    backup_legacy_files(install_dir)

    os.makedirs(os.path.dirname(hanhua_js), exist_ok=True)
    with open(hanhua_js, "w", encoding="utf-8") as f:
        f.write(build_injection_js())

    changed = False
    inject_str = '<script src="../../../../ag_agent_hanhua.js"></script>'
    for html_path in targets:
        if not os.path.exists(html_path):
            continue
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
        content = re.sub(r"<script[^>]*ag_agent_hanhua\.js[^>]*></script>", "", content)
        content = content.replace("</body>", f"{inject_str}</body>") if "</body>" in content else content + inject_str
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(content)
        changed = True
        print(f"[√] 已注入: {os.path.basename(html_path)}")

    if os.path.exists(product_json):
        update_legacy_checksums(product_json, install_dir)
    if not changed:
        raise RuntimeError("未找到旧版 workbench HTML，无法执行旧版注入。")


def update_legacy_checksums(product_json, install_dir):
    with open(product_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    checksums = data.setdefault("checksums", {})
    for parts in LEGACY_TARGET_FILES:
        rel = rel_path(parts)
        abs_path = os.path.join(install_dir, rel)
        if not os.path.exists(abs_path):
            continue
        key = rel.replace(os.sep, "/").replace("resources/app/out/", "")
        sha256_hash = hashlib.sha256()
        with open(abs_path, "rb") as f:
            for block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(block)
        checksums[key] = base64.b64encode(sha256_hash.digest()).decode("utf-8").rstrip("=")
    with open(product_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent="\t", ensure_ascii=False)
    print("[√] 已同步旧版校验值")


def restore_legacy(install_dir):
    product_json, hanhua_js, targets = legacy_paths(install_dir)
    changed = False
    for path in targets:
        bak_path = path + ".bak"
        if os.path.exists(bak_path):
            shutil.copy2(bak_path, path)
            changed = True
            print(f"[还原] 已恢复: {os.path.basename(path)}")
    if os.path.exists(hanhua_js):
        os.remove(hanhua_js)
        changed = True
        print("[还原] 已删除旧版汉化脚本")
    if changed and os.path.exists(product_json):
        update_legacy_checksums(product_json, install_dir)
    return changed


def asar_paths(install_dir):
    candidates = [
        os.path.join(install_dir, "resources", "app.asar"),
        os.path.join(install_dir, "app.asar"),
        os.path.join(install_dir, "Contents", "Resources", "app.asar"),
    ]
    for asar_path in candidates:
        if os.path.exists(asar_path):
            return asar_path, asar_path + ".hanhua.bak"
    asar_path = candidates[0]
    return asar_path, asar_path + ".hanhua.bak"


def is_asar_layout(install_dir):
    asar_path, _ = asar_paths(install_dir)
    return os.path.exists(asar_path)


def find_preload_file(work_dir):
    preferred = [
        os.path.join(work_dir, "dist", "preload.js"),
        os.path.join(work_dir, "out", "preload.js"),
    ]
    for path in preferred:
        if os.path.exists(path):
            return path

    matches = []
    for current, _, files in os.walk(work_dir):
        for filename in files:
            lower = filename.lower()
            if lower == "preload.js" or lower.endswith(".preload.js"):
                matches.append(os.path.join(current, filename))
    if matches:
        return sorted(matches, key=len)[0]
    return None


def patch_preload(preload_path):
    with open(preload_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = re.sub(
        re.escape(INJECTION_START) + r".*?" + re.escape(INJECTION_END),
        "",
        content,
        flags=re.S,
    ).rstrip()
    content += "\n\n" + build_injection_js().strip() + "\n"

    with open(preload_path, "w", encoding="utf-8") as f:
        f.write(content)


def install_asar(install_dir):
    asar_path, backup_path = asar_paths(install_dir)
    if not os.path.exists(asar_path):
        raise RuntimeError(f"未找到 app.asar: {asar_path}")

    npx = get_npx_command()
    if not os.path.exists(backup_path):
        shutil.copy2(asar_path, backup_path)
        print(f"[备份] 已创建: {backup_path}")
    else:
        print(f"[备份] 已存在，复用: {backup_path}")

    work_dir = tempfile.mkdtemp(prefix="antigravity_hanhua_")
    out_dir = tempfile.mkdtemp(prefix="antigravity_hanhua_pack_")
    new_asar = os.path.join(out_dir, "app.asar")
    try:
        run_command([npx, "--yes", "@electron/asar", "extract", asar_path, work_dir])
        preload_path = find_preload_file(work_dir)
        if not preload_path:
            raise RuntimeError("app.asar 内未找到 preload.js，当前版本暂不支持自动注入。")

        patch_preload(preload_path)
        pack_args = [npx, "--yes", "@electron/asar", "pack"]
        unpack_dir = os.path.join(work_dir, "node_modules", "chrome-devtools-mcp")
        if os.path.isdir(unpack_dir):
            pack_args.extend(["--unpack-dir", "node_modules/chrome-devtools-mcp"])
        pack_args.extend([work_dir, new_asar])
        run_command(pack_args)
        if not os.path.exists(new_asar):
            raise RuntimeError("打包后的 app.asar 未生成。")

        os.replace(new_asar, asar_path)
        print(f"[√] 已完成 app.asar 注入: {asar_path}")
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
        shutil.rmtree(out_dir, ignore_errors=True)


def restore_asar(install_dir):
    asar_path, backup_path = asar_paths(install_dir)
    if not os.path.exists(backup_path):
        return False
    shutil.copy2(backup_path, asar_path)
    print(f"[还原] 已恢复 app.asar: {asar_path}")
    return True


def check_dicts():
    exact_map, patterns, ignored, issues = load_translation_assets()
    errors = [issue for issue in issues if issue.level == "ERROR"]
    warnings = [issue for issue in issues if issue.level == "WARN"]

    print("====== Antigravity 汉化词典检查 ======")
    print(f"[统计] 精确词条: {len(exact_map)}")
    print(f"[统计] 正则模板: {len(patterns)}")
    print(f"[统计] 忽略词条: {len(ignored)}")
    for issue in issues:
        print(str(issue))
    if errors:
        print(f"[错误] 发现 {len(errors)} 个错误，请修复后再注入。")
        return 1
    if warnings:
        print(f"[提示] 发现 {len(warnings)} 个警告，建议后续优化。")
    print("[√] 词典检查完成。")
    return 0


def install(install_dir):
    print("====== Antigravity 汉化注入工具 ======")
    print(f"[路径] 安装目录: {install_dir}")
    if is_legacy_layout(install_dir):
        install_legacy(install_dir)
    elif is_asar_layout(install_dir):
        install_asar(install_dir)
    else:
        raise RuntimeError("未识别 Antigravity 安装结构：既没有旧版 resources/app，也没有 app.asar。请使用 --install-dir 指定正确路径。")
    print("[√] 注入完成，请重新启动 Antigravity。")


def restore(install_dir):
    print("====== 正在恢复 Antigravity 官方原版 ======")
    print(f"[路径] 安装目录: {install_dir}")
    changed = False
    if is_legacy_layout(install_dir):
        changed = restore_legacy(install_dir) or changed
    if is_asar_layout(install_dir):
        changed = restore_asar(install_dir) or changed
    if changed:
        print("[√] 恢复完成。")
    else:
        print("[!] 未找到可用备份，可能尚未安装过汉化。")


def main():
    parser = argparse.ArgumentParser(description="Antigravity 汉化工具")
    parser.add_argument("--install-dir", default=None, help="Antigravity 安装目录、resources 目录或 app.asar 所在目录")
    parser.add_argument("--huifu", action="store_true", help="恢复官方原版")
    parser.add_argument("--check-dicts", action="store_true", help="检查词典 JSON、重复 key 和正则模板")
    args = parser.parse_args()

    if args.check_dicts:
        sys.exit(check_dicts())

    install_dir = install_dir_from_args(args.install_dir)
    if not os.path.isdir(install_dir):
        raise RuntimeError(f"安装目录不存在: {install_dir}")

    if args.huifu:
        restore(install_dir)
    else:
        install(install_dir)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[错误] {exc}", file=sys.stderr)
        sys.exit(1)
