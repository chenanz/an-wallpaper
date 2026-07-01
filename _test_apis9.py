"""Debug: test Safebooru and Zerochan API responses"""
import requests, json

# Test Safebooru with exact working URL format
print("=== Safebooru debug ===")
# The test script used this format and it worked: params dict
url = "https://safebooru.org/index.php"
params = {
    "page": "dapi",
    "s": "post",
    "q": "index",
    "json": "1",
    "tags": "foot_focus 1girl",
    "limit": "5",
    "pid": "0",
}
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
r = requests.get(url, params=params, timeout=15, headers=headers)
print(f"Status: {r.status_code}")
print(f"Content-Type: {r.headers.get('content-type', '')}")
print(f"Content length: {len(r.text)}")
print(f"First 300 chars: {r.text[:300]}")
print(f"URL called: {r.url}")

# Also try the URL format from test (with +)
print()
print("=== Safebooru with + in tags ===")
params2 = {
    "page": "dapi",
    "s": "post",
    "q": "index",
    "json": "1",
    "tags": "foot_focus+1girl",
    "limit": "5",
    "pid": "0",
}
r2 = requests.get(url, params=params2, timeout=15, headers=headers)
print(f"Status: {r2.status_code}")
print(f"Content length: {len(r2.text)}")
print(f"First 300 chars: {r2.text[:300]}")
print(f"URL called: {r2.url}")

# Zerochan debug
print()
print("=== Zerochan debug ===")
z_url = "https://www.zerochan.net/Feet,Anime?json=1&p=1"
z_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://www.zerochan.net/",
}
r3 = requests.get(z_url, timeout=15, headers=z_headers)
print(f"Status: {r3.status_code}")
print(f"Content-Type: {r3.headers.get('content-type', '')}")
print(f"Content length: {len(r3.text)}")
print(f"First 300 chars: {r3.text[:300]}")

# The working test used "Accept: application/json" header
# Let's check what's different
print()
print("=== Check if crawl_feet.py has the right headers ===")
