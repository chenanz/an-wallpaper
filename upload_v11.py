import requests, os

tok_path = "D:/风/hermes/an-app/.gh_token"
with open(tok_path, "r") as f:
    T = f.read().strip()

H = {"Authorization": "token " + T, "Accept": "application/vnd.github+json"}
REPO = "chenanz/an-wallpaper"
APK = "D:/风/hermes/an-app/android/app/build/outputs/apk/debug/app-debug.apk"
VERSION = "v1.1.0"

print(f"[1/2] 创建 Release {VERSION}...")
r = requests.post(f"https://api.github.com/repos/{REPO}/releases", headers=H, json={
    "tag_name": VERSION,
    "target_commitish": "main",
    "name": f"安 — 二游少女壁纸馆 {VERSION}",
    "body": "## v1.1.0 在线更新版\n\n- 图片从云端加载，爬虫新爬的图自动出现\n- APK 瘦身至 4MB（原 100MB）\n- 有网就能用，无需电脑开机\n- 离线时自动 fallback",
    "draft": False,
    "prerelease": False,
}, timeout=30)
if r.status_code == 201:
    upload_url = r.json()["upload_url"]
    print(f"  OK")
elif r.status_code == 422:
    r2 = requests.get(f"https://api.github.com/repos/{REPO}/releases/tags/{VERSION}", headers=H, timeout=30)
    upload_url = r2.json()["upload_url"]
    print(f"  EXISTS")
else:
    print(f"  FAIL: {r.status_code}"); exit(1)

print(f"\n[2/2] 上传 APK (4.2MB)...")
target = upload_url.replace("{?name,label}", "?name=an-wallpaper-v1.1.0.apk")
with open(APK, "rb") as f:
    apk = f.read()
ru = requests.post(target, headers={"Authorization": "token " + T, "Content-Type": "application/vnd.android.package-archive"}, data=apk, timeout=60)
if ru.status_code == 201:
    url = ru.json()["browser_download_url"]
    print(f"\n✅ 上传成功！\n\n📱 下载: {url}\n🔗 Release: https://github.com/{REPO}/releases")
