import requests
import re
import urllib.parse
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
}

# Strategy 1: Bilibili video search with image covers
# This is KNOWN WORKING from the existing sync_bilibili.py
# Video covers are high quality and many are fan art
bili_headers = {
    **headers,
    "Referer": "https://search.bilibili.com/",
}

import urllib.parse
kw = urllib.parse.quote("原神同人 壁纸")
url = f"https://api.bilibili.com/x/web-interface/search/type?keyword={kw}&search_type=1&page=1&page_size=5"
try:
    r = requests.get(url, headers=bili_headers, timeout=15)
    j = r.json()
    if j.get('data', {}).get('result'):
        for item in j['data']['result'][:3]:
            print(f"  Title: {item.get('title','')[:50]}")
            pic = item.get('pic', '')
            print(f"  Pic: http:{pic}" if pic.startswith('//') else f"  Pic: {pic}")
            print(f"  Author: {item.get('author','')}")
            print(f"  Duration: {item.get('duration','')}")
            print()
except Exception as e:
    print(f"Bili search error: {e}")

# Strategy 2: Try bing image search (works in China via cn.bing.com)  
# This is a great source for finding Lofter/other Chinese site fan art
bing_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

bing_params = urllib.parse.urlencode({
    "q": "原神同人壁纸 site:lofter.com",
    "first": 1,
    "count": 10,
    "qft": "+filterui:imagesize-large",
})

# Try Bing image search API
bing_url = f"https://cn.bing.com/images/search?{bing_params}"
try:
    r = requests.get(bing_url, headers=bing_headers, timeout=15)
    print(f"\nBing Images: status={r.status_code} len={len(r.text)}")
    if r.status_code == 200 and len(r.text) > 5000:
        # Extract image URLs from Bing results
        # Bing uses m attribute with JSON data
        m_data = re.findall(r'm="({.*?})"', r.text)
        print(f"  m data blocks: {len(m_data)}")
        for block in m_data[:5]:
            try:
                # Unescape HTML entities
                import html
                unescaped = html.unescape(block)
                j = json.loads(unescaped)
                print(f"  murl: {j.get('murl', '')[:80]}")
                print(f"  turl: {j.get('turl', '')[:80]}")
                print(f"  surl: {j.get('surl', '')[:80]}")
                print(f"  desc: {j.get('t', '')[:40]}")
                print()
            except:
                pass
except Exception as e:
    print(f"Bing error: {e}")

# Strategy 3: Try the Bing Image Search API endpoint
bing_api_params = urllib.parse.urlencode({
    "q": "原神同人壁纸",
    "first": 1,
    "count": 10,
    "mmasync": 1,
})
bing_api_url = f"https://cn.bing.com/images/async?{bing_api_params}"
try:
    r = requests.get(bing_api_url, headers=bing_headers, timeout=15)
    print(f"\nBing Image Async API: status={r.status_code} len={len(r.text)}")
    if r.status_code == 200 and len(r.text) > 500:
        m_data = re.findall(r'm="({.*?})"', r.text)
        print(f"  m data blocks: {len(m_data)}")
        for block in m_data[:3]:
            try:
                import html
                unescaped = html.unescape(block)
                j = json.loads(unescaped)
                print(f"  murl: {j.get('murl', '')[:80]}")
                print(f"  surl (source): {j.get('surl', '')[:60]}")
                print(f"  desc: {j.get('t', '')[:40]}")
            except:
                pass
except Exception as e:
    print(f"Bing async error: {e}")

