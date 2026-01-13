#!/usr/bin/env python3
"""测试 Playwright 抓取 Google Trends"""
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time

vacuum_keywords = [
    'vacuum', 'dyson', 'shark', 'hoover', 'bissell', 'roomba',
    'robot', 'cleaner', 'suction', 'carpet', 'floor',
    'miele', 'samsung', 'tineco', 'lg', 'electrolux'
]

print('🔍 测试 Playwright 抓取 Google Trends...')

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print('   浏览器启动成功！')

        # 测试美国地区
        trends_url = "https://trends.google.com/trends/trendingsearches/daily?geo=US"
        print(f'   访问: {trends_url}')

        page.goto(trends_url, timeout=30000)
        print('   ✅ 页面加载成功')

        # 等待页面加载
        page.wait_for_load_state('networkidle', timeout=15000)
        print('   ✅ 等待网络空闲')

        time.sleep(3)
        print('   ✅ 等待 JavaScript 执行')

        # 截图保存
        page.screenshot(path='trends_screenshot.png')
        print('   ✅ 截图已保存到 trends_screenshot.png')

        # 尝试提取内容
        selectors = [
            'div.feed-load-more-button',
            'div[ng-if*="feedItem"]',
            'span[ng-bind*="title"]',
            'div.feed-item',
            '[class*="feed-item"]',
            'body'
        ]

        for selector in selectors:
            elements = page.query_selector_all(selector)
            if elements:
                print(f'   ✅ 找到 {len(elements)} 个元素: {selector}')

                # 显示前3个元素的文本
                for i, elem in enumerate(elements[:3], 1):
                    try:
                        text = elem.inner_text()
                        if text:
                            preview = text[:100].replace('\n', ' ')
                            print(f'      {i}. {preview}...')

                            # 检查是否与吸尘器相关
                            if any(kw in text.lower() for kw in vacuum_keywords):
                                print(f'         ✅✅✅ 包含吸尘器关键词！')
                    except:
                        pass
                break

        browser.close()
        print('\n✅ 测试完成！')

except Exception as e:
    print(f'❌ 错误: {e}')
    import traceback
    traceback.print_exc()
