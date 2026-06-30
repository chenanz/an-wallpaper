import requests
import json
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://www.lofter.com",
    "Referer": "https://www.lofter.com/",
}

# URL encode the Chinese characters
import urllib.parse
keyword = urllib.parse.quote("原神同人")

# Try with encoded URLs
urls = [
    f"https://api.lofter.com/v2.0/searchPost.api?keyword={keyword}&offset=0&limit=5",
    f"https://api.lofter.com/v2.0/searchPost.api?keyword={keyword}&page=0&limit=5",
    # Try with product=lofter-web
    f"https://api.lofter.com/v2.0/searchPost.api?keyword={keyword}&offset=0&limit=5&product=lofter-web",
    # Try env
    f"https://api.lofter.com/v2.0/searchPost.api?keyword={keyword}&offset=0&limit=5&env=prod",
]

for url in urls:
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"GET status={r.status_code} len={len(r.text)}")
        if r.status_code != 404:
            print(f"  Body: {r.text[:500]}")
        # Check if it's a 404 with a custom error page
        if r.status_code == 404:
            # The 1444 byte response from api.lofter.com might be meaningful
            if 'api.lofter.com' in url and len(r.text) < 2000:
                print(f"  Short 404 response: {r.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")
    print()

# Try web scraping from the explore/tag page
# The website seems to be a SPA that loads data via API
# Try if the lofter API has moved to a different domain
alt_domains = [
    f"https://lofter.com/api/v2.0/searchPost.api?keyword={keyword}&offset=0&limit=5",
    f"https://gw.lofter.com/v2.0/searchPost.api?keyword={keyword}&offset=0&limit=5",
    f"https://gateway.lofter.com/v2.0/searchPost.api?keyword={keyword}&offset=0&limit=5",
]

for url in alt_domains:
    try:
        r = requests.get(url, headers=headers, timeout=5)
        print(f"GET {url[:50]}... status={r.status_code} len={len(r.text)}")
        if r.status_code == 200:
            print(r.text[:1000])
    except Exception as e:
        print(f"Error: {e}")

