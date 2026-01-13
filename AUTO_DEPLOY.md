# 🚀 Vacuum Parts Hub - 24小时自动化部署方案

## 📋 方案概述

这是一个**零配置、全自动**的部署方案喵～

- ✅ **自动构建**：代码推送时自动构建
- ✅ **自动部署**：构建成功后自动部署到 Vercel
- ✅ **24/7 运行**：Vercel 全球 CDN，永远在线
- ✅ **零成本**：个人项目免费使用
- ✅ **HTTPS**：自动配置 SSL 证书

---

## 🎯 一键部署步骤（只需 3 分钟）

### 1️⃣ 连接 GitHub 和 Vercel

1. 访问 [vercel.com](https://vercel.com)
2. 使用 GitHub 账号登录
3. 点击 "Import Project"
4. 选择这个仓库 `vacuum-parts-hub`

### 2️⃣ 配置项目（自动填充）

Vercel 会自动检测到这是 **Next.js** 项目，配置如下：

```bash
Framework Preset: Next.js
Build Command: npm run build
Output Directory: .next
Install Command: npm install
```

### 3️⃣ 点击 Deploy

- 点击 "Deploy" 按钮
- 等待 1-2 分钟...
- ✅ 部署完成！

你会得到一个类似 `vacuum-parts-hub.vercel.app` 的网址喵～

---

## 🔁 自动化工作流程

部署后，每次你推送代码到 `main` 分支：

```bash
git add .
git commit -m "更新内容"
git push origin main
```

**自动发生的事情：**

1. ✅ GitHub Actions 自动触发
2. ✅ 运行构建检查
3. ✅ 自动部署到 Vercel
4. ✅ 全球 CDN 更新
5. ✅ 网站更新完成！

全程自动，无需人工干预喵～

---

## ⚙️ 配置自定义域名（可选）

### 1. 在 Vercel 添加域名

1. 进入项目 Settings → Domains
2. 输入你的域名：`vacuumpartshub.com`
3. Vercel 会提供 DNS 配置

### 2. 更新 DNS 记录

在你的域名提供商添加：

```
Type: CNAME
Name: @
Value: cname.vercel-dns.com
```

### 3. 等待生效

- 通常 5-10 分钟生效
- Vercel 自动配置 SSL 证书
- ✅ 完成！

---

## 🔍 健康检查

定期检查网站是否正常运行：

```bash
# 运行健康检查脚本
./scripts/simple-health-check.sh

# 或手动检查
curl -I https://vacuumpartshub.com
```

---

## 📊 监控和日志

### Vercel Dashboard

访问 [vercel.com/dashboard](https://vercel.com/dashboard) 查看：

- 📈 访问统计
- ⚡ 性能指标
- 🐛 错误日志
- 💰 使用配额

### GitHub Actions

访问仓库的 "Actions" 标签查看：

- ✅ 部署历史
- 📝 构建日志
- ❌ 失败原因

---

## 🎉 完成！

现在你的网站：

- ✅ 24/7 自动运行
- ✅ 全球 CDN 加速
- ✅ 自动 SSL 证书
- ✅ 代码推送自动部署
- ✅ 零维护成本

---

## 🆘 常见问题

### Q: 部署失败怎么办？
A: 检查 GitHub Actions 日志，通常会显示错误原因

### Q: 如何回滚？
A: 在 Vercel Dashboard → Deployments，点击旧版本的 "Promote to Production"

### Q: 多少钱？
A: 个人项目免费！每月 100GB 流量足够使用

### Q: 可以用其他平台吗？
A: 当然！也可以用 Netlify、Railway 等，配置类似

---

## 📝 需要的环境变量（如果有）

在 Vercel 项目设置中添加：

```
NEXT_PUBLIC_SITE_URL=https://vacuumpartshub.com
NODE_ENV=production
```

---

_就这么简单喵～ (๑ˉ∀ˉ๑)_
