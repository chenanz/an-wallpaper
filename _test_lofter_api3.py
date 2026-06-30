import requests
import json
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://www.lofter.com/",
}

# Fetch tag page and look for API calls / embedded data
url = "https://www.lofter.com/tag/原神同人?type=new"
r = requests.get(url, headers=headers, timeout=15)
print(f"Tag page status={r.status_code} len={len(r.text)}")

# Search for API URLs in page
api_patterns = re.findall(r'(https?://[a-zA-Z0-9._/-]+(?:api|gateway|search|post|tag)[a-zA-Z0-9./_-]*)', r.text)
print("API URLs found in page:", api_patterns[:20])

# Look for JSON data embedded in script tags
scripts = re.findall(r'<script[^>]*>(.*?)</script>', r.text, re.DOTALL)
print(f"\nFound {len(scripts)} script tags")
for i, s in enumerate(scripts):
    if len(s) > 100 and len(s) < 50000:
        # Check if it contains post data
        if any(k in s for k in ['postData', 'posts', 'blogList', 'photoLinks', 'img']):
            print(f"\nScript #{i} (len={len(s)}):")
            print(s[:1000])

# Also check /front/gateway pattern
for pattern in re.findall(r'["\'](/front/[a-zA-Z0-9/_.-]+)["\']', r.text):
    print("Front path:", pattern)

# Look for __NEXT_DATA__ or similar hydration
if '__NEXT_DATA__' in r.text:
    match = re.search(r'__NEXT_DATA__\s*=\s*({.*?})</script>', r.text, re.DOTALL)
    if match:
        print("Next.js data found!")
        print(match.group(1)[:2000])

# Look for window.__INITIAL_STATE__ or similar
for pat in [r'window\.__INITIAL_STATE__\s*=\s*({.*?});', r'window\.__DATA__\s*=\s*({.*?});', r'window\.pageData\s*=\s*({.*?});']:
    m = re.search(pat, r.text, re.DOTALL)
    if m:
        print(f"Found {pat}:", m.group(1)[:2000])

