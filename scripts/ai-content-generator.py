#!/usr/bin/env python3
"""
AI 驱动的智能内容生成器
使用 AI API 生成高质量的维修指南内容
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import time
import subprocess
import requests
import random
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# ============================================
# 配置
# ============================================

DATA_DIR = Path(__file__).parent.parent / "data"
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 热门搜索关键词数据库
TRENDING_KEYWORDS = [
    # Dyson 高流量词
    "Dyson V8 battery replacement",
    "Dyson V15 not charging",
    "Dyson V12 pulsing",
    "Dyson V7 motor replacement",
    "Dyson V10 filter cleaning",

    # Shark 高流量词
    "Shark Navigator not working",
    "Shark Rocket brush not spinning",
    "Shark Apex losing suction",
    "Shark Ion battery replacement",
    "Shark Vertex troubleshooting",

    # Bissell 高流量词
    "Bissell Crosswave not spraying",
    "Bissell Little Green mold",
    "Bissell ProHeat not heating",
    "Bissell SpotClean leaking",
    "Bissell Pet Hair Eraser error codes",

    # 机器人吸尘器
    "Roomba not connecting to WiFi",
    "Roomba error 15",
    "Roborock S7 mapping issues",
    "Ecovacs Deebot not charging",
    "Eufy RoboVac stuck",

    # 其他品牌
    "Hoover WindTunnel belt replacement",
    "Miele C1 attachment issues",
    "Tineco iFloor 3 error codes",
    "Samsung Jet 90 battery life"
]

# ============================================
# 日志函数
# ============================================

def log(message, level="INFO"):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] [{level}] {message}"
    print(log_message)

    log_file = LOG_DIR / f"ai-generator-{datetime.now().strftime('%Y%m%d')}.log"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_message + '\n')

# ============================================
# Telegram 通知函数
# ============================================

def send_telegram_notification(generated, skipped, keywords_today):
    """
    发送 Telegram 通知
    需要设置环境变量 TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID
    """
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        log("未配置 TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID，跳过 Telegram 通知", "WARN")
        return

    try:
        # 计算总文章数
        total_files = len(list(DATA_DIR.glob("*.json"))) - 3  # 减去 vacuums.json, sharks.json, bissells.json

        # 构建消息（使用纯文本，避免 Markdown 格式问题）
        emoji = "✅" if generated > 0 else "ℹ️"

        message = f"""{emoji} SEO 内容生成完成

📅 日期: {datetime.now().strftime('%Y-%m-%d')}
🕐 时间: {datetime.now().strftime('%H:%M:%S')}
✅ 新生成: {generated} 篇
⏭️  跳过: {skipped} 篇
📊 网站总文章数: {total_files} 篇"""

        # 如果生成了新文章，添加详细信息
        if generated > 0:
            message += f"\n\n📝 今日生成的文章:\n"
            for kw in keywords_today:
                # 从关键词中提取更友好的中文标题
                title = kw
                if "battery life" in kw.lower():
                    title = kw.replace("battery life", "电池续航")
                elif "battery" in kw.lower():
                    title = kw.replace("battery", "电池")
                elif "charging" in kw.lower():
                    title = kw.replace("charging", "充电")
                elif "attachment" in kw.lower():
                    title = kw.replace("attachment issues", "配件问题").replace("attachment", "配件")
                elif "error codes" in kw.lower():
                    title = kw.replace("error codes", "错误代码")
                elif "not charging" in kw.lower():
                    title = kw.replace("not charging", "无法充电")
                elif "not working" in kw.lower():
                    title = kw.replace("not working", "无法工作")
                message += f"• {title}\n"
        else:
            message += f"\n\n💡 今日所有文章已存在，未生成新内容"

        # 添加提示信息
        message += f"\n\n🔄 下次运行: 明天早上 8 点 (UTC-8)"

        # 发送消息（不使用 parse_mode，使用纯文本）
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message
        }

        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()

        log("✅ Telegram 通知发送成功")

    except Exception as e:
        log(f"⚠️ Telegram 通知发送失败: {str(e)}", "WARN")

# ============================================
# 🚀 高流量 (Traffic) - Google Trends 实时抓取
# ============================================

def fetch_google_trends_rss():
    """
    从 Google Trends 网页直接抓取实时搜索趋势
    使用 Playwright 浏览器自动化，从 explore URLs 提取搜索词
    专注于吸尘器相关的搜索查询
    """
    vacuum_related_keywords = []

    try:
        # 吸尘器相关关键词列表
        vacuum_keywords = [
            'vacuum', 'dyson', 'shark', 'hoover', 'bissell', 'roomba',
            'robot', 'cleaner', 'suction', 'carpet', 'floor',
            'miele', 'samsung', 'tineco', 'lg', 'electrolux',
            'battery', 'charging', 'repair', 'parts', 'filter'
        ]

        log("🔍 正在使用 Playwright 浏览器抓取 Google Trends...", "INFO")

        # 使用 Playwright 启动无头浏览器
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # 尝试多个地区
            regions = ['US', 'GB', 'CA']

            for region in regions:
                try:
                    trends_url = f"https://trends.google.com/trends/trendingsearches/daily?geo={region}"
                    log(f"   🌐 访问 {region} 地区趋势...", "INFO")

                    # 访问页面
                    page.goto(trends_url, timeout=30000)

                    # 等待页面加载完成（更长的超时时间）
                    page.wait_for_load_state('networkidle', timeout=30000)

                    # 等待更长时间让 Angular.js 渲染趋势数据
                    time.sleep(5)

                    # 获取完整 HTML
                    html_content = page.content()
                    import re
                    from urllib.parse import unquote

                    # 方法 1: 从 explore URLs 提取搜索词 (新方法)
                    explore_urls = re.findall(r'/trends/explore\?q=([^"&]+)', html_content)

                    if explore_urls:
                        log(f"   找到 {len(explore_urls)} 个 explore URLs", "INFO")

                        for url_encoded in explore_urls[:50]:  # 取前50个
                            try:
                                # URL 解码
                                search_term = unquote(url_encoded.replace('+', ' '))

                                # 清理搜索词
                                clean_term = search_term.strip().title()

                                if clean_term and len(clean_term) < 100:
                                    term_lower = clean_term.lower()

                                    # 检查是否与吸尘器相关（完整单词匹配）
                                    # 使用正则表达式确保完整单词匹配，避免子字符串误匹配
                                    import re
                                    is_related = False
                                    for kw in vacuum_keywords:
                                        # 使用单词边界 \b 确保完整匹配
                                        pattern = r'\b' + re.escape(kw) + r'\b'
                                        if re.search(pattern, term_lower):
                                            is_related = True
                                            break

                                    if is_related:
                                        if clean_term not in vacuum_related_keywords:
                                            vacuum_related_keywords.append(clean_term)
                                            log(f"   ✅ 发现趋势 (URL): {clean_term}", "INFO")
                                    else:
                                        # 记录非吸尘器趋势用于调试
                                        log(f"   📊 趋势 (非相关): {clean_term}", "DEBUG")

                            except Exception as e:
                                continue

                    # 方法 2: 如果方法 1 没找到足够的词，尝试选择器方法
                    if len(vacuum_related_keywords) < 5:
                        log(f"   尝试选择器方法补充...", "INFO")

                        selectors = [
                            'a[ng-href*="explore"]',
                            'div.feed-item',
                            'md-list-item',
                            'span[ng-bind]',
                            '[class*="feed-list"]',
                            '[class*="trending-search"]'
                        ]

                        for selector in selectors:
                            try:
                                elements = page.query_selector_all(selector)

                                if elements:
                                    for elem in elements[:30]:
                                        try:
                                            text = elem.inner_text()

                                            if text and len(text) < 100:
                                                clean_text = text.strip().split('\n')[0].strip()

                                                if clean_text:
                                                    text_lower = clean_text.lower()
                                                    # 使用完整单词匹配
                                                    import re
                                                    is_related = False
                                                    for kw in vacuum_keywords:
                                                        pattern = r'\b' + re.escape(kw) + r'\b'
                                                        if re.search(pattern, text_lower):
                                                            is_related = True
                                                            break

                                                    if is_related:
                                                        if clean_text not in vacuum_related_keywords:
                                                            vacuum_related_keywords.append(clean_text)
                                                            log(f"   ✅ 发现趋势 (选择器): {clean_text}", "INFO")

                                        except Exception:
                                            continue

                            except Exception:
                                continue

                    # 避免请求过快
                    time.sleep(2)

                except PlaywrightTimeout:
                    log(f"   ⚠️ {region} 地区超时", "WARN")
                    continue
                except Exception as e:
                    log(f"   ⚠️ 抓取 {region} 地区失败: {str(e)}", "WARN")
                    continue

            browser.close()

        log(f"✅ 从 Google Trends 获取了 {len(vacuum_related_keywords)} 个相关关键词", "INFO")

    except Exception as e:
        log(f"⚠️ Google Trends 抓取失败: {str(e)}", "WARN")

    return vacuum_related_keywords

# ============================================
# 💎 高质量 (Quality) - E-E-A-T 人设系统
# ============================================

# E-E-A-T 人设配置
PERSONAS = {
    "tech_expert": {
        "name": "技术专家",
        "tone": "专业、分析性、经验丰富",
        "openings": [
            "Last weekend, I spent 4 hours troubleshooting a {model}...",
            "After testing 15 different {brand} units, I've found the pattern...",
            "I've been repairing vacuum cleaners for 12 years, and here's what most people get wrong about {problem}...",
            "Let me walk you through the exact repair process I use in my shop...",
            "The service manual doesn't tell you this, but here's the real fix..."
        ],
        "phrases": [
            "Based on my technical analysis...",
            "The root cause is almost always...",
            "Here's the professional solution...",
            "Most DIY tutorials miss this critical step...",
            "I've seen this issue hundreds of times..."
        ]
    },
    "frustrated_user": {
        "name": "愤怒用户",
        "tone": "直接、情绪化、痛点共鸣",
        "openings": [
            "I was about to throw my {model} against the wall...",
            "It happened AGAIN. Right in the middle of cleaning...",
            "I'm so done with this {problem} issue. Here's how I finally fixed it...",
            "After 3 repair shops couldn't fix it, I figured it out myself...",
            "Warning: Don't make the same mistake I did with my {model}..."
        ],
        "phrases": [
            "Here's what actually works (trust me, I tried everything)...",
            "Skip the nonsense, here's the fix...",
            "This will save you hours of frustration...",
            "Why isn't this in the manual?!",
            "Finally, a solution that actually lasts..."
        ]
    },
    "product_analyst": {
        "name": "产品分析师",
        "tone": "客观、数据驱动、比较分析",
        "openings": [
            "In my comprehensive testing of 8 vacuum models...",
            "After analyzing 500+ user complaints about {model}...",
            "Let's cut through the marketing hype and look at the real data...",
            "I've compared {brand} against 12 competitors, here's what stands out...",
            "The design flaw behind this {problem} issue is actually fascinating..."
        ],
        "phrases": [
            "The data clearly shows...",
            "Based on extensive testing...",
            "This is a known design limitation...",
            "Here's the cost-benefit analysis...",
            "Industry standards suggest..."
        ]
    }
}

def get_persona_content(problem_type, brand, model, problem_desc):
    """
    根据问题类型选择最合适的人设，并生成真人体验口吻的内容
    """
    # 根据问题类型智能选择人设
    persona_mapping = {
        "battery": "tech_expert",      # 电池问题用技术专家
        "charging": "tech_expert",     # 充电问题用技术专家
        "motor": "tech_expert",        # 电机问题用技术专家
        "error_codes": "tech_expert",  # 错误代码用技术专家
        "not_working": "frustrated_user",  # 无法工作用愤怒用户
        "pulsing": "frustrated_user",  # 脉冲问题用愤怒用户
        "leaking": "frustrated_user",  # 漏水用愤怒用户
        "brush": "product_analyst",    # 刷头问题用分析师
        "filter": "product_analyst",   # 滤网用分析师
        "suction": "product_analyst",  # 吸力用分析师
        "general": "tech_expert"       # 默认用技术专家
    }

    selected_persona = persona_mapping.get(problem_type, "tech_expert")
    persona = PERSONAS[selected_persona]

    # 随机选择一个开场白
    opening_template = random.choice(persona["openings"])

    # 构建真人体验口吻的开场
    full_model_name = f"{brand} {model}" if model else brand

    # 替换模板中的占位符
    opening = opening_template.format(
        model=full_model_name,
        brand=brand,
        problem=problem_desc or "issue"
    )

    # 选择 2-3 个特色短语
    selected_phrases = random.sample(persona["phrases"], min(3, len(persona["phrases"])))

    return {
        "persona_type": selected_persona,
        "persona_name": persona["name"],
        "opening": opening,
        "phrases": selected_phrases,
        "tone": persona["tone"]
    }

# ============================================
# 💰 高转化 (Conversion) - 动态 CTA 系统
# ============================================

# 动态 CTA 配置（根据问题类型和痛点定制）
DYNAMIC_CTAS = {
    "battery": {
        "urgency": "high",
        "cta_text": "⚡ Stop Waiting - Fix Your {model} Battery Today",
        "cta_subtext": "Don't let a dead battery ruin your cleaning routine. Professional replacement ready to ship.",
        "color": "red",
        "icon": "🔋",
        "pain_point": "Your vacuum won't hold a charge"
    },
    "charging": {
        "urgency": "high",
        "cta_text": "🔌 Fix Charging Issues - Get Your {model} Working Again",
        "cta_subtext": "Stop dealing with the frustration of a vacuum that won't charge. We have the solution.",
        "color": "orange",
        "icon": "⚡",
        "pain_point": "Your vacuum won't charge properly"
    },
    "not_charging": {
        "urgency": "critical",
        "cta_text": "🚨 Don't Wait - Your {model} Needs This Fix Now",
        "cta_subtext": "Every day without your vacuum is a day your home isn't clean. Fast shipping available.",
        "color": "red",
        "icon": "⏰",
        "pain_point": "Complete charging failure"
    },
    "brush": {
        "urgency": "medium",
        "cta_text": "🔄 Restore Full Cleaning Power - Replace Your Brush",
        "cta_subtext": "A worn brush won't clean anything. Get genuine replacement for maximum performance.",
        "color": "blue",
        "icon": "🧹",
        "pain_point": "Poor cleaning performance"
    },
    "filter": {
        "urgency": "medium",
        "cta_text": "🌬️ Breathe Easy - Replace Clogged Filters Today",
        "cta_subtext": "Dirty filters reduce suction and damage your motor. Protect your investment.",
        "color": "green",
        "icon": "✨",
        "pain_point": "Reduced suction and air quality"
    },
    "motor": {
        "urgency": "high",
        "cta_text": "💪 Professional Motor Replacement - Don't Risk Further Damage",
        "cta_subtext": "A failing motor can destroy your vacuum. Expert replacement service available.",
        "color": "red",
        "icon": "⚙️",
        "pain_point": "Motor failure or strange noises"
    },
    "suction": {
        "urgency": "medium",
        "cta_text": "📈 Restore Maximum Suction - Professional Parts Ready",
        "cta_subtext": "Weak suction? We have the exact parts to restore your {model}'s power.",
        "color": "blue",
        "icon": "💨",
        "pain_point": "Weak suction power"
    },
    "error_codes": {
        "urgency": "high",
        "cta_text": "🔧 Decoding Error {code}? We Have the Solution",
        "cta_subtext": "Don't let mysterious error codes stop you. Expert diagnostics and parts available.",
        "color": "orange",
        "icon": "❓",
        "pain_point": "Confusing error messages"
    },
    "attachment": {
        "urgency": "low",
        "cta_text": "🔗 Fix Attachment Issues - Get Your Tools Working",
        "cta_subtext": "Loose or broken attachments? We have genuine replacements ready to ship.",
        "color": "blue",
        "icon": "🛠️",
        "pain_point": "Attachments not working properly"
    },
    "belt": {
        "urgency": "high",
        "cta_text": "⚙️ Replace Worn Belt - Restore Full Performance",
        "cta_subtext": "A broken belt means no cleaning. Fast replacement service available.",
        "color": "orange",
        "icon": "🔧",
        "pain_point": "Brush not spinning"
    },
    "leaking": {
        "urgency": "high",
        "cta_text": "🛑 Stop the Leak - Fix Your {model} Now",
        "cta_subtext": "Water damage can destroy your vacuum. Quick fixes available.",
        "color": "red",
        "icon": "💧",
        "pain_point": "Water or liquid leaking"
    },
    "pulsing": {
        "urgency": "high",
        "cta_text": "⚡ Fix Pulsing Issue - Stop the Annoying On-Off Cycle",
        "cta_subtext": "Pulsing means a sensor or blockage issue. We have the parts to fix it permanently.",
        "color": "orange",
        "icon": "📳",
        "pain_point": "Vacuum keeps pulsing on and off"
    },
    "noise": {
        "urgency": "medium",
        "cta_text": "🔇 Silence Strange Noises - Protect Your Vacuum",
        "cta_subtext": "Unusual noises mean wear or damage. Fix it before it becomes a costly repair.",
        "color": "yellow",
        "icon": "🔊",
        "pain_point": "Loud or unusual noises"
    },
    "heating": {
        "urgency": "high",
        "cta_text": "🌡️ Overheating? Fix It Before Permanent Damage",
        "cta_subtext": "Overheating can kill your motor. Quick diagnosis and repair available.",
        "color": "red",
        "icon": "🔥",
        "pain_point": "Vacuum getting too hot"
    },
    "connectivity": {
        "urgency": "low",
        "cta_text": "📶 Fix Connection Issues - Get Smart Features Working",
        "cta_subtext": "WiFi or app problems? We can help restore your smart vacuum's features.",
        "color": "blue",
        "icon": "📱",
        "pain_point": "Can't connect to app or WiFi"
    },
    "mapping": {
        "urgency": "low",
        "cta_text": "🗺️ Fix Navigation Issues - Restore Smart Cleaning",
        "cta_subtext": "Mapping problems? We have sensors and parts to get your robot vacuum back on track.",
        "color": "blue",
        "icon": "🤖",
        "pain_point": "Robot vacuum navigation problems"
    },
    "general": {
        "urgency": "low",
        "cta_text": "🔧 Get Your {model} Running Like New",
        "cta_subtext": "Whatever the issue, we have the parts and expertise to help.",
        "color": "blue",
        "icon": "✅",
        "pain_point": "General performance issues"
    }
}

def generate_dynamic_cta(problem_type, brand, model, error_code=None):
    """
    根据问题类型生成动态 CTA
    返回高度转化的行动号召内容
    """
    # 获取 CTA 配置
    cta_config = DYNAMIC_CTAS.get(problem_type, DYNAMIC_CTAS["general"])

    full_model_name = f"{brand} {model}" if model else brand

    # 构建动态 CTA
    # 注意：需要处理 {code} 占位符，因为 format() 会尝试替换所有花括号
    cta_text = cta_config["cta_text"]
    cta_subtext = cta_config["cta_subtext"]

    # 先替换 {code} 占位符（如果提供了 error_code）
    if error_code:
        cta_text = cta_text.replace("{code}", str(error_code))
    else:
        # 如果没有 error_code，移除 {code} 或使用通用文本
        cta_text = cta_text.replace("{code}", "").replace("  ", " ")

    # 现在安全地使用 format() 替换 {model}
    cta_text = cta_text.format(model=full_model_name)
    cta_subtext = cta_subtext.format(model=full_model_name)

    return {
        "urgency": cta_config["urgency"],
        "text": cta_text,
        "subtext": cta_subtext,
        "color": cta_config["color"],
        "icon": cta_config["icon"],
        "pain_point": cta_config["pain_point"]
    }

# ============================================
# API 调用函数（可以接入各种 AI API）
# ============================================

def call_ai_api(prompt, max_retries=3):
    """
    调用 AI API 生成内容
    支持多种 AI 服务：OpenAI、Claude、本地模型等
    """
    # 这里可以接入真实的 AI API
    # 目前返回模拟数据用于演示

    log(f"调用 AI API 生成内容...")

    # 模拟 API 调用延迟
    time.sleep(1)

    # 返回模拟响应
    # 实际使用时，替换为真实的 API 调用
    return {
        "title": "Common Vacuum Problem",
        "description": "Generated by AI",
        "causes": ["Cause 1", "Cause 2"],
        "solutions": ["Solution 1", "Solution 2"]
    }

# ============================================
# 智能型号解析器
# ============================================

def parse_vacuum_model(keyword):
    """
    智能解析吸尘器型号信息
    返回: (brand, model, problem_description)

    注意: model 字段不包含品牌前缀，避免重复
    例如: "Miele C1" 返回 brand="Miele", model="C1"
    """
    parts = keyword.split()

    # 品牌型号数据库（常见模式）
    brand_patterns = {
        'Dyson': ['V', 'V7', 'V8', 'V10', 'V11', 'V12', 'V15', 'Cyclone', 'Digital Slim'],
        'Shark': ['Navigator', 'Rocket', 'Apex', 'Ion', 'Vertex', 'Rotator', 'Stratos'],
        'Bissell': ['Crosswave', 'Little Green', 'ProHeat', 'SpotClean', 'Pet Hair Eraser', 'PowerForce'],
        'Roomba': ['i', 'e', 's', 'j', '600', '700', '800', '900', 'i7', 'i8', 'e5'],
        'Roborock': ['S4', 'S5', 'S6', 'S7', 'S8', 'Q5', 'Q7', 'E4'],
        'Ecovacs': ['Deebot', 'Ozmo', 'N79', 'S5', 'S6', 'S7'],
        'Eufy': ['RoboVac', 'HomeVac', '11S', '30C', 'G30'],
        'Hoover': ['WindTunnel', 'PowerDrive', 'React', 'ONE', 'Legacy'],
        'Miele': ['C1', 'C2', 'C3', 'Complete', 'Classic', 'Full'],
        'Tineco': ['iFloor', 'Dry', 'Wet', 'Smart', 'Floor ONE'],
        'Samsung': ['Jet', '70', '75', '90', 'Stick', 'Cordless']
    }

    # 提取品牌
    brand = parts[0] if parts else "Unknown"

    # 智能提取型号和问题描述
    model = ""
    problem_desc = ""

    # 常见型号模式（model 不包含品牌前缀）
    if brand == 'Dyson':
        # Dyson V7/V8/V10/V11/V12/V15（型号不包含品牌）
        for i, part in enumerate(parts[1:], 1):
            if part in ['V7', 'V8', 'V10', 'V11', 'V12', 'V15', 'V7+', 'V8+', 'V10+']:
                model = part
                if i < len(parts) - 1:
                    problem_desc = " ".join(parts[i+1:])
                break
            elif part == 'Cyclone' or part == 'Digital':
                # 组合型号（如 Cyclone V10）
                model = part
                if i < len(parts) - 1 and parts[i+1] in ['V7', 'V8', 'V10', 'V11', 'V12', 'V15']:
                    model = f"{part} {parts[i+1]}"
                    if i < len(parts) - 2:
                        problem_desc = " ".join(parts[i+2:])
                    break
                else:
                    if i < len(parts) - 1:
                        problem_desc = " ".join(parts[i+1:])
                    break
        if not model:
            model = "Vacuum"
            problem_desc = " ".join(parts[1:])

    elif brand == 'Shark':
        # Shark Navigator/Rocket/Apex/Ion/Vertex
        for i, part in enumerate(parts[1:], 1):
            if part in brand_patterns.get('Shark', []):
                model = part
                if i < len(parts) - 1:
                    problem_desc = " ".join(parts[i+1:])
                break
        if not model:
            model = "Vacuum"
            problem_desc = " ".join(parts[1:])

    elif brand == 'Bissell':
        # Bissell Crosswave/Little Green/ProHeat/SpotClean
        for i, part in enumerate(parts[1:], 1):
            if part in ['Crosswave', 'Little', 'ProHeat', 'SpotClean', 'Pet']:
                if part == 'Little' and i < len(parts) - 1 and parts[i+1] == 'Green':
                    model = "Little Green"
                    if i < len(parts) - 2:
                        problem_desc = " ".join(parts[i+2:])
                    break
                elif part == 'Pet' and i < len(parts) - 1 and parts[i+1] == 'Hair':
                    model = "Pet Hair Eraser"
                    if i < len(parts) - 2:
                        problem_desc = " ".join(parts[i+2:])
                    break
                else:
                    model = part
                    if i < len(parts) - 1:
                        problem_desc = " ".join(parts[i+1:])
                    break
        if not model:
            model = "Cleaner"
            problem_desc = " ".join(parts[1:])

    elif brand == 'Roomba':
        # Roomba i/e/s/j 系列 + 数字
        for i, part in enumerate(parts[1:], 1):
            if part in ['i', 'e', 's', 'j'] and i < len(parts) - 1:
                model = f"{part} {parts[i+1]}"
                if i < len(parts) - 2:
                    problem_desc = " ".join(parts[i+2:])
                break
            elif part.isdigit() and 500 <= int(part) <= 1000:
                model = part
                if i < len(parts) - 1:
                    problem_desc = " ".join(parts[i+1:])
                break
        if not model:
            model = "Robot Vacuum"
            problem_desc = " ".join(parts[1:])

    elif brand == 'Samsung':
        # Samsung Jet 70/75/90
        for i, part in enumerate(parts[1:], 1):
            if part == 'Jet' and i < len(parts) - 1:
                next_part = parts[i+1]
                if next_part in ['70', '75', '90', 'Stick', 'Cordless']:
                    model = f"Jet {next_part}"
                    if i < len(parts) - 2:
                        problem_desc = " ".join(parts[i+2:])
                    break
            elif part == 'Jet':
                model = "Jet"
                if i < len(parts) - 1:
                    problem_desc = " ".join(parts[i+1:])
                break
        if not model:
            model = "Vacuum"
            problem_desc = " ".join(parts[1:])

    elif brand == 'Miele':
        # Miele C1/C2/C3 + Complete/Classic
        for i, part in enumerate(parts[1:], 1):
            if part in ['C1', 'C2', 'C3']:
                model = part
                if i < len(parts) - 1:
                    problem_desc = " ".join(parts[i+1:])
                break
            elif part in ['Complete', 'Classic', 'Full']:
                model = part
                if i < len(parts) - 1:
                    problem_desc = " ".join(parts[i+1:])
                break
        if not model:
            model = "Vacuum"
            problem_desc = " ".join(parts[1:])

    elif brand == 'Tineco':
        # Tineco iFloor + 数字
        for i, part in enumerate(parts[1:], 1):
            if part == 'iFloor' and i < len(parts) - 1:
                model = f"iFloor {parts[i+1]}"
                if i < len(parts) - 2:
                    problem_desc = " ".join(parts[i+2:])
                break
            elif part in ['Dry', 'Wet', 'Smart']:
                model = part
                if i < len(parts) - 1:
                    problem_desc = " ".join(parts[i+1:])
                break
        if not model:
            model = "Cleaner"
            problem_desc = " ".join(parts[1:])

    else:
        # 默认处理
        model = "Vacuum"
        problem_desc = " ".join(parts[1:])

    # 清理问题描述
    if problem_desc:
        problem_desc = problem_desc.strip()
    else:
        problem_desc = keyword

    return brand, model, problem_desc

# ============================================
# 智能问题类型检测
# ============================================

def detect_problem_type(keyword, problem_desc):
    """
    智能检测问题类型
    根据关键词和问题描述返回最匹配的问题类型
    """
    keyword_lower = keyword.lower()
    desc_lower = problem_desc.lower()

    # 优先级检测（按具体程度排序）
    detection_rules = [
        # 电池相关问题
        (['battery', 'batteries', 'battery life', 'dead battery', 'replace battery'], 'battery'),
        (['battery replacement', 'swap battery', 'change battery'], 'battery'),

        # 充电相关问题
        (['charging', 'charger', 'won\'t charge', 'not charging', 'charge indicator'], 'charging'),
        (['charging problems', 'charging issues', 'charge port'], 'charging'),

        # 错误代码
        (['error', 'error code', 'error codes', 'flashing', 'beeping'], 'error_codes'),

        # 吸力问题
        (['suction', 'losing suction', 'low suction', 'no suction', 'weak suction'], 'suction'),
        (['suction power', 'poor suction', 'suction problems'], 'suction'),

        # 电源/开关问题
        (['not working', 'won\'t turn on', 'won\'t start', 'won\'t power', 'power issues'], 'power'),
        (['dead', 'no power', 'won\'t work', 'not starting'], 'power'),

        # 刷毛相关问题
        (['brush', 'brush roll', 'brushroll', 'brush not spinning'], 'brush'),
        (['roller', 'rotating brush', 'spinning brush'], 'brush'),

        # 滤网问题
        (['filter', 'filters', 'filter cleaning', 'clogged filter'], 'filter'),
        (['filter replacement', 'change filter', 'dirty filter'], 'filter'),

        # 配件/附件问题
        (['attachment', 'attachments', 'tools', 'accessories', 'wand', 'hose'], 'attachment'),
        (['attachment issues', 'loose attachment', 'broken attachment'], 'attachment'),

        # 电机问题
        (['motor', 'motor replacement', 'burnt motor', 'motor noise'], 'motor'),
        (['loud noise', 'grinding noise', 'screaming'], 'motor'),

        # 皮带问题
        (['belt', 'belt replacement', 'broken belt', 'drive belt'], 'belt'),
        (['belt slip', 'loose belt'], 'belt'),

        # WiFi/连接问题
        (['wifi', 'wi-fi', 'connecting', 'connection', 'network'], 'connectivity'),
        (['app', 'connection lost', 'won\'t connect'], 'connectivity'),

        # 泄漏问题
        (['leaking', 'leak', 'spitting', 'spraying'], 'leak'),

        # 脉动问题
        (['pulsing', 'pulse', 'surging'], 'pulsing'),

        # 噪音问题
        (['noise', 'noisy', 'loud', 'sound'], 'noise'),

        # 加热问题
        (['heating', 'heat', 'hot water', 'steam'], 'heating'),

        # 地图问题（机器人吸尘器）
        (['mapping', 'map', 'navigation', 'lost', 'stuck'], 'mapping')
    ]

    # 检测关键词
    for keywords, problem_type in detection_rules:
        for kw in keywords:
            if kw in keyword_lower or kw in desc_lower:
                return problem_type

    # 默认返回通用类型
    return 'general'

# ============================================
# 智能内容生成器
# ============================================

def generate_smart_guide(keyword, trending_source="database"):
    """
    根据关键词智能生成维修指南

    Args:
        keyword: 搜索关键词
        trending_source: 来源标识 ("database", "google_trends", "manual")
    """

    log(f"🤖 正在生成内容: {keyword}")
    if trending_source == "google_trends":
        log(f"   🔥 来源: Google Trends (实时趋势)", "INFO")
    elif trending_source == "database":
        log(f"   📊 来源: Database Rotation (热门轮转)", "INFO")

    # 智能解析型号信息
    brand, model, problem_desc = parse_vacuum_model(keyword)

    log(f"   品牌: {brand}")
    log(f"   型号: {model}")
    log(f"   问题: {problem_desc}")

    # 提取问题类型（更精确的检测）
    problem_type = detect_problem_type(keyword, problem_desc)

    # 使用 AI 生成内容（或使用模板）
    problem_data = generate_problem_by_type(problem_type, brand, model, problem_desc, keyword)

    # 更新 trending_source 标记
    problem_data["trending_source"] = trending_source

    # 构建完整指南
    # 构建完整型号名称（品牌 + 型号，用于显示）
    full_model_name = f"{brand} {model}" if model else brand

    guide = {
        "brand": brand,
        "model": full_model_name,  # 存储完整型号名称（例如 "Miele C1"）
        "model_code": model,  # 存储型号代码（例如 "C1"），用于搜索匹配
        "problem_description": problem_desc,
        "manual_pdf": f"{brand.lower()}-{model.lower().replace(' ', '-').replace('+', 'plus')}.pdf",
        "seo_keywords": generate_seo_keywords(keyword, brand, full_model_name, problem_desc),
        "auto_generated": True,
        "generated_date": datetime.now().isoformat(),
        "source_keyword": keyword,
        "problem_type": problem_type,
        "trending_score": calculate_trending_score(keyword),
        "trending_source": trending_source,  # 添加来源标识
        "problems": [problem_data]
    }

    return guide

# ============================================
# 问题类型生成器
# ============================================

def generate_problem_by_type(problem_type, brand, model, problem_desc, keyword):
    """
    根据问题类型生成具体的问题数据
    problem_type: 问题类型
    brand: 品牌
    model: 型号代码（例如 "C1"）
    problem_desc: 问题描述
    keyword: 原始关键词
    """

    # 构建完整型号名称（用于显示）
    full_model_name = f"{brand} {model}" if model else brand

    # 构建问题描述（用于显示）
    if problem_desc and problem_desc != keyword:
        display_desc = f"{problem_desc} on your {full_model_name}"
    else:
        display_desc = f"issues with your {full_model_name}"

    # 重新定义 model 为完整型号名称（用于模板中的 f-string）
    # 这样所有模板都可以直接使用 {model} 而不需要修改
    model = full_model_name

    # 动态生成问题模板（避免 f-string 变量作用域问题）
    problem_templates = {
        "battery": {
            "id": "battery-replacement",
            "title": f"How to Replace {model} Battery",
            "description": f"Step-by-step guide to replace the battery in your {model}. Restore runtime and performance with a new battery.",
            "possible_causes": [
                "Battery has degraded after 2-3 years of regular use",
                "Battery cells have failed due to age or heat",
                "Battery is not holding charge for more than 10 minutes",
                "Charging cycles have exceeded the battery's lifespan",
                "Battery has been stored at low charge for extended periods"
            ],
            "solution_steps": [
                f"Purchase a genuine replacement battery compatible with {model}",
                "Power off the vacuum completely and remove from charger",
                f"Locate the battery compartment on your {model} (typically on the rear or bottom panel)",
                "Use a suitable screwdriver to remove the battery cover screws",
                "Carefully disconnect the old battery connector, noting the polarity",
                "Remove the old battery and inspect the compartment for any damage",
                "Install the new battery, ensuring correct polarity (+ and - alignment)",
                "Secure the battery compartment cover and tighten all screws",
                f"Charge your {model} for 4-6 hours before the first use"
            ],
            "required_parts": [
                {
                    "name": f"{model} Replacement Battery",
                    "search_query": f"{model} battery"
                }
            ]
        },
        "charging": {
            "id": "charging-issues",
            "title": "Charging Problems & Solutions",
            "description": f"Troubleshooting and fixing charging issues with {brand} {model}.",
            "possible_causes": [
                "Dirty charging contacts",
                "Faulty charger or docking station",
                "Battery cannot accept charge anymore",
                "Charging port damage"
            ],
            "solution_steps": [
                "Clean the metal contacts on both vacuum and charger",
                "Try a different power outlet",
                "Check if the charger LED indicator is working",
                "Inspect the charging port for debris or damage",
                "Test with a different charger if available",
                f"If charger is faulty, replace with genuine {brand} charger"
            ],
            "required_parts": [
                {
                    "name": f"{model} Charger",
                    "search_query": f"{model} charger replacement"
                }
            ]
        },
        "filter": {
            "id": "filter-maintenance",
            "title": "Filter Cleaning & Replacement",
            "description": f"Proper filter maintenance for optimal performance of {brand} {model}.",
            "possible_causes": [
                "Filter is clogged with dust and debris",
                "Filter hasn't been cleaned recently",
                "Filter is damaged or torn",
                "Using wrong filter type"
            ],
            "solution_steps": [
                "Check the filter indicator light (if available)",
                "Remove the pre-filter and post-filter",
                "Tap the filter to remove loose dust",
                "Rinse with cold water only (no soap)",
                "Shake gently and let air dry for 24 hours",
                "Replace if filter is damaged or performance doesn't improve"
            ],
            "required_parts": [
                {
                    "name": f"{model} Replacement Filter",
                    "search_query": f"{model} filter"
                }
            ]
        },
        "power": {
            "id": "power-issues",
            "title": "Vacuum Won't Turn On or Start",
            "description": f"Diagnosing why your {brand} {model} won't power on.",
            "possible_causes": [
                "Battery is completely drained",
                "Battery is dead and needs replacement",
                "Power button malfunction",
                "Internal electrical fault"
            ],
            "solution_steps": [
                "Charge the vacuum for at least 4 hours",
                "Check all connections are secure",
                "Test the power button responsiveness",
                "Look for any error lights or beeps",
                "If completely dead, battery replacement is likely needed"
            ],
            "required_parts": [
                {
                    "name": f"{model} Diagnostic Tool",
                    "search_query": f"{model} troubleshooting"
                }
            ]
        },
        "brush": {
            "id": "brush-roll-issues",
            "title": "Brush Roll Not Spinning",
            "description": f"Fixing brush roll problems on {brand} {model}.",
            "possible_causes": [
                "Debris tangled around brush roll",
                "Brush roll belt is broken",
                "Motor for brush roll failed",
                "Obstruction preventing rotation"
            ],
            "solution_steps": [
                "Turn off and unplug the vacuum",
                "Remove the brush roll cover",
                "Clean all hair and debris from brush roll",
                "Check the belt for wear or damage",
                "Test brush roll motor (if applicable)",
                "Replace belt or brush roll if needed"
            ],
            "required_parts": [
                {
                    "name": f"{model} Brush Roll",
                    "search_query": f"{model} brush roll replacement"
                }
            ]
        },
        "suction": {
            "id": "low-suction",
            "title": "Loss of Suction Power",
            "description": f"Restoring suction power to your {brand} {model}.",
            "possible_causes": [
                "Clogged filters or dust bin",
                "Blockage in the wand or hose",
                "Brush roll not spinning",
                "Dust bin is overfilled"
            ],
            "solution_steps": [
                "Empty the dust bin completely",
                "Clean or replace all filters",
                "Check for blockages in the vacuum head",
                "Inspect the wand and hose for clogs",
                "Remove any debris from the air pathways",
                "Test suction after each step"
            ],
            "required_parts": [
                {
                    "name": f"{model} Replacement Filter",
                    "search_query": f"{model} suction problem"
                }
            ]
        },
        "connectivity": {
            "id": "wifi-connectivity",
            "title": "WiFi & App Connection Issues",
            "description": f"Fixing connectivity problems with {brand} {model}.",
            "possible_causes": [
                "WiFi network changed",
                "App needs update",
                "Firmware outdated",
                "Router interference"
            ],
            "solution_steps": [
                "Ensure vacuum is in WiFi coverage area",
                "Update the companion app to latest version",
                "Reset vacuum's WiFi connection",
                "Restart your router",
                "Reconnect through the app step by step",
                "Update vacuum firmware if available"
            ],
            "required_parts": [
                {
                    "name": f"{model} App",
                    "search_query": f"{model} app download"
                }
            ]
        },
        "error_codes": {
            "id": "error-codes-troubleshooting",
            "title": f"{model} Error Codes Explained",
            "description": f"Understanding and resolving error codes on your {model}. Complete error code reference with solutions.",
            "possible_causes": [
                "Brush roll obstruction detected by sensors",
                "Battery communication failure",
                "Motor overload or overheating",
                "Filter clogged or not properly installed",
                "Internal sensor malfunction",
                "PCB board error detected"
            ],
            "solution_steps": [
                f"Turn off your {model} and wait 30 seconds",
                "Check for any visible obstructions in the brush roll area",
                "Remove and clean all filters thoroughly",
                "Ensure the dust bin is properly installed and not overfilled",
                "Check battery connections and terminals for corrosion",
                "Look up the specific error code in the user manual",
                f"If error persists after troubleshooting, contact {brand} support",
                "Consider resetting the vacuum by removing the battery for 1 minute"
            ],
            "required_parts": [
                {
                    "name": f"{model} Replacement Filter",
                    "search_query": f"{model} filter"
                },
                {
                    "name": f"{model} Brush Roll",
                    "search_query": f"{model} brush roll"
                }
            ]
        },
        "attachment": {
            "id": "attachment-troubleshooting",
            "title": f"{model} Attachment & Accessory Problems",
            "description": f"Solving issues with attachments, tools, and accessories for your {model}. Fix loose or malfunctioning attachments.",
            "possible_causes": [
                "Attachment not properly locked into place",
                "Connection mechanism is dirty or damaged",
                "Accessory release button is stuck or broken",
                "Wand or hose is clogged with debris",
                "Electrical contacts are dirty or corroded",
                "Attachment motor has failed"
            ],
            "solution_steps": [
                f"Remove all attachments from your {model} and inspect them",
                "Clean the connection points with a dry cloth",
                "Check the release mechanism for debris or damage",
                "Test each attachment individually to identify the problematic one",
                "Lubricate moving parts if applicable (check manual first)",
                "Ensure attachments are fully clicked into position",
                "Inspect the electrical contacts for corrosion or dirt",
                "Replace the attachment if the issue persists after cleaning"
            ],
            "required_parts": [
                {
                    "name": f"{model} Replacement Attachment",
                    "search_query": f"{model} attachment"
                },
                {
                    "name": f"{model} Wand or Hose",
                    "search_query": f"{model} wand hose"
                }
            ]
        },
        "motor": {
            "id": "motor-replacement",
            "title": f"How to Replace {model} Motor",
            "description": f"Complete motor replacement guide for {model}. Fix loud noises, burning smells, or complete motor failure.",
            "possible_causes": [
                "Motor bearings have worn out after years of use",
                "Motor has overheated and windings are damaged",
                "Foreign object damaged the motor fan or impeller",
                "Water or liquid damage to motor electronics",
                "Electrical surge or short circuit burned motor",
                "Brushes have worn down (for brushed motors)"
            ],
            "solution_steps": [
                f"Confirm the motor is the issue on your {model} (listen for unusual sounds)",
                "Purchase a compatible replacement motor specific to {model}",
                "Remove the battery and any external covers",
                "Document all wire connections with photos before disconnecting",
                "Carefully disconnect all motor electrical connectors",
                "Remove mounting screws securing the motor housing",
                f"Lift out the old motor from your {model} carefully",
                "Install the new motor and reconnect all wires matching your photos",
                "Reassemble in reverse order and test operation"
            ],
            "required_parts": [
                {
                    "name": f"{model} Replacement Motor",
                    "search_query": f"{model} motor"
                },
                {
                    "name": f"Motor Wiring Harness",
                    "search_query": f"{model} wire harness"
                }
            ]
        },
        "belt": {
            "id": "belt-replacement",
            "title": f"How to Replace {model} Belt",
            "description": f"Step-by-step belt replacement guide for {model}. Fix brush roll not spinning or loss of cleaning power.",
            "possible_causes": [
                "Belt has stretched or worn over time",
                "Belt has broken due to age or obstruction",
                "Belt slipped off the pulley due to debris",
                "Belt melted from motor friction or overheating",
                "Brush roll seized causing belt failure",
                "Poor maintenance led to premature belt wear"
            ],
            "solution_steps": [
                f"Purchase the correct replacement belt for {model}",
                "Remove the battery and bottom plate from {model}",
                "Remove the brush roll and set aside",
                "Clean any debris or hair from the pulley area",
                "Remove the old belt from both motor and brush roll pulleys",
                "Install the new belt, ensuring proper tension",
                "Verify the belt sits correctly in the pulley grooves",
                "Reinstall the brush roll and test rotation",
                "Reassemble the vacuum and test operation"
            ],
            "required_parts": [
                {
                    "name": f"{model} Replacement Belt",
                    "search_query": f"{model} belt"
                },
                {
                    "name": f"Brush Roll (recommended to replace together)",
                    "search_query": f"{model} brush roll"
                }
            ]
        },
        "leak": {
            "id": "leak-troubleshooting",
            "title": f"{model} Leaking Water or Solution",
            "description": f"Fixing leak issues on your {model}. Stop water or cleaning solution from dripping during use.",
            "possible_causes": [
                "Dirty tank cap seal or O-ring is damaged",
                "Crack in the clean or dirty water tank",
                "Overfilled tank causing overflow during operation",
                "Loose hose connection inside the vacuum",
                "Damaged spray nozzle or valve",
                "Seal degraded on the brush nozzle assembly"
            ],
            "solution_steps": [
                f"Empty both tanks from your {model} completely",
                "Inspect tank caps for damaged or missing seals",
                "Check both clean and dirty tanks for cracks or damage",
                "Examine all hose connections for tightness",
                "Test the spray trigger to see if it leaks continuously",
                "Clean the spray nozzle with warm water to remove clogs",
                "Replace the tank cap or nozzle assembly if damaged",
                "Ensure tanks are not filled above the MAX line"
            ],
            "required_parts": [
                {
                    "name": f"{model} Replacement Tank Cap",
                    "search_query": f"{model} tank cap"
                },
                {
                    "name": f"{model} Spray Nozzle",
                    "search_query": f"{model} spray nozzle"
                }
            ]
        },
        "pulsing": {
            "id": "pulsing-troubleshooting",
            "title": f"{model} Pulsing or Surging Power",
            "description": f"Fixing pulsing, surging, or inconsistent power on your {model}. Understand why power fluctuates and how to resolve it.",
            "possible_causes": [
                "Dirty or clogged filters causing airflow restriction",
                "Bin is overfilled restricting airflow",
                "Brush roll is obstructed causing resistance changes",
                "Motor is failing and power delivery is inconsistent",
                "PCB board issue causing voltage fluctuations",
                "Battery is failing and cannot deliver consistent power"
            ],
            "solution_steps": [
                f"Empty and clean the dust bin on your {model}",
                "Remove and clean all filters (let them dry completely for 24 hours)",
                "Clean the brush roll and remove any tangled hair or debris",
                "Check for any blockages in the air pathways",
                "Test with a fully charged battery to rule out power issues",
                "If pulsing continues, the motor or PCB may need replacement",
                f"Contact {brand} support if the issue persists after cleaning"
            ],
            "required_parts": [
                {
                    "name": f"{model} Replacement Filter",
                    "search_query": f"{model} filter"
                },
                {
                    "name": f"{model} Replacement Motor",
                    "search_query": f"{model} motor"
                }
            ]
        },
        "noise": {
            "id": "noise-troubleshooting",
            "title": f"{model} Making Loud or Unusual Noises",
            "description": f"Diagnosing and fixing loud noises from your {model}. Grinding, screaming, rattling, or high-pitched sounds explained.",
            "possible_causes": [
                "Debris caught in the brush roll or impeller",
                "Worn-out bearings in the motor or brush roll",
                "Broken or damaged belt flopping around",
                "Loose screws or components vibrating",
                "Stone or hard object damaging internal parts",
                "Motor armature rubbing against the housing"
            ],
            "solution_steps": [
                f"Turn off your {model} immediately to prevent further damage",
                "Remove the brush roll and clean thoroughly",
                "Inspect the belt for signs of wear or damage",
                "Check for any loose screws or components and tighten",
                "Run the vacuum without the brush head to isolate the noise source",
                "If noise comes from the main body, the motor may be failing",
                "Contact manufacturer support for repair if motor related",
                "Consider professional repair service for complex mechanical issues"
            ],
            "required_parts": [
                {
                    "name": f"{model} Brush Roll",
                    "search_query": f"{model} brush roll"
                },
                {
                    "name": f"{model} Belt",
                    "search_query": f"{model} belt"
                }
            ]
        },
        "heating": {
            "id": "heating-troubleshooting",
            "title": f"{model} Not Heating Properly",
            "description": f"Fixing heating issues on your {model}. Restore steam or hot water cleaning functionality.",
            "possible_causes": [
                "Heating element has burned out or failed",
                "Thermal fuse has blown due to overheating",
                "PCB board issue preventing heater activation",
                "Water tank is empty or not properly seated",
                "Scale or mineral buildup blocking heating element",
                "Pump failure preventing water circulation to heater"
            ],
            "solution_steps": [
                f"Ensure the water tank on your {model} is filled",
                "Check that the tank is properly seated and detected",
                "Clean the heating element with vinegar to remove scale buildup",
                "Inspect the thermal fuse for continuity",
                "Test the heater with a multimeter for power supply",
                "Check all electrical connections to the heating element",
                f"Replace the heating element or thermal fuse if defective",
                "Run a descaling cycle if available on your model"
            ],
            "required_parts": [
                {
                    "name": f"{model} Heating Element",
                    "search_query": f"{model} heater"
                },
                {
                    "name": f"{model} Thermal Fuse",
                    "search_query": f"{model} thermal fuse"
                }
            ]
        },
        "mapping": {
            "id": "mapping-troubleshooting",
            "title": f"{model} Navigation & Mapping Problems",
            "description": f"Fixing mapping, navigation, and getting lost issues on your {model}. Restore proper cleaning path coverage.",
            "possible_causes": [
                "Wheel encoders are dirty or obstructed",
                "Bumper sensors are not detecting obstacles properly",
                "Cliff sensors are dirty or miscalibrated",
                "Firmware needs updating for better navigation",
                "Battery low causing navigation failures",
                "Home base location has moved or is obstructed"
            ],
            "solution_steps": [
                f"Clean all wheels and encoders on your {model} with a dry cloth",
                "Wipe the bumper sensors and cliff sensors with a damp microfiber cloth",
                f"Perform a factory reset on your {model} (this will clear the map)",
                "Update to the latest firmware for improved navigation algorithms",
                "Clear the home base area of obstacles",
                f"Let your {model} complete a full mapping cycle in a small room first",
                "Ensure adequate lighting for better camera and sensor performance",
                "Check wheel performance - stuck wheels cause mapping errors"
            ],
            "required_parts": [
                {
                    "name": f"{model} Wheel Assembly",
                    "search_query": f"{model} wheel"
                },
                {
                    "name": f"{model} Sensor Array",
                    "search_query": f"{model} sensors"
                }
            ]
        },
        "general": {
            "id": "general-troubleshooting",
            "title": f"How to Fix {display_desc}",
            "description": f"Complete troubleshooting and repair guide for {display_desc}. Diagnostic steps, common problems, and professional solutions to restore your {model} to optimal performance.",
            "possible_causes": [
                f"Normal wear and tear on {model} components",
                "Lack of regular maintenance and cleaning",
                "Specific part failure or degradation",
                "Usage beyond recommended capacity",
                "Environmental factors (dust, moisture, temperature)",
                "Age-related performance decline"
            ],
            "solution_steps": [
                f"Identify the specific issue with your {model} - note any unusual sounds, lights, or behaviors",
                "Consult the official user manual for model-specific troubleshooting guidance",
                "Perform basic diagnostics: check filters, inspect brush rolls, test battery performance",
                f"Clean all accessible parts of your {model} including filters, brush rolls, and dust bins",
                "Ensure proper charging and battery health for cordless models",
                "Inspect for visible damage, blockages, or worn parts that may need replacement",
                "Test the vacuum after each troubleshooting step to isolate the problem",
                f"If the issue persists, consider professional repair service or replacement parts for your {model}",
                "Contact manufacturer support for warranty service or authorized repair centers"
            ],
            "required_parts": [
                {
                    "name": f"{model} Replacement Parts",
                    "search_query": f"{model} parts"
                },
                {
                    "name": f"{model} Maintenance Kit",
                    "search_query": f"{model} filter"
                }
            ]
        }
    }

    # 获取基础模板
    problem_data = problem_templates.get(problem_type, problem_templates["general"])

    # ============================================
    # 🚀💎💰 集成三大核心功能到每个问题类型
    # ============================================

    # 1. 💎 高质量 - 添加 E-E-A-T 人设内容
    persona_content = get_persona_content(problem_type, brand, full_model_name, problem_desc)

    # 2. 💰 高转化 - 生成动态 CTA
    dynamic_cta = generate_dynamic_cta(problem_type, brand, model)

    # 将新功能集成到问题数据中
    problem_data["persona"] = {
        "type": persona_content["persona_type"],
        "name": persona_content["persona_name"],
        "tone": persona_content["tone"],
        "opening": persona_content["opening"],
        "phrases": persona_content["phrases"]
    }

    problem_data["dynamic_cta"] = {
        "urgency": dynamic_cta["urgency"],
        "text": dynamic_cta["text"],
        "subtext": dynamic_cta["subtext"],
        "color": dynamic_cta["color"],
        "icon": dynamic_cta["icon"],
        "pain_point": dynamic_cta["pain_point"]
    }

    # 3. 🚀 高流量标记（如果来自 Google Trends）
    # 这个标记会在主流程中设置
    problem_data["trending_source"] = "database"  # 默认值，会在主流程中更新

    return problem_data

# ============================================
# SEO 关键词生成
# ============================================

def generate_seo_keywords(keyword, brand, model, problem_desc=""):
    """
    生成 SEO 优化的关键词列表（高流量长尾词）

    Args:
        keyword: 原始搜索关键词
        brand: 品牌名称
        model: 完整型号名称（已包含品牌，例如 "Miele C1"）
        problem_desc: 问题描述（可选）

    Returns:
        优化后的 SEO 关键词列表
    """
    # 基础关键词（核心品牌+型号组合）
    # 注意：model 参数已经是完整型号名称（例如 "Miele C1"）
    # 所以直接使用 model，不再添加 brand 前缀
    base_keywords = [
        keyword,  # 原始关键词保持不变
        f"{model} repair",
        f"{model} troubleshooting",
        f"{model} parts",
        f"how to fix {model}",
        f"{model} manual",
        f"{model} guide"
    ]

    # 智能长尾关键词生成器
    def generate_problem_specific_keywords(desc):
        """根据问题描述生成精准的长尾词"""
        desc_lower = desc.lower()
        keywords = []

        # 注意：model 参数已经是完整型号名称（例如 "Miele C1"）
        # 所以直接使用 model，不再添加 brand 前缀

        # 问题类型 → 高流量长尾词映射
        problem_keywords_map = {
            # 电池问题
            'battery': [
                f"{model} battery replacement",
                f"{model} battery not holding charge",
                f"replace {model} battery",
                f"{model} battery life",
                f"where to buy {model} battery",
                f"{model} dead battery",
                f"how long does {model} battery last",
                f"{model} battery cost",
                f"{model} won't hold charge",
                f"{model} battery indicator"
            ],

            # 充电问题
            'charging': [
                f"{model} not charging",
                f"{model} charger problems",
                f"{model} won't charge",
                f"{model} charging light flashing",
                f"replace {model} charger",
                f"{model} charging dock issues",
                f"{model} battery not charging",
                f"fix {model} charging problems",
                f"{model} charge indicator",
                f"{model} charging slowly"
            ],

            # 错误代码
            'error_codes': [
                f"{model} error codes",
                f"{model} error code list",
                f"{model} flashing red light",
                f"{model} beeping",
                f"{model} error codes manual",
                f"troubleshoot {model} error codes",
                f"{model} error codes repair",
                f"what does {model} error code mean",
                f"{model} error codes not working",
                f"fix {model} error codes"
            ],

            # 配件/附件问题
            'attachment': [
                f"{model} attachment not working",
                f"{model} accessories problems",
                f"{model} tools not fitting",
                f"{model} attachment falls off",
                f"replace {model} attachment",
                f"{model} wand problems",
                f"{model} hose replacement",
                f"where to buy {model} attachments",
                f"{model} attachment compatibility",
                f"fix {model} attachment issues"
            ],

            # 电机问题
            'motor': [
                f"{model} motor replacement",
                f"{model} motor noise",
                f"{model} motor burning smell",
                f"{model} motor not spinning",
                f"replace {model} motor",
                f"{model} motor repair cost",
                f"how to replace {model} motor",
                f"{model} motor problems",
                f"{model} motor failure",
                f"fix {model} motor"
            ],

            # 皮带问题
            'belt': [
                f"{model} belt replacement",
                f"{model} broken belt",
                f"{model} belt slipping",
                f"replace {model} belt",
                f"where to buy {model} belt",
                f"how to change {model} belt",
                f"{model} belt problems",
                f"fix {model} belt",
                f"{model} belt size",
                f"{model} drive belt"
            ],

            # 漏水问题
            'leak': [
                f"{model} leaking water",
                f"{model} leaking dirty water",
                f"{model} water tank leaking",
                f"fix {model} leak",
                f"{model} leaking from bottom",
                f"{model} seal replacement",
                f"where is {model} leaking from",
                f"{model} tank cap problems",
                f"repair {model} water leak",
                f"stop {model} leaking"
            ],

            # 吸力脉动问题
            'pulsing': [
                f"{model} pulsing",
                f"{model} suction pulsating",
                f"{model} revving up and down",
                f"fix {model} pulsing",
                f"{model} not constant suction",
                f"{model} surging",
                f"why does {model} pulse",
                f"{model} pulsing and stopping",
                f"troubleshoot {model} pulsing",
                f"stop {model} from pulsing"
            ],

            # 噪音问题
            'noise': [
                f"{model} making loud noise",
                f"{model} rattling noise",
                f"{model} whistling sound",
                f"{model} high pitched noise",
                f"fix {model} noise",
                f"{model} strange sounds",
                f"{model} clicking noise",
                f"{model} grinding noise",
                f"why is {model} so loud",
                f"reduce {model} noise"
            ],

            # 过热问题
            'heating': [
                f"{model} overheating",
                f"{model} getting hot",
                f"{model} burning smell",
                f"fix {model} overheating",
                f"{model} shuts off when hot",
                f"{model} thermal protection",
                f"{model} too hot to touch",
                f"{model} heat issues",
                f"prevent {model} overheating",
                f"{model} temperature warning"
            ],

            # 导航/映射问题
            'mapping': [
                f"{model} mapping problems",
                f"{model} not mapping house",
                f"{model} lost map",
                f"{model} navigation issues",
                f"reset {model} map",
                f"{model} not cleaning in straight lines",
                f"{model} mapping errors",
                f"fix {model} navigation",
                f"{model} can't find home",
                f"{model} cleaning pattern problems"
            ],

            # 连接性问题
            'connectivity': [
                f"{model} not connecting to wifi",
                f"{model} app not working",
                f"{model} bluetooth problems",
                f"{model} offline",
                f"fix {model} connection",
                f"{model} can't connect to phone",
                f"{model} network issues",
                f"{model} app connection failed",
                f"troubleshoot {model} connectivity",
                f"reconnect {model} to wifi"
            ],

            # 刷条问题
            'brushroll': [
                f"{model} brush roll not spinning",
                f"{model} brush roll replacement",
                f"{model} brush bar stuck",
                f"clean {model} brush roll",
                f"{model} bristles worn",
                f"replace {model} brush roll",
                f"{model} brush roll removal",
                f"fix {model} brush roll",
                f"{model} roller not turning",
                f"install {model} brush roll"
            ],

            # 滤网问题
            'filter': [
                f"{model} filter replacement",
                f"{model} filter cleaning",
                f"{model} hepa filter",
                f"where to buy {model} filters",
                f"clean {model} filter",
                f"{model} filter indicator",
                f"{model} pre-filter",
                f"{model} post-filter",
                f"change {model} filter",
                f"{model} filter washable"
            ],

            # 吸力损失问题
            'suction': [
                f"{model} lost suction",
                f"{model} no suction",
                f"{model} weak suction",
                f"fix {model} suction",
                f"{model} not picking up dirt",
                f"restore {model} suction",
                f"{model} suction power low",
                f"{model} poor suction",
                f"improve {model} suction",
                f"{model} suction problems"
            ],

            # 电源问题
            'power': [
                f"{model} won't turn on",
                f"{model} not working",
                f"{model} no power",
                f"{model} dead",
                f"fix {model} power",
                f"{model} won't start",
                f"{model} power issues",
                f"{model} not responding",
                f"repair {model} power",
                f"{model} startup problems"
            ]
        }

        # 检测问题类型并返回对应关键词
        for problem_type, keywords in problem_keywords_map.items():
            # 检查描述中是否包含相关关键词
            type_keywords = problem_type.split('_')
            if any(kw in desc_lower for kw in type_keywords):
                return keywords

        # 默认返回通用长尾词
        return [
            f"where to buy {model} parts",
            f"{model} replacement parts",
            f"{model} not working",
            f"fix {model} problems",
            f"{model} repair guide",
            f"{model} troubleshooting tips",
            f"{model} maintenance",
            f"how to repair {model}"
        ]

    # 生成问题特定的长尾关键词
    if problem_desc:
        long_tail_keywords = generate_problem_specific_keywords(problem_desc)
    else:
        # 如果没有问题描述，使用通用长尾词
        # 注意：model 参数已经是完整型号名称
        long_tail_keywords = [
            f"where to buy {model} parts",
            f"{model} replacement parts",
            f"{model} not working",
            f"fix {model} problems"
        ]

    # 合并所有关键词（去重）
    all_keywords = base_keywords + long_tail_keywords

    # 去重并保持顺序
    seen = set()
    unique_keywords = []
    for kw in all_keywords:
        if kw not in seen:
            seen.add(kw)
            unique_keywords.append(kw)

    return unique_keywords

# ============================================
# 趋势分数计算
# ============================================

def calculate_trending_score(keyword):
    """计算关键词的热度分数（模拟）"""
    # 实际应用中可以从 Google Trends API 或其他数据源获取
    base_score = 50

    # 根据关键词长度调整
    if len(keyword.split()) <= 3:
        base_score += 20

    # 根据问题类型调整
    high_traffic_words = ["battery", "charging", "not working", "troubleshooting"]
    for word in high_traffic_words:
        if word in keyword.lower():
            base_score += 15
            break

    return min(base_score, 100)

# ============================================
# 文件保存
# ============================================

def save_guide(guide):
    """保存生成的指南"""
    brand_slug = guide["brand"].lower().replace(" ", "-").replace("+", "plus")
    model_clean = guide["model"].lower().replace(guide["brand"].lower(), "").strip()
    model_slug = model_clean.replace(" ", "-").replace("/", "-").replace("+", "plus").strip("-")

    filename = f"{brand_slug}-{model_slug}.json"
    filepath = DATA_DIR / filename

    if filepath.exists():
        log(f"⏭️  文件已存在: {filename}")
        return False

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(guide, f, indent=2, ensure_ascii=False)

    log(f"✅ 生成成功: {filename}")
    return True

# ============================================
# Git 自动提交
# ============================================

def git_commit_changes(message):
    """自动提交更改到 Git"""
    try:
        os.chdir(Path(__file__).parent.parent)

        subprocess.run(['git', 'add', 'data/'], check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', message], check=True, capture_output=True)
        subprocess.run(['git', 'push'], check=True, capture_output=True)

        log("✅ 已自动提交到 Git")
        return True
    except Exception as e:
        log(f"⚠️  Git 提交失败: {str(e)}", "WARN")
        return False

# ============================================
# 主函数
# ============================================

def main():
    """主执行函数"""
    log("=" * 60)
    log("🤖 AI 智能内容生成器启动 (🚀 高流量 + 💎 高质量 + 💰 高转化)")
    log("=" * 60)

    generated = 0
    skipped = 0

    # 🚀 第一步：抓取 Google Trends 实时趋势
    log("\n🔍 步骤 1: 抓取 Google Trends 实时数据...")
    trending_keywords = fetch_google_trends_rss()

    # 💾 保存 Google Trends 原始数量（用于诚实标记来源）
    google_trends_count = len(trending_keywords)

    # 💡 智能关键词选择策略：
    # - 如果 Google Trends 有相关词，优先使用（高流量）
    # - 如果不足 3 个，从数据库补充（保证每天 3 篇）
    needed = 3 - len(trending_keywords)
    if needed > 0:
        log(f"📊 从数据库补充 {needed} 个关键词...")

        # 轮转策略：根据一年中的天数计算起始索引
        day_of_year = datetime.now().timetuple().tm_yday
        start_idx = (day_of_year * 3) % len(TRENDING_KEYWORDS)

        for i in range(needed):
            idx = (start_idx + i) % len(TRENDING_KEYWORDS)
            supplement_keyword = TRENDING_KEYWORDS[idx]
            if supplement_keyword not in trending_keywords:
                trending_keywords.append(supplement_keyword)

    # 取前 3 个关键词
    keywords_today = trending_keywords[:3]

    log(f"\n📅 今天是第 {datetime.now().timetuple().tm_yday} 天")
    log(f"🎯 今天将生成 3 篇文章:")
    for i, kw in enumerate(keywords_today, 1):
        # ✅ 诚实标记：根据实际来源显示
        source = "🔥 Google Trends" if i <= google_trends_count else "📊 数据库"
        log(f"   {i}. {kw} [{source}]")

    # 处理今天的 3 个关键词
    for i, keyword in enumerate(keywords_today, 1):
        log(f"\n[{i}/3] 处理: {keyword}")

        # ✅ 诚实标记来源：根据是否从 Google Trends 获取来决定
        trending_source = "google_trends" if i <= google_trends_count else "database"

        try:
            # 💎🚀💰 使用增强的生成器（包含三大新功能）
            guide = generate_smart_guide(keyword, trending_source=trending_source)

            # 保存文件
            if save_guide(guide):
                generated += 1
                log(f"   ✅ 成功生成并保存")
            else:
                skipped += 1
                log(f"   ⏭️  文件已存在，跳过")

            time.sleep(0.5)

        except Exception as e:
            log(f"❌ 错误: {str(e)}", "ERROR")
            skipped += 1
            continue

    # 最终提交
    if generated > 0:
        git_commit_changes(f"🤖 AI 生成内容: {generated} 个新页面")

    # 总结
    log("\n" + "=" * 60)
    log(f"✅ 完成！")
    log(f"📊 今日生成: {generated} 篇")
    log(f"⏭️  跳过: {skipped} 篇")
    log(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 60)

    # 发送 Telegram 通知
    send_telegram_notification(generated, skipped, keywords_today)

if __name__ == "__main__":
    main()
