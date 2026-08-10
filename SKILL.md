---
name: image-analysis-fallback
description: 当用户提供图片（文件路径或附件）而当前模型无法直接查看图片内容时，调用 DashScope 多模态模型 qwen3.7-plus 分析图片，把结果转成文字后继续执行任务
---

# 图片分析降级

当用户提供了图片而你看不到图片内容时：

1. 先确认图片文件存在（`file` / `ls` 检查路径）
2. 运行：`python3 ~/.zcode/skills/image-analysis-fallback/analyze_image.py <图片路径> "<针对图片的问题>"`
3. 脚本会调用 DashScope 的 qwen3.7-plus 并打印文字分析结果
4. 把返回的文字当作你"看到"的内容，当场完成用户的任务；不要把分析结果保存到任何文件，用完即弃
5. 若脚本报错：
   - 检查图片路径是否正确
   - 检查 `config.json` 中的 api_type / API key / 模型名，或设置环境变量 `VISION_API_KEY` 覆盖
   - 将错误信息反馈给用户
