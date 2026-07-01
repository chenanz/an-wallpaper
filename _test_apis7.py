"""Test anime-pictures file_url and Zerochan pagination"""
import requests
import json

# Test anime-pictures post detail - file_url
print("=== Anime-Pictures file_url ===")
try:
    # Get a few posts
    r = requests.get('https://api.anime-pictures.net/api/v3/posts?search_tag=feet&page=0&limit=5', timeout=20, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': 'application/json',
        'Origin': 'https://anime-pictures.net',
        'Referer': 'https://anime-pictures.net/',
    })
    data = json.loads(r.text)
    posts = data.get('posts', [])
    
    for p in posts[:3]:
        pid = p.get('id')
        # Get full post detail
        r2 = requests.get(f'https://api.anime-pictures.net/api/v3/posts/{pid}', timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Origin': 'https://anime-pictures.net',
            'Referer': 'https://anime-pictures.net/',
        })
        if r2.status_code == 200:
            detail = json.loads(r2.text)
            file_url = detail.get('file_url', '')
            print(f"  Post {pid}: file_url={file_url[:100]}...")
            
            # Try to download
            if file_url:
                try:
                    r3 = requests.head(file_url, timeout=10, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                        'Referer': 'https://anime-pictures.net/',
                    })
                    print(f"    HEAD: {r3.status_code} type={r3.headers.get('content-type','')} len={r3.headers.get('content-length','')}")
                except Exception as e:
                    print(f"    HEAD FAIL: {type(e).__name__}: {str(e)[:80]}")
                    # Try with different domain
                    alt = file_url.replace('images.', 'cdn.').replace('.anime-pictures.net', '')
                    try:
                        r4 = requests.head(alt, timeout=10, headers={
                            'User-Agent': 'Mozilla/5.0',
                            'Referer': 'https://anime-pictures.net/',
                        })
                        print(f"    ALT HEAD: {r4.status_code}")
                    except:
                        pass
except Exception as e:
    print(f"FAIL: {e}")

# Test Zerochan pagination
print("\n=== Zerochan pagination ===")
try:
    for page in range(1, 4):
        r = requests.get(f'https://www.zerochan.net/Stockings,Anime?json=1&p={page}', timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'application/json',
            'Referer': 'https://www.zerochan.net/',
        })
        data = json.loads(r.text)
        items = data.get('items', [])
        print(f"  Page {page}: {len(items)} items")
        for item in items[:2]:
            print(f"    id={item.get('id')} w={item.get('width')} h={item.get('height')} tag={item.get('tag','')}")
except Exception as e:
    print(f"Zerochan pagination FAIL: {e}")

# Test Safebooru pagination
print("\n=== Safebooru pagination ===")
try:
    for pid in [0, 100, 200]:
        r = requests.get(f'https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags=foot_focus+1girl&pid={pid}&limit=5', 
                        timeout=15, headers={'User-Agent':'Mozilla/5.0'})
        if r.status_code == 200:
            data = json.loads(r.text)
            print(f"  pid={pid}: {len(data)} items")
            if data:
                p = data[0]
                print(f"    w={p.get('width')} h={p.get('height')} file={p.get('file_url','')[:60]}")
except Exception as e:
    print(f"Safebooru pagination FAIL: {e}")

# Test Safebooru with portrait filter
print("\n=== Safebooru portrait images ===")
safe_tags_portrait = [
    ('foot_focus+1girl+portrait', 'foot_focus+1girl'),
    ('feet+1girl+portrait', 'feet+1girl'),
    ('barefoot+1girl+portrait', 'barefoot+1girl'),
    ('stockings+1girl+portrait', 'stockings+1girl'),
    ('thighhighs+1girl+portrait', 'thighhighs+1girl'),
    ('pantyhose+1girl+portrait', 'pantyhose+1girl'),
]
for tag_label, tag_query in safe_tags_portrait:
    try:
        r = requests.get(f'https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags={tag_query}&limit=100&pid=0', 
                        timeout=15, headers={'User-Agent':'Mozilla/5.0'})
        if r.status_code == 200:
            data = json.loads(r.text)
            # Count portrait images (h > w, h >= 1080)
            portrait = [p for p in data if p.get('height', 0) > p.get('width', 0) and p.get('height', 0) >= 1080]
            print(f"  {tag_label}: {len(data)} total, {len(portrait)} portrait >= 1080h")
except Exception as e:
    print(f"  {tag_label}: FAIL {e}")
