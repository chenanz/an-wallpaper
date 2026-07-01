import re, os, json
from collections import Counter

# Read old fixed data (105 non-足社 + 60 足社 = 165)
old_data = open('D:/风/hermes/an-app/old_data_fixed.js', 'r', encoding='utf-8').read()
local_files = set(os.listdir('public/images/'))

# Extract entries by splitting on the pattern
# Each entry starts with { and ends with }
# Use a state machine to properly parse nested braces
def extract_entries(text):
    """Extract individual JSON object strings from array"""
    entries = []
    start = text.find('[')
    if start < 0:
        return entries
    
    i = start + 1
    while i < len(text):
        # Find next {
        brace_start = text.find('{', i)
        if brace_start < 0:
            break
        
        # Find matching }
        depth = 0
        j = brace_start
        while j < len(text):
            if text[j] == '{':
                depth += 1
            elif text[j] == '}':
                depth -= 1
                if depth == 0:
                    entries.append(text[brace_start:j+1])
                    i = j + 1
                    break
            j += 1
        else:
            break
    
    return entries

# Get non-足社 entries from old data
old_entries = extract_entries(old_data.split('wallpaperData')[1] if 'wallpaperData' in old_data else old_data)

non_feet = []
feet_old = []
for entry in old_entries:
    game_m = re.search(r'"game":\s*"(.*?)"', entry)
    file_m = re.search(r'"imageFile":\s*"(.*?)"', entry)
    if not game_m or not file_m:
        continue
    
    game = game_m.group(1)
    img = file_m.group(1)
    
    if img not in local_files:
        continue  # Skip entries with missing images
    
    if game == '足社':
        feet_old.append(entry)
    else:
        non_feet.append(entry)

print(f"Old data: {len(non_feet)} non-**社 + {len(feet_old)} **社 = {len(non_feet)+len(feet_old)}")

# Get current 足社 entries and fix them
cur_data = open('src/data.js', 'r', encoding='utf-8').read()
cur_entries = extract_entries(cur_data.split('wallpaperData')[1] if 'wallpaperData' in cur_data else cur_data)

fixed_feet = []
for entry in cur_entries:
    game_m = re.search(r'"game":\s*"(.*?)"', entry)
    if not game_m or game_m.group(1) != '足社':
        continue
    
    file_m = re.search(r'"imageFile":\s*"(.*?)"', entry)
    if not file_m:
        continue
    
    img = file_m.group(1)
    # Convert png→jpg reference
    if img.endswith('.png'):
        jpg_name = img.replace('.png', '.jpg')
        if jpg_name in local_files:
            img = jpg_name
            entry = entry.replace(file_m.group(0), f'"imageFile": "{jpg_name}"')
        elif img not in local_files:
            continue
    
    if img not in local_files:
        continue
    
    # Fix nsfw
    entry = re.sub(r'"nsfw:\s*false', '"nsfw": false', entry)
    entry = re.sub(r'"nsfw:\s*true', '"nsfw": true', entry)
    
    # Extract fields
    title_m = re.search(r'"title":\s*"(.*?)"', entry)
    char_m = re.search(r'"characterName":\s*"(.*?)"', entry)
    tags_m = re.search(r'"tags":\s*\[(.*?)\]', entry, re.DOTALL)
    source_m = re.search(r'"source":\s*"(.*?)"', entry)
    
    tags_str = tags_m.group(1) if tags_m else '"足社"'
    tags_list = [t.strip().strip('"').strip("'") for t in tags_str.split(',') if t.strip()]
    
    # Build clean entry
    clean = {
        "id": 0,  # placeholder
        "title": title_m.group(1) if title_m else '美少女·精选',
        "characterName": char_m.group(1) if char_m else '美少女',
        "game": "足社",
        "gender": "女",
        "style": "二次元",
        "tags": tags_list,
        "likes": 0,
        "rarity": "SSR",
        "source": source_m.group(1) if source_m else 'Safebooru',
        "nsfw": False,
        "imageFile": img
    }
    fixed_feet.append(clean)

print(f"Fixed **社 entries: {len(fixed_feet)}")

# Now build non-足社 clean entries
clean_non_feet = []
for entry in non_feet:
    # Parse fields
    id_m = re.search(r'"id":\s*(\d+)', entry)
    title_m = re.search(r'"title":\s*"(.*?)"', entry)
    char_m = re.search(r'"characterName":\s*"(.*?)"', entry)
    game_m = re.search(r'"game":\s*"(.*?)"', entry)
    gender_m = re.search(r'"gender":\s*"(.*?)"', entry)
    style_m = re.search(r'"style":\s*"(.*?)"', entry)
    tags_m = re.search(r'"tags":\s*\[(.*?)\]', entry, re.DOTALL)
    likes_m = re.search(r'"likes":\s*(\d+)', entry)
    rarity_m = re.search(r'"rarity":\s*"(.*?)"', entry)
    source_m = re.search(r'"source":\s*"(.*?)"', entry)
    file_m = re.search(r'"imageFile":\s*"(.*?)"', entry)
    
    tags_str = tags_m.group(1) if tags_m else ''
    tags_list = [t.strip().strip('"').strip("'") for t in tags_str.split(',') if t.strip()]
    
    clean = {
        "id": 0,
        "title": title_m.group(1) if title_m else '精选壁纸',
        "characterName": char_m.group(1) if char_m else '美少女',
        "game": game_m.group(1) if game_m else '原神',
        "gender": gender_m.group(1) if gender_m else '女',
        "style": style_m.group(1) if style_m else '动漫插画',
        "tags": tags_list,
        "likes": 0,
        "rarity": rarity_m.group(1) if rarity_m else 'SSR',
        "source": source_m.group(1) if source_m else '米游社',
        "nsfw": False,
        "imageFile": file_m.group(1) if file_m else ''
    }
    clean_non_feet.append(clean)

print(f"Clean non-**社: {len(clean_non_feet)}")

# Merge all and renumber IDs
all_entries = clean_non_feet + fixed_feet
for i, entry in enumerate(all_entries):
    entry['id'] = i + 1

# Collect games
games_set = set()
for e in all_entries:
    games_set.add(e['game'])

games_array = [{"id": g, "name": g} for g in sorted(games_set)]

# Write data.js
def entry_to_json(e):
    return json.dumps(e, ensure_ascii=False, indent=4)

entries_json = ',\n'.join(entry_to_json(e) for e in all_entries)

output = f'''// 自动生成：多源爬虫（米游社 + B站 + 百度图 + 官方 + 足社爬虫v3）

export const GAMES = {json.dumps(games_array, ensure_ascii=False, indent=2)}

export const STYLES = ["3D渲染", "2.5D", "动漫插画", "Live2D"];

export const wallpaperData = [
{entries_json}
]
'''

open('src/data.js', 'w', encoding='utf-8').write(output)

# Stats
feet_chars = [e['characterName'] for e in all_entries if e['game'] == '足社']
non_feet_games = [e['game'] for e in all_entries if e['game'] != '足社']

print(f"\n=== FINAL ===")
print(f"Total: {len(all_entries)}")
print(f"Non-**社: {len(clean_non_feet)} ({Counter(non_feet_games).most_common()})")
print(f"**社: {len(fixed_feet)} (角色: {Counter(feet_chars).most_common(15)})")
