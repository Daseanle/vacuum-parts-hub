#!/usr/bin/env python3
"""测试 Google Trends 抓取"""
import requests
import re
import time

vacuum_keywords = [
    'vacuum', 'dyson', 'shark', 'hoover', 'bissell', 'roomba',
    'robot', 'cleaner', 'suction', 'carpet', 'floor',
    'miele', 'samsung', 'tineco', 'lg', 'electrolux'
]

print('🔍 测试抓取 Google Trends 网页...')

regions = ['US', 'GB']

for region in regions:
    url = f'https://trends.google.com/trends/trendingsearches/daily?geo={region}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f'\n{region} 地区状态码: {response.status_code}')

        if response.status_code == 200:
            content = response.text

            # 尝试多种模式提取
            patterns = [
                r'\\"([^"]+)\\"[,\s]+\d+[,\s]+\d+',  # JSON 数组格式
                r'query:\s*\\"([^"]+)\\"',  # query: "搜索词"
                r'\[\\\"\\"([^\\]+)\\\"\\"',  # 转义的 Unicode
            ]

            for pattern in patterns:
                matches = re.findall(pattern, content)
                if matches:
                    print(f'   模式匹配成功: 找到 {len(matches)} 个')
                    for i, match in enumerate(matches[:5], 1):
                        print(f'   {i}. {match}')
                        if any(kw in match.lower() for kw in vacuum_keywords):
                            print(f'      ✅ 吸尘器相关！')
                    break
            else:
                print(f'   没有找到匹配的模式')

        time.sleep(1)

    except Exception as e:
        print(f'   错误: {e}')
