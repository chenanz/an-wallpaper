import requests
import json
import re

# First, visit the main page and capture any cookies
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
})

# Visit main lofter page
r = session.get("https://www.lofter.com/", timeout=15)
print(f"Main page: {r.status_code}, cookies: {dict(session.cookies)}")

# Visit search page
r = session.get("https://www.lofter.com/search?q=原神同人", timeout=15)
print(f"Search page: {r.status_code}, len={len(r.text)}")

# Get cookie values
cookies_str = "; ".join(f"{k}={v}" for k, v in session.cookies.items())
print(f"Cookies: {cookies_str[:200]}")

# Now try API with these cookies
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.lofter.com/search?q=原神同人",
    "Origin": "https://www.lofter.com",
    "Cookie": cookies_str,
}

# Try the endpoints that api.lofter.com returns 404 for - maybe needs auth headers
# Common网易系API patterns
apis_to_try = [
    # 网易系 common pattern
    ("v2 searchPost with clienttype", "GET", "https://api.lofter.com/v2.0/searchPost.api?keyword=原神同人&offset=0&limit=5&clienttype=web"),
    # Front gateway - this is the 网易 pattern
    ("POST searchPost JSON", "POST", "https://www.lofter.com/front/gateway/searchPost.api"),
    ("POST searchPost2", "POST", "https://www.lofter.com/front/api/searchPost.api"),
    # With form data
    ("POST searchPost formdata", "POST_FORM", "https://www.lofter.com/front/gateway/searchPost.api"),
]

for name, method, url in apis_to_try:
    try:
        if method == "POST":
            r = requests.post(url, headers={**headers, "Content-Type": "application/json"}, 
                              json={"keyword": "原神同人", "offset": 0, "limit": 5}, timeout=10)
        elif method == "POST_FORM":
            r = requests.post(url, headers=headers, 
                              data={"keyword": "原神同人", "offset": 0, "limit": 5}, timeout=10)
        else:
            r = requests.get(url, headers=headers, timeout=10)
        print(f"\n[{name}] {method} status={r.status_code} len={len(r.text)} ct={r.headers.get('content-type','')[:40]}")
        if r.status_code == 200 and len(r.text) > 2:
            print(r.text[:2000])
            try:
                j = r.json()
                print(f"JSON! keys={list(j.keys())[:10]}")
            except:
                pass
        elif r.status_code != 404:
            print(r.text[:500])
    except Exception as e:
        print(f"Error: {e}")

