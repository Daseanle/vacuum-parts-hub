#!/bin/bash
# SEO 内容生成监控脚本
# 监控生成的内容数量和质量

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$PROJECT_DIR/data"

cd "$PROJECT_DIR"

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}📊 SEO 内容监控报告${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# 统计文件数量
TOTAL_FILES=$(find "$DATA_DIR" -name "*.json" -not -name "vacuums.json" -not -name "sharks.json" -not -name "bissells.json" | wc -l)

echo -e "${GREEN}📁 总维修指南数: $TOTAL_FILES${NC}"

# 统计各品牌数量
echo ""
echo -e "${BLUE}📊 各品牌内容统计:${NC}"
echo ""

for brand in dyson shark bissell irobot hoover miele roborock eufy tineco; do
    count=$(find "$DATA_DIR" -name "${brand}-*.json" | wc -l)
    if [ $count -gt 0 ]; then
        echo -e "  ${GREEN}✓${NC} $(echo "$brand" | sed 's/.*/\U&/')${NC}: $count 个指南"
    fi
done

# 最新生成的文件
echo ""
echo -e "${BLUE}📝 最新生成的 5 个文件:${NC}"
echo ""
ls -t "$DATA_DIR"/*.json 2>/dev/null | grep -v -E "(vacuums|sharks|bissells)\.json" | head -5 | while read file; do
    filename=$(basename "$file")
    echo "  📄 $filename"
done

# 检查自动生成的内容
echo ""
echo -e "${BLUE}🤖 AI 生成内容统计:${NC}"
echo ""

AUTO_GEN=$(grep -l '"auto_generated": true' "$DATA_DIR"/*.json 2>/dev/null | wc -l)
echo -e "  ${GREEN}✓${NC} AI 生成: $AUTO_GEN 个"

# 检查今日生成
TODAY=$(date +%Y-%m-%d)
TODAY_COUNT=$(grep -l "\"generated_date\": \"$TODAY" "$DATA_DIR"/*.json 2>/dev/null | wc -l)
echo -e "  ${GREEN}✓${NC} 今日新增: $TODAY_COUNT 个"

# 预估页面覆盖率
echo ""
echo -e "${BLUE}📈 SEO 覆盖率估算:${NC}"
echo ""

# 读取一个示例文件，提取关键词数量
SAMPLE_FILE=$(find "$DATA_DIR" -name "*.json" -not -name "vacuums.json" | head -1)
if [ -n "$SAMPLE_FILE" ]; then
    KEYWORDS=$(python3 -c "import json; data=json.load(open('$SAMPLE_FILE')); print(len(data.get('seo_keywords', [])))" 2>/dev/null || echo "5")
    TOTAL_KEYWORDS=$((TOTAL_FILES * KEYWORDS))
    echo -e "  ${GREEN}✓${NC} 总关键词数: ~$TOTAL_KEYWORDS 个"
    echo -e "  ${GREEN}✓${NC} 每页平均: $KEYWORDS 个关键词"
fi

echo ""
echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}✅ 监控完成${NC}"
echo -e "${BLUE}======================================${NC}"
echo -e "${YELLOW}💡 提示: 运行 ./scripts/run-automation.sh 生成更多内容${NC}"
echo ""
