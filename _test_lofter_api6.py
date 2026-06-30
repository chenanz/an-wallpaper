import requests
import json
import re

# Let's look at the actual lofter tag page more carefully
# and try to scrape via the web page itself

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "text/html",
    "Referer": "https://www.lofter.com/",
}

# Use the tag page that returned 200
r = requests.get("https://www.lofter.com/tag/原神同人?type=new", headers=headers, timeout=15)
print(f"Tag page: status={r.status_code} len={len(r.text)}")

# Find ALL script src and inline scripts
all_scripts = re.findall(r'<script[^>]*(?:src="([^"]+)")?[^>]*>(.*?)</script>', r.text, re.DOTALL)
print(f"Total {len(all_scripts)} scripts")
for src, body in all_scripts:
    if src:
        print(f"  External: {src}")
    elif len(body) > 50:
        print(f"  Inline ({len(body)} chars): {body[:200]}")
        # Check for state/data
        for kw in ['__INITIAL', '__NEXT', 'pageData', 'postData', 'INITIAL_DATA', 'fetchData']:
            if kw in body:
                print(f"  >>> Contains {kw}!")

# Find link rel=preload/prefetch
links = re.findall(r'<link[^>]+href="([^"]+)"', r.text)
print(f"\nLinks ({len(links)}):")
for l in links[:15]:
    print(f"  {l}")

# Look for XHR/fetch patterns in JS
for src, body in all_scripts:
    if src and 'dll' in src:
        try:
            r2 = requests.get(src, headers=headers, timeout=15)
            api_matches = re.findall(r'["\'](/[a-zA-Z0-9/_.-]{5,80})["\']', r2.text)
            interesting = [a for a in api_matches if any(k in a.lower() for k in ['api', 'search', 'post', 'tag', 'gate', 'front', 'blog'])]
            if interesting:
                print(f"\n  Interesting paths in {src[:50]}: {list(set(interesting))[:30]}")
        except:
            pass

