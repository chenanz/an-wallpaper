import re

data = open('src/data.js', 'r', encoding='utf-8').read()

# Fix leaked feet_4711b8.jpg entry - change game from 原神 to 足社
old = data
# Find the entry block containing feet_4711b8 and game=原神
pattern = r'(\{[^}]*"game":\s*")原神("[^}]*"imageFile":\s*"feet_4711b8[^}]*\})'
m = re.search(pattern, data, re.DOTALL)
if m:
    data = data[:m.start()] + m.group(1) + '足社' + m.group(2) + data[m.end():]
    print('Fixed: feet_4711b8 原神→足社')
else:
    print('Not found, trying simpler approach')
    # Just replace in the raw text near the file ref
    idx = data.find('feet_4711b8')
    if idx > 0:
        # Look back for game field
        chunk = data[max(0, idx-500):idx+100]
        chunk = chunk.replace('"game": "原神"', '"game": "足社"')
        data = data[:max(0, idx-500)] + chunk + data[idx+100:]
        print('Fixed via chunk replacement')

if data != old:
    open('src/data.js', 'w', encoding='utf-8').write(data)
    print('Written')
else:
    print('No changes made')
