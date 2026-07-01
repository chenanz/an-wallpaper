"""Test more API connectivity"""
import requests
import json

urls = [
    # Safebooru with various feet-related tags
    ('Safebooru-feet', 'https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags=feet+1girl&limit=5'),
    ('Safebooru-stockings', 'https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags=stockings+1girl&limit=5'),
    ('Safebooru-barefoot', 'https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags=barefoot+1girl&limit=5'),
    ('Safebooru-soles', 'https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags=soles+1girl&limit=5'),
    ('Safebooru-pantyhose', 'https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags=pantyhose+1girl&limit=5'),
    # Lolibooru
    ('Lolibooru', 'https://lolibooru.moe/post.json?tags=feet+rating:safe&limit=3'),
    # ATBooru 
    ('ATBooru', 'https://booru.allthefallen.moe/posts.json?tags=feet+rating:s&limit=3'),
    # Rule34xxx (has safe content with feet)
    ('Rule34', 'https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags=feet+rating:safe+1girl&limit=3'),
    #猫娘FM / bilibili API
    ('Bilibili-h5', 'https://api.bilibili.com/x/space/wbi/arc/search?mid=0&ps=1&keyword=anime+feet'),
    # Pixiv ranking (public)
    ('Pixiv-rank', 'https://www.pixiv.net/ranking.php?mode=daily&content=illust&format=json&p=1'),
    # e621 (has anime content)
    ('e621', 'https://e621.net/posts.json?tags=feet+rating:s+anime&limit=3'),
]

for name, url in urls:
    try:
        r = requests.get(url, timeout=20, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        print(f'{name}: {r.status_code} len={len(r.text)}')
        if r.status_code == 200 and r.text:
            # Try to parse as json
            try:
                data = json.loads(r.text)
                if isinstance(data, list):
                    print(f'  items: {len(data)}')
                    if data:
                        print(f'  sample keys: {list(data[0].keys())[:8]}')
                elif isinstance(data, dict):
                    print(f'  keys: {list(data.keys())[:8]}')
            except:
                print(f'  not json, preview: {r.text[:200]}')
    except Exception as e:
        print(f'{name}: FAIL {type(e).__name__}: {str(e)[:100]}')

# Also test Safebooru image download
print("\n--- Testing Safebooru image download ---")
try:
    r = requests.get('https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags=feet+1girl+barefoot&limit=2', timeout=15, headers={'User-Agent':'Mozilla/5.0'})
    posts = json.loads(r.text)
    for p in posts[:2]:
        file_url = p.get('file_url', '')
        sample_url = p.get('sample_url', '')
        print(f"  file_url: {file_url}")
        print(f"  sample_url: {sample_url}")
        print(f"  width: {p.get('width')} height: {p.get('height')}")
        if file_url:
            try:
                ir = requests.head(file_url, timeout=10, headers={'User-Agent':'Mozilla/5.0', 'Referer': 'https://safebooru.org/'})
                print(f"  img head: {ir.status_code} content-type={ir.headers.get('content-type','')} content-len={ir.headers.get('content-length','')}")
            except Exception as e2:
                print(f"  img head FAIL: {e2}")
except Exception as e:
    print(f"Safebooru parse FAIL: {e}")
