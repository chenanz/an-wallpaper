import requests
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://www.lofter.com/",
}

# Test tag post listing endpoints (these are more likely to work than search)
endpoints = [
    # Tag post list - various formats
    ("tag posts v2", "GET", "https://api.lofter.com/v2.0/tagPosts.api?tagname=原神同人&offset=0&limit=5&type=new"),
    ("tag posts www", "GET", "https://www.lofter.com/api/v2/tagPosts.api?tagname=原神同人&offset=0&limit=5"),
    # Explore endpoint
    ("explore", "GET", "https://www.lofter.com/api/v2/explorePost.api?tag=原神同人&offset=0&limit=5"),
    # Search via www
    ("www search", "POST", "https://www.lofter.com/api/v2/searchPost.api"),
    # Try with cookie/token header
    ("tag posts with token", "GET", "https://api.lofter.com/v2.0/tagPosts.api?tagname=原神同人&offset=0&limit=5&type=new", {"X-Requested-With": "XMLHttpRequest"}),
    # Blog posts
    ("blogPosts", "GET", "https://api.lofter.com/v2.0/blogPosts.api?blogId=0&offset=0&limit=5"),
    # Post detail 
    ("post detail", "GET", "https://api.lofter.com/v2.0/postDetail.api?postId=0"),
]

for ep in endpoints:
    name, method, url = ep[0], ep[1], ep[2]
    extra_headers = ep[3] if len(ep) > 3 else {}
    h = {**headers, **extra_headers}
    try:
        if method == "POST":
            r = requests.post(url, headers=h, data={"keyword": "原神同人", "offset": 0, "limit": 5}, timeout=10)
        else:
            r = requests.get(url, headers=h, timeout=10)
        print(f"[{name}] {method} status={r.status_code} len={len(r.text)} ct={r.headers.get('content-type','')[:30]}")
        if r.status_code == 200 and 'json' in r.headers.get('content-type', ''):
            print(r.text[:1000])
            try:
                j = r.json()
                print("JSON keys:", list(j.keys())[:10] if isinstance(j, dict) else "non-dict")
            except:
                pass
        elif r.status_code != 404:
            print(r.text[:300])
    except Exception as e:
        print(f"[{name}] Error: {e}")
    print()

# Try fetching from explore.lofter.com
for url in [
    "https://www.lofter.com/explore/ajax/tag?tagname=原神同人&type=new&offset=0&limit=5",
    "https://www.lofter.com/api/tagPosts?tagname=原神同人&type=new&offset=0&limit=5",
]:
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"GET {url[:50]}... status={r.status_code} len={len(r.text)}")
        if r.status_code == 200 and len(r.text) > 50:
            print(r.text[:1500])
    except Exception as e:
        print(f"Error: {e}")
    print()

