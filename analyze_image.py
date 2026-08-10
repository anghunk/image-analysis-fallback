#!/usr/bin/env python3
"""通过多模态 API 分析图片，输出文字结果。兼容多种 API 格式。

用法:
    python3 analyze_image.py <图片路径> [问题]

配置优先级: 环境变量 > 本目录 config.json

config.json 字段:
    api_type - 接口格式: anthropic | openai | gemini | dashscope（默认 anthropic）
    api_key  - API key
    api_url  - 接口地址（gemini 类型为 base 地址，模型名自动拼入 URL）
    model    - 模型名

环境变量（同名覆盖）:
    VISION_API_TYPE / VISION_API_KEY / VISION_API_URL / VISION_MODEL / VISION_MAX_TOKENS
"""
import base64
import json
import mimetypes
import os
import ssl
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ANTHROPIC_VERSION = "2023-06-01"

DEFAULT_URLS = {
    "anthropic": "https://api.anthropic.com/v1/messages",
    "openai": "https://api.openai.com/v1/chat/completions",
    "gemini": "https://generativelanguage.googleapis.com/v1beta",
    "dashscope": "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
}
ENV_MAP = {
    "api_type": "VISION_API_TYPE",
    "api_key": "VISION_API_KEY",
    "api_url": "VISION_API_URL",
    "model": "VISION_MODEL",
}


def ssl_context():
    """优先用 certifi 证书库，解决 macOS Python 自带 CA 不完整导致的校验失败。"""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def load_config():
    cfg = {"api_type": "anthropic", "model": "qwen3.7-plus"}
    cfg_file = os.path.join(HERE, "config.json")
    if os.path.exists(cfg_file):
        with open(cfg_file, encoding="utf-8") as f:
            cfg.update(json.load(f))
    cfg["api_type"] = (cfg.get("api_type") or "anthropic").lower()
    for key, env in ENV_MAP.items():
        if os.environ.get(env):
            cfg[key] = os.environ[env]
    cfg.setdefault("api_url", DEFAULT_URLS.get(cfg["api_type"], ""))
    return cfg


def http_post(url, headers, payload, timeout=120):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_context()) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode(errors='replace')}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"网络错误: {e.reason}")


def join_text(content):
    """兼容 content 为字符串或 [{text}] 列表两种形态。"""
    if isinstance(content, str):
        return content
    return "".join(b.get("text", "") for b in content if isinstance(b, dict))


# ---- 各格式适配 ----

def call_anthropic(cfg, media_type, b64, question, max_tokens):
    payload = {
        "model": cfg["model"],
        "max_tokens": max_tokens,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
                {"type": "text", "text": question},
            ],
        }],
    }
    result = http_post(cfg["api_url"], {
        "Content-Type": "application/json",
        "x-api-key": cfg["api_key"],
        "anthropic-version": ANTHROPIC_VERSION,
    }, payload)
    # 跳过 thinking 等非 text 块
    return "".join(b.get("text", "") for b in result.get("content", []))


def call_openai(cfg, media_type, b64, question, max_tokens):
    payload = {
        "model": cfg["model"],
        "max_tokens": max_tokens,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": question},
                {"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{b64}"}},
            ],
        }],
    }
    result = http_post(cfg["api_url"], {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {cfg['api_key']}",
    }, payload)
    return join_text(result["choices"][0]["message"]["content"])


def call_gemini(cfg, media_type, b64, question, max_tokens):
    url = f"{cfg['api_url'].rstrip('/')}/models/{cfg['model']}:generateContent"
    payload = {
        "contents": [{
            "role": "user",
            "parts": [
                {"text": question},
                {"inline_data": {"mime_type": media_type, "data": b64}},
            ],
        }],
        "generationConfig": {"maxOutputTokens": max_tokens},
    }
    result = http_post(url, {
        "Content-Type": "application/json",
        "x-goog-api-key": cfg["api_key"],
    }, payload)
    parts = result.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    return "\n".join(p.get("text", "") for p in parts if p.get("text"))


def call_dashscope(cfg, media_type, b64, question, max_tokens):
    payload = {
        "model": cfg["model"],
        "input": {"messages": [{
            "role": "user",
            "content": [
                {"image": f"data:{media_type};base64,{b64}"},
                {"text": question},
            ],
        }]},
        "parameters": {"max_tokens": max_tokens},
    }
    result = http_post(cfg["api_url"], {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {cfg['api_key']}",
    }, payload)
    return join_text(result["output"]["choices"][0]["message"]["content"])


CALLERS = {
    "anthropic": call_anthropic,
    "openai": call_openai,
    "gemini": call_gemini,
    "dashscope": call_dashscope,
}


def main():
    if len(sys.argv) < 2:
        print("用法: analyze_image.py <图片路径> [问题]", file=sys.stderr)
        return 2
    image_path = sys.argv[1]
    question = sys.argv[2] if len(sys.argv) > 2 else "请详细描述这张图片的内容"

    if not os.path.isfile(image_path):
        print(f"图片不存在: {image_path}", file=sys.stderr)
        return 1

    cfg = load_config()
    if cfg["api_type"] not in CALLERS:
        print(f"不支持的 api_type: {cfg['api_type']}（支持: {', '.join(CALLERS)}）", file=sys.stderr)
        return 1
    if not cfg.get("api_key"):
        print("缺少 API key：请设置环境变量 VISION_API_KEY 或编辑 config.json", file=sys.stderr)
        return 1

    media_type = mimetypes.guess_type(image_path)[0] or "image/png"
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    max_tokens = int(os.environ.get("VISION_MAX_TOKENS", 1024))
    try:
        text = CALLERS[cfg["api_type"]](cfg, media_type, b64, question, max_tokens)
    except RuntimeError as e:
        print(f"调用失败 ({cfg['api_type']}): {e}", file=sys.stderr)
        return 1
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as e:
        print(f"响应解析失败 ({cfg['api_type']}): {e}", file=sys.stderr)
        return 1

    print(text.strip())


if __name__ == "__main__":
    sys.exit(main())
