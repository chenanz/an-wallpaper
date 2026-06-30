import requests
tok_path = "D:/风/hermes/an-app/.gh_token"
with open(tok_path) as f: T = f.read().strip()
H = {"Authorization": "token " + T, "Accept": "application/vnd.github+json"}
REPO = "chenanz/an-wallpaper"
APK = "D:/风/hermes/an-app/android/app/build/outputs/apk/debug/app-debug.apk"
V = "v1.4.0"
r = requests.post(f"https://api.github.com/repos/{REPO}/releases", headers=H, json={
    "tag_name": V, "target_commitish": "main",
    "name": f"安 — 二游少女壁纸馆 {V}",
    "body": "## v1.4.0 彻底修复滚动\n\n- 根因：嵌套 flex+overflow 在 Android WebView 中触摸事件被吞\n- 修复：只有一层滚动容器(.app-content)，所有 Tab 内容直接放进去\n- body touch-action:none 阻止系统吞滑动手势\n- viewport-fit=cover + interactive-widget=resizes-content\n- sticky 头部搜索栏/标签栏不随滚走\n- 图片 lazy+async 按需加载\n- 玉足社隐藏入口（左上角连续点5次解锁）\n- 爬虫关键词扩充：足/腿/丝袜/黑丝/白丝 etc.",
    "draft": False, "prerelease": False,
}, timeout=30)
u = r.json().get("upload_url") if r.status_code == 201 else requests.get(f"https://api.github.com/repos/{REPO}/releases/tags/{V}", headers=H, timeout=30).json().get("upload_url")
target = u.replace("{?name,label}", "?name=an-wallpaper-v1.4.0.apk")
with open(APK, "rb") as f: apk = f.read()
ru = requests.post(target, headers={"Authorization": "token " + T, "Content-Type": "application/vnd.android.package-archive"}, data=apk, timeout=60)
if ru.status_code == 201: print(f"✅ https://github.com/{REPO}/releases/download/{V}/an-wallwall-v1.4.0.apk")
else: print(f"FAIL {ru.status_code}")
