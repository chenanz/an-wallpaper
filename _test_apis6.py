"""Test Zerochan full image download and Anime-Pictures CDN"""
import requests
import json

# Test Zerochan full image download
print("=== Zerochan full image download ===")
try:
    # Test the full URL format we found
    test_url = "https://static.zerochan.net/Ellen.Joe.full.4226141.jpg"
    r = requests.head(test_url, timeout=15, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Referer': 'https://www.zerochan.net/',
    })
    print(f"Full URL: {r.status_code} type={r.headers.get('content-type','')} len={r.headers.get('content-length','')}")
    
    # Try downloading the actual image
    if r.status_code == 200:
        r2 = requests.get(test_url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Referer': 'https://www.zerochan.net/',
        })
        print(f"Downloaded: {len(r2.content)} bytes")
    
    # Now let's get multiple items with full image URLs
    # Get more tags
    tags_to_test = ['Feet,Anime', 'Stockings,Anime', 'Barefoot,Anime', 'Pantyhose,Anime', 'Socks,Anime']
    for tag in tags_to_test:
        try:
            r = requests.get(f'https://www.zerochan.net/{tag}?json=1&p=1', timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Referer': 'https://www.zerochan.net/',
                'Accept': 'application/json',
            })
            if r.status_code == 200:
                data = json.loads(r.text)
                items = data.get('items', [])
                total = data.get('total', 0)
                print(f"  {tag}: {total} total, {len(items)} on this page")
                if items:
                    item = items[0]
                    # Get full img URL from page
                    iid = item.get('id')
                    page = requests.get(f'https://www.zerochan.net/{iid}', timeout=15, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                    })
                    import re
                    full_match = re.search(r'https://static\.zerochan\.net/[^"]+\.full\.\d+\.jpg', page.text)
                    if full_match:
                        print(f"    Full img URL: {full_match.group()[:80]}...")
                    char_tag = item.get('tag', 'Unknown')
                    print(f"    Character: {char_tag}, w={item.get('width')}, h={item.get('height')}")
        except Exception as e:
            print(f"  {tag}: FAIL {e}")
except Exception as e:
    print(f"Zerochan test FAIL: {e}")

# Test Anime-Pictures with CDN variations
print("\n=== Anime-Pictures CDN test ===")
try:
    r = requests.get('https://api.anime-pictures.net/api/v3/posts?search_tag=feet&page=0&limit=5', timeout=20, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': 'application/json',
        'Origin': 'https://anime-pictures.net',
        'Referer': 'https://anime-pictures.net/',
    })
    data = json.loads(r.text)
    posts = data.get('posts', [])
    if posts:
        # Full post details
        p = posts[0]
        pid = p.get('id')
        # Try getting post details
        r2 = requests.get(f'https://api.anime-pictures.net/api/v3/posts/{pid}', timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Origin': 'https://anime-pictures.net',
            'Referer': 'https://anime-pictures.net/',
        })
        print(f"  Post detail API: {r2.status_code} len={len(r2.text)}")
        if r2.status_code == 200:
            detail = json.loads(r2.text)
            # Look for download URL in response
            print(f"  Detail keys: {list(detail.keys())[:15]}")
            if 'download_small' in detail:
                print(f"  download_small: {detail['download_small'][:100]}")
            elif 'small_url' in detail:
                print(f"  small_url: {detail['small_url'][:100]}")
        
        # Check CDN domains
        cdn_tests = [
            f"https://cdn.anime-pictures.net/pictures/{pid}.jpg",
            f"https://cdn1.anime-pictures.net/pictures/{pid}.jpg", 
            f"https://a.anime-pictures.net/pictures/{pid}.jpg",
        ]
        for url in cdn_tests:
            try:
                r3 = requests.head(url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                    'Referer': 'https://anime-pictures.net/',
                })
                print(f"  {url[:50]}: {r3.status_code}")
            except Exception as e:
                print(f"  {url[:50]}: FAIL {type(e).__name__}")
except Exception as e:
    print(f"Anime-Pictures CDN test FAIL: {e}")
