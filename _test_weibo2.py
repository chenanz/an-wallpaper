import requests
import json
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
}

# Weibo requires login for most API calls
# Let's try another approach: use the Weibo AJAX API that works without login for public content

# The correct endpoint for weibo search
import urllib.parse
keyword = urllib.parse.quote("原神同人")

# Try containerid approach (Weibo's new search API)
urls_to_try = [
    # Weibo Msearch (mobile-ish)
    f"https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D1%26q%3D{keyword}&page_type=searchall",
    f"https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D61%26q%3D{keyword}&page_type=searchall",
    # Weibo ajax search with bid
    f"https://weibo.com/ajax/side/search?q={keyword}",
    # Try the super topic
    f"https://m.weibo.cn/api/container/getIndex?containerid=1008084c08f0f006b7236e1c411948bb5e8cf8",
]

for url in urls_to_try:
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"GET status={r.status_code} len={len(r.text)}")
        ct = r.headers.get('content-type', '')
        print(f"  CT: {ct}")
        if r.status_code == 200 and 'json' in ct:
            j = r.json()
            print(f"  JSON keys: {list(j.keys())[:10]}")
            if 'data' in j:
                data = j['data']
                if isinstance(data, dict):
                    print(f"  data keys: {list(data.keys())[:10]}")
                    # Search for cards
                    cards = data.get('cards', [])
                    print(f"  Cards: {len(cards)}")
                    if cards:
                        for card in cards[:2]:
                            print(f"  Card: {json.dumps(card, ensure_ascii=False)[:500]}")
                elif isinstance(data, list):
                    print(f"  data list len: {len(data)}")
                    for item in data[:2]:
                        print(f"  Item: {json.dumps(item, ensure_ascii=False)[:300]}")
    except Exception as e:
        print(f"  Error: {e}")
    print()

