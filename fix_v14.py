import requests
tok_path = "D:/风/hermes/an-app/.gh_token"
with open(tok_path) as f: T = f.read().strip()
H = {"Authorization": "token " + T, "Accept": "application/vnd.github+json"}
REPO = "chenanz/an-wallpaper"
APK = "D:/风/hermes/an-app/android/app/build/outputs/apk/debug/app-debug.apk"
V = "v1.4.0"

# 删掉刚才上传错误的 asset
rels = requests.get(f"https://api.github.com/repos/{REPO}/releases/tags/{V}", headers=H, timeout=30).json()
for a in rels.get("assets", []):
    if "an-wallwall" in a["name"]:
        requests.delete(f"https://api.github.com/repos/{REPO}/releases/assets/{a['id']}", headers=H, timeout=10)
        print(f"deleted wrong asset {a['name']}")

# 重新上传正确文件名
u = rels["upload_url"]
target = u.replace("{?name,label}", "?name=an-wallpaper-v1.4.0.apk")
with open(APK, "rb") as f: apk = f.read()
ru = requests.post(target, headers={"Authorization": "token " + T, "Content-Type": "application/vnd.android.package-archive"}, data=apk, timeout=60)
if ru.status_code == 201:
    print(f"✅ https://github.com/{REPO}/releases/download/{V}/an-wallpaper-v1.4.0.apk")
else:
    print(f"FAIL {ru.status_code} {ru.text[:200]}")
