"""Test Bing downloading and Lolibooru/Safebooru tag info extraction"""
import requests, re, json
from urllib.parse import unquote

# Test Bing image download with different source sites
print("=== Bing image download test ===")
r = requests.get('https://cn.bing.com/images/async', params={
    'q': 'anime feet barefoot 1girl wallpaper',
    'first': '1',
    'count': '35',
    'qft': '+filterui:aspect-tall+filterui:photo-photo',
}, timeout=15, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
})
mediaurls = re.findall(r'mediaurl=(https?%3[Aa]%2[Ff][^&\"]+)', r.text)
decoded_urls = [unquote(u) for u in mediaurls]

print(f"Found {len(decoded_urls)} URLs")
# Test download of a few
for url in decoded_urls[:5]:
    print(f"  Testing: {url[:80]}...")
    try:
        r2 = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        }, allow_redirects=True)
        ct = r2.headers.get('content-type', '')
        is_image = 'image' in ct or r2.content[:4] in [b'\xff\xd8\xff\xe0', b'\x89PNG']
        size = len(r2.content)
        print(f"    -> {r2.status_code} ct={ct[:20]} size={size} is_img={is_image}")
    except Exception as e:
        print(f"    -> FAIL: {type(e).__name__}: {str(e)[:60]}")

# Test Safebooru tag extraction for character names
print("\n=== Safebooru tag extraction ===")
r = requests.get('https://safebooru.org/index.php', params={
    'page': 'dapi', 's': 'post', 'q': 'index',
    'json': '1', 'tags': 'foot_focus 1girl',
    'limit': '5',
}, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
if r.status_code == 200:
    data = json.loads(r.text)
    for p in data[:3]:
        pid = p.get('id')
        # Get tags from the API
        tags = p.get('tags', '')
        print(f"  Post {pid}: tags={tags[:100]}...")
        print(f"    w={p.get('width')} h={p.get('height')}")
        
        # Also check if has character field
        print(f"    creator_id={p.get('creator_id')} owner={p.get('owner')} has_children={p.get('has_children')}")
        print(f"    All keys: {list(p.keys())}")

# Test Zerochan for getting more pages
print("\n=== Zerochan scrolling ===")
for tag in ['Feet,Anime', 'Stockings,Anime', 'Barefoot,Anime', 'Pantyhose,Anime']:
    all_items = []
    for page in range(1, 4):
        try:
            r = requests.get(f'https://www.zerochan.net/{tag}?json=1&p={page}', timeout=15, headers={
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'application/json',
                'Referer': 'https://www.zerochan.net/',
            })
            if r.status_code == 200:
                data = json.loads(r.text)
                items = data.get('items', [])
                all_items.extend(items)
        except:
            pass
    # Filter portrait images
    portrait = [i for i in all_items if i.get('height', 0) > i.get('width', 0) and i.get('height', 0) >= 1080]
    print(f"  {tag}: {len(all_items)} total across 3 pages, {len(portrait)} portrait >= 1080h")
