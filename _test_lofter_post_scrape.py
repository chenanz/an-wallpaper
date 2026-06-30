import requests
import json
import re
import urllib.parse

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

# Test scraping individual Lofter blog posts
post_urls = [
    "https://niubenben95905.lofter.com/post/319cfd71_2b546d249",
    "https://nuonuo573.lofter.com/",
    "https://synapse123.lofter.com/",
]

for url in post_urls:
    try:
        r = requests.get(url, headers=headers, timeout=15)
        print(f"GET {url[:55]}... status={r.status_code} len={len(r.text)}")
        
        if r.status_code == 200 and len(r.text) > 5000:
            # Extract all image URLs (Lofter images are typically on imglf*.lf127.net or similar CDN)
            all_imgs = re.findall(r'(https?://[a-z0-9._:/-]+\.(?:jpg|png|jpeg|webp|gif)(?:\?[^\s"\')]*)?)', r.text, re.IGNORECASE)
            print(f"  All image URLs: {len(all_imgs)}")
            for img in all_imgs[:8]:
                print(f"    {img}")
            
            # Check for JSON data in the page
            json_blocks = re.findall(r'window\.__initialize_data__\s*=\s*({.*?});', r.text, re.DOTALL)
            if json_blocks:
                print(f"  Found __initialize_data__ ({len(json_blocks[0])} chars)")
            
            # Check for post data in the HTML
            # Lofter embeds post data for SSR sometimes
            post_data = re.findall(r'"photoUrl"\s*:\s*"(https?://[^"]+)"', r.text)
            if post_data:
                print(f"  Photo URLs from JSON: {post_data[:5]}")
            
            # Look for og:image meta tags (often used for previews)
            og_images = re.findall(r'<meta\s+(?:property|name)="og:image"\s+content="([^"]+)"', r.text)
            if og_images:
                print(f"  OG images: {og_images}")
            
            # Look for img tags
            img_tags = re.findall(r'<img[^>]+src="([^"]+)"', r.text)
            if img_tags:
                print(f"  <img> src tags: {len(img_tags)}")
                for img in img_tags[:5]:
                    print(f"    {img}")
                    
        elif r.status_code == 200 and len(r.text) < 10000:
            # SPA template - try with JS rendering
            print(f"  Likely SPA template ({len(r.text)} chars)")
            # Check if there are any inline script data
            scripts = re.findall(r'<script[^>]*>(.*?)</script>', r.text, re.DOTALL)
            for s in scripts:
                if 'img' in s.lower() or 'photo' in s.lower():
                    print(f"  Script with img/photo data: {s[:500]}")
    except Exception as e:
        print(f"  Error: {e}")
    print()

