import requests, json

tok_path = "D:/风/hermes/an-app/.gh_token"
with open(tok_path, "r") as f:
    T = f.read().strip()

H = {"Authorization": "token " + T, "Accept": "application/vnd.github+json"}

# 查 Pages 详细错误
r = requests.get("https://api.github.com/repos/chenanz/an-wallpaper/pages", headers=H, timeout=30)
print(json.dumps(r.json(), indent=2))

# 查最近的 Pages build
r2 = requests.get("https://api.github.com/repos/chenanz/an-wallpaper/pages/builds", headers=H, timeout=30)
if r2.status_code == 200:
    builds = r2.json()
    print(f"\nBuilds: {len(builds)} total")
    for b in builds[:3]:
        print(f"  id={b['id']} status={b['status']} error={b.get('error',{}).get('message','none')}")
else:
    print(f"builds api: {r2.status_code}")
