import requests, json

token = open("D:/风/hermes/an-app/.gh_token","r").read().strip()
headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}

# Get latest runs
r = requests.get("https://api.github.com/repos/chenanz/an-wallpaper/actions/runs?per_page=3", headers=headers, timeout=15)
runs = r.json().get("workflow_runs", [])
for run in runs:
    rid = run["id"]
    name = run["name"]
    status = run["status"]
    conclusion = run.get("conclusion", "n/a")
    branch = run["head_branch"]
    print(f"{name} | branch={branch} | {status} | {conclusion}")
    
    if conclusion == "failure":
        # Get jobs
        jr = requests.get(f"https://api.github.com/repos/chenanz/an-wallpaper/actions/runs/{rid}/jobs", headers=headers, timeout=15)
        jobs = jr.json().get("jobs", [])
        for job in jobs:
            for step in job.get("steps", []):
                if step.get("conclusion") == "failure":
                    print(f"  FAILED: step #{step['number']} - {step['name']}")
        
        # Get logs
        lr = requests.get(f"https://api.github.com/repos/chenanz/an-wallpaper/actions/runs/{rid}/jobs", headers=headers, timeout=15)
        for job in lr.json().get("jobs", []):
            if job.get("conclusion") == "failure":
                log_url = f"https://api.github.com/repos/chenanz/an-wallpaper/actions/jobs/{job['id']}/logs"
                logs = requests.get(log_url, headers=headers, timeout=15)
                lines = logs.text.split("\n")
                # Find error lines
                for i, line in enumerate(lines):
                    if "error" in line.lower() or "FAIL" in line or "Error" in line:
                        start = max(0, i-2)
                        end = min(len(lines), i+3)
                        for l in lines[start:end]:
                            print(f"  {l}")
                        print("  ...")
