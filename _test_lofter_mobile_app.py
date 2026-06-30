import requests
import json
import re
import urllib.parse

# Lofter mobile app uses a different API than the web
# The mobile app API URL format and headers are different
# Let's try with the exact mobile app headers

keyword = urllib.parse.quote("原神同人")

# Common Lofter mobile API patterns found in various sources
# The key insight: Lofter mobile app uses a specific auth header
# and the API endpoint has changed over time

mobile_headers = {
    "User-Agent": "LOFTER/7.8.4 (iPhone; iOS 17.5; Scale/3.00) AppleWebKit/605.1.15",
    "Accept": "application/json",
    "X-Lofter-Client": "ios",
    "X-Lofter-Version": "7.8.4",
    "X-Lofter-Os": "17.5",
    "Referer": "Lofter://",
}

# Try the search via the mobile API
apis = [
    # Search posts
    f"https://api.lofter.com/v2.0/searchPost.api?keyword={keyword}&page=0&limit=5",
    f"https://api.lofter.com/v2.0/searchPost.api?keyword={keyword}&offset=0&limit=5",
    # Tag posts
    f"https://api.lofter.com/v2.0/tagPosts.api?tagName={keyword}&offset=0&limit=5&type=new",
    f"https://api.lofter.com/v2.0/tagPosts.api?tag={keyword}&offset=0&limit=5",
    # New API format
    f"https://api.lofter.com/newapi/v2.0/searchPost.api?keyword={keyword}&offset=0&limit=5",
    f"https://api.lofter.com/newapi/searchPost.api?keyword={keyword}&offset=0&limit=5",
    # Home/explore
    f"https://api.lofter.com/v2.0/explorePost.api?offset=0&limit=5&tag={keyword}",
]

for url in apis:
    try:
        r = requests.get(url, headers=mobile_headers, timeout=10)
        print(f"GET status={r.status_code} len={len(r.text)}")
        if r.status_code == 200 and len(r.text) > 50:
            print(f"  Body: {r.text[:1500]}")
        elif r.status_code != 404:
            print(f"  Body: {r.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")
    print()

# Also try with Android app UA
android_headers = {
    "User-Agent": "LOFTER/7.8.4 (Android 14; Scale/2.75)",
    "Accept": "application/json",
    "X-Lofter-Client": "android",
}

for url in apis[:3]:
    try:
        r = requests.get(url, headers=android_headers, timeout=10)
        if r.status_code != 404:
            print(f"Android: status={r.status_code} len={len(r.text)}")
            if r.status_code == 200:
                print(r.text[:500])
    except:
        pass

