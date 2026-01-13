#!/bin/bash
# 本地自动化内容生成脚本
# 可以在主人的电脑上定时运行

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}🤖 SEO 自动化内容生成器${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# 获取脚本目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo -e "${YELLOW}📍 项目目录: $PROJECT_DIR${NC}"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python3 未安装，尝试使用系统 Python...${NC}"
    PYTHON=python
else
    PYTHON=python3
fi

echo -e "${GREEN}✅ 使用 Python: $PYTHON${NC}"
echo ""

# 创建日志目录
mkdir -p logs

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}开始生成内容...${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# 运行 AI 内容生成器
$PYTHON scripts/ai-content-generator.py

# 检查是否生成了新文件
NEW_FILES=$(git status data/ --short | grep "^??" | wc -l)

echo ""
echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}✅ 生成完成！${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

if [ $NEW_FILES -gt 0 ]; then
    echo -e "${GREEN}📊 生成了 $NEW_FILES 个新文件${NC}"
    echo ""
    echo -e "${YELLOW}📝 下一步操作:${NC}"
    echo "1. 检查生成的内容: git status"
    echo "2. 提交更改: git add data/ && git commit -m '新增 SEO 内容'"
    echo "3. 推送到 GitHub: git push"
    echo ""
    echo -e "${YELLOW}或者一键执行:${NC}"
    echo -e "${GREEN}git add data/ && git commit -m '🤖 新增 SEO 内容' && git push${NC}"
else
    echo -e "${YELLOW}⚠️  没有生成新文件（可能关键词已存在）${NC}"
fi

echo ""
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}📅 运行时间: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo -e "${BLUE}======================================${NC}"
