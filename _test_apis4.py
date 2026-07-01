"""Test Anime-Pictures API details and Zerochan API"""
import requests
import json

# Test Anime-Pictures more deeply
print("=== Anime-Pictures API ===")
urls_to_test = [
    'https://api.anime-pictures.net/api/v3/posts?search_tag=feet&page=0&limit=5',
    'https://api.anime-pictures.net/api/v3/posts?search_tag=stockings&page=0&limit=5',
    'https://api.anime-pictures.net/api/v3/posts?search_tag=barefeet&page=0&limit=5',
    'https://api.anime-pictures.net/api/v3/posts?search_tag=pantyhose&page=0&limit=5',
]

for url in urls_to_test:
    tag = url.split('search_tag=')[1].split('&')[0]
    try:
        r = requests.get(url, timeout=20, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'application/json',
        })
        if r.status_code == 200:
            data = json.loads(r.text)
            posts = data.get('posts', [])
            print(f"  tag={tag}: {data.get('posts_count',0)} total, returned={len(posts)}")
            for p in posts[:2]:
                print(f"    id={p.get('id')}, w={p.get('width')}, h={p.get('height')}, tags={p.get('tags',[])[:5]}")
        else:
            print(f"  tag={tag}: status={r.status_code}")
    except Exception as e:
        print(f"  tag={tag}: FAIL {e}")

# Test Zerochan API
print("\n=== Zerochan API ===")
z_urls = [
    'https://www.zerochan.net/Feet,Anime?json=1&p=1',
    'https://www.zerochan.net/Stockings,Anime?json=1&p=1',
]
for url in z_urls:
    tag = url.split('net/')[1].split('?')[0]
    try:
        r = requests.get(url, timeout=20, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'application/json',
            'Referer': 'https://www.zerochan.net/',
        })
        if r.status_code == 200:
            try:
                data = json.loads(r.text)
                items = data.get('items', data) if isinstance(data, dict) else data
                count = len(items) if isinstance(items, list) else 'unknown'
                print(f"  tag={tag}: {count} items")
                if isinstance(items, list) and items:
                    print(f"    sample: {json.dumps(items[0], indent=2)[:300]}")
            except:
                print(f"  tag={tag}: not json, preview: {r.text[:200]}")
        else:
            print(f"  tag={tag}: status={r.status_code}")
    except Exception as e:
        print(f"  tag={tag}: FAIL {e}")

# Test Safebooru with pagination and different tags
print("\n=== Safebooru detailed ===")
safe_tags = [
    'feet+1girl',
    'barefoot+1girl',
    'soles+1girl',
    'stockings+1girl',
    'pantyhose+1girl',
    'thighhighs+1girl',
    'toes+1girl',
    'bare_legs+1girl',
    'foot_focus+1girl',
]
for tags in safe_tags:
    try:
        r = requests.get(f'https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags={tags}&limit=1', 
                        timeout=15, headers={'User-Agent':'Mozilla/5.0'})
        if r.status_code == 200:
            data = json.loads(r.text)
            count = len(data)
            if data:
                p = data[0]
                print(f"  {tags}: {count} results, sample w={p.get('width')} h={p.get('height')} file={p.get('file_url','')[:60]}")
            else:
                print(f"  {tags}: 0 results")
    except Exception as e:
        print(f"  {tags}: FAIL {e}")

# Test downloading an anime-pictures image
print("\n=== Test anime-pictures image download ===")
try:
    r = requests.get('https://api.anime-pictures.net/api/v3/posts?search_tag=feet&page=0&limit=2', timeout=20, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    })
    data = json.loads(r.text)
    posts = data.get('posts', [])
    if posts:
        p = posts[0]
        pid = p.get('id')
        # Construct image URL - anime-pictures has specific URL format
        # Try the small preview first
        preview_url = f"https://api.anime-pictures.net/api/v3/download/small/{pid}"
        print(f"  Trying preview: {preview_url}")
        r2 = requests.head(preview_url, timeout=10, headers={'User-Agent':'Mozilla/5.0'})
        print(f"  result: {r2.status_code} type={r2.headers.get('content-type','')} len={r2.headers.get('content-length','')}")
        
        # Try direct image URL
        md5 = p.get('md5', '')
        ext = p.get('extension', 'jpg')
        if md5:
            direct_url = f"https://images.anime-pictures.net/{md5[:2]}/{md5}.{ext}"
            print(f"  Trying direct: {direct_url}")
            r3 = requests.head(direct_url, timeout=10, headers={'User-Agent':'Mozilla/5.0'})
            print(f"  result: {r3.status_code} type={r3.headers.get('content-type','')} len={r3.headers.get('content-length','')}")
except Exception as e:
    print(f"  FAIL: {e}")
