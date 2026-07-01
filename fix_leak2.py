import json

data = open('src/data.js', 'r', encoding='utf-8').read()

# Find the line with feet_609e4d and fix game field
lines = data.split('\n')
in_leak = False
for i, line in enumerate(lines):
    if 'feet_609e4d' in line:
        # Look backwards for game field in same block
        for j in range(i-1, max(i-15, 0), -1):
            if '"game": "原神"' in lines[j] and any('feet_' in lines[k] for k in range(j, i+1)):
                lines[j] = lines[j].replace('"game": "原神"', '"game": "足社"')
                print(f'Fixed line {j+1}: 原神→足社')
                break
        break

open('src/data.js', 'w', encoding='utf-8').write('\n'.join(lines))
print('Done')
