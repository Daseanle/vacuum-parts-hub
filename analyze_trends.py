#!/usr/bin/env python3
"""深度分析 Google Trends 页面"""
from playwright.sync_api import sync_playwright
import time
import re
import json

print('🔍 深度分析 Google Trends 页面结构...\n')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    trends_url = "https://trends.google.com/trends/trendingsearches/daily?geo=US"
    print(f'📱 访问: {trends_url}')

    page.goto(trends_url, timeout=30000)

    # 等待页面加载
    print('⏳ 等待页面加载...')
    page.wait_for_load_state('networkidle', timeout=30000)
    print('✅ 网络加载完成')

    # 等待 JavaScript 渲染
    print('⏳ 等待 JavaScript 渲染（10秒）...')
    time.sleep(10)

    # 1. 获取页面标题
    title = page.title()
    print(f'\n📄 页面标题: {title}')

    # 2. 获取完整 HTML 并分析
    html = page.content()

    # 保存 HTML 供分析
    with open('trends_full.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('💾 完整 HTML 已保存到 trends_full.html')

    # 3. 分析 HTML 中的 JavaScript 数据
    print('\n🔍 分析页面中的数据...')

    # 查找可能的 JSON 数据块
    json_patterns = [
        (r'\[{[^\]]{20,200}\]', '嵌套数组'),
        (r'\{[^{}]*"title"[^{}]*\}', '包含 title 的对象'),
        (r'\{[^{}]*"query"[^{}]*\}', '包含 query 的对象'),
        (r'"title"\s*:\s*"([^"]+)"', 'title 值'),
        (r'"query"\s*:\s*"([^"]+)"', 'query 值'),
        (r'"text"\s*:\s*"([^"]+)"', 'text 值'),
    ]

    found_data = []
    for pattern, desc in json_patterns:
        matches = re.findall(pattern, html)
        if matches:
            print(f'\n✅ 找到 {len(matches)} 个 {desc}')
            for i, match in enumerate(matches[:5], 1):
                clean = match[:200].replace('\n', ' ')
                print(f'   {i}. {clean}...')
                found_data.append(match)

    # 4. 尝试提取所有可能的关键词
    print('\n🔍 提取可能的关键词...')

    # 查找所有引号包围的文本（可能是搜索词）
    quoted_text = re.findall(r'"([A-Za-z][A-Za-z0-9\s]{5,50})"', html)

    # 过滤出可能与搜索相关的词
    search_related = []
    filter_words = ['vacuum', 'dyson', 'shark', 'hoover', 'bissell', 'cleaner', 'robot']

    for text in quoted_text:
        text = text.strip()
        if any(fw in text.lower() for fw in filter_words):
            if text not in search_related and len(text) > 3:
                search_related.append(text)

    if search_related:
        print(f'\n✅ 找到 {len(search_related)} 个可能与搜索相关的词:')
        for i, word in enumerate(search_related[:10], 1):
            print(f'   {i}. {word}')
    else:
        print('⚠️ 没有找到明显的搜索相关词')

    # 5. 查找页面中的所有文本节点
    print('\n🔍 提取页面主要文本...')
    body_text = page.inner_text('body')

    # 保存文本
    with open('trends_body_text.txt', 'w', encoding='utf-8') as f:
        f.write(body_text)
    print('💾 页面文本已保存到 trends_body_text.txt')

    # 查找包含我们关键词的行
    vacuum_keywords = ['vacuum', 'dyson', 'shark', 'hoover', 'bissell', 'roomba', 'cleaner']
    relevant_lines = []

    for line in body_text.split('\n'):
        line_lower = line.lower()
        if any(kw in line_lower for kw in vacuum_keywords):
            relevant_lines.append(line.strip())

    if relevant_lines:
        print(f'\n✅ 找到 {len(relevant_lines)} 行包含吸尘器关键词:')
        for i, line in enumerate(relevant_lines[:10], 1):
            print(f'   {i}. {line[:100]}...')
    else:
        print('⚠️ 页面文本中没有找到吸尘器关键词')

    # 6. 截图
    page.screenshot(path='trends_analysis.png', full_page=True)
    print('\n📸 截图已保存到 trends_analysis.png')

    browser.close()

print('\n' + '='*60)
print('📊 分析总结:')
print('='*60)
print(f'✅ HTML 大小: {len(html)} 字节')
print(f'✅ 提取的数据块: {len(found_data)} 个')
print(f'✅ 搜索相关词: {len(search_related)} 个')
print(f'✅ 吸尘器相关行: {len(relevant_lines)} 行')
print('\n💡 请查看生成的文件:')
print('   - trends_full.html (完整 HTML)')
print('   - trends_body_text.txt (页面文本)')
print('   - trends_analysis.png (截图)')
print('='*60)
