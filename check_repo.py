import requests

TOKEN = "***"  # will be replaced
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json",
}

r = requests.get('https://api.github.com/repos/chenanz/an-wallpaper/contents/', headers=HEADERS)
if r.status_code == 200:
    items = r.json()
    print(f'仓库根目录已有 {len(items)} 个文件/文件夹:')
    for item in items[:20]:
        sz = item.get("size", 0)
        sz_str = f"{sz//1024}KB" if sz < 1024*1024 else f"{sz//1024//1024}MB"
        print(f'  {item["type"]:4s} {item["name"]:30s} {sz_str}')
    if len(items) > 20:
        print(f'  ... 共 {len(items)} 项')
elif r.status_code == 404:
    print('仓库为空或不存在')
else:
    print(f'status={r.status_code} {r.text[:200]}')
