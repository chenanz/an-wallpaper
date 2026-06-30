import requests, time

tok_path = "D:/风/hermes/an-app/.gh_token"
with open(tok_path, "r") as f:
    T = f.read().strip()

H = {"Authorization": "token " + T, "Accept": "application/vnd.github+json"}

print("等待 GitHub Pages 构建中...")
for attempt in range(6):
    r = requests.get("https://api.github.com/repos/chenanz/an-wallpaper/pages", headers=H, timeout=30)
    if r.status_code == 200:
        d = r.json()
        status = d.get("status", "unknown")
        url = d.get("html_url", "")
        print(f"  [{attempt+1}] status={status} url={url}")
        if status == "built":
            # 实际访问测试
            rr = requests.get(url, timeout=15, allow_redirects=True)
            print(f"  访问测试: {rr.status_code}")
            if rr.status_code == 200:
                print(f"\n✅ 部署成功! {url}")
                break
    else:
        print(f"  [{attempt+1}] api status={r.status_code}")
    time.sleep(30)
else:
    print("超时，但 Pages 可能仍在构建。1-3分钟后手动访问:")
    print("https://chenanz.github.io/an-wallpaper/")
