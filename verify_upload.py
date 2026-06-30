import requests

tok_path = "D:/风/hermes/an-app/.gh_token"
with open(tok_path, "r") as f:
    T = f.read().strip()

H = {"Authorization": "token " + T, "Accept": "application/vnd.github+json"}

r = requests.get("https://api.github.com/repos/chenanz/an-wallpaper/contents/index.html", headers=H, timeout=30)
if r.status_code == 200:
    import base64
    content = base64.b64decode(r.json()["content"]).decode()
    has_prefix = "an-wallpaper" in content
    print(f"index.html contains 'an-wallpaper': {has_prefix}")
    if not has_prefix:
        # Re-upload
        with open("D:/风/hermes/an-app/dist/index.html", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        sha = r.json()["sha"]
        data = {"message": "fix base path", "content": b64, "branch": "main", "sha": sha}
        rr = requests.put("https://api.github.com/repos/chenanz/an-wallpaper/contents/index.html", headers=H, json=data, timeout=30)
        print(f"Re-upload: {rr.status_code}")
    else:
        print("Already has correct prefix")
else:
    print(f"status={r.status_code}")
