import urllib.request
import json

# Search GitHub for lofter scrapers
repos = [
    "nickliqian/lofter-crawler",
    "YunZhiFord/LofterCrawler",
    "maplestage/lofter-scraper",
    "lamfeeling/Lofter-Scraper",
]

for repo in repos:
    try:
        url = f"https://api.github.com/repos/{repo}"
        req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.v3+json", "User-Agent": "Python"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            branch = data.get('default_branch', 'main')
            print(f"Found repo: {repo} (branch: {branch})")
            
            # Try to get tree
            tree_url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
            req2 = urllib.request.Request(tree_url, headers={"Accept": "application/vnd.github.v3+json", "User-Agent": "Python"})
            with urllib.request.urlopen(req2, timeout=10) as resp2:
                tree_data = json.loads(resp2.read())
                py_files = [t['path'] for t in tree_data.get('tree', []) if t['path'].endswith('.py')]
                print(f"  Python files: {py_files}")
                
                # Get content of first python file
                for pf in py_files[:3]:
                    raw_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{pf}"
                    req3 = urllib.request.Request(raw_url, headers={"User-Agent": "Python"})
                    try:
                        with urllib.request.urlopen(req3, timeout=10) as resp3:
                            content = resp3.read().decode('utf-8', errors='replace')
                            print(f"\n  === {pf} ({len(content)} chars) ===")
                            # Look for API URLs
                            import re
                            urls_found = re.findall(r'https?://[a-zA-Z0-9._:/-]*lofter[a-zA-Z0-9._:/\-?=&]*', content)
                            if urls_found:
                                print(f"  Lofter URLs: {list(set(urls_found))[:10]}")
                            api_patterns = re.findall(r'(?:searchPost|tagPosts|searchBlog|postDetail|blogPosts)[a-zA-Z._/-]*', content)
                            if api_patterns:
                                print(f"  API patterns: {list(set(api_patterns))[:10]}")
                            print(content[:3000])
                    except Exception as e3:
                        print(f"  Error fetching {pf}: {e3}")
    except Exception as e:
        print(f"Error with {repo}: {e}")

