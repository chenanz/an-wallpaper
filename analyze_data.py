"""Analyze data.js for feet entries"""
import json, re

with open('src/data.js', 'r', encoding='utf-8') as f:
    c = f.read()

m = re.search(r'export const wallpaperData = (\[.*\]);', c, re.DOTALL)
d = json.loads(m.group(1))

print('Total:', len(d))
feet = [x for x in d if x.get('game') == '足社']
print('Feet game:', len(feet))
chars = set(x['characterName'] for x in feet)
print('Feet chars:', sorted(chars))
print('---')
other_feet = [x for x in d if x.get('imageFile','').startswith('feet_') and x.get('game') != '足社']
print('Feet images in wrong game:', len(other_feet))
if other_feet:
    for x in other_feet:
        print(f"  id={x['id']} game={x['game']} file={x['imageFile']}")
games = set(x['game'] for x in d)
print('Games:', sorted(games))
# Count per game
from collections import Counter
gc = Counter(x['game'] for x in d)
print('Game counts:', gc.most_common())
