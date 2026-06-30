#!/usr/bin/env python3
"""检查 GitHub 仓库上传状态"""
import requests, os, sys

TOKEN = os.environ.get("GHTOKEN", "")
if not TOKEN:
    tok_file = "D:/风/hermes/an-app/.gh_token"
    if os.path.exists(tok_file):
        with open(tok_file, "r") as f:
            TOKEN = f.read().strip()
if not TOKEN:
    print("No token"); sys.exit(1)

HEADERS = {
    "Authorization": "token " + TOKEN,
    "Accept": "application/vnd.github+json",
}

OWNER = "chenanz"
REPO = "an-wallpaper"

# images
r = requests.get(f'https://api.github.com/repos/{OWNER}/{REPO}/contents/images', headers=HEADERS, timeout=30)
if r.status_code == 200:
    items = r.json()
    uploaded = [x["name"] for x in items if x["type"] == "file"]
    print(f'images/ 已上传 {len(uploaded)} 张')
    local = [f for f in os.listdir("D:/风/hermes/an-app/dist/images") if f.endswith(".jpg")]
    print(f'dist/images/ 共 {len(local)} 张')
    missing = set(local) - set(uploaded)
    print(f'还缺 {len(missing)} 张')
else:
    print(f'images/ status={r.status_code}')

# assets
r2 = requests.get(f'https://api.github.com/repos/{OWNER}/{REPO}/contents/assets', headers=HEADERS, timeout=30)
if r2.status_code == 200:
    print(f'assets/ 已上传 {len(r2.json())} 个文件')

# Pages
r3 = requests.get(f'https://api.github.com/repos/{OWNER}/{REPO}/pages', headers=HEADERS, timeout=30)
if r3.status_code == 200:
    d = r3.json()
    print(f'\nPages: {d.get("html_url","?")} status={d.get("status","?")}')
else:
    print(f'\nPages: not enabled ({r3.status_code})')
