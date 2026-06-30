import requests
import re
import json
import html
import urllib.parse

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://cn.bing.com/",
}

# Test: Bing Image Search with Lofter site filter AND with generic anime queries
queries = [
    "原神同人壁纸 site:lofter.com",
    "原神同人壁纸",
    "崩坏星穹铁道同人壁纸",
    "明日方舟同人壁纸",
]

for q in queries:
    params = urllib.parse.urlencode({
        "q": q,
        "first": 1,
        "count": 10,
        "qft": "+filterui:photo-photo+filterui:aspect-tall",
    })
    url = f"https://cn.bing.com/images/async?{params}"
    try:
        r = requests.get(url, headers=headers, timeout=15)
        print(f"\nQuery: {q}")
        if r.status_code == 200:
            m_data = re.findall(r'm="({.*?})"', r.text)
            print(f"  Results: {len(m_data)}")
            lofter_count = 0
            for block in m_data[:5]:
                try:
                    unescaped = html.unescape(block)
                    j = json.loads(unescaped)
                    murl = j.get('murl', '')
                    surl = j.get('surl', '')
                    desc = j.get('t', '')
                    print(f"  murl: {murl[:70]}")
                    print(f"  surl: {surl[:70]}")
                    print(f"  desc: {desc[:50]}")
                    if 'lofter' in murl.lower() or 'lofter' in surl.lower() or 'lf127' in murl.lower():
                        lofter_count += 1
                    print()
                except:
                    pass
            if 'site:lofter' in q:
                print(f"  Lofter images: {lofter_count}/{len(m_data)}")
    except Exception as e:
        print(f"  Error: {e}")

# Also test with portrait/vertical image filter
print("\n\n=== Testing portrait filter ===")
params = urllib.parse.urlencode({
    "q": "原神同人壁纸",
    "first": 1, 
    "count": 15,
    "qft": "+filterui:photo-photo+filterui:aspect-tall+filterui:imagesize-large",
})
url = f"https://cn.bing.com/images/async?{params}"
try:
    r = requests.get(url, headers=headers, timeout=15)
    m_data = re.findall(r'm="({.*?})"', r.text)
    print(f"Portrait results: {len(m_data)}")
    for block in m_data[:5]:
        try:
            unescaped = html.unescape(block)
            j = json.loads(unescaped)
            murl = j.get('murl', '')
            desc = j.get('t', '')
            # Check image dimensions if available
            w = j.get('mw', 0)
            h = j.get('mh', 0)
            print(f"  {w}x{h} | {desc[:40]} | {murl[:60]}")
        except:
            pass
except Exception as e:
    print(f"Error: {e}")

