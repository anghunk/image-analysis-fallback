# image-analysis-fallback

ZCode skill：当当前模型不支持多模态、无法直接查看图片时，自动调用 DashScope 多模态模型（qwen3.7-plus）分析图片，把结果转成文字，让当前模型继续执行任务。

## 安装

```bash
# 用户级（所有 workspace 生效）
git clone https://github.com/anghunk/image-analysis-fallback.git ~/.zcode/skills/image-analysis-fallback

# 或项目级（随仓库共享）
git clone https://github.com/anghunk/image-analysis-fallback.git <repo>/.zcode/skills/image-analysis-fallback
```

## 配置

二选一，环境变量优先级更高：

```bash
# 方式一：复制示例配置并填入 API key（config.json 已被 .gitignore 排除，不会提交）
cp config.example.json config.json
# 编辑 config.json 填入 api_key

# 方式二：环境变量
export VISION_API_KEY=sk-xxxx
```

## 使用

新会话中，当用户提供图片而当前模型无法直接查看时，模型会自动加载本 skill；也可以手动触发：

```bash
python3 ~/.zcode/skills/image-analysis-fallback/analyze_image.py <图片路径> [问题]
```

## 支持的 API 格式

`config.json` 的 `api_type` 字段（或环境变量 `VISION_API_TYPE`）选择接口格式：

| api_type | 适用服务 | api_url 示例 |
|---|---|---|
| `anthropic`（默认） | Claude 直连、DashScope Anthropic 兼容接口 | `https://api.anthropic.com/v1/messages`、`https://coding.dashscope.aliyuncs.com/apps/anthropic/v1/messages` |
| `openai` | OpenAI、通义千问 OpenAI 兼容模式、Ollama、vLLM、LM Studio 等 | `https://api.openai.com/v1/chat/completions`、`https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions` |
| `gemini` | Google Gemini 原生接口（api_url 为 base 地址，模型名自动拼入 URL） | `https://generativelanguage.googleapis.com/v1beta` |
| `dashscope` | 阿里云 DashScope 原生多模态接口 | `https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation` |

## 配置项

| 环境变量 | 说明 | 默认值 |
|---|---|---|
| `VISION_API_TYPE` | 接口格式（anthropic / openai / gemini / dashscope） | `anthropic` |
| `VISION_API_KEY` | API key（优先级高于 config.json） | 读取 `config.json` |
| `VISION_API_URL` | Anthropic 兼容 messages 接口地址 | `https://coding.dashscope.aliyuncs.com/apps/anthropic/v1/messages` |
| `VISION_MODEL` | 模型名 | `qwen3.7-plus` |
| `VISION_MAX_TOKENS` | 最大输出 token 数 | `1024` |

## 安全

- `config.json` 包含真实 API key，已被 `.gitignore` 排除，不会提交到仓库
- 分析结果只输出到 stdout，不落盘、不保存图片
- 兼容任何 Anthropic Messages 格式的服务（如 Claude 直连），只需改 `VISION_API_URL` / `VISION_MODEL`
