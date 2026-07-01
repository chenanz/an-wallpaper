import requests, random, re, hashlib

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
]

headers = {
    "User-Agent": random.choice(USER_AGENTS),
    "Referer": "https://image.baidu.com/",
}
url = "https://image.baidu.com/search/flip"
params = {
    "tn": "baiduimage",
    "word": "原神 女角色 壁纸 高清",
    "rn": "30",
    "pn": "0",
    "ie": "utf-8",
    "oe": "utf-8",
    "z": "0",
    "height": "1280",
    "width": "720",
}

try:
    resp = requests.get(url, headers=headers, params=params, timeout=20)
    print(f"Status: {resp.status_code}")
    html = resp.text
    
    obj_urls = re.findall(r'"objURL"\s*:\s*"([^"]+)"', html)
    img_data_list = re.findall(r'data-imgurl="([^"]+)"', html)
    all_urls = list(set(obj_urls + img_data_list))
    
    print(f"objURLs: {len(obj_urls)}")
    print(f"data-imgurl: {len(img_data_list)}")
    print(f"Unique total: {len(all_urls)}")
    
    if all_urls:
        print(f"\nFirst 3 URLs:")
        for u in all_urls[:3]:
            print(f"  {u[:120]}...")
            # Try downloading
            try:
                r = requests.get(u.replace("\\/", "/"), headers=headers, timeout=15)
                print(f"  Download: status={r.status_code}, size={len(r.content)} bytes")
                ct = r.headers.get('content-type','')
                print(f"  Content-Type: {ct}")
            except Exception as e:
                print(f"  Download failed: {e}")
except Exception as e:
    print(f"Error: {e}")
