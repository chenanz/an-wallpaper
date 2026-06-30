import requests
import json
import re
import urllib.parse

session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
}
session.headers.update(headers)

# Visit lofter.com first to get cookies
r = session.get("https://www.lofter.com/", timeout=15)
print(f"Homepage: {r.status_code}")
print(f"Cookies: {list(session.cookies.keys())}")

# Get discover bundle JS
r = session.get("https://lofter.lf127.net/nos-upload-cli/1695691864965/bundle.js", timeout=15)
if r.status_code == 200:
    content = r.text
    all_strings = re.findall(r'["\']([^"\']{5,150})["\']', content)
    interesting = [u for u in all_strings if any(k in u for k in ['http', '/api', '/front', '/search', '/tag', '/post', 'fetch', 'ajax', 'gateway', 'lofter'])]
    print(f"Discover bundle interesting: {list(set(interesting))[:30]}")

# Let's try a completely different approach: use the web scraping method
# Visit tag page and try to find the data that's rendered
# The tag page at https://www.lofter.com/tag/XXX returns a login redirect
# Maybe we need to use the /front/ routes

# Actually, let's try what a web browser does when searching on lofter.com
# by looking at the JS bundles in the main SPA
# Visit the main page and find ALL JS bundles including lazy-loaded ones
r = session.get("https://www.lofter.com/front/discover", timeout=15)
js_urls = re.findall(r'(?:src|href)="(https?://[^"]+\.js[^"]*)"', r.text)
print(f"\nDiscover JS: {js_urls}")

# Also check for prefetch/preload links
preload = re.findall(r'rel="preload"[^>]+href="([^"]+)"', r.text)
prefetch = re.findall(r'rel="prefetch"[^>]+href="([^"]+)"', r.text)
print(f"Preload: {preload}")
print(f"Prefetch: {prefetch}")

# Let's try the most aggressive approach: use selenium-like manual analysis
# Actually, let me just try scraping the HTML directly from the profile/blog pages
# Some lofter profiles are publicly accessible

# Test: get a specific post page
test_urls = [
    "https://www.lofter.com/front/api/post/detail?postId=test",
    "https://www.lofter.com/front/api/tag/posts?tag=原神同人&offset=0&limit=5",
    "https://www.lofter.com/front/api/v1/search?keyword=原神同人&offset=0&limit=5",
    "https://www.lofter.com/api/lofter-tag/posts?tagName=原神同人&offset=0&limit=5",
]

api_headers = {
    **headers,
    "Referer": "https://www.lofter.com/front/discover",
    "Origin": "https://www.lofter.com",
    "X-Requested-With": "XMLHttpRequest",
}

for url in test_urls:
    try:
        r = requests.get(url, headers=api_headers, timeout=10)
        print(f"\nGET status={r.status_code} len={len(r.text)} ct={r.headers.get('content-type','')[:40]}")
        if r.status_code == 200 and 'json' in r.headers.get('content-type', ''):
            print(r.text[:2000])
            try:
                j = r.json()
                print(f"JSON keys: {list(j.keys())[:10]}")
            except:
                pass
    except Exception as e:
        print(f"Error: {e}")

