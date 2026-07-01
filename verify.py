#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re, json

with open(r'D:\风\hermes\an-app\src\data.js', 'r', encoding='utf-8') as f:
    content = f.read()

m = re.search(r'export const wallpaperData = (\[.*\]);', content, re.DOTALL)
if m:
    txt = m.group(1)
    clean = re.sub(r',\s*}', '}', txt)
    clean = re.sub(r',\s*]', ']', clean)
    data = json.loads(clean)
    print(f'wallpaperData 解析成功: {len(data)} 条')
    
    game_counts = {}
    char_counts = {}
    for e in data:
        g = e.get('game', '未知')
        game_counts[g] = game_counts.get(g, 0) + 1
        c = e.get('characterName', '未知')
        if g == '足社':
            char_counts[c] = char_counts.get(c, 0) + 1
    
    print('按游戏统计:')
    for g, c in sorted(game_counts.items()):
        print(f'  {g}: {c}')
    
    print('\n足社角色名分布 (前20):')
    for c, n in sorted(char_counts.items(), key=lambda x: -x[1])[:20]:
        print(f'  {c}: {n}')
else:
    print('找不到 wallpaperData')
