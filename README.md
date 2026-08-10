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

## 配置项

| 环境变量 | 说明 | 默认值 |
|---|---|---|
| `VISION_API_KEY` | API key（优先级高于 config.json） | 读取 `config.json` |
| `VISION_API_URL` | Anthropic 兼容 messages 接口地址 | `https://coding.dashscope.aliyuncs.com/apps/anthropic/v1/messages` |
| `VISION_MODEL` | 模型名 | `qwen3.7-plus` |
| `VISION_MAX_TOKENS` | 最大输出 token 数 | `1024` |

## 安全

- `config.json` 包含真实 API key，已被 `.gitignore` 排除，不会提交到仓库
- 分析结果只输出到 stdout，不落盘、不保存图片
- 兼容任何 Anthropic Messages 格式的服务（如 Claude 直连），只需改 `VISION_API_URL` / `VISION_MODEL`
