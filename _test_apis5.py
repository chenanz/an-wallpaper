"""Test image download from Zerochan and Anime-Pictures"""
import requests
import json

# Test Zerochan image download
print("=== Zerochan image download ===")
try:
    r = requests.get('https://www.zerochan.net/Feet,Anime?json=1&p=1', timeout=20, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': 'application/json',
        'Referer': 'https://www.zerochan.net/',
    })
    data = json.loads(r.text)
    items = data.get('items', [])
    print(f"Got {len(items)} items")
    
    # Try to download full image from Zerochan
    if items:
        item = items[0]
        item_id = item.get('id')
        md5 = item.get('md5', '')
        print(f"  Item {item_id}: md5={md5}, w={item.get('width')}, h={item.get('height')}")
        
        # Try different image URL formats
        test_urls = [
            f"https://static.zerochan.net/Full/{md5}.jpg",
            f"https://static.zerochan.net/{md5}.jpg",
            f"https://s1.zerochan.net/{md5}.jpg",
            # The thumbnail we know works
            item.get('thumbnail', ''),
        ]
        for url in test_urls:
            if not url:
                continue
            try:
                r2 = requests.head(url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                    'Referer': 'https://www.zerochan.net/',
                })
                print(f"  {url[:80]}... -> {r2.status_code} type={r2.headers.get('content-type','')} len={r2.headers.get('content-length','')}")
            except Exception as e:
                print(f"  {url[:80]}... -> FAIL {e}")
        
        # Try the full page URL to get actual image link
        page_url = f"https://www.zerochan.net/{item_id}"
        print(f"\n  Trying page: {page_url}")
        try:
            r3 = requests.get(page_url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            })
            import re
            # Find full res image URLs
            full_urls = re.findall(r'https://static\.zerochan\.net/[^\s"]+\.full\.[^\s"]+', r3.text)
            png_urls = re.findall(r'https://static\.zerochan\.net/[^\s"]+\.png', r3.text)
            jpg_urls = re.findall(r'href="(https://static\.zerochan\.net/[^"]+)"', r3.text)
            print(f"  Found .full urls: {full_urls[:3]}")
            print(f"  Found png urls: {png_urls[:3]}")
            print(f"  Found href static urls: {jpg_urls[:5]}")
            
            if jpg_urls:
                for u in jpg_urls[:2]:
                    try:
                        r4 = requests.head(u, timeout=10, headers={
                            'User-Agent': 'Mozilla/5.0',
                            'Referer': 'https://www.zerochan.net/',
                        })
                        print(f"    {u[:80]}... -> {r4.status_code} len={r4.headers.get('content-length','')}")
                    except Exception as e:
                        print(f"    FAIL {e}")
        except Exception as e:
            print(f"  Page fetch FAIL: {e}")
except Exception as e:
    print(f"Zerochan FAIL: {e}")

# Test Anime-Pictures download with different approaches
print("\n=== Anime-Pictures download ===")
try:
    r = requests.get('https://api.anime-pictures.net/api/v3/posts?search_tag=feet&page=0&limit=3', timeout=20, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    })
    data = json.loads(r.text)
    posts = data.get('posts', [])
    if posts:
        p = posts[0]
        pid = p.get('id')
        md5 = p.get('md5', '')
        ext = p.get('extension', 'jpg')
        print(f"  Post {pid}: md5={md5}, ext={ext}, w={p.get('width')}, h={p.get('height')}")
        
        # Try various URL patterns for anime-pictures
        test_urls = [
            f"https://api.anime-pictures.net/api/v3/download/original/{pid}",
            f"https://api.anime-pictures.net/api/v3/download/big/{pid}",
            f"https://api.anime-pictures.net/api/v3/download/medium/{pid}",
            f"https://api.anime-pictures.net/api/v3/download/small/{pid}",
        ]
        for url in test_urls:
            try:
                r2 = requests.head(url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                    'Referer': 'https://anime-pictures.net/',
                })
                print(f"  {url.split('net/')[-1][:50]} -> {r2.status_code} type={r2.headers.get('content-type','')} len={r2.headers.get('content-length','')}")
            except Exception as e:
                print(f"  {url.split('net/')[-1][:50]} -> FAIL {e}")
except Exception as e:
    print(f"Anime-Pictures download FAIL: {e}")

# Test Safebooru download speed and size
print("\n=== Safebooru download speed test ===")
import time
try:
    r = requests.get('https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags=foot_focus+1girl&limit=3', 
                    timeout=15, headers={'User-Agent':'Mozilla/5.0'})
    posts = json.loads(r.text)
    if posts:
        p = posts[0]
        file_url = p.get('file_url', '')
        sample_url = p.get('sample_url', '')
        print(f"  w={p.get('width')} h={p.get('height')}")
        print(f"  file_url: {file_url}")
        
        if file_url:
            start = time.time()
            r2 = requests.get(file_url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0',
                'Referer': 'https://safebooru.org/',
            })
            elapsed = time.time() - start
            print(f"  Downloaded: {r2.status_code} size={len(r2.content)} bytes in {elapsed:.1f}s")
except Exception as e:
    print(f"Safebooru speed test FAIL: {e}")
