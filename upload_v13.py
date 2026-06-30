import requests, os

tok_path = "D:/风/hermes/an-app/.gh_token"
with open(tok_path, "r") as f:
    T = f.read().strip()

H = {"Authorization": "token " + T, "Accept": "application/vnd.github+json"}
REPO = "chenanz/an-wallpaper"
APK = "D:/风/hermes/an-app/android/app/build/outputs/apk/debug/app-debug.apk"
VERSION = "v1.3.0"

r = requests.post(f"https://api.github.com/repos/{REPO}/releases", headers=H, json={
    "tag_name": VERSION, "target_commitish": "main",
    "name": f"安 — 二游少女壁纸馆 {VERSION}",
    "body": "## v1.3.0 流畅版\n\n- 修复下滑卡顿：去掉 236 张图同时预加载\n- 虚拟列表：只渲染可见区域，丝滑滚动\n- IntersectionObserver 懒加载：滚动到才加载\n- 图片渐显动画\n- 全屏预览独立加载高清大图\n- 并发限制 6 个请求，不堵主线程",
    "draft": False, "prerelease": False,
}, timeout=30)
if r.status_code == 201:
    upload_url = r.json()["upload_url"]; print("OK")
elif r.status_code == 422:
    r2 = requests.get(f"https://api.github.com/repos/{REPO}/releases/tags/{VERSION}", headers=H, timeout=30)
    upload_url = r2.json()["upload_url"]; print("EXISTS")
else:
    print(f"FAIL: {r.status_code}"); exit(1)

target = upload_url.replace("{?name,label}", "?name=an-wallpaper-v1.3.0.apk")
with open(APK, "rb") as f:
    apk = f.read()
ru = requests.post(target, headers={"Authorization": "token " + T, "Content-Type": "application/vnd.android.package-archive"}, data=apk, timeout=60)
if ru.status_code == 201:
    print(f"\n✅\n\n📱 https://github.com/{REPO}/releases/download/{VERSION}/an-wallpaper-v1.3.0.apk")
