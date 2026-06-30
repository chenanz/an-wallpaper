import requests
import re
import urllib.parse
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
}

# Step 1: Use Baidu to find Lofter post URLs 
keywords = ["原神同人 site:lofter.com", "崩坏星穹铁道同人 site:lofter.com"]

for kw in keywords:
    params = urllib.parse.urlencode({"wd": kw, "rn": "10", "tn": "json"})
    url = f"https://www.baidu.com/s?{params}"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"Baidu JSON: status={r.status_code} len={len(r.text)}")
        if r.status_code == 200:
            # Try to parse as JSON
            try:
                j = json.loads(r.text)
                feed = j.get("feed", {})
                entries = feed.get("entry", [])
                print(f"  Entries: {len(entries)}")
                for entry in entries[:5]:
                    title = entry.get("title", "")
                    url = entry.get("url", "")
                    print(f"  - {title[:40]} | {url[:60]}")
            except:
                # Parse HTML results
                pass
    except Exception as e:
        print(f"Error: {e}")
    print()

# Try the HTML version of Baidu search
for kw in keywords:
    params = urllib.parse.urlencode({"wd": kw, "rn": "10"})
    url = f"https://www.baidu.com/s?{params}"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"Baidu HTML: status={r.status_code} len={len(r.text)}")
        # Extract Lofter URLs
        lofter_urls = re.findall(r'(https?://[a-z0-9._-]+\.lofter\.com/[a-z0-9_/:-]+)', r.text)
        lofter_urls = list(set(lofter_urls))
        print(f"  Lofter URLs: {len(lofter_urls)}")
        for u in lofter_urls[:10]:
            print(f"  - {u}")
        
        # Extract titles
        titles = re.findall(r'<h3[^>]*class="[^"]*t[^"]*"[^>]*>(.*?)</h3>', r.text, re.DOTALL)
        clean_titles = [re.sub(r'<[^>]+>', '', t).strip() for t in titles if 'lofter' in t.lower()]
        if clean_titles:
            print(f"  Titles with lofter: {clean_titles[:5]}")
    except Exception as e:
        print(f"  Error: {e}")
    print()

