# image-analysis-fallback

> [中文文档](./README.zh-CN.md)

Bridge any non-multimodal model to an external vision API: when the current model cannot see an image, this skill sends it to a multimodal model (default: `qwen3.7-plus`) and feeds the textual result back, so the agent can continue the task.

Works with any agent that supports `SKILL.md` — Claude Code, Codex, Cursor, ZCode, and more. No platform-specific dependencies.

## Install

Clone or symlink this repo into any skill directory:

```bash
git clone https://github.com/anghunk/image-analysis-fallback.git ~/.claude/skills/image-analysis-fallback
```

| Tool | Skill directory |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.codex/skills/` |
| Cursor | `.cursor/skills/` |
| ZCode | `~/.zcode/skills/` |

## Configuration

Env vars take precedence over `config.json`:

```bash
# Option 1: config file
cp config.example.json config.json   # fill in your api_key

# Option 2: env vars
export VISION_API_KEY=sk-xxxx
```

## Usage

The skill triggers automatically in new sessions when the user provides an image the current model cannot see. You can also call it manually:

```bash
python3 analyze_image.py <image-path> "[question]"
```

## Supported API formats

Set `api_type` in `config.json` (or `VISION_API_TYPE`) to choose the API dialect:

| api_type | Providers | Example api_url |
|---|---|---|
| `anthropic` (default) | Claude, DashScope Anthropic-compatible | `https://api.anthropic.com/v1/messages` |
| `openai` | OpenAI, Qwen OpenAI-compatible mode, Ollama, vLLM, LM Studio | `https://api.openai.com/v1/chat/completions` |
| `gemini` | Google Gemini native (`api_url` is the base URL; model name is appended) | `https://generativelanguage.googleapis.com/v1beta` |
| `dashscope` | Alibaba DashScope native multimodal API | `https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation` |

## Options

| Env var | Description | Default |
|---|---|---|
| `VISION_API_TYPE` | API dialect: anthropic / openai / gemini / dashscope | `anthropic` |
| `VISION_API_KEY` | API key (overrides config.json) | from `config.json` |
| `VISION_API_URL` | API endpoint (for `gemini`: base URL) | per api_type |
| `VISION_MODEL` | Model name | `qwen3.7-plus` |
| `VISION_MAX_TOKENS` | Max output tokens | `1024` |
