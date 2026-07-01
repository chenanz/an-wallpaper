import re
from collections import Counter

data = open('src/data.js', 'r', encoding='utf-8').read()
games = re.findall(r'"game":\s*"(.*?)"', data)
print("按game分布:")
for g, c in Counter(games).most_common():
    print(f'  {g}: {c}')

# **社角色名
entries = re.findall(r'"game":\s*"足社".*?"characterName":\s*"(.*?)"', data, re.DOTALL)
print(f"\n**社角色名 (共{len(entries)}条):")
for n, c in Counter(entries).most_common(20):
    print(f'  {n}: {c}')

# 非足社但有feet_图片
leaked = re.findall(r'"game":\s*"(?!足社)(.*?)".*?"imageFile":\s*"(feet_.*?)"', data, re.DOTALL)
print(f"\n泄露(非**社但有feet_图): {len(leaked)}")
for g, f in leaked[:5]:
    print(f'  game={g} file={f}')
