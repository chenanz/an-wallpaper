import requests
import re
import urllib.parse

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://www.lofter.com/",
}

# Test scraping blog pages (these are public)
# Common lofter blog pattern: username.lofter.com or www.lofter.com/blog/username
test_urls = [
    # Individual post - these have a known pattern
    "https://www.lofter.com/lpost/1ce2e0e2_1ccbf81c2",
    # Try a public blog
    "https://genshinwall.lofter.com/",
    # Try a tag page with pagination
    "https://www.lofter.com/tag/原神同人?type=new&page=1",
]

for url in test_urls:
    try:
        r = requests.get(url, headers=headers, timeout=15)
        print(f"GET {url[:60]}... status={r.status_code} len={len(r.text)}")
        if r.status_code == 200 and len(r.text) > 1000:
            # Extract image URLs from the page
            img_urls = re.findall(r'(?:src|data-original|data-src)="(https?://[^"]+?(?:img\.lf127|img\.lofter|imglf\d|nos\.net|netease)[^"]*?)(?:\?[^"]*)?"', r.text)
            if not img_urls:
                img_urls = re.findall(r'(https?://[a-z0-9._/-]+(?:lf127|lofter|netease|126\.net)[a-z0-9._/:-]*\.(?:jpg|png|webp|gif)[^"\s)]*)', r.text)
            if img_urls:
                print(f"  Found {len(img_urls)} image URLs")
                for iu in img_urls[:5]:
                    print(f"  - {iu}")
            else:
                # Check what's in the page
                all_imgs = re.findall(r'(https?://[a-zA-Z0-9._:/-]+\.(?:jpg|png|webp|gif)[^"\s)]*)', r.text)
                print(f"  All image URLs: {len(all_imgs)}")
                for iu in all_imgs[:5]:
                    print(f"  - {iu}")
            
            # Check for data in window.__initialize_data__
            init_data = re.search(r'window\.__initialize_data__\s*=\s*({.*?});', r.text, re.DOTALL)
            if init_data:
                import json
                try:
                    j = json.loads(init_data.group(1))
                    print(f"  __initialize_data__ keys: {list(j.keys())[:10]}")
                except:
                    pass
    except Exception as e:
        print(f"  Error: {e}")
    print()

