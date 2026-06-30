import requests

tok_path = "D:/风/hermes/an-app/.gh_token"
with open(tok_path, "r") as f:
    T = f.read().strip()

H = {"Authorization": "token " + T, "Accept": "application/vnd.github+json"}
REPO = "chenanz/an-wallpaper"
APK = "D:/风/hermes/an-app/android/app/build/outputs/apk/debug/app-debug.apk"
V = "v1.3.1"

r = requests.post(f"https://api.github.com/repos/{REPO}/releases", headers=H, json={
    "tag_name": V, "target_commitish": "main",
    "name": f"安 — 二游少女壁纸馆 {V}",
    "body": "## v1.3.1 滚动修复版\n\n- 去掉虚拟列表（和瀑布流不兼容导致无法滚动）\n- 改用 flex 双列布局替代 CSS column-count\n- 所有滚动容器加 -webkit-overflow-scrolling: touch + touch-action: pan-y\n- 图片 loading=lazy + decoding=async 按需加载\n- 瀑布流不再出现 column 脱离文档流问题",
    "draft": False, "prerelease": False,
}, timeout=30)
if r.status_code == 201:
    u = r.json()["upload_url"]
elif r.status_code == 422:
    r2 = requests.get(f"https://api.github.com/repos/{REPO}/releases/tags/{V}", headers=H, timeout=30)
    u = r2.json()["upload_url"]
else:
    print(f"FAIL {r.status_code}"); exit(1)

target = u.replace("{?name,label}", "?name=an-wallpaper-v1.3.1.apk")
with open(APK, "rb") as f: apk = f.read()
ru = requests.post(target, headers={"Authorization": "token " + T, "Content-Type": "application/vnd.android.package-archive"}, data=apk, timeout=60)
if ru.status_code == 201:
    print(f"✅ https://github.com/{REPO}/releases/download/{V}/an-wallpaper-v1.3.1.apk")
