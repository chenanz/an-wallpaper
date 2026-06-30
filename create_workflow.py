import requests, json, base64

tok_path = "D:/风/hermes/an-app/.gh_token"
with open(tok_path, "r") as f:
    T = f.read().strip()

H = {"Authorization": "token " + T, "Accept": "application/vnd.github+json"}
OWNER = "chenanz"
REPO = "an-wallpaper"

# 1. 切换 Pages 到 GitHub Actions 模式
r = requests.put(f"https://api.github.com/repos/{OWNER}/{REPO}/pages", headers=H,
    json={"build_type": "workflow"}, timeout=30)
print(f"Switch to workflow: {r.status_code}")
if r.status_code != 200:
    print(r.text[:300])

# 2. 创建 GitHub Actions workflow 文件
workflow = """name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup Pages
        uses: actions/configure-pages@v5
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: '.'
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
"""

workflow_b64 = base64.b64encode(workflow.encode()).decode()
path = ".github/workflows/deploy.yml"

# 检查是否已存在
rget = requests.get(f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}", headers=H, timeout=30)
data = {"message": "add GitHub Actions deploy workflow", "content": workflow_b64, "branch": "main"}
if rget.status_code == 200:
    data["sha"] = rget.json()["sha"]

r2 = requests.put(f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}", headers=H, json=data, timeout=30)
print(f"Workflow upload: {r2.status_code}")

if r2.status_code in [200, 201]:
    print("✅ workflow 上传成功! GitHub Actions 会自动构建部署")
    print("等待 1-2 分钟后访问: https://chenanz.github.io/an-wallpaper/")
else:
    print(r2.text[:300])
