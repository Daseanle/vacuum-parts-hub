# 🤖 24小时自动化 SEO 内容生成系统

## 📋 系统概述

这是一个全自动的 SEO 内容生成系统，每天自动为网站生成新的维修指南页面，增加搜索引擎流量喵～

### ✨ 核心功能

- 🤖 **AI 驱动**：智能识别热门搜索关键词
- 📝 **自动生成**：基于关键词生成高质量的维修指南
- 🔄 **定时执行**：每天凌晨 3 点自动运行
- 🚀 **自动部署**：生成内容后自动提交并部署
- 📊 **数据监控**：实时跟踪生成的内容数量和质量

---

## 🚀 快速开始

### 方式一：GitHub Actions 自动运行（推荐）

**优点**：完全自动化，24/7 运行，无需人工干预

1. ✅ 已经配置好：`.github/workflows/seo-generator.yml`
2. ⏰ 自动运行时间：每天凌晨 3 点（北京时间）
3. 🔄 每周日额外运行一次，生成更多内容

**无需任何操作，系统会自动工作！**喵～

---

### 方式二：手动运行脚本

**适合**：测试或临时需要生成内容时

#### 在本地运行：

```bash
# 1. 进入项目目录
cd /path/to/vacuum-parts-hub

# 2. 运行自动化脚本
./scripts/run-automation.sh

# 3. 查看生成的内容
./scripts/seo-monitor.sh

# 4. 提交到 GitHub（如果需要）
git add data/
git commit -m "🤖 新增 SEO 内容"
git push
```

---

## 📁 文件说明

### 核心脚本

| 文件 | 说明 |
|------|------|
| `scripts/ai-content-generator.py` | AI 内容生成器（主要） |
| `scripts/auto-seo-generator.py` | 关键词组合生成器 |
| `scripts/run-automation.sh` | 一键运行脚本 |
| `scripts/seo-monitor.sh` | SEO 内容监控脚本 |

### 配置文件

| 文件 | 说明 |
|------|------|
| `.github/workflows/seo-generator.yml` | GitHub Actions 定时任务 |
| `lib/vacuum-data.ts` | 数据加载逻辑 |
| `data/*.json` | 生成的维修指南数据 |

---

## 🔧 配置和自定义

### 修改热门关键词列表

编辑 `scripts/ai-content-generator.py`:

```python
TRENDING_KEYWORDS = [
    "Dyson V8 battery replacement",  # 添加你想要的关键词
    "Shark Apex losing suction",
    # ... 添加更多关键词
]
```

### 修改生成内容数量

在 `scripts/ai-content-generator.py` 中：

```python
# 处理前 20 个关键词
for i, keyword in enumerate(TRENDING_KEYWORDS[:20], 1):
    # 改成 [:50] 生成 50 个
```

### 添加自定义问题类型

编辑 `generate_problem_by_type` 函数，添加新的问题类型模板：

```python
problem_templates = {
    "your_new_type": {
        "id": "custom-problem",
        "title": "Your Custom Problem",
        # ... 更多配置
    }
}
```

---

## 📊 监控和统计

### 查看生成统计

```bash
./scripts/seo-monitor.sh
```

**输出示例**：
```
======================================
📊 SEO 内容监控报告
======================================

📁 总维修指南数: 75

📊 各品牌内容统计:
  DYSON: 25 个指南
  SHARK: 18 个指南
  BISSELL: 15 个指南
  ...

🤖 AI 生成内容统计:
  ✓ AI 生成: 50 个
  ✓ 今日新增: 5 个
```

### 查看日志

```bash
# 查看 AI 生成日志
cat logs/ai-generator-20250107.log

# 查看 SEO 生成日志
cat logs/seo-generator-20250107.log
```

---

## 🎯 工作流程

### 自动化流程

```
1. 每天凌晨 3 点
   ↓
2. GitHub Actions 触发
   ↓
3. 运行 AI 内容生成器
   ↓
4. 生成新的 JSON 文件
   ↓
5. 自动提交到 Git
   ↓
6. 推送到 GitHub
   ↓
7. 触发 Vercel 部署
   ↓
8. 新页面上线！
```

---

## 💡 高级用法

### 接入真实 AI API

如果想使用真实的 AI API（如 OpenAI）：

```python
# 在 scripts/ai-content-generator.py 中添加

import openai

def call_ai_api(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

然后在 GitHub Secrets 中添加 `OPENAI_API_KEY`

### 使用 Google Trends API

获取真实的搜索量数据：

```python
import requests

def get_search_volume(keyword):
    # 使用 Google Trends API 或其他数据源
    # 返回实际的搜索量
    pass
```

### 自定义生成策略

```python
# 只生成特定品牌
if brand == "Dyson":
    generate_detailed_guide()  # 生成详细指南

# 只生成特定问题类型
if "battery" in keyword:
    generate_battery_guide()  # 生成电池专题
```

---

## 📈 SEO 优化建议

### 关键词策略

1. **长尾关键词**：3-5 个词的短语更容易排名
   - ✓ 好：`"Dyson V8 battery replacement guide"`
   - ✗ 差：`"Dyson"`

2. **问题导向**：用户搜索的是问题，不是品牌
   - ✓ 好：`"Dyson V8 not charging"`
   - ✗ 差：`"Dyson V8 features"`

3. **本地化**：添加地理位置关键词
   - `"Dyson repair near me"`
   - `"vacuum parts San Francisco"`

### 内容质量

- ✅ 每个页面至少 5 个 SEO 关键词
- ✅ 包含具体的问题描述
- ✅ 提供详细的解决步骤
- ✅ 推荐相关的替换零件

---

## 🔄 定时任务说明

### GitHub Actions 定时

```yaml
schedule:
  # 每天凌晨 3 点（北京时间）
  - cron: '0 19 * * *'

  # 每周日额外运行
  - cron: '0 19 * * 0'
```

### 本地定时任务（macOS/Linux）

使用 `cron` 设置本地定时任务：

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每天凌晨 3 点运行）
0 3 * * * cd /path/to/vacuum-parts-hub && ./scripts/run-automation.sh
```

---

## ⚠️ 注意事项

### 避免重复生成

- ✅ 脚本会自动检查文件是否已存在
- ✅ 存在的文件会被跳过
- ✅ 可以安全地多次运行

### Git 提交策略

- ✅ 每 10 个文件提交一次（避免过多提交）
- ✅ 自动生成友好的提交信息
- ✅ 推送失败不会影响内容生成

### 内容质量控制

- 💡 建议定期检查生成的内容
- 💡 可以手动编辑不满意的 JSON 文件
- 💡 删除低质量页面：`rm data/xxx.json`

---

## 🆘 常见问题

### Q: 如何立即生成内容？

A: 运行 `./scripts/run-automation.sh` 或在 GitHub Actions 页面点击 "Run workflow"

### Q: 生成的内容在哪里？

A: 保存在 `data/` 目录，格式为 `brand-model.json`

### Q: 如何编辑生成的内容？

A: 直接编辑对应的 JSON 文件，然后提交到 Git

### Q: 如何删除某个页面？

A:
```bash
# 删除文件
rm data/dyson-v8-absolute.json

# 提交更改
git add data/
git commit -m "删除页面"
git push
```

### Q: 为什么有些页面没有生成？

A: 可能是文件名冲突，检查是否已存在相同的文件

### Q: 如何增加生成数量？

A: 修改 `TRENDING_KEYWORDS` 列表，添加更多关键词

---

## 📞 需要帮助？

遇到问题请检查：

1. 📋 查看日志：`logs/` 目录
2. 🔍 检查 GitHub Actions 运行记录
3. 📊 运行监控脚本：`./scripts/seo-monitor.sh`

---

_祝主人的网站流量暴涨喵～ (๑ˉ∀ˉ๑)_
