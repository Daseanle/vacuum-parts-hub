#!/bin/bash
# 环境变量检查脚本
# 用于在部署前验证所有必需的环境变量是否已设置

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 环境变量检查开始..."
echo ""

# 必需的环境变量列表
required_vars=(
  "NODE_ENV"
  "PORT"
  "NEXT_PUBLIC_SITE_URL"
)

# 可选的环境变量列表
optional_vars=(
  "VERCEL_TOKEN"
  "VERCEL_ORG_ID"
  "VERCEL_PROJECT_ID"
  "NEXT_PUBLIC_GA_ID"
)

# 检查必需变量
echo "📋 检查必需的环境变量..."
missing_required=0

for var in "${required_vars[@]}"; do
  if [ -z "${!var}" ]; then
    echo -e "${RED}✗${NC} $var 未设置"
    missing_required=1
  else
    echo -e "${GREEN}✓${NC} $var 已设置"
  fi
done

echo ""
echo "📋 检查可选的环境变量..."

for var in "${optional_vars[@]}"; do
  if [ -z "${!var}" ]; then
    echo -e "${YELLOW}⚠${NC} $var 未设置（可选）"
  else
    echo -e "${GREEN}✓${NC} $var 已设置"
  fi
done

echo ""

if [ $missing_required -eq 1 ]; then
  echo -e "${RED}❌ 错误：缺少必需的环境变量${NC}"
  echo "请设置所有必需的环境变量后重试"
  exit 1
else
  echo -e "${GREEN}✅ 所有必需的环境变量已设置${NC}"
  exit 0
fi
