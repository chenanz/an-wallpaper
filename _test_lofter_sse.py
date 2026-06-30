import requests
import json
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
}

# The tag pages return 200 but same SPA template (9338 bytes)
# The actual content must come from JS loading
# Let's try the SSE/EventSource pattern and also check for /front/gateway with POST

# Go to the tag page
url = "https://www.lofter.com/tag/原神同人?type=new"
r = requests.get(url, headers=headers, timeout=15)
print(f"Tag page: {r.status_code} len={len(r.text)}")

# The SPA on this page loads data from somewhere
# Let's check the origin of the SPA JS to find the real API
# The login app JS is: lofter.lf127.net/webpack/lofter-client-account/...
# This is just the LOGIN page! The tag/search page must be a DIFFERENT SPA

# Let's try:
# 1. The tag application might be served from a different URL
# 2. The API might be at a completely different domain now

# Try fetching content with different Accept headers 
# (server-side rendering might work for search engines)
bot_headers = {
    "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Accept": "text/html",
}

r = requests.get(url, headers=bot_headers, timeout=15)
print(f"\nGooglebot: {r.status_code} len={len(r.text)}")
if len(r.text) > 10000:
    # This might be a server-rendered version!
    all_imgs = re.findall(r'(https?://[a-zA-Z0-9._:/-]+\.(?:jpg|png|webp|gif)[^"\s)]*)', r.text)
    print(f"  Images: {len(all_imgs)}")
    for iu in all_imgs[:10]:
        print(f"  - {iu}")

# Try another crawler UA
bing_headers = {
    "User-Agent": "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
}
r = requests.get(url, headers=bing_headers, timeout=15)
print(f"\nBingbot: {r.status_code} len={len(r.text)}")
if len(r.text) > 10000:
    all_imgs = re.findall(r'(https?://[a-zA-Z0-9._:/-]+\.(?:jpg|png|webp|gif)[^"\s)]*)', r.text)
    print(f"  Images: {len(all_imgs)}")

# Maybe Lofter uses SSR for SEO - try a specific post URL format
for fmt in [
    "https://www.lofter.com/lpost/{blog_id}_{post_id}",
    "https://username.lofter.com/post/{post_id}",
]:
    # Just test if the format is valid
    pass

# Let's also check if there's a mobile API that still works
mobile_headers = {
    "User-Agent": "LOFTER/7.6.2 (iPhone; iOS 16.0; Scale/3.00)",
    "Accept": "application/json",
}

# Mobile app API endpoints
mobile_apis = [
    "https://api.lofter.com/v2.0/searchPost.api?keyword=原神同人&offset=0&limit=5",
    "https://api.lofter.com/v2.0/tagPosts.api?tagName=原神同人&offset=0&limit=5&type=new",
    "https://api.lofter.com/2.0/searchPost.api?keyword=原神同人&offset=0&limit=5",
]

for url in mobile_apis:
    try:
        r = requests.get(url, headers=mobile_headers, timeout=10)
        print(f"\nMobile GET {url[:50]}... status={r.status_code} len={len(r.text)}")
        if r.status_code != 404:
            print(r.text[:500])
    except Exception as e:
        print(f"Error: {e}")

