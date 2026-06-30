import requests
from PIL import Image
from io import BytesIO
import hashlib

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
}

# Test downloading one of the images found
test_urls = [
    "https://www.acgtubao.com/wp-content/uploads/2021/03/87277970_p0-698x1024.jpg",
    "https://c-ssl.dtstatic.com/uploads/blog/202310/20/3BS4Q97lizVywql.thumb.1000_0",
]

for url in test_urls[:1]:
    try:
        r = requests.get(url, headers=headers, timeout=30)
        print(f"Download: status={r.status_code} len={len(r.content)}")
        
        if r.status_code == 200 and len(r.content) > 20*1024:
            img = Image.open(BytesIO(r.content))
            print(f"  Size: {img.size}")
            print(f"  Mode: {img.mode}")
            
            # Test compression
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            w, h = img.size
            max_w = 1200
            if w > max_w:
                ratio = max_w / w
                img = img.resize((max_w, int(h * ratio)), Image.Resampling.LANCZOS)
                print(f"  Resized to: {img.size}")
            
            # Compress
            quality = 90
            out = BytesIO()
            while quality >= 60:
                out.seek(0)
                out.truncate()
                img.save(out, format="JPEG", quality=quality, optimize=True)
                size_kb = out.tell() / 1024
                if out.tell() <= 800 * 1024:
                    break
                quality -= 5
            
            print(f"  Final: quality={quality} size={size_kb:.0f}KB")
            
            # MD5 hash
            md5 = hashlib.md5(str(url).encode()).hexdigest()[:8]
            print(f"  MD5: {md5}")
    except Exception as e:
        print(f"  Error: {e}")

