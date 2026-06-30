import urllib.request
import json
import re

# Let's try a more focused search
search_url = "https://api.github.com/search/repositories?q=lofter+scraper&sort=stars&per_page=10"
req = urllib.request.Request(search_url, headers={"Accept": "application/vnd.github.v3+json", "User-Agent": "Python"})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
        for item in data.get('items', []):
            print(f"{item['full_name']} ★{item.get('stargazers_count',0)} ({item.get('updated_at','')}) - {(item.get('description','') or '')[:80]}")
except Exception as e:
    print(f"Error: {e}")

# Also try searching code for the API URL directly
for q in ["lofter+searchPost.api", "lofter+v2.0+tagPosts", "api.lofter.com+crawler"]:
    search_url = f"https://api.github.com/search/code?q={q}&per_page=3"
    req = urllib.request.Request(search_url, headers={"Accept": "application/vnd.github.v3+json", "User-Agent": "Python"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            for item in data.get('items', []):
                print(f"  Code: {item['repository']['full_name']}/{item.get('path','')}")
    except Exception as e:
        pass

