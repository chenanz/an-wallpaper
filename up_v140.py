import requests
tok_path = "D:/风/hermes/an-app/.gh_token"
with open(tok_path) as f: T = f.read().strip()
H = {"Authorization": "token " + T, "Accept": "application/vnd.github+json"}
REPO = "chenanz/an-wallpaper"
APK = "D:/风/hermes/an-app/android/app/build/outputs/apk/debug/app-debug.apk"

# 先删 v1.4.0 的错误 asset
rels = requests.get(f"https://api.github.com/repos/{REPO}/releases/tags/v1.4.0", headers=H, timeout=30).json()
for a in rels.get("assets", []):
    requests.delete(a["url"], headers=H, timeout=10)
    print(f"  deleted {a['name']}")

# 删掉 v1.4.0 release 本身
requests.delete(f"https://api.github.com/repos/{REPO}/releases/{rels['id']}", headers=H, timeout=10)
requests.delete(f"https://api.github.com/repos/{REPO}/git/refs/tags/v1.4.0", headers=H, timeout=10)
print("  v1.4.0 cleaned")

# 创建 v1.4.0 重新来
V = "v1.4.0"
r = requests.post(f"https://api.github.com/repos/{REPO}/releases", headers=H, json={
    "tag_name": V, "target_commitish": "main",
    "name": f"安 — 二游少女壁纸馆 {V}",
    "body": "## v1.4.0 彻底修复滚动\n\n- 只有1层滚动容器，消灭嵌套flex+overflow在WebView中吞触摸事件\n- body touch-action:none\n- viewport-fit=cover\n- 玉足社隐藏入口（左上角连续5次点）",
    "draft": False, "prerelease": False,
}, timeout=30)
u = r.json()["upload_url"]
target = u.replace("{?name,label}", "?name=an-wallpaper-v1.4.0.apk")
with open(APK, "rb") as f: apk = f.read()
ru = requests.post(target, headers={"Authorization": "token " + T, "Content-Type": "application/vnd.android.package-archive"}, data=apk, timeout=60)
if ru.status_code == 201: print(f"\n✅ https://github.com/{REPO}/releases/download/{V}/an-wallpaper-v1.4.0.apk")
else: print(f"FAIL {ru.status_code} {ru.text[:200]}")
