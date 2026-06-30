import requests, os, base64, time

tok_path = "D:/风/hermes/an-app/.gh_token"
with open(tok_path, "r") as f:
    T = f.read().strip()

H = {"Authorization": "token " + T, "Accept": "application/vnd.github+json"}
OWNER = "chenanz"
REPO = "an-wallpaper"
DIST = "D:/风/hermes/an-app/dist"

def upload_or_update(remote_path, local_path):
    with open(local_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{remote_path}"
    data = {"message": f"fix paths {remote_path}", "content": b64, "branch": "main"}
    rget = requests.get(url, headers=H, timeout=30)
    if rget.status_code == 200:
        data["sha"] = rget.json()["sha"]
    r = requests.put(url, headers=H, json=data, timeout=60)
    return r.status_code in [200, 201]

for root, dirs, files in os.walk(DIST):
    for fname in files:
        fpath = os.path.join(root, fname)
        rel = os.path.relpath(fpath, DIST).replace("\\", "/")
        if rel.startswith("images/"):
            continue
        ok = upload_or_update(rel, fpath)
        print(f"  {'ok' if ok else 'FAIL'} {rel}")
        time.sleep(0.4)

print("\n上传完成，等待 Pages 重建...")
time.sleep(45)

ts = int(time.time())
r = requests.get(f"https://chenanz.github.io/an-wallpaper/?_={ts}", headers={"Cache-Control": "no-cache"}, timeout=15)
has_an = "an-wallpaper" in r.text
has_base = "BASE_URL" in r.text or "/an-wallpaper/images/" in r.text
print(f"Has /an-wallpaper/ prefix: {has_an}")
print(f"Has base images path: {has_base}")
if has_an:
    print(f"\n✅ https://chenanz.github.io/an-wallpaper/")
