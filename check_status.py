import re, os
from collections import Counter

data = open('src/data.js', 'r', encoding='utf-8').read()

# Get all imageFile values
imageFiles = re.findall(r'"imageFile":\s*"(.+?)"', data)
local = set(os.listdir('public/images'))

missing = [f for f in imageFiles if f not in local]
print(f'Total entries: {len(imageFiles)}')
print(f'Local images: {len(local)}')
print(f'Missing images: {len(missing)}')
print(f'Present: {len(imageFiles) - len(missing)}')

# Check game/category distribution
games = re.findall(r'"game":\s*"(.+?)"', data)
sources = re.findall(r'"source":\s*"(.+?)"', data)
print(f'\nGames: {dict(Counter(games))}')
print(f'Sources: {dict(Counter(sources))}')

# Count missing per source
all_entries = re.findall(r'"id":\s*(\d+).*?"imageFile":\s*"(.+?)".*?"game":\s*"(.+?)".*?"source":\s*"(.+?)"', data, re.DOTALL)

# Find yuzu/足 entries
yuzu_lines = []
for line in data.split('\n'):
    if '足' in line or '黑丝' in line or '白丝' in line or '裸足' in line or '美腿' in line or '丝袜' in line:
        yuzu_lines.append(line.strip())
print(f'\n**社 related lines: {len(yuzu_lines)}')
for l in yuzu_lines[:10]:
    print(f'  {l[:100]}')
