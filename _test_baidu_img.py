import requests
import re
import urllib.parse
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://image.baidu.com/",
}

# Try Baidu Image Search API
# The key API: https://image.baidu.com/search/acjson
keyword = "原神同人壁纸"
params = {
    "tn": "resultjson_com",
    "word": keyword,
    "pn": 0,  # offset
    "rn": 10,  # results per page
    "ipn": "dj",
    "fp": "result",
    "queryWord": keyword,
}

url = f"https://image.baidu.com/search/acjson?{urllib.parse.urlencode(params)}"
try:
    r = requests.get(url, headers=headers, timeout=15)
    print(f"Baidu Image API: status={r.status_code} len={len(r.text)}")
    if r.status_code == 200:
        j = r.json()
        data = j.get("data", [])
        print(f"Results: {len(data)}")
        for item in data[:5]:
            if isinstance(item, dict):
                print(f"  title: {item.get('fromPageTitleEnc', '')[:40]}")
                print(f"  thumb: {item.get('thumbURL', '')[:80]}")
                print(f"  full: {item.get('objURL', '')[:80]}")
                print(f"  width: {item.get('width', 0)} height: {item.get('height', 0)}")
                print(f"  fromURL: {item.get('fromURL', '')[:60]}")
                print()
except Exception as e:
    print(f"Error: {e}")

