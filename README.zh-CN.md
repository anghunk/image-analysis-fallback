# image-analysis-fallback

> [English](./README.md)

一个通用的"视觉桥接"技能：当当前模型不支持多模态、无法直接查看图片时，自动将图片交给外部多模态模型（默认 `qwen3.7-plus`）分析，把文字结果反馈回来，让当前模型继续执行任务。

兼容所有支持 `SKILL.md` 的 agent（Claude Code、Codex、Cursor、ZCode 等），无任何平台绑定。

## 安装

将本仓库克隆或软链到任意技能的扫描目录：

```bash
git clone https://github.com/anghunk/image-analysis-fallback.git ~/.zcode/skills/image-analysis-fallback
```

| 工具 | 技能目录 |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.codex/skills/` |
| Cursor | `.cursor/skills/` |
| ZCode | `~/.zcode/skills/` |

## 配置

环境变量优先于 `config.json`：

```bash
# 方式一：配置文件
cp config.example.json config.json   # 填入你的 API key

# 方式二：环境变量
export VISION_API_KEY=sk-xxxx
```

## 使用

新会话中，当用户提供图片而当前模型无法查看时，技能会自动触发；也可以手动调用：

```bash
python3 analyze_image.py <图片路径> "[问题]"
```

## 支持的 API 格式

通过 `config.json` 的 `api_type` 字段（或环境变量 `VISION_API_TYPE`）选择接口格式：

| api_type | 适用服务 | api_url 示例 |
|---|---|---|
| `anthropic`（默认） | Claude、DashScope Anthropic 兼容接口 | `https://api.anthropic.com/v1/messages` |
| `openai` | OpenAI、通义千问 OpenAI 兼容模式、Ollama、vLLM、LM Studio | `https://api.openai.com/v1/chat/completions` |
| `gemini` | Google Gemini 原生接口（api_url 为 base 地址，模型名自动拼入 URL） | `https://generativelanguage.googleapis.com/v1beta` |
| `dashscope` | 阿里云 DashScope 原生多模态接口 | `https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation` |

## 配置项

| 环境变量 | 说明 | 默认值 |
|---|---|---|
| `VISION_API_TYPE` | 接口格式：anthropic / openai / gemini / dashscope | `anthropic` |
| `VISION_API_KEY` | API key（优先于 config.json） | 读取 `config.json` |
| `VISION_API_URL` | 接口地址（gemini 类型为 base 地址） | 随 api_type |
| `VISION_MODEL` | 模型名 | `qwen3.7-plus` |
| `VISION_MAX_TOKENS` | 最大输出 token 数 | `1024` |
