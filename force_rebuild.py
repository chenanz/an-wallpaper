import requests

tok_path = "D:/风/hermes/an-app/.gh_token"
with open(tok_path, "r") as f:
    T = f.read().strip()

H = {"Authorization": "token " + T, "Accept": "application/vnd.github+json"}

# 方案：用 GitHub API 创建一个空 commit 并推到 main，这会触发 Pages 重新构建
# 或者：切换回 legacy 模式强制重建

# 1. 先试切换到 legacy 再切回 workflow
r1 = requests.put("https://api.github.com/repos/chenanz/an-wallpaper/pages", headers=H,
    json={"build_type": "legacy", "source": {"branch": "main", "path": "/"}}, timeout=30)
print(f"Step 1 (legacy): {r1.status_code}")

import time
time.sleep(5)

r2 = requests.put("https://api.github.com/repos/chenanz/an-wallpaper/pages", headers=H,
    json={"build_type": "workflow"}, timeout=30)
print(f"Step 2 (workflow): {r2.status_code}")

# 2. 其实这可能导致更多问题。不如直接用 legacy 模式
# Legacy 模式就是直接从 main 分支读文件
r3 = requests.put("https://api.github.com/repos/chenanz/an-wallpaper/pages", headers=H,
    json={"build_type": "legacy", "source": {"branch": "main", "path": "/"}}, timeout=30)
print(f"Step 3 (back to legacy): {r3.status_code}")

# 检查
time.sleep(3)
rp = requests.get("https://api.github.com/repos/chenanz/an-wallpaper/pages", headers=H, timeout=30)
if rp.status_code == 200:
    d = rp.json()
    print(f"Pages: build_type={d.get('build_type')} status={d.get('status')}")

print("等待30秒让 Pages 重建...")
time.sleep(30)

# 验证
r4 = requests.get("https://chenanz.github.io/an-wallpaper/", headers={"Cache-Control": "no-cache"}, timeout=15)
has_prefix = "an-wallpaper" in r4.text
print(f"Has prefix: {has_prefix}")
