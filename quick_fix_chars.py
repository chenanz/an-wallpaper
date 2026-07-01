"""快速修复角色名：从 feet_meta.json 读取 tags 匹配中文名"""
import re, json
from collections import Counter

CHAR_MAP = {
    'nahida': '纳西妲', 'hu_tao': '胡桃', 'ganyu': '甘雨', 'keqing': '刻晴',
    'raiden_shogun': '雷电将军', 'raiden_ei': '雷电将军', 'yoimiya': '宵宫',
    'yae_miko': '八重神子', 'nilou': '妮露', 'fischl': '菲谢尔',
    'shenhe': '申鹤', 'eula': '优菈', 'yelan': '夜兰', 'furina': '芙宁娜',
    'arlecchino': '阿蕾奇诺', 'lumine': '荧', 'kamisato_ayaka': '绫华',
    'ayaka': '绫华', 'rosaria': '罗莎莉亚', 'barbara': '芭芭拉', 'mona': '莫娜',
    'sayu': '早柚', 'ningguang': '凝光', 'diona': '迪奥娜', 'qiqi': '七七',
    'sucrose': '砂糖', 'noelle': '诺艾尔', 'lisa': '丽莎', 'amber': '安柏',
    'jean': '琴', 'xiangling': '香菱', 'yanfei': '烟绯', 'collei': '柯莱',
    'kirara': '绮良良', 'kuki_shinobu': '久岐忍', 'beidou': '北斗',
    'kokomi': '珊瑚宫心海', 'sangonomiya_kokomi': '珊瑚宫心海',
    'paimon': '派蒙', 'yaoyao': '瑶瑶', 'shinobu': '忍',
    'kafka': '卡芙卡', 'himeko': '姬子', 'murata_himeko': '姬子',
    'seele': '希儿', 'bronya': '布洛妮娅', 'silver_wolf': '银狼',
    'firefly': '流萤', 'robin': '知更鸟', 'sparkle': '花火',
    'acheron': '黄泉', 'ruan_mei': '阮梅', 'black_swan': '黑天鹅',
    'topaz': '托帕', 'stelle': '星', 'march_7th': '三月七',
    'herta': '黑塔', 'natasha': '娜塔莎', 'serval': '希露瓦',
    'tingyun': '停云', 'qingque': '青雀', 'huohuo': '藿藿',
    'guinaifen': '桂乃芬', 'sushang': '素裳', 'asta': '艾丝妲',
    'pela': '佩拉', 'lynx': '玲可', 'bailu': '白露', 'jingliu': '镜流',
    'jade': '翡翠',
    'amiya': '阿米娅', 'texas': '德克萨斯', 'exusiai': '能天使',
    'angelina': '安洁莉娜', 'skadi': '斯卡蒂', 'specter': '幽灵鲨',
    'mudrock': '泥岩', 'surtr': '澄闪', 'ch_en': '陈',
    'blaze': '煌', 'saria': '塞雷娅', 'lappland': '拉普兰德',
    'mostima': '莫斯提马', 'nian': '年', 'dusk': '夕', 'ling': '令',
    'kal_tsit': '凯尔希',
    'hoshino': '星野', 'nonomi': '野宫', 'iroha': '伊吕波',
    'aru': '阿露', 'mika': '米卡', 'alice': '爱丽丝',
    'saki': '纱纪', 'tsubaki': '椿', 'miyako': '都子',
    'shiroko': '白子', 'hasumi': '莲见', 'hina': '日奈',
    'hanako': '花子', 'mashiro': '真白', 'momoi': '桃井',
    'midori': '翠', 'yuzu': '柚子', 'noa': '诺亚', 'yuuka': '优香',
    'asuna': '明日奈', 'karin': '花凛', 'neru': '妮露',
    'anby': '安比', 'nicole': '妮可', 'ellen': '艾莲',
    'zhu_yuan': '朱鸢', 'qingyi': '青衣', 'jane_doe': '简·杜',
    'miyabi': '雅', 'yanagi': '柳', 'burnice': '柏妮思',
    'zero_two': '02', 'hatsune_miku': '初音未来', 'miku': '初音未来',
    'rem': '雷姆', 'emilia': '艾米莉亚', 'megumin': '惠惠',
    'makima': '玛奇玛', 'kobeni': '小花',
    'tohru': '托尔', 'kanna': '康娜', 'lucoa': '露科亚',
    'mikasa': '三笠', 'saber': 'Saber', 'rin_tohsaka': '远坂凛',
    'sakura_matou': '间桐樱', 'illyasviel': '伊莉雅',
    # extra: common booru character tags
    'venti': '温迪', 'venti_(genshin_impact)': '温迪',
    'diona_(genshin_impact)': '迪奥娜', 'hu_tao_(genshin_impact)': '胡桃',
    'wanderer': '流浪者', 'alhaitham': '艾尔海森',
    'tighnari': '提纳里', 'cyno': '赛诺', 'candace': '坎蒂丝',
    'dehya': '迪希雅', 'faruzan': '珐露珊', 'layla': '莱依拉',
    'collei_(genshin_impact)': '柯莱',
    'lynette': '琳妮特', 'lyney': '林尼', 'freminet': '菲米尼',
    'navia': '娜维娅', 'charlotte': '夏洛蒂', 'chiori': '千织',
    'sigewinne': '希格雯', 'emilie': '艾梅莉埃',
    'xilonen': '希诺宁', 'citlali': '茜特菈莉', 'mavuika': '玛薇卡',
    'chasca': '恰斯卡',
    # Star rail continued
    'bailu_(honkai:_star_rail)': '白露',
    'march_7th_(honkai:_star_rail)': '三月七',
    'hanya': '寒鸦', 'yukong': '驭空', 'fuxuan': '符玄',
    'luocha': '罗刹', 'jingyuan': '景元', 'dan_heng': '丹恒',
    'blade': '刃', 'sam': '萨姆',
}

def match_char(tags_str):
    """从 booru tags 中提取角色中文名"""
    tags = tags_str.split() if isinstance(tags_str, str) else []
    for tag in tags:
        # Try direct match first
        if tag in CHAR_MAP:
            return CHAR_MAP[tag]
        # Character tag format: name_(series)
        m = re.match(r'^([a-z_]+?)_\((.+?)\)$', tag)
        if m:
            char_key = m.group(1)
            if char_key in CHAR_MAP:
                return CHAR_MAP[char_key]
        # Try without series suffix
        base = tag.split('_(')[0] if '_(' in tag else tag
        if base in CHAR_MAP:
            return CHAR_MAP[base]
    return None

# Load meta
raw = json.load(open('feet_meta.json', 'r', encoding='utf-8'))
meta = {item.get('filename', str(i)): item for i, item in enumerate(raw)}

# Build file→character mapping (key = base name without extension)
file_to_char = {}
for file_id, info in meta.items():
    if isinstance(info, dict) and 'tags' in info:
        tags = info['tags']
        char = match_char(tags)
        if char:
            fn = info.get('filename', '')
            if fn:
                base = fn.rsplit('.', 1)[0] if '.' in fn else fn
                file_to_char[base] = char

print(f"Matched {len(file_to_char)} characters from meta")

# Parse data.js
data_js = open('src/data.js', 'r', encoding='utf-8').read()
start = data_js.find('export const wallpaperData = [')
end = data_js.rfind(']')
array_start = data_js.find('[', start)
array_text = data_js[array_start:end+1]

entries = json.loads(array_text)
print(f"Parsed {len(entries)} entries")

# Fix character names
fixed = 0
for entry in entries:
    if entry.get('game') == '足社' and entry.get('characterName') == '美少女':
        fn = entry.get('imageFile', '')
        if fn in file_to_char:
            entry['characterName'] = file_to_char[fn]
            entry['title'] = entry['title'].replace('美少女', entry['characterName'])
            fixed += 1
        else:
            base = fn.rsplit('.', 1)[0] if '.' in fn else fn
            if base in file_to_char:
                entry['characterName'] = file_to_char[base]
                entry['title'] = entry['title'].replace('美少女', entry['characterName'])
                fixed += 1

print(f"Fixed {fixed} character names")

# Re-number
for i, e in enumerate(entries):
    e['id'] = i + 1

# Rebuild data.js
games_set = sorted(set(e['game'] for e in entries))
games_arr = [{"id": g, "name": g} for g in games_set]

entries_json = json.dumps(entries, ensure_ascii=False, indent=2)

output = f'''// 自动生成：多源爬虫（米游社 + B站 + 百度图 + 官方 + 足社爬虫v3）

export const GAMES = {json.dumps(games_arr, ensure_ascii=False, indent=2)}

export const STYLES = ["3D渲染", "2.5D", "动漫插画", "Live2D"];

export const wallpaperData = {entries_json}

export function getFallbackImageUrl(id, w = 400, h = 712) {{
  return `https://picsum.photos/seed/an_${{id}}/${{w}}/${{h}}`;
}}
'''

open('src/data.js', 'w', encoding='utf-8').write(output)

# Stats
feet_chars = [e['characterName'] for e in entries if e.get('game') == '足社']
print(f"\n=== RESULT ===")
print(f"Total: {len(entries)}")
print(f"**社: {len([e for e in entries if e.get('game') == '足社'])}")
print(f"Fixed: {fixed}")
print(f"**社角色名: {Counter(feet_chars).most_common(20)}")
