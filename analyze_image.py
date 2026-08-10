#!/usr/bin/env python3
"""通过 DashScope Anthropic 兼容接口分析图片，输出文字结果。

用法:
    python3 analyze_image.py <图片路径> [问题]

配置优先级: 环境变量 > 本目录 config.json
    VISION_API_KEY   - API key
    VISION_API_URL   - 完整 messages 接口地址
    VISION_MODEL     - 模型名
    VISION_MAX_TOKENS- 最大输出 token 数（默认 1024）
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
DEFAULTS = {
    "api_url": "https://coding.dashscope.aliyuncs.com/apps/anthropic/v1/messages",
    "model": "qwen3.7-plus",
}


def ssl_context():
    """优先用 certifi 证书库，解决 macOS Python 自带 CA 不完整导致的校验失败。"""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def load_config():
    cfg = dict(DEFAULTS)
    cfg_file = os.path.join(HERE, "config.json")
    if os.path.exists(cfg_file):
        with open(cfg_file, encoding="utf-8") as f:
            cfg.update(json.load(f))
    cfg["api_key"] = os.environ.get("VISION_API_KEY", cfg.get("api_key", ""))
    cfg["api_url"] = os.environ.get("VISION_API_URL", cfg["api_url"])
    cfg["model"] = os.environ.get("VISION_MODEL", cfg["model"])
    return cfg


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
    if not cfg["api_key"]:
        print("缺少 API key：请设置环境变量 VISION_API_KEY 或编辑 config.json", file=sys.stderr)
        return 1

    media_type = mimetypes.guess_type(image_path)[0] or "image/png"
    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()

    payload = {
        "model": cfg["model"],
        "max_tokens": int(os.environ.get("VISION_MAX_TOKENS", 1024)),
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": data}},
                {"type": "text", "text": question},
            ],
        }],
    }

    req = urllib.request.Request(
        cfg["api_url"],
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "x-api-key": cfg["api_key"],
            "anthropic-version": ANTHROPIC_VERSION,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120, context=ssl_context()) as resp:
            result = json.load(resp)
    except urllib.error.HTTPError as e:
        print(f"API 调用失败 (HTTP {e.code}): {e.read().decode(errors='replace')}", file=sys.stderr)
        return 1
    except urllib.error.URLError as e:
        print(f"网络错误: {e.reason}", file=sys.stderr)
        return 1

    text = "".join(b.get("text", "") for b in result.get("content", []))
    print(text.strip())


if __name__ == "__main__":
    sys.exit(main())
