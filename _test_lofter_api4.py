import requests
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://www.lofter.com/",
    "Accept": "application/json",
}

# Try Lofter mobile API endpoints found in various scrapers
endpoints = [
    # Mobile API (often different from web)
    "https://api.lofter.com/v2.0/searchPost.api?keyword=原神同人&page=0&limit=5&type=new",
    "https://api.lofter.com/v2.0/searchPost.api?keyword=原神同人&offset=0&limit=5",
    # Legacy endpoints
    "https://www.lofter.com/api/v2/searchPost?keyword=原神同人&page=0&limit=5",
    # Alloy rendering service
    "https://www.lofter.com/alloy/renderPost.api?keyword=原神同人&page=0&limit=5",
    # Perhaps POST with different content type
    "https://api.lofter.com/v2.0/searchPost.api",
    # v1 endpoints
    "https://api.lofter.com/v1/lofter.searchPost.api?keyword=原神同人&page=0&limit=5",
    # New frontend gateway
    "https://www.lofter.com/front/api/searchPost?keyword=原神同人&page=0&limit=5",
    # Specific blog post fetching
    "https://api.lofter.com/v2.0/tagPosts.api?tagname=原神同人&offset=0&limit=5",
    "https://api.lofter.com/v2.0/tagPosts.api?tag=原神同人&offset=0&limit=5",
    # Try with different param names
    "https://api.lofter.com/v2.0/searchPost.api?q=原神同人&start=0&num=5",
    # Mobile site
    "https://m.lofter.com/search?keyword=原神同人",
    # Newapi
    "https://api.lofter.com/newapi/v2.0/searchPost.api?keyword=原神同人&page=0&limit=5",
]

for url in endpoints:
    try:
        if "searchPost.api" in url and not "?" in url:
            # POST
            r = requests.post(url, headers=headers, data={"keyword": "原神同人", "page": 0, "limit": 5}, timeout=10)
            print(f"POST {url[:60]}... status={r.status_code} len={len(r.text)}")
        else:
            r = requests.get(url, headers=headers, timeout=10)
            print(f"GET  {url[:80]}... status={r.status_code} len={len(r.text)}")
        
        if r.status_code == 200 and len(r.text) > 50 and len(r.text) < 10000:
            print(r.text[:500])
            try:
                j = r.json()
                print("JSON! keys:", list(j.keys())[:10] if isinstance(j, dict) else "list/arr")
            except:
                pass
        elif r.status_code == 200 and len(r.text) > 10000:
            print("Large page, first 300:", r.text[:300])
    except Exception as e:
        print(f"Error: {e}")
    print()

# Also try without the .api suffix
for suffix in ["searchPost", "searchBlog", "tagPosts"]:
    url = f"https://api.lofter.com/v2.0/{suffix}?keyword=原神同人&page=0&limit=5"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"GET  {url[:80]}... status={r.status_code} len={len(r.text)}")
        if r.status_code == 200 and len(r.text) > 50:
            print(r.text[:500])
    except Exception as e:
        print(f"Error: {e}")
    print()

