import re, json

with open('D:/风/hermes/an-app/src/data.js', 'r', encoding='utf-8') as f:
    c = f.read()

# Test the same regex as the script
m = re.search(r'export const wallpaperData = (\[.*\])\s*\r?\n', c, re.DOTALL)
if m:
    try:
        d = json.loads(m.group(1))
        print(f"items={len(d)}")
    except Exception as e:
        print(f"parse error: {e}")
        # show the last 100 chars of the match to debug
        print(f"end of match: {repr(m.group(1)[-100:])}")
else:
    print("no match")
    # try simpler patterns
    m2 = re.search(r'wallpaperData = \[', c)
    print(f"wallpaperData = [ found: {bool(m2)}")
    if m2:
        print(f"at position: {m2.start()}")
