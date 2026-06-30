import subprocess
import json
import os

# Search for lofter scraper repos via GitHub API
headers = {"Accept": "application/vnd.github.v3+json"}

# Try to find lofter crawler repos
repos_to_check = [
    "nickliqian/lofter-crawler",
    "YunZhiFord/LofterCrawler",
    "Stuairs/Lofter-Crawler",
    "Cheng안/lofter-scraper",
    "Gerapy77/lofter-downloader",
]

for repo in repos_to_check:
    try:
        url = f"https://api.github.com/repos/{repo}"
        result = subprocess.run(["curl", "-s", "-H", "Accept: application/vnd.github.v3+json", url], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            j = json.loads(result.stdout)
            if 'default_branch' in j:
                branch = j['default_branch']
                print(f"Found: {repo} (branch: {branch})")
    except:
        pass

# Let's try direct raw content fetching via curl
for repo_file in [
    ("nickliqian/lofter-crawler", "main/crawler.py"),
    ("nickliqian/lofter-crawler", "master/crawler.py"),
    ("YunZhiFord/LofterCrawler", "main/lofter_cralwer.py"),
    ("YunZhiFord/LofterCrawler", "main/crawler.py"),
]:
    repo, path = repo_file
    try:
        result = subprocess.run(
            ["curl", "-sL", f"https://raw.githubusercontent.com/{repo}/{path}"],
            capture_output=True, text=True, timeout=10
        )
        if result.stdout and len(result.stdout) > 100 and '404' not in result.stdout[:10]:
            print(f"\n===== {repo}/{path} =====")
            print(result.stdout[:5000])
    except Exception as e:
        print(f"Error: {e}")

