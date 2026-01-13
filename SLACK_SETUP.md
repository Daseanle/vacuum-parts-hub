# 🔔 Slack 通知设置指南

## 📋 概述

AI 内容生成器现在支持每天自动发送运行报告到 Slack 喵～这样主人就可以实时了解内容生成情况了呢！

---

## 🚀 快速设置

### 步骤 1: 创建 Slack Incoming Webhook

1. 访问 [Slack API](https://api.slack.com/apps)
2. 点击 **"Create New App"** 创建新应用
3. 给应用起个名字，比如 "SEO Content Generator"
4. 选择你的 Workspace
5. 在左侧菜单选择 **"Incoming Webhooks"**
6. 开启 **"Activate Incoming Webhooks"**
7. 点击 **"Add New Webhook to Workspace"**
8. 选择要接收通知的频道
9. 复制生成的 **Webhook URL**（格式：`https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX`）

### 步骤 2: 配置 GitHub Secrets

1. 打开你的 GitHub 仓库
2. 进入 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **"New repository secret"**
4. 创建以下 Secret：
   - **Name**: `SLACK_WEBHOOK_URL`
   - **Value**: 粘贴刚才复制的 Webhook URL
5. 点击 **"Add secret"**

### 步骤 3: 测试通知

运行一次脚本测试 Slack 通知是否正常：

```bash
# 设置环境变量（临时测试）
export SLACK_WEBHOOK_URL="你的 Webhook URL"

# 运行脚本
python3 scripts/ai-content-generator.py
```

---

## 📊 通知内容

每天生成完成后，Slack 会收到类似这样的通知：

```
✅ SEO 内容生成完成

📅 日期:    2026-01-07
🕐 时间:    03:00:15
✅ 新生成:  3 篇
⏭️ 跳过:    0 篇
📊 总文章数: 103 篇

📝 今日生成的文章:
• Dyson V8 battery replacement
• Dyson V15 not charging
• Dyson V12 pulsing
```

---

## 🎨 通知样式

- ✅ **绿色通知**：生成了新文章
- ℹ️ **灰色通知**：所有文章都已存在（跳过）

---

## 🔧 可选配置

### 发送到不同的频道

如果想发送到不同的 Slack 频道：

1. 在 Slack 中创建新的 Incoming Webhook
2. 在 GitHub Secrets 中添加新的 Secret，比如 `SLACK_WEBHOOK_URL_BACKUP`
3. 修改 `scripts/ai-content-generator.py` 中的 `send_slack_notification` 函数

### 自定义通知消息

编辑 `scripts/ai-content-generator.py` 中的 `send_slack_notification` 函数，可以自定义：
- 通知标题
- 颜色
- 显示的字段
- 添加更多统计信息

### 添加邮件通知

如果想同时发送邮件通知，可以修改函数：

```python
def send_notification(generated, skipped, keywords_today):
    # Slack 通知
    send_slack_notification(generated, skipped, keywords_today)

    # 邮件通知（需要配置 SMTP）
    send_email_notification(generated, skipped, keywords_today)
```

---

## ⚠️ 故障排除

### 问题：没有收到 Slack 通知

**检查清单：**

1. ✅ 确认 Webhook URL 已正确添加到 GitHub Secrets
2. ✅ 确认选择了正确的 Slack 频道
3. ✅ 检查日志中是否有错误信息：
   ```bash
   cat logs/ai-generator-20260107.log | grep -i slack
   ```
4. ✅ 测试 Webhook 是否有效：
   ```bash
   curl -X POST "你的 Webhook URL" \
     -H 'Content-Type: application/json' \
     -d '{"text":"测试通知"}'
   ```

### 问题：通知格式异常

- 检查 Slack API 是否有更新
- 查看 Actions 运行日志
- 尝试重新发送通知

---

## 📱 其他通知方式

### Discord Webhook

也可以使用 Discord 代替 Slack：

1. 在 Discord 服务器设置中创建 Webhook
2. 使用相同的代码，只需替换 URL 即可
3. Discord Webhook 格式兼容 Slack

### 企业微信/钉钉

如果想使用企业微信或钉钉，浮浮酱可以帮你添加对应的通知函数喵～

---

## 🎯 最佳实践

1. **专用频道**：创建专门的 `#seo-content-updates` 频道
2. **设置提醒**：在 Slack 中为该频道开启通知提醒
3. **定期检查**：定期查看通知，确保系统正常运行
4. **保存日志**：保留 Slack 通知历史，便于追踪生成记录

---

_祝主人的网站流量暴涨喵～ (๑ˉ∀ˉ๑)_
