"""
反查 Safebooru API 获取每张 feet_ 图片的真实 character 标签，
用完整映射表转中文名，直接修改 data.js
"""
import re, json, requests, os, time, hashlib
from collections import Counter

# ===== 完整角色英文名→中文映射表 =====
CHAR_MAP = {
    # 原神
    'nahida': '纳西妲', 'hu_tao': '胡桃', 'ganyu': '甘雨', 'keqing': '刻晴',
    'raiden_shogun': '雷电将军', 'raiden_ei': '雷电将军', 'yoimiya': '宵宫',
    'yae_miko': '八重神子', 'nilou': '妮露', 'fischl': '菲谢尔',
    'shenhe': '申鹤', 'eula': '优菈', 'yelan': '夜兰', 'furina': '芙宁娜',
    'arlecchino': '阿蕾奇诺', 'lumine': '荧', 'aether': '空',
    'kamisato_ayaka': '绫华', 'ayaka': '绫华', 'rosaria': '罗莎莉亚',
    'barbara': '芭芭拉', 'mona': '莫娜', 'sayu': '早柚', 'ningguang': '凝光',
    'diona': '迪奥娜', 'qiqi': '七七', 'sucrose': '砂糖', 'noelle': '诺艾尔',
    'lisa': '丽莎', 'amber': '安柏', 'jean': '琴', 'xiangling': '香菱',
    'yanfei': '烟绯', 'collei': '柯莱', 'kirara': '绮良良',
    'kuki_shinobu': '久岐忍', 'beidou': '北斗', 'xingqiu': '行秋',
    'chongyun': '重云', 'xinyan': '辛焱', 'sara': '九条裟罗',
    'yoimiya': '宵宫', 'shinobu': '忍', 'layla': '莱依拉',
    'faruzan': '珐露珊', 'candace': '坎蒂丝', 'collei': '柯莱',
    'dehya': '迪希雅', 'mika': '米卡', 'kaveh': '卡维',
    'baizhu': '白术', 'lynette': '琳妮特', 'freminet': '菲米尼',
    'lyney': '林尼', 'navia': '娜维娅', 'chevreuse': '夏沃蕾',
    'charlotte': '夏洛蒂', 'cloud_retainer': '留云借风真君',
    'gaming': '嘉明', 'chiori': '千织', 'sigewinne': '希格雯',
    'emilie': '艾梅莉埃', 'sethos': '赛索斯', 'kachina': '卡齐娜',
    'xilonen': '希诺宁', 'citlali': '茜特菈莉', 'mavuika': '玛薇卡',
    'mualani': '玛拉妮', 'kinich': '基尼奇', 'ororon': '欧洛伦',
    'chasca': '恰斯卡', 'iana': '伊安珊',
    'paimon': '派蒙', 'dainsleif': '戴因斯雷布',
    'la_signora': '女士', 'tsaritsa': '冰之女皇',
    'yaoyao': '瑶瑶', 'shenhe': '申鹤', 'yelan': '夜兰',
    'kokomi': '珊瑚宫心海', 'sangonomiya_kokomi': '珊瑚宫心海',
    'raiden_mei': '雷电芽衣', 'yae_sakura': '八重樱',
    # 星铁
    'kafka': '卡芙卡', 'himeko': '姬子', 'murata_himeko': '姬子',
    'seele': '希儿', 'bronya': '布洛妮娅', 'silver_wolf': '银狼',
    'firefly': '流萤', 'robin': '知更鸟', 'sparkle': '花火',
    'acheron': '黄泉', 'ruan_mei': '阮梅', 'black_swan': '黑天鹅',
    'topaz': '托帕', 'stelle': '星', 'caelus': '穹',
    'march_7th': '三月七', 'herta': '黑塔', 'natasha': '娜塔莎',
    'serval': '希露瓦', 'tingyun': '停云', 'yukong': '驭空',
    'qingque': '青雀', 'fuxuan': '符玄', 'luofu': '罗浮',
    'linxueyi': '藿藿', 'huohuo': '藿藿', 'guinaifen': '桂乃芬',
    'sushang': '素裳', 'yukong': '驭空', 'astar': '艾丝妲',
    'asta': '艾丝妲', 'pela': '佩拉', 'lynx': '玲可',
    'drupe': '弗兰明', 'bailu': '白露', 'jingliu': '镜流',
    'feixiao': '飞霄', 'mihua': '迷幻', 'luka': '卢卡',
    'yukong': '驭空', 'xueyi': '雪衣', 'misha': '米沙',
    'danheng': '丹恒', 'bladeland': '刃', 'jade': '翡翠',
    'boyan': '波提欧', 'lignue': '云璃', 'moze': '貊泽',
    # 方舟
    'amiya': '阿米娅', 'texas': '德克萨斯', 'exusiai': '能天使',
    'angelina': '安洁莉娜', 'skadi': '斯卡蒂', 'specter': '幽灵鲨',
    'mudrock': '泥岩', 'surtr': '澄闪', 'ch_en': '陈',
    'ch_en_the_holungday': '陈', 'exusiai': '能天使',
    'blaze': '煌', 'ifrit': '伊芙利特', 'magallan': '麦哲伦',
    'magallanica': '麦哲伦', 'saria': '塞雷娅', 'siesta': '睡神',
    'shamare': '巫恋', 'swire': '诗怀雅', 'lappland': '拉普兰德',
    'mostima': '莫斯提马', 'exusiai': '能天使', 'saga': '嵯峨',
    ' meticulously': '谜图', 'nian': '年', 'dusk': '夕',
    'ling': '令', 'iris': '鸢尾', 'rosmontis': '迷迭香',
    'kal_tsit': '凯尔希', 'w': 'W', 'hoederer': '赫德雷',
    'ines': '伊内丝', 'virtuosa': '织芸', 'muelsyse': "缪尔赛思",
    # 蔚蓝档案 BA
    'hoshino': '星野', 'nonomi': '野宫', 'iroha': '伊吕波',
    'aru': '阿露', 'mika': '米卡', 'alice': '爱丽丝',
    'saki': '纱纪', 'tsubaki': '椿', 'miyako': '都子',
    'shiroko': '白子', 'ayane': '绫音', 'hasumi': '莲见',
    'hina': '日奈', 'hanako': '花子', 'mashiro': '真白',
    'haruka': '遥香', 'serika': '芹香', 'akane': '茜',
    'chinatsu': '千夏', 'kotama': '小玉', 'junko': '纯子',
    'momoi': '桃井', 'midori': '翠', 'yuzu': '柚子',
    'noa': '诺亚', 'yuuka': '优香', 'asuna': '明日奈',
    'karin': '花凛', 'neru': '妮露', 'toki': '时雨',
    'hatsune': '初音', 'shun': '瞬', 'koharu': '小春',
    'hanako_(blue_archive)': '花子', 'himari': '日鞠',
    # 绝区零
    'anby': '安比', 'nicole': '妮可', 'ellen': '艾莲',
    'zhu_yuan': '朱鸢', 'qingyi': '青衣', 'jane_doe': '简·杜',
    'nornis': '伯尼斯', 'seth': '赛斯', 'hoshino_(zzz)': '星见雅',
    'miyabi': '雅', 'harumasa': '晴雅', 'yanagi': '柳',
    'burnice': '柏妮思', 'lighter': '莱特',
    # 其他常见动漫角色
    'zero_two': '02', 'hatsune_miku': '初音未来', 'miku': '初音未来',
    'rem_(re_zero)': '雷姆', 'ram_(re_zero)': '拉姆',
    'emilia': '艾米莉亚', 'megumin': '惠惠', 'aqua_(konosuba)': '阿库娅',
    'darkness': '达克妮丝', 'misato': '美里', 'rei': '丽',
    'asuka': '明日香', 'mikasa': '三笠', 'saber': 'Saber',
    'rin_tohsaka': '远坂凛', 'sakura_matou': '间桐樱',
    'illyasviel': '伊莉雅', 'ishtar': '伊什塔尔',
    'tohru': '托尔', 'kanna': '康娜', 'lucoa': '露科亚',
    'elma': '艾尔玛', 'saiko': '赛子',
    'makima': '玛奇玛', 'power_(chainsaw_man)': '帕瓦',
    'kobeni': '小花', 'denji': '电次',
    'zero_two': '02', 'ichigo': '莓', 'goko': '五条',
}

# 游戏名映射
GAME_MAP = {
    'genshin_impact': '原神', 'honkai_star_rail': '崩坏：星穹铁道',
    'honkai:_star_rail': '崩坏：星穹铁道', 'arknights': '明日方舟',
    'blue_archive': '蔚蓝档案', 'zenless_zone_zero': '绝区零',
    'fate/series': 'Fate', 'fate_grand_order': 'Fate/GO',
    'chainsaw_man': '电锯人', 'darling_in_the_franxx': 'DARLING',
    'kono_subarashii_sekai_ni_shukufuku_wo': '为美好的世界献上祝福',
    'miss_kobayashi_dragon_maid': '小林家的龙女仆',
    'neon_genesis_evangelion': 'EVA', 'attack_on_titan': '进击的巨人',
}

def match_char(tags_str):
    """从 booru tags 中提取角色中文名"""
    tags = tags_str.split()
    for tag in tags:
        # Character tag format: name_(series)
        m = re.match(r'^([a-z_]+?)_\((.+?)\)$', tag)
        if m:
            char_key = m.group(1)
            if char_key in CHAR_MAP:
                return CHAR_MAP[char_key]
        # Direct match
        if tag in CHAR_MAP:
            return CHAR_MAP[tag]
        # Try without suffixes
        base = tag.split('_(')[0] if '_(' in tag else tag
        if base in CHAR_MAP:
            return CHAR_MAP[base]
    return None

# Read current data.js
data_js = open('src/data.js', 'r', encoding='utf-8').read()

# Find all 足社 entries with characterName="美少女"
# First, collect all feet_ imageFiles that need character name lookup
feet_files = re.findall(r'"imageFile":\s*"(feet_\w+\.\w+)"', data_js)
print(f"Found {len(feet_files)} feet_ images in data.js")

# Build a file→metadata lookup by querying Safebooru for each image's hash
# Since we can't reverse-lookup by file, we'll re-query Safebooru with tags
# and match by file_url MD5

# Actually, let's check feet_meta.json from the previous crawler run
meta = {}
if os.path.exists('feet_meta.json'):
    try:
        raw = json.load(open('feet_meta.json', 'r', encoding='utf-8'))
        if isinstance(raw, list):
            meta = {item.get('filename', str(i)): item for i, item in enumerate(raw)}
        else:
            meta = raw
        print(f"Loaded feet_meta.json: {len(meta)} entries")
    except:
        print("Failed to load feet_meta.json")

# Build imageFile → characterName mapping
file_to_char = {}
for file_id, info in meta.items():
    if isinstance(info, dict) and 'tags' in info:
        tags = info['tags']
        char = match_char(tags)
        if char:
            fn = info.get('filename', info.get('imageFile', ''))
            # The filename in meta might not have extension matching data.js
            # Store mapping by both with and without extension
            if fn:
                file_to_char[fn] = char
                base = fn.rsplit('.', 1)[0] if '.' in fn else fn
                file_to_char[base] = char

print(f"Matched {len(file_to_char)} characters from meta")

# Also try to match by looking at the existing tags in data.js entries
# and using Safebooru API to get more character tags

# For remaining "美少女" entries, try specific character+feet searches on Safebooru
# This will give us known characters with feet art

CHARACTER_SEARCHES = [
    ('nahida_(genshin_impact) feet', '纳西妲'),
    ('hu_tao_(genshin_impact) feet', '胡桃'),
    ('ganyu_(genshin_impact) barefoot', '甘雨'),
    ('keqing_(genshin_impact) feet', '刻晴'),
    ('raiden_shogun_(genshin_impact) feet', '雷电将军'),
    ('yoimiya_(genshin_impact) feet', '宵宫'),
    ('yae_miko_(genshin_impact) feet', '八重神子'),
    ('nilou_(genshin_impact) barefoot', '妮露'),
    ('fischl_(genshin_impact) feet', '菲谢尔'),
    ('shenhe_(genshin_impact) barefoot', '申鹤'),
    ('eula_(genshin_impact) feet', '优菈'),
    ('furina_(genshin_impact) feet', '芙宁娜'),
    ('arlecchino_(genshin_impact) feet', '阿蕾奇诺'),
    ('kamisato_ayaka_(genshin_impact) feet', '绫华'),
    ('barbara_(genshin_impact) barefoot', '芭芭拉'),
    ('mona_(genshin_impact) feet', '莫娜'),
    ('kokomi_(genshin_impact) feet', '珊瑚宫心海'),
    ('kafka_(honkai:_star_rail) feet', '卡芙卡'),
    ('himeko_(honkai:_star_rail) feet', '姬子'),
    ('seele_(honkai:_star_rail) feet', '希儿'),
    ('silver_wolf_(honkai:_star_rail) feet', '银狼'),
    ('firefly_(honkai:_star_rail) feet', '流萤'),
    ('robin_(honkai:_star_rail) feet', '知更鸟'),
    ('sparkle_(honkai:_star_rail) feet', '花火'),
    ('acheron_(honkai:_star_rail) feet', '黄泉'),
    ('skadi_(arknights) feet', '斯卡蒂'),
    ('angelina_(arknights) feet', '安洁莉娜'),
]

# Download more character-specific images
new_downloads = []
downloaded_hashes = set(os.listdir('public/images/'))

for search_tags, char_name in CHARACTER_SEARCHES:
    try:
        url = "https://safebooru.org/index.php"
        params = {
            'page': 'dapi',
            's': 'post',
            'q': 'index',
            'tags': search_tags + ' rating:safe',
            'limit': 40,
            'pid': 0,
            'json': 1
        }
        r = requests.get(url, params=params, timeout=15)
        posts = r.json() if r.text.strip() else []
        
        valid = 0
        for post in posts:
            if not isinstance(post, dict):
                continue
            file_url = post.get('file_url', '')
            if not file_url:
                continue
            
            # Get dimensions
            w = post.get('width', 0) or 0
            h = post.get('height', 0) or 0
            if w <= 500 or h <= 800 or h <= w:
                continue
            
            # Generate filename and check dedup
            img_hash = hashlib.md5(file_url.encode()).hexdigest()[:6]
            ext = file_url.rsplit('.', 1)[-1].split('?')[0]
            if ext not in ('jpg', 'jpeg', 'png', 'webp'):
                ext = 'jpg'
            fname = f"feet_{img_hash}.jpg"
            if fname in downloaded_hashes:
                continue
            
            # Download
            try:
                ir = requests.get(file_url, timeout=20)
                if ir.status_code != 200 or len(ir.content) < 10000:
                    continue
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(ir.content)).convert('RGB')
                fname = f"feet_{img_hash}.jpg"
                img.save(f'public/images/{fname}', 'JPEG', quality=90)
                downloaded_hashes.add(fname)
                
                # Get tags
                tags = post.get('tags', '')
                char_found = match_char(tags) or char_name
                
                new_downloads.append({
                    'file': fname,
                    'char': char_found,
                    'tags': tags,
                    'search': search_tags,
                })
                valid += 1
            except:
                continue
        
        print(f"  {char_name}: +{valid} downloads")
        time.sleep(0.5)
    except Exception as e:
        print(f"  {char_name}: ERROR {e}")
        continue

print(f"\nTotal new character-specific downloads: {len(new_downloads)}")

# Now update data.js with:
# 1. Character names from meta data where available
# 2. New downloaded images added as new entries
# 3. Replace "美少女" where possible

# Parse data.js as JSON
data_js = open('src/data.js', 'r', encoding='utf-8').read()

# Find wallpaperData array
start = data_js.find('export const wallpaperData = [')
end = data_js.rfind(']')
if start < 0 or end < 0:
    print("ERROR: can't find wallpaperData array")
    exit(1)

# Extract the array portion
array_start = data_js.find('[', start)
array_text = data_js[array_start:end+1]

# Parse entries
try:
    entries = json.loads(array_text)
    print(f"Parsed {len(entries)} entries from data.js")
except json.JSONDecodeError as e:
    print(f"JSON parse error: {e}")
    print("Falling back to regex parsing...")
    # Try regex extraction
    entry_pattern = re.compile(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', re.DOTALL)
    raw_entries = entry_pattern.findall(array_text)
    entries = []
    for raw in raw_entries:
        try:
            e = json.loads(raw)
            entries.append(e)
        except:
            continue
    print(f"Regex parsed {len(entries)} entries")

# Fix character names from meta
fixed_count = 0
for entry in entries:
    if entry.get('game') == '足社' and entry.get('characterName') == '美少女':
        fn = entry.get('imageFile', '')
        if fn in file_to_char:
            entry['characterName'] = file_to_char[fn]
            entry['title'] = entry['title'].replace('美少女', entry['characterName'])
            fixed_count += 1
        else:
            # Try matching by base name (without extension)
            base = fn.rsplit('.', 1)[0] if '.' in fn else fn
            if base in file_to_char:
                entry['characterName'] = file_to_char[base]
                entry['title'] = entry['title'].replace('美少女', entry['characterName'])
                fixed_count += 1

print(f"Fixed {fixed_count} character names from meta")

# Try to match by tags already in entry
for entry in entries:
    if entry.get('game') == '足社' and entry.get('characterName') == '美少女':
        for tag in entry.get('tags', []):
            matched = match_char(tag)
            if matched:
                entry['characterName'] = matched
                entry['title'] = entry['title'].replace('美少女', matched)
                break

# Add new downloads
next_id = max(e['id'] for e in entries) + 1 if entries else 1

TAG_ZH = {
    'barefoot': '裸足', 'soles': '脚底', 'toes': '脚趾',
    'foot_focus': '足特写', 'feet': '裸足', 'stockings': '黑丝',
    'black_thighhighs': '黑丝', 'white_thighhighs': '白丝',
    'thighhighs': '过膝袜', 'pantyhose': '连裤袜',
    'kneesocks': '膝上袜', 'socks': '短袜', 'bare_legs': '裸腿',
    'legs': '美腿', 'sindentation': '绝对领域',
}

for dl in new_downloads:
    tags = dl['tags'].split()
    tags_zh = ['足社']
    for t in tags:
        if t in TAG_ZH:
            tags_zh.append(TAG_ZH[t])
    if len(tags_zh) == 1:
        tags_zh.append('裸足')
    
    entry = {
        "id": next_id,
        "title": f"{dl['char']}·{tags_zh[-1]}",
        "characterName": dl['char'],
        "game": "足社",
        "gender": "女",
        "style": "二次元",
        "tags": tags_zh[:5],
        "likes": 0,
        "rarity": "SSR",
        "source": "Safebooru",
        "nsfw": False,
        "imageFile": dl['file']
    }
    entries.append(entry)
    next_id += 1

print(f"Added {len(new_downloads)} new entries")

# Re-number all IDs
for i, entry in enumerate(entries):
    entry['id'] = i + 1

# Collect all games
games_set = sorted(set(e['game'] for e in entries))
games_array = [{"id": g, "name": g} for g in games_set]

# Write data.js
entries_json = json.dumps(entries, ensure_ascii=False, indent=2)

output = f'''// 自动生成：多源爬虫（米游社 + B站 + 百度图 + 官方 + 足社爬虫v3）

export const GAMES = {json.dumps(games_array, ensure_ascii=False, indent=2)}

export const STYLES = ["3D渲染", "2.5D", "动漫插画", "Live2D"];

export const wallpaperData = {entries_json}

export function getFallbackImageUrl(id, w = 400, h = 712) {{
  return `https://picsum.photos/seed/an_${{id}}/${{w}}/${{h}}`;
}}
'''

open('src/data.js', 'w', encoding='utf-8').write(output)

# Stats
feet_chars = [e['characterName'] for e in entries if e.get('game') == '足社']
non_feet_games = [e['game'] for e in entries if e.get('game') != '足社']

print(f"\n=== FINAL ===")
print(f"Total: {len(entries)}")
print(f"Non-**社: {len([e for e in entries if e.get('game') != '足社'])}")
print(f"**社: {len([e for e in entries if e.get('game') == '足社'])}")
print(f"**社角色名分布: {Counter(feet_chars).most_common(20)}")
