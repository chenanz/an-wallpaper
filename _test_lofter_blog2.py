import requests
import json
import re
import urllib.parse

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "text/html",
}

# Try specific blog subdomains
# Format: username.lofter.com
test_blogs = [
    "https://genshinimpact.lofter.com/",
    "https://arknights.lofter.com/",
    # Or just try lofter.com/blogname
    "https://www.lofter.com/blog/genshinimpact",
]

for url in test_blogs:
    try:
        r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        print(f"GET {url[:50]}... status={r.status_code} len={len(r.text)}")
        if r.status_code == 200 and len(r.text) > 5000:
            imgs = re.findall(r'(https?://[a-z0-9._:/-]+\.(?:jpg|png|webp)[^"\s)]*)', r.text)
            print(f"  Images: {len(imgs)}")
            for i in imgs[:3]:
                print(f"    {i}")
    except Exception as e:
        print(f"  Error: {e}")

# Let's try a completely different strategy: use third-party Lofter aggregators
# Sites like lofter.fm, lofter.chafor.net (Lofter backup tools), etc.
alt_sites = [
    ("lofter.la backup tool", "https://lofter.la/"),
    ("Lofter posts search via baidu", "https://www.baidu.com/s?wd=site%3Alofter.com+%E5%8E%9F%E7%A5%9E%E5%90%8C%E4%BA%BA&rn=5"),
]

for name, url in alt_sites:
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"\n[{name}] status={r.status_code} len={len(r.text)}")
        if r.status_code == 200 and len(r.text) > 1000:
            # Search for Lofter image URLs
            imgs = re.findall(r'(https?://[a-z0-9._:/-]+(?:lf127|126\.net|lofter)[a-z0-9._/:-]*\.(?:jpg|png|webp)[^"\s)]*)', r.text)
            if imgs:
                print(f"  Lofter images: {len(imgs)}")
                for i in imgs[:5]:
                    print(f"    {i}")
    except Exception as e:
        print(f"  Error: {e}")

# Strategy 3: Use Baidu to find Lofter posts with images
# This is a reliable approach that doesn't require Lofter API access
import urllib.parse
baidu_url = f"https://www.baidu.com/s?{urllib.parse.urlencode({'wd': '原神同人 site:lofter.com', 'rn': '10'})}"
try:
    r = requests.get(baidu_url, headers=headers, timeout=15)
    print(f"\nBaidu search: status={r.status_code} len={len(r.text)}")
    if r.status_code == 200:
        # Extract lofter URLs from Baidu results
        lofter_urls = re.findall(r'(https?://[a-z0-9._-]+\.lofter\.com/[a-z0-9_/:-]*)', r.text)
        print(f"Lofter URLs in results: {list(set(lofter_urls))[:10]}")
except Exception as e:
    print(f"Error: {e}")

