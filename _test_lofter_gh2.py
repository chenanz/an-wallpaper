import urllib.request
import json
import re

# Search GitHub API for lofter-related repos
search_url = "https://api.github.com/search/repositories?q=lofter+crawler&sort=updated&per_page=5"
req = urllib.request.Request(search_url, headers={"Accept": "application/vnd.github.v3+json", "User-Agent": "Python"})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
        for item in data.get('items', []):
            print(f"{item['full_name']} ({item.get('updated_at','')}) - {item.get('description','')[:80]}")
except Exception as e:
    print(f"Search error: {e}")

# Also search for lofter API
search_url2 = "https://api.github.com/search/repositories?q=lofter+api+python&sort=updated&per_page=5"
req2 = urllib.request.Request(search_url2, headers={"Accept": "application/vnd.github.v3+json", "User-Agent": "Python"})
try:
    with urllib.request.urlopen(req2, timeout=10) as resp2:
        data2 = json.loads(resp2.read())
        for item in data2.get('items', []):
            print(f"{item['full_name']} ({item.get('updated_at','')}) - {item.get('description','')[:80]}")
except Exception as e:
    print(f"Search error: {e}")

