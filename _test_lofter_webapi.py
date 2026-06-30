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
print(f"Cookies: {dict(session.cookies)}")

# Visit the discover page (different SPA, has its own JS bundle)
r = session.get("https://www.lofter.com/front/discover", timeout=15)
print(f"Discover: {r.status_code} len={len(r.text)}")

# Try scraping more webpack JS bundles
js_urls = re.findall(r'src="(https?://[^"]+\.js[^"]*)"', r.text)
print(f"Discover JS files: {js_urls}")

# Fetch the discover bundle JS
for js_url in js_urls:
    try:
        r2 = session.get(js_url, timeout=15)
        if r2.status_code == 200 and len(r2.text) > 1000:
            # Look for API endpoint definitions
            api_urls = re.findall(r'["\']([a-zA-Z0-9/_.-]*(?:search|post|tag|explore|discover|gate)[a-zA-Z0-9/_.-]*)["\']', r2.text, re.IGNORECASE)
            interesting = [u for u in api_urls if len(u) > 5 and '/' in u]
            if interesting:
                print(f"\n  Bundle {js_url[:50]}... APIs: {list(set(interesting))[:30]}")
            
            # Look for fetch/axios calls
            fetch_urls = re.findall(r'(?:fetch|axios|request|get|post)\s*\(\s*["\'''"]([^"\'\'']+)', r2.text)
            if fetch_urls:
                print(f"  Fetch URLs: {list(set(fetch_urls))[:10]}")
            
            # Look for URL construction patterns
            url_patterns = re.findall(r'["\']https?://[^"\']+["\']', r2.text)
            lofter_urls = [u.strip('"\'') for u in url_patterns if 'lofter' in u.lower() or '126.net' in u.lower() or 'lf127' in u.lower()]
            if lofter_urls:
                print(f"  Lofter/126 URLs: {list(set(lofter_urls))[:10]}")
    except:
        pass

# Let's try the actual tag page data flow
# When Lofter loads a tag page like /tag/原神同人, the SPA makes XHR calls
# Let's try to intercept by visiting the page and then hitting common API patterns

# Some known patterns from working with Lofter:
# - /api/v2/ is old and deprecated
# - They may use /front/gateway/ with specific parameters
# - They may require a valid session

# Let's look at what the SPA on /front/discover does more carefully
try:
    r3 = session.get("https://lofter.lf127.net/nos-upload-cli/1695691864965/bundle.js", timeout=15)
    if r3.status_code == 200:
        # This bundle is small enough to analyze
        content = r3.text
        # Search for API endpoint patterns more broadly
        all_urls = re.findall(r'["\']([^"\']{5,100})["\']', content)
        interesting = [u for u in all_urls if any(k in u for k in ['http', '/api', '/front', '/search', '/tag', '/post', 'fetch', 'ajax'])]
        print(f"\nDiscover bundle interesting strings: {list(set(interesting))[:30]}")
except Exception as e:
    print(f"Error: {e}")

# Try the ____lofter_token approach (CSRF-like token)
# Lofter uses NTESwebSI and __lfgw_sid cookies - maybe the API needs these
cookie_header = "; ".join(f"{k}={v}" for k, v in session.cookies.items())
api_headers = {
    "User-Agent": headers["User-Agent"],
    "Accept": "application/json",
    "Referer": "https://www.lofter.com/front/discover",
    "Origin": "https://www.lofter.com",
    "Cookie": cookie_header,
    "X-Requested-With": "XMLHttpRequest",
}

# Test with CSRF
csrf_urls = [
    f"https://www.lofter.com/front/api/v2/searchPost?keyword={urllib.parse.quote('原神同人')}&offset=0&limit=5",
    f"https://www.lofter.com/front/api/searchPost?keyword={urllib.parse.quote('原神同人')}&offset=0&limit=5",
    f"https://www.lofter.com/front/gateway/v2/searchPost?keyword={urllib.parse.quote('原神同人')}&offset=0&limit=5",
    f"https://www.lofter.com/api/searchPost?keyword={urllib.parse.quote('原神同人')}&offset=0&limit=5",
]

for url in csrf_urls:
    try:
        r = requests.get(url, headers=api_headers, timeout=10)
        if r.status_code != 404:
            print(f"\nNON-404: {url} status={r.status_code} len={len(r.text)}")
            print(r.text[:1000])
    except:
        pass

