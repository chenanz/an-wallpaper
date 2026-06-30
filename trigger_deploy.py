import requests, base64, time

tok_path = "D:/风/hermes/an-app/.gh_token"
with open(tok_path, "r") as f:
    T = f.read().strip()

H = {"Authorization": "token " + T, "Accept": "application/vnd.github+json"}

# 创建一个 dummy commit 触发重新部署
# 更新 .nojekyll 的 commit message
rget = requests.get("https://api.github.com/repos/chenanz/an-wallpaper/contents/.nojekyll", headers=H, timeout=30)
if rget.status_code == 200:
    sha = rget.json()["sha"]
    b64 = base64.b64encode(b"").decode()
    data = {"message": "trigger redeploy - fix base path", "content": b64, "branch": "main", "sha": sha}
    r = requests.put("https://api.github.com/repos/chenanz/an-wallpaper/contents/.nojekyll", headers=H, json=data, timeout=30)
    print(f"Trigger commit: {r.status_code}")

print("等待 Pages 重建 (60s)...")
time.sleep(60)

# 验证 - 加 timestamp 防缓存
ts = int(time.time())
r = requests.get(f"https://chenanz.github.io/an-wallpaper/?_={ts}", headers={"Cache-Control": "no-cache"}, timeout=15, allow_redirects=True)
has_prefix = "an-wallpaper" in r.text
has_images = "/images/" in r.text if has_prefix else True
print(f"Has /an-wallpaper/ prefix: {has_prefix}")
if has_prefix:
    for line in r.text.splitlines():
        if 'href' in line or 'src' in line:
            print(f"  {line.strip()}")
else:
    print("Still cached. Try in 2-3 minutes manually:")
    print("https://chenanz.github.io/an-wallpaper/")
