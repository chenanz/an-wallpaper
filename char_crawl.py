"""
增量大爬：按角色搜索 Safebooru，获取有确定角色名的足相关图
搜索格式：角色名+series+feet/barefoot/stockings
"""
import requests, json, hashlib, os, time, io, re
from PIL import Image
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

CHAR_MAP = {
    'nahida': '纳西妲', 'hu_tao': '胡桃', 'ganyu': '甘雨', 'keqing': '刻晴',
    'raiden_shogun': '雷电将军', 'yoimiya': '宵宫', 'yae_miko': '八重神子',
    'nilou': '妮露', 'fischl': '菲谢尔', 'shenhe': '申鹤', 'eula': '优菈',
    'yelan': '夜兰', 'furina': '芙宁娜', 'arlecchino': '阿蕾奇诺',
    'kamisato_ayaka': '绫华', 'rosaria': '罗莎莉亚', 'barbara': '芭芭拉',
    'mona': '莫娜', 'kokomi': '珊瑚宫心海', 'diona': '迪奥娜',
    'sayu': '早柚', 'ningguang': '凝光', 'beidou': '北斗',
    'yaoyao': '瑶瑶', 'kuki_shinobu': '久岐忍', 'kirara': '绮良良',
    'yanfei': '烟绯', 'xiangling': '香菱', 'collei': '柯莱',
    'amber': '安柏', 'lisa': '丽莎', 'noelle': '诺艾尔',
    'sucrose': '砂糖', 'jean': '琴', 'qiqi': '七七',
    'lumine': '荧', 'paimon': '派蒙', 'venti': '温迪',
    'dehya': '迪希雅', 'faruzan': '珐露珊', 'layla': '莱依拉',
    'candace': '坎蒂丝', 'navia': '娜维娅', 'chiori': '千织',
    'sigewinne': '希格雯', 'emilie': '艾梅莉埃',
    # 星铁
    'kafka': '卡芙卡', 'himeko': '姬子', 'seele': '希儿',
    'bronya': '布洛妮娅', 'silver_wolf': '银狼', 'firefly': '流萤',
    'robin': '知更鸟', 'sparkle': '花火', 'acheron': '黄泉',
    'ruan_mei': '阮梅', 'black_swan': '黑天鹅', 'topaz': '托帕',
    'march_7th': '三月七', 'herta': '黑塔', 'huohuo': '藿藿',
    'bailu': '白露', 'jingliu': '镜流', 'qingque': '青雀',
    'serval': '希露瓦', 'tingyun': '停云', 'sushang': '素裳',
    'natasha': '娜塔莎', 'pela': '佩拉', 'lynx': '玲可',
    'guinaifen': '桂乃芬', 'asta': '艾丝妲', 'jade': '翡翠',
    # 方舟
    'amiya': '阿米娅', 'texas': '德克萨斯', 'exusiai': '能天使',
    'angelina': '安洁莉娜', 'skadi': '斯卡蒂', 'specter': '幽灵鲨',
    'mudrock': '泥岩', 'blaze': '煌', 'saria': '塞雷娅',
    'lappland': '拉普兰德', 'mostima': '莫斯提马', 'nian': '年',
    'dusk': '夕', 'ling': '令', 'kal_tsit': '凯尔希',
    # BA
    'hoshino': '星野', 'nonomi': '野宫', 'iroha': '伊吕波',
    'aru': '阿露', 'alice': '爱丽丝', 'mika': '米卡',
    'shiroko': '白子', 'hina': '日奈', 'hanako': '花子',
    'hasumi': '莲见', 'mashiro': '真白', 'momoi': '桃井',
    'asuna': '明日奈', 'karin': '花凛', 'yuuka': '优香',
    # 绝区零
    'anby_demara': '安比', 'nicole_demara': '妮可', 'ellen_joe': '艾莲',
    'zhu_yuan': '朱鸢', 'qingyi': '青衣',
    # 通用动漫
    'zero_two': '02', 'hatsune_miku': '初音未来',
    'makima': '玛奇玛', 'mikasa_ackerman': '三笠',
    'rem_(re:zero)': '雷姆', 'emilia_(re:zero)': '艾米莉亚',
}

# 角色库存搜索列表: (search_tags, char_name)
SEARCHES = []
for eng, cn in CHAR_MAP.items():
    # feet
    SEARCHES.append((f'{eng} feet rating:safe', cn))
    # barefoot
    SEARCHES.append((f'{eng} barefoot rating:safe', cn))

TAG_ZH = {
    'barefoot': '裸足', 'soles': '脚底', 'toes': '脚趾',
    'foot_focus': '足特写', 'feet': '裸足', 'stockings': '黑丝',
    'black_thighhighs': '黑丝', 'white_thighhighs': '白丝',
    'thighhighs': '过膝袜', 'pantyhose': '连裤袜',
    'kneesocks': '膝上袜', 'socks': '短袜', 'bare_legs': '裸腿',
}

local_files = set(os.listdir('public/images/'))
downloaded = 0
skipped = 0
results = []  # (filename, char_name, tags_list)

for search_tags, char_name in SEARCHES:
    try:
        url = "https://safebooru.org/index.php"
        params = {
            'page': 'dapi', 's': 'post', 'q': 'index',
            'tags': search_tags, 'limit': 40, 'pid': 0, 'json': 1
        }
        r = requests.get(url, params=params, timeout=15)
        if r.status_code != 200 or not r.text.strip():
            continue
        posts = r.json()
        if not isinstance(posts, list):
            continue
        
        count = 0
        for post in posts:
            if not isinstance(post, dict):
                continue
            file_url = post.get('file_url', '')
            if not file_url:
                continue
            w = post.get('width', 0) or 0
            h = post.get('height', 0) or 0
            if w <= 500 or h <= 800 or h <= w:
                continue
            
            img_hash = hashlib.md5(file_url.encode()).hexdigest()[:6]
            fname = f"feet_{img_hash}.jpg"
            if fname in local_files:
                skipped += 1
                continue
            
            try:
                ir = requests.get(file_url, timeout=20)
                if ir.status_code != 200 or len(ir.content) < 10000:
                    continue
                img = Image.open(io.BytesIO(ir.content)).convert('RGB')
                iw, ih = img.size
                if iw <= 500 or ih <= 800 or ih <= iw:
                    continue
                img.save(f'public/images/{fname}', 'JPEG', quality=90)
                local_files.add(fname)
                
                # Build tags
                raw_tags = post.get('tags', '').split()
                tags_zh = ['足社']
                for t in raw_tags:
                    if t in TAG_ZH and TAG_ZH[t] not in tags_zh:
                        tags_zh.append(TAG_ZH[t])
                if len(tags_zh) == 1:
                    tags_zh.append('裸足')
                
                results.append((fname, char_name, tags_zh[:5]))
                downloaded += 1
                count += 1
            except:
                continue
        
        print(f"  {char_name}: +{count}")
        time.sleep(0.3)
    except Exception as e:
        print(f"  {char_name}: ERR {e}")

print(f"\nDownloaded: {downloaded}, Skipped (exists): {skipped}")

# Now append to data.js
data_js = open('src/data.js', 'r', encoding='utf-8').read()
start = data_js.find('export const wallpaperData = [')
end = data_js.rfind(']')
array_start = data_js.find('[', start)
entries = json.loads(data_js[array_start:end+1])

next_id = max(e['id'] for e in entries) + 1
for fname, char_name, tags in results:
    entry = {
        "id": next_id,
        "title": f"{char_name}·{tags[-1] if len(tags) > 1 else '精选'}",
        "characterName": char_name,
        "game": "足社",
        "gender": "女",
        "style": "二次元",
        "tags": tags,
        "likes": 0,
        "rarity": "SSR",
        "source": "Safebooru",
        "nsfw": False,
        "imageFile": fname
    }
    entries.append(entry)
    next_id += 1

# Also fix existing 美少女 entries that now have matching downloaded images
# (not applicable here since new downloads are separate)

# Re-number
for i, e in enumerate(entries):
    e['id'] = i + 1

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

feet_chars = [e['characterName'] for e in entries if e.get('game') == '足社']
print(f"\n=== FINAL ===")
print(f"Total: {len(entries)}")
print(f"**社: {len([e for e in entries if e.get('game') == '足社'])}")
print(f"**社角色名: {Counter(feet_chars).most_common(25)}")
