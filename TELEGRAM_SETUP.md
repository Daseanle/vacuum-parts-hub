# 📱 Telegram 通知设置指南

## 📋 概述

AI 内容生成器现在支持每天自动发送运行报告到 Telegram 喵～
主人可以实时了解内容生成情况，比 Slack 更简单、更高效呢！

---

## 🚀 快速设置（3 步完成）

### 步骤 1: 创建 Telegram Bot

1. **打开 Telegram**
   - 搜索 `@BotFather`（官方机器人）
   - 点击开始对话

2. **创建新机器人**
   - 发送命令 `/newbot`
   - 按提示输入机器人名称（如 "Vacuum SEO Bot"）
   - 输入用户名（如 `vacuum_seo_bot`，必须以 `_bot` 结尾）

3. **获取 Bot Token**
   - BotFather 会返回类似这样的 token：
     ```
     123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
     ```
   - **保存这个 token**，后面要用！

---

### 步骤 2: 获取 Chat ID

1. **给你的 Bot 发消息**
   - 在 Telegram 中找到刚创建的 bot
   - 发送任意消息（如 "hello"）

2. **访问 API 获取 Chat ID**
   - 在浏览器中访问（替换 `<YOUR_BOT_TOKEN>`）：
     ```
     https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
     ```
   - 找到 `"chat":{"id":123456}` 中的数字
   - **这就是你的 Chat ID**

3. **或者用更简单的方法**
   - 在 Telegram 中搜索 `@userinfobot`
   - 点击开始，它会直接告诉你你的 Chat ID

---

### 步骤 3: 配置 GitHub Secrets

1. **打开你的 GitHub 仓库**
   - 进入仓库页面
   - 点击 **Settings**（设置）

2. **添加 Secrets**
   - 左侧菜单找到 **Secrets and variables** → **Actions**
   - 点击 **New repository secret** 按钮

3. **添加第一个 Secret**
   - **Name**: `TELEGRAM_BOT_TOKEN`
   - **Value**: 粘贴你的 bot token（如 `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`）
   - 点击 **Add secret**

4. **添加第二个 Secret**
   - **Name**: `TELEGRAM_CHAT_ID`
   - **Value**: 粘贴你的 chat ID（如 `123456`）
   - 点击 **Add secret**

---

## 🧪 测试通知

运行一次脚本测试 Telegram 通知是否正常：

```bash
# 进入项目目录
cd /Volumes/MOVESPEED/下载/AIcode/vacuum-parts-hub

# 设置环境变量（临时测试）
export TELEGRAM_BOT_TOKEN="你的 bot token"
export TELEGRAM_CHAT_ID="你的 chat id"

# 运行脚本
python3 scripts/ai-content-generator.py
```

如果配置成功，浮浮酱会收到类似这样的通知：

```
✅ SEO 内容生成完成

📅 日期: 2026-01-07
🕐 时间: 03:00:15
✅ 新生成: 3 篇
⏭️ 跳过: 0 篇
📊 总文章数: 103 篇

📝 今日生成的文章:
• Dyson V8 battery replacement
• Dyson V15 not charging
• Dyson V12 pulsing
```

---

## 📊 通知内容说明

每次生成完成后，Telegram 会收到：

- ✅ **绿色通知**：成功生成了新文章
- ℹ️ **灰色通知**：所有文章都已存在（跳过）

**通知包含的信息：**
- 📅 生成日期
- 🕐 生成时间
- ✅ 新生成文章数
- ⏭️ 跳过文章数（文件已存在）
- 📊 网站总文章数
- 📝 今日生成的文章列表

---

## 🔧 高级配置（可选）

### 发送到群组

如果想发送到 Telegram 群组：

1. **把 Bot 添加到群组**
   - 群组设置 → 管理员 → 添加机器人
   - 选择你创建的 bot

2. **获取群组 Chat ID**
   - 访问 `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - 在群组中发一条消息
   - 找到 `"chat":{"id":-1001234567890}`（群组 ID 通常是负数）

3. **更新 GitHub Secret**
   - 修改 `TELEGRAM_CHAT_ID` 为群组 ID（如 `-1001234567890`）

### 自定义通知消息

如果主人想自定义通知格式，可以修改 `scripts/ai-content-generator.py` 中的 `send_telegram_notification` 函数喵～

可以自定义：
- 通知标题
- 表情符号
- 显示的字段
- 添加更多统计信息

---

## ⚠️ 故障排除

### 问题 1: 没有收到 Telegram 通知

**检查清单：**

1. ✅ 确认 Bot Token 和 Chat ID 已正确添加到 GitHub Secrets
2. ✅ 检查日志中是否有错误信息：
   ```bash
   cat logs/ai-generator-20260107.log | grep -i telegram
   ```
3. ✅ 确认你已经给 bot 发送过至少一条消息（激活聊天）
4. ✅ 检查 bot token 是否正确复制（没有多余空格）

### 问题 2: 通知格式异常

- 检查 Telegram API 是否有更新
- 查看 GitHub Actions 运行日志
- 尝试在本地手动运行脚本

### 问题 3: Bot 无响应

- 确认 bot 已创建并激活
- 检查 bot token 是否有效
- 重新获取 token（可能 BotFather 那里有问题）

---

## 💡 提示

1. **保存凭证**：把 bot token 和 chat id 保存在安全的地方
2. **测试连接**：配置完成后立即测试，确保能收到通知
3. **检查权限**：确认 bot 有发送消息的权限
4. **保持活跃**：定期给 bot 发消息，保持连接活跃

---

## 🎯 为什么选择 Telegram 而不是 Slack？

主人选择 Telegram 是因为更简单高效喵～ (๑•̀ㅂ•́)و✧

**Telegram 的优势：**
- ✅ 不需要创建 workspace
- ✅ 不需要创建 webhook
- ✅ 直接用手机号登录
- ✅ API 更简单
- ✅ 支持群组和频道
- ✅ 移动端体验更好
- ✅ 支持消息编辑和删除
- ✅ 完全免费

**相比之下 Slack：**
- ❌ 需要创建整个 workspace
- ❌ webhook 配置复杂
- ❌ 免费版有消息历史限制
- ❌ 移动端体验一般

---

## 🎉 完成！

现在主人已经设置好了 Telegram 通知，每天凌晨 3 点（北京时间）自动生成 3 篇 SEO 文章后，就会收到 Telegram 通知喵～

主人可以：
1. 查看每天生成的文章数量
2. 了解网站总文章数
3. 追踪内容生成进度
4. 及时发现系统问题

浮浮酱会每天为主人自动生成内容，主人只需要坐等流量增长就好啦！o(*￣︶￣*)o

---

_祝主人的网站流量暴涨喵～ ฅ'ω'ฅ_
