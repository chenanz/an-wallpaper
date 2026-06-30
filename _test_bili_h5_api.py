import requests
import json
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/",
}

# Bilibili has multiple search types - let's test various search types
# search_type values: 1=video, 2=topic, 7=article, 12=live_room, ...
# For images, there might be a specific type or use subtype

import urllib.parse
keyword = urllib.parse.quote("原神同人")

tests = [
    # Article search (type=7) - used by sync_bilibili.py already
    f"https://api.bilibili.com/x/web-interface/search/type?keyword={keyword}&search_type=7&page=1&page_size=5",
    # Picture/photo search (some internal types)
    f"https://api.bilibili.com/x/web-interface/search/type?keyword={keyword}&search_type=3&page=1&page_size=5",
    f"https://api.bilibili.com/x/web-interface/search/type?keyword={keyword}&search_type=4&page=1&page_size=5",
    # Comprehensive search
    f"https://api.bilibili.com/x/web-interface/wbi/search/all?keyword={keyword}&page=1",
    # Bilibili H5.pic search 
    f"https://api.bilibili.com/x/web-interface/search/type?keyword={keyword}&search_type=46&page=1&page_size=5",
    # Bilibili topic/api
    f"https://api.bilibili.com/x/web-interface/search/type?keyword={keyword}&search_type=50&page=1&page_size=5",
]

for url in tests:
    try:
        r = requests.get(url, headers=headers, timeout=10)
        j = r.json()
        code = j.get('code', -1)
        msg = j.get('message', '')
        data = j.get('data', {})
        result = data.get('result', [])
        print(f"  code={code} msg={msg[:30]} data_keys={list(data.keys())[:5] if isinstance(data, dict) else type(data)} result_len={len(result) if isinstance(result, list) else 'N/A'}")
        if isinstance(result, list) and len(result) > 0:
            print(f"  First result: {json.dumps(result[0], ensure_ascii=False)[:400]}")
    except Exception as e:
        print(f"  Error: {e}")
    print()

# Let's also check Bilibili's popular feeds API (bilibili popular/trending images)
popular_tests = [
    "https://api.bilibili.com/x/web-interface/popular?ps=5&pn=1",
    "https://api.bilibili.com/x/web-interface/dynamic/region?rid=1&ps=5",
    # Bilibili channel videos with tag (can find anime fan art)
    "https://api.bilibili.com/x/web-interface/search/type?keyword=原神+同人+壁纸&search_type=1&page=1&page_size=3",
    # Video search with fansort (sorted by likes)
    f"https://api.bilibili.com/x/web-interface/search/type?keyword={keyword}&search_type=1&page=1&page_size=3&order=click",
]

for url in popular_tests:
    try:
        r = requests.get(url, headers=headers, timeout=10)
        j = r.json()
        code = j.get('code', -1)
        data = j.get('data', {})
        if isinstance(data, dict):
            result = data.get('result', data.get('list', data.get('archives', [])))
            print(f"  code={code} result_len={len(result) if isinstance(result, list) else 'N/A'}")
            if isinstance(result, list) and len(result) > 0:
                print(f"  Sample: {json.dumps(result[0], ensure_ascii=False)[:300]}")
        else:
            print(f"  code={code} data_type={type(data)}")
    except Exception as e:
        print(f"  Error: {e}")
    print()

