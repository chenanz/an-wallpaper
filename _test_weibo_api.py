import requests
import json
import re
import urllib.parse

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://s.weibo.com/",
}

# Weibo search API (known working endpoint)
keyword = urllib.parse.quote("原神同人")
url = f"https://s.weibo.com/ajax/topic/info?tag={keyword}"

# Also try the container API which is commonly used for search
urls = [
    f"https://s.weibo.com/ajax/topic/info?tag={keyword}",
    f"https://s.weibo.com/ajax/direct?type=tag&tag={keyword}",
    # Weibo search with XHR
    f"https://s.weibo.com/weibo?q={keyword}&page=1",
]

for url in urls:
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"GET {url[:60]}... status={r.status_code} len={len(r.text)}")
        if r.status_code == 200:
            ct = r.headers.get('content-type', '')
            print(f"  Content-Type: {ct}")
            if 'json' in ct:
                print(f"  Body: {r.text[:2000]}")
            elif 'html' in ct and len(r.text) > 5000:
                # Look for image URLs
                imgs = re.findall(r'(https?://[a-z0-9._:/-]+\.sinaimg\.[a-z]+/[a-zA-Z0-9._/:-]+\.(?:jpg|png|webp|gif))', r.text)
                if imgs:
                    print(f"  Found {len(imgs)} images")
                    for i in imgs[:5]:
                        print(f"    {i}")
    except Exception as e:
        print(f"Error: {e}")
    print()

# Test weibo2 search (the newer WebV2 format)
r = requests.get(f"https://s.weibo.com/weibo?q={keyword}", headers={
    "User-Agent": headers["User-Agent"],
    "Accept": "text/html",
}, timeout=15)

if r.status_code == 200 and len(r.text) > 5000:
    print(f"Weibo search page: len={len(r.text)}")
    # Look for image URLs  
    imgs = re.findall(r'(https?://[a-z0-9._:/-]+\.sinaimg\.[a-z]+/[a-zA-Z0-9._/:-]+\.(?:jpg|png|webp|gif))', r.text)
    if imgs:
        print(f"Found {len(imgs)} images in search results!")
        for i in imgs[:5]:
            print(f"  {i}")
    # Also look for JSON data
    json_data = re.search(r'\$render_data\s*=\s*(\[.*?\])\s*;', r.text, re.DOTALL)
    if json_data:
        print(f"Found $render_data ({len(json_data.group(1))} chars)")

