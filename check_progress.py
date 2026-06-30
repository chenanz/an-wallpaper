import requests, os

tok_path = "D:/风/hermes/an-app/.gh_token"
with open(tok_path, "r") as f:
    T = f.read().strip()

H = {"Authorization": "token " + T, "Accept": "application/vnd.github+json"}

r = requests.get('https://api.github.com/repos/chenanz/an-wallpaper/contents/images', headers=H, timeout=30)
n = len([x for x in r.json() if x['type']=='file']) if r.status_code==200 else 0
local = len([f for f in os.listdir('D:/风/hermes/an-app/dist/images') if f.endswith('.jpg')])
print(f'uploaded={n} local={local} remaining={local-n}')

rp = requests.get('https://api.github.com/repos/chenanz/an-wallpaper/pages', headers=H, timeout=30)
print(f'pages_status={rp.status_code}')
if rp.status_code == 200:
    d = rp.json()
    print(f'pages_url={d.get("html_url","?")}')
