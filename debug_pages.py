import requests, base64

tok_path = "D:/风/hermes/an-app/.gh_token"
with open(tok_path, "r") as f:
    T = f.read().strip()

H = {"Authorization": "token " + T, "Accept": "application/vnd.github+json"}

# 读 GitHub 仓库里的 index.html
r = requests.get("https://api.github.com/repos/chenanz/an-wallpaper/contents/index.html", headers=H, timeout=30)
content = base64.b64decode(r.json()["content"]).decode()
print("=== GitHub repo index.html ===")
for line in content.splitlines():
    if 'href' in line or 'src' in line:
        print(line.strip())
