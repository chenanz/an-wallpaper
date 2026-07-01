"""Test more sources - moebooru variants and other domestic options"""
import requests
import json

urls = [
    # GB-based booru mirrors that might work in China
    ('GB-Safebooru', 'https://safebooru.donmai.us/posts.json?tags=feet+rating:s&limit=3'),
    ('Sakuga', 'https://sakugabooru.com/post.json?tags=feet+rating:safe&limit=2'),
    # Anime-Pictures (popular anime image site)
    ('AnimePictures', 'https://api.anime-pictures.net/api/v3/posts?search_tag=feet&page=0&limit=3'),
    # Zerochan
    ('Zerochan', 'https://www.zerochan.net/Feet,Anime?q=Feet&jos=1&p=1&s=random_json'),
    # E-Shuushuu
    ('E-Shuushuu', 'https://e-shuushuu.net/api/search/?tags=feet&limit=3'),
    # The Big ImageBoard (tbib)
    ('TBIB', 'https://tbib.org/index.php?page=dapi&s=post&q=index&json=1&tags=feet+rating:safe+1girl&limit=3'),
    # Hypnohub
    ('Hypnohub', 'https://hypnohub.net/post.json?tags=feet+rating:safe&limit=2'),
    # Xbooru
    ('Xbooru', 'https://xbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags=feet+rating:safe+1girl&limit=3'),
    # Bing Image Search (domestic friendly)
    ('Bing-CN', 'https://cn.bing.com/images/search?q=anime+feet+wallpaper+vertical&first=1&count=5&qft=+filterui:photo-photo&form=IRFLTR'),
    # Lolibooru alt
    ('Lolibooru-API', 'https://lolibooru.moe/post.json?tags=feet+rating:safe&limit=2'),
    # Behoimi (3dbooru) 
    ('Behoimi', 'http://behoimi.org/index.php?page=dapi&s=post&q=index&json=1&tags=feet+rating:safe&limit=2'),
    # Danbooru alt domain
    ('Danbooru-safe', 'https://safebooru.donmai.us/posts.json?tags=feet+rating:s&limit=2'),
]

for name, url in urls:
    try:
        r = requests.get(url, timeout=15, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        print(f'{name}: {r.status_code} len={len(r.text)}')
        if r.status_code == 200 and r.text:
            try:
                data = json.loads(r.text)
                if isinstance(data, list) and data:
                    print(f'  items: {len(data)}, sample keys: {list(data[0].keys())[:6]}')
                elif isinstance(data, list):
                    print(f'  items: 0')
                elif isinstance(data, dict):
                    print(f'  keys: {list(data.keys())[:8]}')
            except:
                ct = r.headers.get('content-type','')
                print(f'  not json (type={ct}), preview: {r.text[:150]}')
    except Exception as e:
        print(f'{name}: FAIL {type(e).__name__}: {str(e)[:120]}')
