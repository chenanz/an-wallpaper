import requests
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
}

# The m.weibo.cn API works with certain containerids
# Let's try specific game topic pages on m.weibo.cn
tests = [
    # Game super topics (超话)
    {"url": "https://m.weibo.cn/api/container/getIndex?containerid=1008084c08f0f006b7236e1c411948bb5e8cf8", "desc": "原神超话"},
    # Try searching for "原神 同人 图" via m.weibo.cn
    {"url": "https://m.weibo.cn/api/container/getIndex?containerid=100103type=1&q=原神同人图", "desc": "m.weibo search"},
    # Weibo ajax endpoint (the new PC API)
    {"url": "https://weibo.com/ajax/statuses/hot_topic", "desc": "hot topic"},
    # Weibo open API
    {"url": "https://open.weibo.com/api/common/get_zone", "desc": "open API"},
]

import urllib.parse
for t in tests:
    url = t["url"]
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"[{t['desc']}] status={r.status_code} len={len(r.text)}")
        if r.status_code == 200 and len(r.text) > 10:
            try:
                j = r.json()
                print(f"  JSON keys: {list(j.keys())[:5]}")
                if 'data' in j and isinstance(j['data'], dict):
                    print(f"  data keys: {list(j['data'].keys())[:5]}")
            except:
                print(f"  Not JSON: {r.text[:200]}")
    except Exception as e:
        print(f"  Error: {e}")
    print()

# The most reliable approach: use m.weibo.cn container API
# We need to first get a valid containerid for searches
# Let's check the m.weibo.cn search page first
import urllib.parse
keyword = urllib.parse.quote("原神同人")
search_url = f"https://m.weibo.cn/search?containerid=100103type%3D1%26q%3D{keyword}"
r = requests.get(search_url, headers=headers, timeout=10)
print(f"Search page: {r.status_code} len={len(r.text)}")

# Try a different approach: use the m.weibo.cn/p/ API
# or the user timeline API which is publicly accessible (some users)
# Actually the simplest may be just https://m.weibo.cn/api/container/getIndex
# with proper containerid formatting

# For search: containerid = "100103type=1&q=KEYWORD"
# For images specifically: containerid = "100103type=2&q=KEYWORD&filter=haspic"
encoded_kw = urllib.parse.quote("原神同人")
# Type 1 = all, Type 2 = images
cid = f"100103type=2&q={encoded_kw}&filter=haspic"
url = f"https://m.weibo.cn/api/container/getIndex?containerid={urllib.parse.quote(cid, safe='')}&page_type=searchall"
try:
    r = requests.get(url, headers=headers, timeout=10)
    print(f"\nSearch with haspic filter: status={r.status_code} len={len(r.text)}")
    if r.status_code == 200:
        try:
            j = r.json()
            print(f"  JSON ok! keys: {list(j.keys())}")
            if 'data' in j:
                d = j['data']
                if isinstance(d, dict):
                    print(f"  data keys: {list(d.keys())[:10]}")
                    cards = d.get('cards', [])
                    print(f"  cards: {len(cards)}")
                    if cards:
                        print(f"  First card: {json.dumps(cards[0], ensure_ascii=False)[:500]}")
        except:
            print(f"  Not JSON: {r.text[:300]}")
except Exception as e:
    print(f"Error: {e}")

