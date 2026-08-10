# image-analysis-fallback

Bridge any non-multimodal model to an external vision API: when the current model cannot see an image, this skill sends it to a multimodal model (default: `qwen3.7-plus`) and feeds the textual result back, so the agent can continue the task.

一个通用的"视觉桥接"技能：当当前模型不支持多模态、无法直接查看图片时，自动将图片交给外部多模态模型（默认 `qwen3.7-plus`）分析，把文字结果反馈回来，让当前模型继续执行任务。

Works with any agent that supports `SKILL.md` — Claude Code, Codex, Cursor, ZCode, and more. No platform-specific dependencies.
兼容所有支持 `SKILL.md` 的 agent（Claude Code、Codex、Cursor、ZCode 等），无任何平台绑定。

## Install / 安装

Clone or symlink this repo into any skill directory:
将本仓库克隆或软链到任意技能的扫描目录：

```bash
git clone https://github.com/anghunk/image-analysis-fallback.git ~/.claude/skills/image-analysis-fallback
```

| Tool | Skill directory |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.codex/skills/` |
| Cursor | `.cursor/skills/` |
| ZCode | `~/.zcode/skills/` |

## Configuration / 配置

Env vars take precedence over `config.json`. 环境变量优先于 `config.json`：

```bash
# Option 1: config file（配置文件）
cp config.example.json config.json   # fill in your api_key

# Option 2: env vars（环境变量）
export VISION_API_KEY=sk-xxxx
```

## Usage / 使用

The skill triggers automatically in new sessions when the user provides an image the current model cannot see. You can also call it manually:
新会话中，当用户提供图片而当前模型无法查看时，技能会自动触发；也可以手动调用：

```bash
python3 analyze_image.py <image-path> "[question]"
```

## Supported API formats / 支持的 API 格式

Set `api_type` in `config.json` (or `VISION_API_TYPE`) to choose the API dialect:
通过 `config.json` 的 `api_type` 字段（或环境变量 `VISION_API_TYPE`）选择接口格式：

| api_type | Providers | Example api_url |
|---|---|---|
| `anthropic` (default) | Claude, DashScope Anthropic-compatible | `https://api.anthropic.com/v1/messages` |
| `openai` | OpenAI, Qwen OpenAI-compatible mode, Ollama, vLLM, LM Studio | `https://api.openai.com/v1/chat/completions` |
| `gemini` | Google Gemini native (`api_url` is the base URL; model name is appended) | `https://generativelanguage.googleapis.com/v1beta` |
| `dashscope` | Alibaba DashScope native multimodal API | `https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation` |

## Options / 配置项

| Env var | Description | Default |
|---|---|---|
| `VISION_API_TYPE` | API dialect: anthropic / openai / gemini / dashscope | `anthropic` |
| `VISION_API_KEY` | API key (overrides config.json) | from `config.json` |
| `VISION_API_URL` | API endpoint (for `gemini`: base URL) | per api_type |
| `VISION_MODEL` | Model name | `qwen3.7-plus` |
| `VISION_MAX_TOKENS` | Max output tokens | `1024` |

## Security / 安全

- `config.json` holds your real API key and is excluded via `.gitignore` — never commit it. `config.json` 含真实 API key，已被 `.gitignore` 排除，请勿提交。
- Analysis results go to stdout only; images and results are never persisted. 分析结果只输出到 stdout，图片与结果均不落盘。
- `config.example.json` is a template with placeholder values. `config.example.json` 是带占位值的模板。
