"""Quick test - download one image from Safebooru"""
import requests, json, hashlib

url = "https://safebooru.org/index.php"
params = {
    "page": "dapi", "s": "post", "q": "index",
    "json": "1", "tags": "barefoot 1girl",
    "limit": "5", "pid": "0",
}
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

resp = requests.get(url, params=params, timeout=20, headers=headers)
print(f"Status: {resp.status_code}")
print(f"Content-Type: {resp.headers.get('content-type', '')}")
print(f"Content length: {len(resp.text)}")
try:
    posts = json.loads(resp.text)
    print(f"Posts: {len(posts)}")
    for p in posts[:2]:
        w, h = p.get("width", 0), p.get("height", 0)
        furl = p.get("file_url", "")
        surl = p.get("sample_url", "")
        print(f"  size: {w}x{h}, file_url: {furl[:80]}..., sample: {surl[:80]}")
        # Try downloading
        if furl:
            try:
                r = requests.get(furl, headers=headers, timeout=20)
                print(f"  Download status: {r.status_code}, size: {len(r.content)}")
            except Exception as e:
                print(f"  Download failed: {e}")
except Exception as e:
    print(f"Parse error: {e}")
    print(f"Raw: {resp.text[:500]}")
