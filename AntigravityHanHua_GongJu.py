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


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INSTALL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir))

LEGACY_TARGET_FILES = [
    r"resources\app\out\vs\code\electron-browser\workbench\workbench-jetski-agent.html",
    r"resources\app\out\vs\code\electron-browser\workbench\workbench.html",
]

INJECTION_START = "// >>> ANTIGRAVITY_HANHUA_INJECTION_START"
INJECTION_END = "// <<< ANTIGRAVITY_HANHUA_INJECTION_END"


def normalize_text(text):
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text).strip()
    return text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')


def load_dictionary():
    total_map = {}
    dicts_dir = os.path.join(SCRIPT_DIR, "dicts")
    if not os.path.isdir(dicts_dir):
        return total_map

    for filename in os.listdir(dicts_dir):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(dicts_dir, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for key, value in data.items():
                norm_key = normalize_text(key)
                if norm_key:
                    total_map[norm_key] = value
        except Exception as exc:
            print(f"[!] 跳过词典 {filename}: {exc}")
    return total_map


def build_injection_js():
    full_dict = load_dictionary()
    long_entries = sorted(full_dict.items(), key=lambda x: len(x[0]), reverse=True)
    dict_json = json.dumps(full_dict, ensure_ascii=False)
    entries_json = json.dumps(long_entries, ensure_ascii=False)

    return f"""
{INJECTION_START}
(() => {{
    if (window.__antigravityHanhuaInstalled) return;
    window.__antigravityHanhuaInstalled = true;

    const map = new Map(Object.entries({dict_json}));
    const lowerMap = new Map();
    for (const [k, v] of map.entries()) lowerMap.set(k.toLowerCase(), v);
    const longEntries = {entries_json};
    const done = new WeakSet();

    const BLOCKED_CLASSES = [
        'monaco-editor', 'editor-container', 'terminal', 'output-view',
        'debug-console', 'code-view', 'artifact-container', 'suggest-widget'
    ];
    const BLOCKED_TAGS = [
        'SCRIPT', 'STYLE', 'CODE', 'PRE', 'INPUT', 'TEXTAREA',
        'SVG', 'CANVAS', 'SYMBOL', 'PATH'
    ];

    function norm(s) {{
        if (!s) return '';
        return s.replace(/\\s+/g, ' ')
            .replace(/[‘’]/g, "'")
            .replace(/[“”]/g, '"')
            .trim();
    }}

    function isBlocked(node) {{
        let curr = node && node.nodeType === Node.TEXT_NODE ? node.parentElement : node;
        let depth = 0;
        while (curr && depth < 12) {{
            if (curr.nodeType === Node.ELEMENT_NODE) {{
                const tag = curr.tagName && curr.tagName.toUpperCase();
                if (BLOCKED_TAGS.includes(tag)) return true;
                if (curr.getAttribute && curr.getAttribute('contenteditable') === 'true') return true;

                const className = curr.className || '';
                if (typeof className === 'string' &&
                    BLOCKED_CLASSES.some(cls => className.includes(cls))) {{
                    return true;
                }}
            }}
            curr = curr.parentElement || (curr.parentNode && curr.parentNode.host);
            depth++;
        }}
        return false;
    }}

    function translateNode(node) {{
        try {{
            if (!node || done.has(node)) return;

            if (node.nodeType === Node.ELEMENT_NODE) {{
                const tag = node.tagName && node.tagName.toUpperCase();
                if (BLOCKED_TAGS.includes(tag)) return;

                if (!isBlocked(node)) {{
                    for (const attr of ['placeholder', 'title', 'aria-label']) {{
                        const value = node.getAttribute && node.getAttribute(attr);
                        if (!value) continue;
                        const text = norm(value);
                        if (map.has(text)) node.setAttribute(attr, map.get(text));
                        else if (lowerMap.has(text.toLowerCase())) node.setAttribute(attr, lowerMap.get(text.toLowerCase()));
                    }}
                }}

                if (node.shadowRoot) translateNode(node.shadowRoot);
                for (const child of node.childNodes) translateNode(child);
                return;
            }}

            if (node.nodeType !== Node.TEXT_NODE) return;
            const original = node.nodeValue;
            if (!original || original.trim().length < 1 || isBlocked(node)) return;

            let next = original;
            const text = norm(original);
            const lower = text.toLowerCase();
            if (map.has(text)) {{
                next = map.get(text);
            }} else if (lowerMap.has(lower)) {{
                next = lowerMap.get(lower);
            }} else {{
                for (const [key, translated] of longEntries) {{
                    if (key.length > 20 && text.includes(key)) {{
                        next = next.split(key).join(translated);
                    }}
                }}
            }}

            if (next !== original) {{
                node.nodeValue = next;
                done.add(node);
                setTimeout(() => done.delete(node), 1000);
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
        raise RuntimeError("未找到 npx。当前 Antigravity 2.0.6 的 app.asar 修改需要 Node.js/npm。")
    return npx


def install_dir_from_args(path):
    return os.path.abspath(path or DEFAULT_INSTALL_DIR)


def legacy_paths(install_dir):
    product_json = os.path.join(install_dir, r"resources\app\product.json")
    hanhua_js = os.path.join(install_dir, r"resources\app\out\ag_agent_hanhua.js")
    targets = [os.path.join(install_dir, rel) for rel in LEGACY_TARGET_FILES]
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
        content = re.sub(r"<script.*ag_agent_hanhua\.js.*</script>", "", content)
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
    for rel_path in LEGACY_TARGET_FILES:
        abs_path = os.path.join(install_dir, rel_path)
        if not os.path.exists(abs_path):
            continue
        key = rel_path.replace("\\", "/").replace("resources/app/out/", "")
        sha256_hash = hashlib.sha256()
        with open(abs_path, "rb") as f:
            for block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(block)
        checksums[key] = base64.b64encode(sha256_hash.digest()).decode("utf-8").rstrip("=")
    with open(product_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent="\t")
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
    asar_path = os.path.join(install_dir, r"resources\app.asar")
    backup_path = asar_path + ".hanhua.bak"
    return asar_path, backup_path


def is_asar_layout(install_dir):
    asar_path, _ = asar_paths(install_dir)
    return os.path.exists(asar_path)


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
        preload_path = os.path.join(work_dir, "dist", "preload.js")
        if not os.path.exists(preload_path):
            raise RuntimeError("app.asar 内未找到 dist/preload.js，当前版本暂不支持自动注入。")

        patch_preload(preload_path)
        run_command([
            npx,
            "--yes",
            "@electron/asar",
            "pack",
            "--unpack-dir",
            "node_modules/chrome-devtools-mcp",
            work_dir,
            new_asar,
        ])
        if not os.path.exists(new_asar):
            raise RuntimeError("打包后的 app.asar 未生成。")

        os.replace(new_asar, asar_path)
        print("[√] 已完成 Antigravity 2.0.6 app.asar 注入")
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


def install(install_dir):
    print("====== Antigravity 汉化注入工具 ======")
    print(f"[路径] 安装目录: {install_dir}")
    if is_legacy_layout(install_dir):
        install_legacy(install_dir)
    elif is_asar_layout(install_dir):
        install_asar(install_dir)
    else:
        raise RuntimeError("未识别 Antigravity 安装结构：既没有旧版 resources\\app，也没有 resources\\app.asar。")
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
    parser.add_argument("--install-dir", default=None, help="Antigravity 安装目录")
    parser.add_argument("--huifu", action="store_true", help="恢复官方原版")
    args = parser.parse_args()

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
