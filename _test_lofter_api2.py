import requests
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://www.lofter.com/",
    "Origin": "https://www.lofter.com",
}

# Test various endpoints
tests = [
    # Found in various lofter scraper repos
    ("v2.0 searchBlog", "GET", "https://api.lofter.com/v2.0/searchBlog.api?keyword=原神同人&page=1&limit=5"),
    ("v2 search", "POST", "https://api.lofter.com/v2.0/searchPost.api"),
    ("v2 explore", "GET", "https://www.lofter.com/explore/ajax/search?keyword=原神同人&page=1&limit=5"),
    ("v2 tag", "GET", "https://api.lofter.com/v2.0/tagPosts.api?tag=原神同人&limit=5"),
    ("lofter tag", "GET", "https://www.lofter.com/tag/原神同人?type=new&limit=5"),
    # POST form
    ("searchPost POST form", "POST", "https://api.lofter.com/v2.0/searchPost.api"),
    # front gateway  
    ("front gateway search", "GET", "https://www.lofter.com/front/gateway/searchPost?keyword=原神同人&page=1&limit=5"),
    ("front gateway2", "POST", "https://www.lofter.com/front/gateway/searchPost"),
]

for name, method, url in tests:
    try:
        if method == "POST":
            r = requests.post(url, headers=headers, data={"keyword": "原神同人", "page": 1, "limit": 5}, timeout=10)
        else:
            r = requests.get(url, headers=headers, timeout=10)
        print(f"[{name}] method={method} status={r.status_code} len={len(r.text)}")
        if r.status_code == 200 and len(r.text) > 50:
            txt = r.text[:2000]
            print(txt)
            try:
                j = r.json()
                print("JSON parsed, keys:", list(j.keys()) if isinstance(j, dict) else "list")
            except:
                pass
        elif r.status_code != 404:
            print(r.text[:500])
    except Exception as e:
        print(f"[{name}] Error: {e}")
    print("---")
