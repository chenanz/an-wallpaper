import requests, json

token = open("D:/风/hermes/an-app/.gh_token","r").read().strip()
headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}

# Get latest successful run (second failure)
r = requests.get("https://api.github.com/repos/chenanz/an-wallpaper/actions/runs?per_page=5", headers=headers, timeout=15)
runs = r.json().get("workflow_runs", [])

for run in runs:
    if run["name"] == "Build + Deploy + Release APK" and run.get("conclusion") == "failure":
        rid = run["id"]
        print(f"Run {rid} created {run['created_at']}")
        
        # Get jobs
        jr = requests.get(f"https://api.github.com/repos/chenanz/an-wallpaper/actions/runs/{rid}/jobs", headers=headers, timeout=15)
        for job in jr.json().get("jobs", []):
            if job.get("conclusion") == "failure":
                jid = job["id"]
                print(f"  Failed job: {job['name']} (id={jid})")
                
                # Get logs
                lr = requests.get(f"https://api.github.com/repos/chenanz/an-wallpaper/actions/jobs/{jid}/logs", headers=headers, timeout=15)
                lines = lr.text.split("\n")
                # Find Gradle error
                for i, line in enumerate(lines):
                    if "FAILURE" in line or "What went wrong" in line or "error" in line.lower():
                        start = max(0, i-1)
                        end = min(len(lines), i+8)
                        for l in lines[start:end]:
                            print(f"  {l}")
                        print("  ...")
                        break
        break
