import requests
import json
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://www.lofter.com/",
    "Accept": "application/json, text/plain, */*",
    "X-Requested-With": "XMLHttpRequest",
}

# The proper working Lofter API endpoints based on scraping tool implementations:
endpoints = [
    # Tag/Topic post listing (this is the primary way to get content in Lofter)
    ("POST tagposts", "POST", "https://www.lofter.com/front/api/tag/posts",
        {"data": {"tag": "原神同人", "type": "new", "offset": 0, "limit": 5}}),
    # Search posts
    ("POST searchPosts", "POST", "https://www.lofter.com/front/api/search/posts",
        {"data": {"keyword": "原神同人", "offset": 0, "limit": 5}}),
    # Explore
    ("POST explore", "POST", "https://www.lofter.com/front/api/explore/posts",
        {"data": {"tag": "原神同人", "offset": 0, "limit": 5}}),
    # Try GET versions
    ("GET tagposts", "GET", "https://www.lofter.com/front/api/tag/posts?tag=原神同人&type=new&offset=0&limit=5", None),
    ("GET searchPosts", "GET", "https://www.lofter.com/front/api/search/posts?keyword=原神同人&offset=0&limit=5", None),
]

for name, method, url, extra in endpoints:
    try:
        extra_headers = {**headers, "Content-Type": "application/json"}
        if method == "POST" and extra:
            r = requests.post(url, headers=extra_headers, json=extra["data"], timeout=10)
        elif method == "POST":
            r = requests.post(url, headers=extra_headers, json={"keyword": "原神同人", "offset": 0, "limit": 5}, timeout=10)
        else:
            r = requests.get(url, headers=headers, timeout=10)
        
        print(f"[{name}] {method} status={r.status_code} len={len(r.text)} ct={r.headers.get('content-type','')[:40]}")
        if r.status_code == 200 and len(r.text) > 50:
            print(r.text[:2000])
            try:
                j = r.json()
                print(f"JSON keys: {list(j.keys())[:10] if isinstance(j, dict) else 'array'}")
            except:
                pass
        elif r.status_code != 404:
            print(r.text[:500])
    except Exception as e:
        print(f"Error: {e}")
    print()

# Also try with X-Lofter-* headers (Lofter's CORS-like headers)
lofter_headers = {
    **headers,
    "X-Lofter-Client-Type": "web",
    "X-Lofter-Requested-With": "XMLHttpRequest",
}

for name, method, url, extra in endpoints[:2]:
    try:
        if method == "POST" and extra:
            r = requests.post(url, headers=lofter_headers, json=extra["data"], timeout=10)
        else:
            r = requests.get(url, headers=lofter_headers, timeout=10)
        print(f"[{name}+lofter-headers] status={r.status_code} len={len(r.text)}")
        if r.status_code == 200 and len(r.text) > 50:
            print(r.text[:2000])
    except Exception as e:
        print(f"Error: {e}")
    print()

