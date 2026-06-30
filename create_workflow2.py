import requests, json, base64

tok_path = "D:/风/hermes/an-app/.gh_token"
with open(tok_path, "r") as f:
    T = f.read().strip()

H = {"Authorization": "token " + T, "Accept": "application/vnd.github+json"}
OWNER = "chenanz"
REPO = "an-wallpaper"

# Create .gitignore first to ensure .github path works
gitignore = "node_modules/\n.env\n*.py\n.gh_token\n"
gitignore_b64 = base64.b64encode(gitignore.encode()).decode()

r0 = requests.get(f"https://api.github.com/repos/{OWNER}/{REPO}/contents/.gitignore", headers=H, timeout=30)
data0 = {"message": "add .gitignore", "content": gitignore_b64, "branch": "main"}
if r0.status_code == 200:
    data0["sha"] = r0.json()["sha"]
r0r = requests.put(f"https://api.github.com/repos/{OWNER}/{REPO}/contents/.gitignore", headers=H, json=data0, timeout=30)
print(f".gitignore: {r0r.status_code}")

# Try workflow again
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

rget = requests.get(f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}", headers=H, timeout=30)
data = {"message": "add GitHub Actions deploy workflow", "content": workflow_b64, "branch": "main"}
if rget.status_code == 200:
    data["sha"] = rget.json()["sha"]

r = requests.put(f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}", headers=H, json=data, timeout=30)
print(f"workflow: {r.status_code}")
if r.status_code in [200, 201]:
    print("SUCCESS - GitHub Actions will auto-deploy!")
else:
    print(r.text[:300])

# Verify pages mode
rp = requests.get(f"https://api.github.com/repos/{OWNER}/{REPO}/pages", headers=H, timeout=30)
if rp.status_code == 200:
    print(f"\nPages: {rp.json().get('build_type','?')} status={rp.json().get('status','?')}")
