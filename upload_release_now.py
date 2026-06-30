import requests, os, json

tok_path = "D:/风/hermes/an-app/.gh_token"
with open(tok_path, "r") as f:
    T = f.read().strip()

H = {"Authorization": "token " + T, "Accept": "application/vnd.github+json"}
REPO = "chenanz/an-wallpaper"
APK = "D:/风/hermes/an-app/android/app/build/outputs/apk/debug/app-debug.apk"
VERSION = "v1.0.0"

# 1. 创建 Release
print("[1/2] 创建 Release...")
url = f"https://api.github.com/repos/{REPO}/releases"
data = {
    "tag_name": VERSION,
    "target_commitish": "main",
    "name": f"安 — 二游少女壁纸馆 {VERSION}",
    "body": "## 安 — 二游少女壁纸馆\n\n二游少女壁纸 App (Debug)\n\n- 5大图源自动爬取\n- 8大游戏分类\n- 手机壁纸一键保存/设置\n- 深色模式\n- 仅限女性角色",
    "draft": False,
    "prerelease": False,
}
r = requests.post(url, headers=H, json=data, timeout=30)
if r.status_code == 201:
    rel = r.json()
    upload_url = rel["upload_url"]
    print(f"  OK: {rel['html_url']}")
elif r.status_code == 422:
    r2 = requests.get(f"https://api.github.com/repos/{REPO}/releases/tags/{VERSION}", headers=H, timeout=30)
    if r2.status_code == 200:
        rel = r2.json()
        upload_url = rel["upload_url"]
        print(f"  EXISTS: {rel['html_url']}")
    else:
        print(f"  FAIL: {r2.status_code}"); exit(1)
else:
    print(f"  FAIL: {r.status_code} {r.text[:200]}"); exit(1)

# 2. 上传 APK
print("\n[2/2] 上传 APK (100MB)...")
apk_size = os.path.getsize(APK)
print(f"  大小: {apk_size // 1024 // 1024}MB")
upload_target = upload_url.replace("{?name,label}", "?name=an-wallpaper-debug.apk")

with open(APK, "rb") as f:
    apk_data = f.read()

uh = {"Authorization": "token " + T, "Content-Type": "application/vnd.android.package-archive"}
ru = requests.post(upload_target, headers=uh, data=apk_data, timeout=600)
if ru.status_code == 201:
    asset = ru.json()
    print(f"\n  ✅ 上传成功！")
    print(f"  📱 下载: {asset['browser_download_url']}")
else:
    print(f"  ❌ 失败: {ru.status_code} {ru.text[:300]}")
    exit(1)

print(f"\n🔗 Release: https://github.com/{REPO}/releases")
