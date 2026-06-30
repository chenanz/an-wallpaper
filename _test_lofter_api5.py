import requests
import json

# Try the Lofter search page and look at what the JS app calls
# When you visit https://www.lofter.com/search?q=xxx it makes XHR calls

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.lofter.com/",
    "Origin": "https://www.lofter.com",
}

# Try lofter.com/front/gateway - this is the actual endpoint used by the web app
gateway_urls = [
    # These are common gateway patterns for lofter SPA
    ("POST front/gateway/searchPost", "https://www.lofter.com/front/gateway/searchPost", {"keyword": "原神同人", "page": 1, "limit": 5}),
    ("POST front/gateway/searchBlogPost", "https://www.lofter.com/front/gateway/searchBlogPost", {"keyword": "原神同人", "page": 1, "limit": 5}),
    ("POST front/gateway/search", "https://www.lofter.com/front/gateway/search", {"keyword": "原神同人", "page": 1, "limit": 5, "searchType": 0}),
    # Note: Lofter also uses json content type for POST
    ("POST JSON front/gateway/searchPost", "https://www.lofter.com/front/gateway/searchPost", None),
    # Also common: /newapi/
    ("GET newapi/searchPost", "https://api.lofter.com/newapi/searchPost.api", None),
]

for name, url, data in gateway_urls:
    try:
        if name.startswith("POST JSON"):
            r = requests.post(url, headers={**headers, "Content-Type": "application/json"}, 
                              json={"keyword": "原神同人", "page": 1, "limit": 5}, timeout=10)
        elif name.startswith("POST"):
            if data:
                r = requests.post(url, headers=headers, data=data, timeout=10)
            else:
                r = requests.post(url, headers=headers, timeout=10)
        else:
            params = {"keyword": "原神同人", "page": 1, "limit": 5}
            r = requests.get(url, headers=headers, params=params, timeout=10)
        
        print(f"[{name}] status={r.status_code} len={len(r.text)}")
        ct = r.headers.get('content-type', '')
        print(f"  Content-Type: {ct}")
        if r.status_code == 200 and len(r.text) > 50:
            print(f"  Body: {r.text[:1500]}")
            try:
                j = r.json()
                print(f"  JSON keys: {list(j.keys())[:10]}")
            except:
                pass
        elif r.status_code != 404:
            print(f"  Body: {r.text[:500]}")
    except Exception as e:
        print(f"[{name}] Error: {e}")
    print()

# Let's also try to fetch the main JS bundle to find API endpoints
js_urls = [
    "https://lofter.lf127.net/webpack/lofter-client-account/src/applications/login/pc.6e0bab7d780c9d7ce5cf.css",
]
# Actually, let's find the main JS file from the page
r = requests.get("https://www.lofter.com/tag/原神同人?type=new", headers=headers, timeout=15)
import re
js_files = re.findall(r'src="(https?://[^"]+\.js[^"]*)"', r.text)
print(f"\nFound {len(js_files)} JS files")
for jf in js_files[:5]:
    print(f"  {jf}")
    try:
        r2 = requests.get(jf, headers=headers, timeout=15)
        # Search for API endpoints in JS
        apis = re.findall(r'["\'](/(?:api|front|newapi|v[12])[a-zA-Z0-9/_.-]*(?:search|post|tag)[a-zA-Z0-9/_.-]*)["\']', r2.text)
        if apis:
            print(f"    API paths: {apis[:20]}")
        # Also look for full URLs
        full_apis = re.findall(r'["\'](https?://[a-z.]*lofter[a-z.]*(?:/[^"\'){1,80})["\']', r2.text)
        lofter_apis = [a for a in full_apis if 'api' in a.lower() or 'gateway' in a.lower() or 'search' in a.lower()]
        if lofter_apis:
            print(f"    Full API URLs: {list(set(lofter_apis))[:10]}")
    except:
        pass

