import requests
import re
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Get the discover/explore page which should have post data
pages = [
    "https://www.lofter.com/front/discover",
    "https://www.lofter.com/explore",
    "https://www.lofter.com/discover",
]

for url in pages:
    try:
        r = requests.get(url, headers=headers, timeout=15)
        print(f"GET {url}: status={r.status_code} len={len(r.text)}")
        if r.status_code == 200:
            # Look for JS bundles
            js_urls = re.findall(r'src="(https?://[^"]+\.js[^"]*)"', r.text)
            print(f"  JS: {js_urls[:5]}")
            # Check for inline data
            inline_data = re.findall(r'window\.__initialize_data__\s*=\s*({.*?});', r.text, re.DOTALL)
            if inline_data:
                print(f"  Found __initialize_data__ ({len(inline_data[0])} chars)")
                try:
                    j = json.loads(inline_data[0])
                    print(f"  Keys: {list(j.keys())[:10]}")
                except:
                    pass
    except Exception as e:
        print(f"  Error: {e}")
    print()

# The tag page had __initialize_data__ with loginPageData
# Let's try visiting the tag page more thoroughly and see if we can get post data
# Try fetching a specific post URL
post_urls = [
    "https://www.lofter.com/tag/原神同人?type=new",
    "https://www.lofter.com/tag/崩坏星穹铁道同人?type=new",
]

for url in post_urls:
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            # Extract all window.* = data patterns
            data_patterns = re.findall(r'window\.(\w+)\s*=\s*({.*?});', r.text, re.DOTALL)
            for name, data in data_patterns:
                if len(data) > 50:
                    print(f"  window.{name} = ({len(data)} chars)")
                    if len(data) < 5000:
                        print(f"    {data[:2000]}")
    except Exception as e:
        print(f"  Error: {e}")

