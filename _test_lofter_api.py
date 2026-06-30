import requests
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://www.lofter.com/",
}

# Test several Lofter API endpoints
endpoints = [
    ("searchPost.api", "https://api.lofter.com/v2.0/searchPost.api?keyword=原神同人&page=1&limit=5"),
    ("searchPost New", "https://api.lofter.com/newapi/searchPost.api?keyword=原神同人&page=1&limit=5"),
    ("searchPost v1", "https://api.lofter.com/v1.0/searchPost.api?keyword=原神同人&page=1&limit=5"),
    ("lofter.com explore", "https://www.lofter.com/api/v2/searchPost?keyword=原神同人&page=1&limit=5"),
]

for name, url in endpoints:
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"[{name}] status={r.status_code} len={len(r.text)}")
        if r.status_code == 200 and len(r.text) > 10:
            print(r.text[:1500])
            print("---")
            # try parse json
            try:
                j = r.json()
                print("JSON keys:", list(j.keys()) if isinstance(j, dict) else type(j))
                if 'data' in j or 'posts' in j or 'result' in j:
                    print("Has data/posts/result!")
            except:
                print("Not JSON")
    except Exception as e:
        print(f"[{name}] Error: {e}")
    print()
