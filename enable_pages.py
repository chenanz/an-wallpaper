import requests

tok_path = "D:/风/hermes/an-app/.gh_token"
with open(tok_path, "r") as f:
    T = f.read().strip()

H = {"Authorization": "token " + T, "Accept": "application/vnd.github+json"}

# 1. 添加 .nojekyll
import base64
nojekyll_b64 = base64.b64encode(b"").decode()
url1 = "https://api.github.com/repos/chenanz/an-wallpaper/contents/.nojekyll"
rget = requests.get(url1, headers=H, timeout=30)
data1 = {"message": "add .nojekyll", "content": nojekyll_b64, "branch": "main"}
if rget.status_code == 200:
    data1["sha"] = rget.json()["sha"]
r1 = requests.put(url1, headers=H, json=data1, timeout=30)
print(f".nojekyll: {r1.status_code}")

# 2. 确保 index.html 在根目录
r2 = requests.get("https://api.github.com/repos/chenanz/an-wallpaper/contents/index.html", headers=H, timeout=30)
print(f"index.html exists: {r2.status_code == 200}")

# 3. 启用 GitHub Pages
rp = requests.post("https://api.github.com/repos/chenanz/an-wallpaper/pages", headers=H,
    json={"source": {"branch": "main", "path": "/"}}, timeout=30)
print(f"Pages enable: {rp.status_code}")
if rp.status_code == 201:
    print(f"URL: {rp.json().get('html_url','')}")
elif rp.status_code == 409:
    # already exists, try update
    rpu = requests.put("https://api.github.com/repos/chenanz/an-wallpaper/pages", headers=H,
        json={"source": {"branch": "main", "path": "/"}}, timeout=30)
    print(f"Pages update: {rpu.status_code}")
    if rpu.status_code == 200:
        print(f"URL: {rpu.json().get('html_url','')}")
else:
    print(rp.text[:300])

print("\nFinal URL: https://chenanz.github.io/an-wallpaper/")
