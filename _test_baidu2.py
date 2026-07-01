import requests, random, re, hashlib, os
from io import BytesIO
from PIL import Image
from pathlib import Path

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
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

resp = requests.get(url, headers=headers, params=params, timeout=20)
html = resp.text
obj_urls = re.findall(r'"objURL"\s*:\s*"([^"]+)"', html)
all_urls = list(set(obj_urls))[:5]

for img_url in all_urls:
    img_url = img_url.replace("\\/", "/").replace("&", "&")
    print(f"\n--- Testing: {img_url[:100]}")
    
    # Strip @ params for cleaner URL
    clean_url = img_url.split("@")[0] if "@" in img_url else img_url
    print(f"  Clean URL: {clean_url[:100]}")
    
    try:
        r = requests.get(img_url, headers=headers, timeout=20)
        print(f"  Direct download: status={r.status_code}, size={len(r.content)}")
        
        if len(r.content) < 20 * 1024:
            print(f"  SKIP: too small ({len(r.content)} < 20480)")
            continue
            
        data = r.content
        img = Image.open(BytesIO(data))
        print(f"  PIL OK: mode={img.mode}, size={img.size}")
        
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        w, h = img.size
        if w > 1200:
            ratio = 1200 / w
            img = img.resize((1200, int(h * ratio)), Image.Resampling.LANCZOS)
            print(f"  Resized to: {img.size}")
        
        # Save
        save_path = "public/images/_test_save.jpg"
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        quality = 90
        out = BytesIO()
        while quality >= 55:
            out.seek(0)
            out.truncate()
            img.save(out, format="JPEG", quality=quality, optimize=True)
            if out.tell() <= 800 * 1024:
                break
            quality -= 5
        
        with open(save_path, "wb") as f:
            f.write(out.getvalue())
        print(f"  Saved OK: {out.tell()} bytes, quality={quality}")
        
    except Exception as e:
        print(f"  ERROR: {e}")
