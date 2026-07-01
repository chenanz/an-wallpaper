"""Test API connectivity from China"""
import requests

urls = [
    ('Gelbooru', 'https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags=feet+rating:safe+1girl&limit=3'),
    ('Danbooru', 'https://danbooru.donmai.us/posts.json?tags=feet+rating:s&limit=3'),
    ('Safebooru', 'https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags=feet+1girl&limit=3'),
    ('Wallhaven', 'https://wallhaven.cc/api/v1/search?q=anime+feet&categories=010&purity=100&limit=3'),
    ('Konachan', 'https://konachan.com/post.json?tags=feet+rating:safe&limit=3'),
    ('Yandere', 'https://yande.re/post.json?tags=feet+rating:safe&limit=3'),
]

for name, url in urls:
    try:
        r = requests.get(url, timeout=15, headers={'User-Agent':'Mozilla/5.0'})
        print(f'{name}: {r.status_code} len={len(r.text)}')
        if r.status_code == 200:
            print(f'  preview: {r.text[:300]}')
    except Exception as e:
        print(f'{name}: FAIL {e}')
