# Vacuum Parts Hub - Docker 配置
# 多阶段构建，优化镜像大小和构建速度

# ============================================
# Stage 1: 依赖安装阶段
# ============================================
FROM node:20-alpine AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# 复制依赖文件
COPY package.json package-lock.json* ./
# 使用 npm ci 进行快速、可靠的安装
RUN npm ci --only=production && \
    npm cache clean --force

# ============================================
# Stage 2: 构建阶段
# ============================================
FROM node:20-alpine AS builder
WORKDIR /app

# 复制依赖（从上一个阶段）
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# 设置环境变量
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

# 构建应用
RUN npm run build && \
    # 清理开发依赖
    rm -rf .next/cache

# ============================================
# Stage 3: 运行阶段
# ============================================
FROM node:20-alpine AS runner
WORKDIR /app

# 设置非 root 用户以提高安全性
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# 复制必要文件
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json

# 自动利用输出跟踪来减小镜像大小
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

CMD ["node", "server.js"]
