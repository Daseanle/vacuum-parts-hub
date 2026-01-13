#!/usr/bin/env python3
"""调试 Google Trends 页面内容"""
from playwright.sync_api import sync_playwright
import time
import re
import json

print('🔍 调试 Google Trends 页面...')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # 非无头模式，方便观察
    page = browser.new_page()

    trends_url = "https://trends.google.com/trends/trendingsearches/daily?geo=US"
    print(f'访问: {trends_url}')

    page.goto(trends_url, timeout=30000)
    page.wait_for_load_state('networkidle', timeout=30000)
    time.sleep(8)  # 等待更长时间

    # 保存完整 HTML
    html = page.content()
    with open('trends_debug.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('✅ 完整 HTML 已保存到 trends_debug.html')

    # 截图
    page.screenshot(path='trends_debug.png', full_page=True)
    print('✅ 截图已保存到 trends_debug.png')

    # 尝试查找所有包含搜索词的文本
    all_text = page.inner_text('body')
    with open('trends_text.txt', 'w', encoding='utf-8') as f:
        f.write(all_text)
    print('✅ 页面文本已保存到 trends_text.txt')

    # 查找所有链接
    links = page.query_selector_all('a')
    with open('trends_links.txt', 'w', encoding='utf-8') as f:
        for link in links[:50]:
            href = link.get_attribute('href')
            text = link.inner_text()
            f.write(f'{text} -> {href}\n')
    print(f'✅ 找到 {len(links)} 个链接，已保存到 trends_links.txt')

    # 尝试各种 JSON 模式
    patterns_to_try = [
        (r'\["([^"]+)",\d+,\d+', 'JSON 数组'),
        (r'"text"\s*:\s*"([^"]+)"', 'text 字段'),
        (r'"title"\s*:\s*"([^"]+)"', 'title 字段'),
        (r'"query"\s*:\s*"([^"]+)"', 'query 字段'),
        (r'\\u003C[^>]*\\u003E([^\\]+)\\u003C', 'Unicode 转义'),
    ]

    for pattern, desc in patterns_to_try:
        matches = re.findall(pattern, html)
        if matches:
            print(f'\n✅ 模式 "{desc}" 找到 {len(matches)} 个匹配:')
            for i, match in enumerate(matches[:10], 1):
                print(f'   {i}. {match}')

    # 搜索 "vacuum", "dyson" 等关键词
    vacuum_kw = ['vacuum', 'dyson', 'shark', 'hoover', 'bissell', 'roomba']
    for kw in vacuum_kw:
        if kw.lower() in all_text.lower():
            print(f'\n✅✅✅ 找到关键词: {kw}')

    print('\n按 Ctrl+C 关闭浏览器...')
    input('按 Enter 关闭...')

    browser.close()

print('调试完成！请查看生成的文件:')
print('  - trends_debug.html (完整 HTML)')
print('  - trends_debug.png (截图)')
print('  - trends_text.txt (页面文本)')
print('  - trends_links.txt (所有链接)')
