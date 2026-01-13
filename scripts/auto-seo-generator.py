#!/usr/bin/env python3
"""
自动化 SEO 内容生成器
每天自动搜索热门关键词并生成新的吸尘器维修指南页面
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================
# 配置部分
# ============================================

# 品牌列表（用于生成组合关键词）
BRANDS = [
    "Dyson", "Shark", "Bissell", "iRobot", "Roomba",
    "Hoover", "Eureka", "Miele", "Samsung", "LG",
    "Tineco", "Roborock", "Ecovacs", "Eufy", "Black+Decker"
]

# 常见型号关键词
MODEL_PATTERNS = [
    "V{}", "V{} Absolute", "V{} Animal", "V{} Detect",
    "{} Series", "{} Pro", "{} Plus", "{} Max",
    "Robot {}", "Cordless {}", "Pet {}", "Crosswave {}"
]

# 常见问题关键词（SEO 流量词）
PROBLEM_KEYWORDS = [
    "not turning on",
    "not charging",
    "battery replacement",
    "filter cleaning",
    "motor pulsing",
    "lost suction",
    "brush not spinning",
    "making noise",
    "red light flashing",
    "won't hold charge",
    "overheating",
    "clogged",
    "troubleshooting",
    "reset button",
    "error codes",
    "replacement parts",
    "where to buy",
    "manual pdf",
    "repair guide"
]

# 数据目录
DATA_DIR = Path(__file__).parent.parent / "data"
LOG_DIR = Path(__file__).parent.parent / "logs"

# 创建必要目录
LOG_DIR.mkdir(exist_ok=True)

# ============================================
# 日志函数
# ============================================

def log(message, level="INFO"):
    """记录日志到文件和控制台"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] [{level}] {message}"

    # 输出到控制台
    print(log_message)

    # 写入日志文件
    log_file = LOG_DIR / f"seo-generator-{datetime.now().strftime('%Y%m%d')}.log"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_message + '\n')

# ============================================
# 关键词生成器
# ============================================

def generate_keyword_combinations():
    """生成品牌+型号+问题的关键词组合"""
    keywords = []

    log("开始生成关键词组合...")

    # 生成品牌 + 问题组合
    for brand in BRANDS:
        for problem in PROBLEM_KEYWORDS:
            keyword = f"{brand} {problem}"
            keywords.append({
                "keyword": keyword,
                "search_volume": "estimated",  # 实际应用中可以从 API 获取
                "type": "brand_problem"
            })

    # 生成型号 + 问题组合
    for brand in ["Dyson", "Shark", "Bissell"]:  # 专注主要品牌
        for pattern in MODEL_PATTERNS[:5]:  # 只取前5个模式
            for num in range(7, 16):  # V7-V15
                model = pattern.format(num)
                for problem in PROBLEM_KEYWORDS[:8]:  # 只取前8个问题
                    keyword = f"{brand} {model} {problem}"
                    keywords.append({
                        "keyword": keyword,
                        "search_volume": "estimated",
                        "type": "model_problem"
                    })

    log(f"生成了 {len(keywords)} 个关键词组合")
    return keywords

# ============================================
# 内容生成器
# ============================================

def generate_vacuum_guide(brand, model, keyword):
    """根据关键词自动生成吸尘器维修指南数据"""

    # 从关键词中提取问题
    problem = keyword.replace(brand, "").replace(model, "").strip()

    # 生成 SEO 关键词
    seo_keywords = [
        keyword,
        f"{brand} {model} repair",
        f"{brand} {model} parts",
        f"{brand} {model} troubleshooting",
        f"how to fix {brand} {model}"
    ]

    # 生成常见问题
    problems = []

    # 根据问题类型生成对应内容
    if "not turning on" in problem.lower() or "won't start" in problem.lower():
        problems.append({
            "id": "not-turning-on",
            "title": "Vacuum Won't Turn On",
            "description": f"The {brand} {model} does not respond when pressing the power button.",
            "possible_causes": [
                "Battery is completely drained",
                "Battery is faulty or dead",
                "Charger is not working properly",
                "Power button malfunction"
            ],
            "solution_steps": [
                "Charge the vacuum for at least 4 hours",
                "Check the charger indicator light",
                "Try a different outlet",
                "If still not working, battery replacement may be needed"
            ],
            "required_parts": [
                {
                    "name": f"{brand} {model} Replacement Battery",
                    "search_query": f"{brand} {model} battery replacement"
                }
            ]
        })

    elif "not charging" in problem.lower() or "won't charge" in problem.lower():
        problems.append({
            "id": "not-charging",
            "title": "Battery Not Charging",
            "description": f"The {brand} {model} does not charge when placed on the charger.",
            "possible_causes": [
                "Dirty charging contacts",
                "Faulty charger",
                "Battery has reached end of life",
                "Charging port damage"
            ],
            "solution_steps": [
                "Clean the charging contacts on both vacuum and charger",
                "Check if charger indicator light turns on",
                "Try a different power outlet",
                "Inspect charging port for damage or debris"
            ],
            "required_parts": [
                {
                    "name": f"{brand} {model} Charger",
                    "search_query": f"{brand} {model} charger replacement"
                },
                {
                    "name": f"{brand} {model} Battery",
                    "search_query": f"{brand} {model} battery"
                }
            ]
        })

    elif "filter" in problem.lower():
        problems.append({
            "id": "filter-issues",
            "title": "Filter Cleaning or Replacement",
            "description": f"The {brand} {model} shows reduced suction or filter indicator.",
            "possible_causes": [
                "Filter is clogged with dust and debris",
                "Filter is damaged or worn out",
                "Filter hasn't been cleaned in a long time"
            ],
            "solution_steps": [
                "Remove the filter according to the manual",
                "Wash the filter with cold water only",
                "Let it air dry for 24 hours",
                "Replace if damaged or not improving suction"
            ],
            "required_parts": [
                {
                    "name": f"{brand} {model} Replacement Filter",
                    "search_query": f"{brand} {model} filter replacement"
                }
            ]
        })

    else:
        # 通用问题模板
        problems.append({
            "id": "general-issue",
            "title": f"Common {brand} {model} Problem",
            "description": f"Issue reported with {brand} {model}: {problem}",
            "possible_causes": [
                "Normal wear and tear",
                "Lack of maintenance",
                "Part failure",
                "Blockage in the system"
            ],
            "solution_steps": [
                "Refer to the official manual for troubleshooting",
                "Check for any blockages in the vacuum head or wand",
                "Ensure all filters are clean and properly installed",
                "Contact manufacturer support if problem persists"
            ],
            "required_parts": [
                {
                    "name": f"{brand} {model} Replacement Parts",
                    "search_query": f"{brand} {model} parts"
                }
            ]
        })

    # 构建完整的数据结构
    guide_data = {
        "brand": brand,
        "model": f"{brand} {model}",
        "manual_pdf": f"{brand}-{model.lower().replace(' ', '-')}.pdf",
        "seo_keywords": seo_keywords,
        "auto_generated": True,
        "generated_date": datetime.now().isoformat(),
        "source_keyword": keyword,
        "problems": problems
    }

    return guide_data

# ============================================
# 文件保存器
# ============================================

def save_guide_to_json(guide_data):
    """将生成的指南保存为 JSON 文件"""
    # 生成文件名
    brand_slug = guide_data["brand"].lower().replace(" ", "-").replace("+", "plus")
    model_slug = guide_data["model"].lower().replace(" ", "-").replace("/", "-").replace("+", "plus")
    filename = f"{brand_slug}-{model_slug}.json"

    file_path = DATA_DIR / filename

    # 检查文件是否已存在
    if file_path.exists():
        log(f"文件已存在，跳过: {filename}")
        return False

    # 保存文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(guide_data, f, indent=2, ensure_ascii=False)

    log(f"✅ 成功生成: {filename}")
    return True

# ============================================
# 主函数
# ============================================

def main():
    """主执行函数"""
    log("=" * 60)
    log("🚀 SEO 自动内容生成器启动")
    log("=" * 60)

    # 生成关键词
    keywords = generate_keyword_combinations()

    # 统计
    generated_count = 0
    skipped_count = 0

    # 处理前 20 个关键词（避免一次生成太多）
    for i, kw in enumerate(keywords[:20], 1):
        log(f"\n[{i}/{20}] 处理关键词: {kw['keyword']}")

        try:
            # 解析品牌和型号
            parts = kw['keyword'].split()

            if len(parts) < 2:
                log(f"⚠️  跳过无效关键词: {kw['keyword']}")
                skipped_count += 1
                continue

            brand = parts[0]
            model = " ".join(parts[1:]).split(" not ")[0].split(" won't")[0].split(" battery")[0].strip()

            # 生成指南数据
            guide_data = generate_vacuum_guide(brand, model, kw['keyword'])

            # 保存文件
            if save_guide_to_json(guide_data):
                generated_count += 1
            else:
                skipped_count += 1

            # 避免请求过快
            time.sleep(0.5)

        except Exception as e:
            log(f"❌ 处理关键词时出错: {kw['keyword']}, 错误: {str(e)}", "ERROR")
            skipped_count += 1
            continue

    # 总结
    log("\n" + "=" * 60)
    log(f"✅ 生成完成！")
    log(f"📊 生成文件: {generated_count}")
    log(f"⏭️  跳过文件: {skipped_count}")
    log(f"📅 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 60)

if __name__ == "__main__":
    main()
