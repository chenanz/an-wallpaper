#!/usr/bin/env python3
"""
将 APK 上传到 GitHub Release 并生成下载链接
用法：python upload_release.py <apk路径>
"""
import requests, os, sys, json

# --- 配置 ---
REPO = "chenanz/an-wallpaper"

tok_path = "D:/风/hermes/an-app/.gh_token"
if not os.path.exists(tok_path):
    print("ERROR: .gh_token not found"); sys.exit(1)
with open(tok_path, "r") as f:
    TOKEN = f.read().strip()

HEADERS = {
    "Authorization": "token " + TOKEN,
    "Accept": "application/vnd.github+json",
}

# APK 路径
apk_path = sys.argv[1] if len(sys.argv) > 1 else "D:/风/hermes/an-app/android/app/build/outputs/apk/debug/app-debug.apk"

if not os.path.exists(apk_path):
    print(f"ERROR: APK 不存在: {apk_path}")
    sys.exit(1)

apk_name = os.path.basename(apk_path)
apk_size = os.path.getsize(apk_path)
version = "v1.0.0"

print(f"📦 APK: {apk_name} ({apk_size // 1024 // 1024}MB)")

# 1. 创建 Release
print("\n[1/2] 创建 GitHub Release...")
release_url = f"https://api.github.com/repos/{REPO}/releases"
release_data = {
    "tag_name": version,
    "target_commitish": "main",
    "name": f"安 — 二游少女壁纸馆 {version}",
    "body": "## 安 — 二游少女壁纸馆\n\n二游少女壁纸 App\n\n### 功能\n- 🔥 5大图源自动爬取（米游社/B站/百度/Bing/官方）\n- 🎮 8大游戏分类（原神/崩铁/崩3/绝区零/明日方舟/蔚蓝档案/碧蓝航线/第七史诗）\n- 📱 手机壁纸一键设置/保存\n- 🌙 深色模式\n- ♀️ 仅限女性角色",
    "draft": False,
    "prerelease": False,
}

r = requests.post(release_url, headers=HEADERS, json=release_data, timeout=30)
if r.status_code == 201:
    release = r.json()
    release_id = release["id"]
    upload_url_template = release["upload_url"]
    print(f"  ✅ Release 创建成功: {release['html_url']}")
elif r.status_code == 422:
    # tag 已存在，获取现有 release
    r = requests.get(f"https://api.github.com/repos/{REPO}/releases/tags/{version}", headers=HEADERS, timeout=30)
    if r.status_code == 200:
        release = r.json()
        release_id = release["id"]
        upload_url_template = release["upload_url"]
        print(f"  ⚠️ Release 已存在，更新: {release['html_url']}")
    else:
        print(f"  ❌ 获取现有 Release 失败: {r.status_code}")
        sys.exit(1)
else:
    print(f"  ❌ 创建失败: {r.status_code} {r.text[:200]}")
    sys.exit(1)

# 2. 上传 APK
print("\n[2/2] 上传 APK...")
# upload_url 格式: https://uploads.github.com/repos/.../releases/{id}/assets{?name,label}
upload_url = upload_url_template.replace("{?name,label}", f"?name={apk_name}")

with open(apk_path, "rb") as f:
    apk_data = f.read()

upload_headers = {
    "Authorization": "token " + TOKEN,
    "Content-Type": "application/vnd.android.package-archive",
}

ru = requests.post(upload_url, headers=upload_headers, data=apk_data, timeout=300)
if ru.status_code == 201:
    asset = ru.json()
    download_url = asset["browser_download_url"]
    print(f"\n  ✅ 上传成功！")
    print(f"\n  📱 下载链接: {download_url}")
else:
    print(f"  ❌ 上传失败: {ru.status_code} {ru.text[:200]}")
    sys.exit(1)

print(f"\n🔗 Release 页面: https://github.com/{REPO}/releases")
