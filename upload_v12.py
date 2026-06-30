import requests, os

tok_path = "D:/风/hermes/an-app/.gh_token"
with open(tok_path, "r") as f:
    T = f.read().strip()

H = {"Authorization": "token " + T, "Accept": "application/vnd.github+json"}
REPO = "chenanz/an-wallpaper"
APK = "D:/风/hermes/an-app/android/app/build/outputs/apk/debug/app-debug.apk"
VERSION = "v1.2.0"

print(f"[1/2] Release {VERSION}...")
r = requests.post(f"https://api.github.com/repos/{REPO}/releases", headers=H, json={
    "tag_name": VERSION, "target_commitish": "main",
    "name": f"安 — 二游少女壁纸馆 {VERSION}",
    "body": "## v1.2.0 适配修复版\n\n- Android 返回键：全屏预览→关闭，子页面→返回，首页→双击退出\n- Edge-to-edge 适配 K80 至尊版等全面屏手机\n- 系统手势导航条不再遮挡底部导航\n- 状态栏/导航栏透明沉浸\n- 图片云端加载，4MB 超轻量",
    "draft": False, "prerelease": False,
}, timeout=30)
if r.status_code == 201:
    upload_url = r.json()["upload_url"]; print("  OK")
elif r.status_code == 422:
    r2 = requests.get(f"https://api.github.com/repos/{REPO}/releases/tags/{VERSION}", headers=H, timeout=30)
    upload_url = r2.json()["upload_url"]; print("  EXISTS")
else:
    print(f"  FAIL: {r.status_code} {r.text[:200]}"); exit(1)

print(f"\n[2/2] Upload APK...")
target = upload_url.replace("{?name,label}", "?name=an-wallpaper-v1.2.0.apk")
with open(APK, "rb") as f:
    apk = f.read()
ru = requests.post(target, headers={"Authorization": "token " + T, "Content-Type": "application/vnd.android.package-archive"}, data=apk, timeout=60)
if ru.status_code == 201:
    url = ru.json()["browser_download_url"]
    print(f"\n✅\n\n📱 下载: {url}\n🔗 https://github.com/{REPO}/releases")
else:
    print(f"  FAIL: {ru.status_code} {ru.text[:200]}")
