#!/bin/bash
# 简单的健康检查脚本
# 用法: ./simple-health-check.sh

SITE_URL="https://vacuumpartshub.com"

echo "🔍 检查网站健康状态..."
echo ""

# 检查网站是否可访问
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SITE_URL")

if [ "$HTTP_CODE" -eq 200 ]; then
  echo "✅ 网站正常运行 (HTTP $HTTP_CODE)"
  echo "📍 网址: $SITE_URL"
  echo "⏰ 检查时间: $(date '+%Y-%m-%d %H:%M:%S')"
  exit 0
else
  echo "❌ 网站异常 (HTTP $HTTP_CODE)"
  echo "📍 网址: $SITE_URL"
  echo "⏰ 检查时间: $(date '+%Y-%m-%d %H:%M:%S')"
  exit 1
fi
