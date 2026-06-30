import requests, json, os, sys

token_file = "D:/风/hermes/an-app/.gh_token"
if not os.path.exists(token_file):
    print("ERROR: .gh_token file not found. Run: echo YOUR_TOKEN > .gh_token")
    sys.exit(1)

with open(token_file, "r") as f:
    TOKEN=f.read().strip()

HEADERS = {
    "Authorization": "token " + TOKEN,
    "Accept": "application/vnd.github+json",
}

OWNER = "chenanz"
REPO = "an-wallpaper"

r = requests.get(f'https://api.github.com/repos/{OWNER}/{REPO}/contents/', headers=HEADERS)
if r.status_code == 200:
    items = r.json()
    print(f'仓库根目录已有 {len(items)} 个文件/文件夹:')
    for item in items[:20]:
        sz = item.get("size", 0)
        sz_str = f"{sz//1024}KB" if sz < 1024*1024 else f"{sz//1024//1024}MB"
        print(f'  {item["type"]:4s} {item["name"]:30s} {sz_str}')
    if len(items) > 20:
        print(f'  ... 共 {len(items)} 项')
else:
    print(f'status={r.status_code}')

# 为 deploy_api2.py 提供 token
print(f"\nTOKEN_LEN={len(TOKEN)}")
