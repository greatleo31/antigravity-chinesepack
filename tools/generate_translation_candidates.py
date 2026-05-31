#!/usr/bin/env python3
import argparse
import datetime as _dt
import json
import os
import re
import sys
import urllib.error
import urllib.request


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DEFAULT_GUIDE = os.path.join(PROJECT_ROOT, "TRANSLATION_STYLE_GUIDE.md")
DEFAULT_GLOSSARY = os.path.join(PROJECT_ROOT, "dicts", "glossary.json")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def collect_entries(source_path):
    data = load_json(source_path)
    if not isinstance(data, dict):
        raise ValueError("当前脚本只支持处理普通对象词典，不支持 patterns.json / ignored.json。")
    items = []
    for key, value in data.items():
        if not isinstance(value, str):
            continue
        items.append({
            "source": key,
            "current_translation": value,
        })
    return items


def build_prompt(source_path, items, glossary, style_guide):
    glossary_lines = "\n".join(f"- {k} -> {v}" for k, v in glossary.items())
    payload = {
        "source_file": os.path.relpath(source_path, PROJECT_ROOT).replace("\\", "/"),
        "items": items,
    }
    return f"""你是专业的软件本地化审校助手，正在为 Antigravity 中文语言包生成候选译文。\n\n请严格遵守以下要求：\n1. 保持原意，不擅自增加产品不存在的信息。\n2. 优先保证术语统一，必须遵守下列术语表。\n3. 输出要自然、简洁、像真实软件界面。\n4. 如果当前译文已经很好，也可以保留。\n5. 不要解释过程，不要输出 Markdown，只输出 JSON。\n6. 输出格式必须为数组，每项包含：source、current_translation、suggested_translation、reason。\n\n【术语表】\n{glossary_lines}\n\n【风格指南】\n{style_guide}\n\n【待处理条目】\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n"""


def extract_json(text):
    text = text.strip()
    if not text:
        raise ValueError("API 返回为空。")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
        if match:
            return json.loads(match.group(1).strip())
        raise


def call_anthropic(api_key, model, prompt, max_tokens):
    url = "https://api.anthropic.com/v1/messages"
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": 0.2,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        data = json.loads(response.read().decode("utf-8"))
    chunks = []
    for item in data.get("content", []):
        if item.get("type") == "text":
            chunks.append(item.get("text", ""))
    return "\n".join(chunks).strip()


def ensure_parent(path):
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description="为词典生成 AI 候选译文（默认使用 Anthropic API）")
    parser.add_argument("--input", required=True, help="需要审校的词典 JSON 文件")
    parser.add_argument("--output", default=None, help="输出候选结果 JSON 文件")
    parser.add_argument("--glossary", default=DEFAULT_GLOSSARY, help="术语表文件路径")
    parser.add_argument("--style-guide", default=DEFAULT_GUIDE, help="风格指南文件路径")
    parser.add_argument("--model", default="claude-sonnet-4-6", help="调用的模型 ID")
    parser.add_argument("--api-key-env", default="ANTHROPIC_API_KEY", help="API Key 环境变量名")
    parser.add_argument("--batch-size", type=int, default=20, help="每批提交的条目数")
    parser.add_argument("--max-tokens", type=int, default=4096, help="单批最大输出 token")
    parser.add_argument("--prompt-only", action="store_true", help="只输出首批 prompt，不调用 API")
    args = parser.parse_args()

    source_path = os.path.abspath(args.input)
    output_path = args.output or os.path.splitext(source_path)[0] + ".candidates.json"
    glossary = load_json(os.path.abspath(args.glossary)) if os.path.isfile(args.glossary) else {}
    style_guide = load_text(os.path.abspath(args.style_guide)) if os.path.isfile(args.style_guide) else ""
    items = collect_entries(source_path)
    if not items:
        raise RuntimeError("没有可处理的词典条目。")

    first_prompt = build_prompt(source_path, items[: args.batch_size], glossary, style_guide)
    if args.prompt_only:
        sys.stdout.write(first_prompt)
        return

    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise RuntimeError(f"未找到环境变量 {args.api_key_env}。可先使用 --prompt-only 手动审校。")

    all_results = []
    for start in range(0, len(items), args.batch_size):
        batch = items[start : start + args.batch_size]
        prompt = build_prompt(source_path, batch, glossary, style_guide)
        print(f"[批次] {start + 1}-{start + len(batch)} / {len(items)}")
        try:
            text = call_anthropic(api_key, args.model, prompt, args.max_tokens)
            batch_result = extract_json(text)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"API 请求失败：HTTP {exc.code}\n{detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"API 请求失败：{exc}") from exc
        if not isinstance(batch_result, list):
            raise RuntimeError("API 返回格式不正确：顶层不是数组。")
        all_results.extend(batch_result)

    result = {
        "source_file": os.path.relpath(source_path, PROJECT_ROOT).replace("\\", "/"),
        "model": args.model,
        "api_key_env": args.api_key_env,
        "generated_at": _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "count": len(all_results),
        "results": all_results,
    }
    ensure_parent(os.path.abspath(output_path))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"[完成] 已生成候选译文：{output_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[错误] {exc}", file=sys.stderr)
        sys.exit(1)
