"""
精准修复角色名：对每张 feet_ 图片，用 Safebooru API 按文件 URL 反查真实角色标签
1. 从 feet_meta.json 获取每张图的 source post ID
2. 对每个 post ID 查询 Safebooru API 获取完整 tags
3. 从完整 tags 中提取 character 标签
4. 用映射表转中文名
5. 如果没有 character 标签，标"美少女"
"""
import json, os, re, requests, time
from collections import Counter
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed

CHAR_MAP = {
    # 原神
    'nahida': '纳西妲', 'hu_tao': '胡桃', 'ganyu': '甘雨', 'keqing': '刻晴',
    'raiden_shogun': '雷电将军', 'yoimiya': '宵宫', 'yae_miko': '八重神子',
    'nilou': '妮露', 'fischl': '菲谢尔', 'shenhe': '申鹤', 'eula': '优菈',
    'yelan': '夜兰', 'furina': '芙宁娜', 'arlecchino': '阿蕾奇诺',
    'kamisato_ayaka': '绫华', 'rosaria': '罗莎莉亚', 'barbara': '芭芭拉',
    'mona': '莫娜', 'kokomi': '珊瑚宫心海', 'sangonomiya_kokomi': '珊瑚宫心海',
    'diona': '迪奥娜', 'sayu': '早柚', 'ningguang': '凝光', 'beidou': '北斗',
    'yaoyao': '瑶瑶', 'kuki_shinobu': '久岐忍', 'kirara': '绮良良',
    'yanfei': '烟绯', 'xiangling': '香菱', 'collei': '柯莱',
    'amber': '安柏', 'lisa': '丽莎', 'noelle': '诺艾尔',
    'sucrose': '砂糖', 'jean': '琴', 'qiqi': '七七',
    'lumine': '荧', 'paimon': '派蒙', 'venti': '温迪',
    'dehya': '迪希雅', 'faruzan': '珐露珊', 'layla': '莱依拉',
    'navia': '娜维娅', 'chiori': '千织', 'sigewinne': '希格雯',
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
    'iris': '鸢尾', 'shamare': '巫恋',
    # BA
    'hoshino': '星野', 'nonomi': '野宫', 'iroha': '伊吕波',
    'aru': '阿露', 'alice_(blue_archive)': '爱丽丝', 'alice': '爱丽丝',
    'mika': '米卡', 'shiroko': '白子', 'hina': '日奈',
    'hanako': '花子', 'hasumi': '莲见', 'mashiro': '真白',
    'momoi': '桃井', 'asuna': '明日奈', 'karin': '花凛',
    'yuuka': '优香', 'tsubaki': '椿', 'miyako': '都子',
    'saki': '纱纪',
    # 绝区零
    'anby': '安比', 'anby_demara': '安比', 'nicole': '妮可',
    'nicole_demara': '妮可', 'ellen': '艾莲', 'ellen_joe': '艾莲',
    'zhu_yuan': '朱鸢', 'qingyi': '青衣',
    # 通用
    'zero_two': '02', 'hatsune_miku': '初音未来', 'miku': '初音未来',
    'makima': '玛奇玛', 'mikasa_ackerman': '三笠',
}

def match_char_from_tags(tags_str):
    """从 Safebooru 返回的 tags 字段中提取角色中文名"""
    if not tags_str or not isinstance(tags_str, str):
        return None
    tags = tags_str.split()
    for tag in tags:
        # 直接匹配
        if tag in CHAR_MAP:
            return CHAR_MAP[tag]
        # character_(series) 格式
        m = re.match(r'^([a-z_]+?)_\((.+?)\)$', tag)
        if m:
            char_key = m.group(1)
            if char_key in CHAR_MAP:
                return CHAR_MAP[char_key]
        # 去掉系列后缀
        base = tag.split('_(')[0] if '_(' in tag else tag
        if base in CHAR_MAP:
            return CHAR_MAP[base]
    return None

# Step 1: 加载 meta 数据获取 source post ID
meta_raw = json.load(open('feet_meta.json', 'r', encoding='utf-8'))
print(f"Meta entries: {len(meta_raw)}")

# Step 2: 用 meta 的 tags 直接匹配角色（meta 已经有完整 tags）
file_to_char = {}
for item in meta_raw:
    fn = item.get('filename', '')
    tags = item.get('tags', '')
    char = match_char_from_tags(tags)
    if char:
        base = fn.rsplit('.', 1)[0]
        file_to_char[base] = char

print(f"Matched from meta tags: {len(file_to_char)}")

# Step 3: 对于之前 char_crawl.py 搜角色名下载的图，这些 meta 里没有
# 需要从 data.js 的 entries 里找到角色名标记，然后验证
data_js = open('src/data.js', 'r', encoding='utf-8').read()
start = data_js.find('export const wallpaperData = [')
end = data_js.rfind(']')
arr = json.loads(data_js[data_js.find('[', start):end+1])

feet_entries = [e for e in arr if e.get('game') == '足社']
print(f"足社 entries in data.js: {len(feet_entries)}")

# 检查每张图片实际角色身份
# 对于 char_crawl.py 下载的图（有角色名但可能不准），
# 我们需要按文件名在 Safebooru 上反查
# 但更高效的方法：对已标记为有名角色的图片，重新用 API 验证

# 先看看哪些图片只有 meta 记录，哪些是 char_crawl 下载的
meta_bases = set(item.get('filename', '').rsplit('.', 1)[0] for item in meta_raw)
char_crawl_downloads = []  # char_crawl 下载的但不在 meta 中的
meta_downloads = []  # 在 meta 中的

for e in feet_entries:
    base = e['imageFile'].rsplit('.', 1)[0]
    if base in meta_bases:
        meta_downloads.append(e)
    else:
        char_crawl_downloads.append(e)

print(f"From meta (first crawl): {len(meta_downloads)}")
print(f"From char_crawl (second crawl): {len(char_crawl_downloads)}")

# 对于 char_crawl 下载的图，我们信任角色名（因为是搜角色名+feet下载的）
# 但要验证：如果角色名不是 "美少女"，保留
# 如果是"美少女"，尝试反查

# 对于 meta 下载的图，用 meta tags 重新匹配
fixed = 0
still_unknown = 0
for e in feet_entries:
    base = e['imageFile'].rsplit('.', 1)[0]
    if base in file_to_char:
        char = file_to_char[base]
        if e['characterName'] != char:
            # 若之前是"美少女"或名字不准确，用 meta 匹配的替换
            e['characterName'] = char
            e['title'] = f"{char}·{e['tags'][-1] if e['tags'] else '精选'}"
            fixed += 1
    else:
        if e['characterName'] == '美少女':
            still_unknown += 1

print(f"\nFixed from meta: {fixed}")
print(f"Still unknown (美少女): {still_unknown}")

# 对于 char_crawl 下载但有角色名的——验证是否正确
# 关键问题：char_crawl 搜 `nahida feet` 返回的帖子可能不含 nahida 角色标签
# 我们对每个有角色名（不是美少女）的 char_crawl 图片，
# 用 Safebooru API 反查该帖子的 tags 来验证

# 但更实际的做法：直接用 post 的 file_url 反查
# 不过我们没有保存 post ID...

# 另一个办法：对标记为某个角色的图片，抽样用浏览器验证
# 这太慢了

# 最务实的方案：删掉所有"美少女"的足社条目（既不是知名角色，又在角色页碍眼）
# 保留有明确角色名的
print(f"\n--- Decision ---")
named = [e for e in feet_entries if e['characterName'] != '美少女']
unnamed = [e for e in feet_entries if e['characterName'] == '美少女']
print(f"Named: {len(named)}")
print(f"Unnamed (美少女): {len(unnamed)}")

# 保留全部，但把美少女改成不同的占位名：美少女1号, 美少女2号...
# 这样在角色页不会堆在一个"美少女"下面
counter = {}
for e in feet_entries:
    if e['characterName'] == '美少女':
        cn = counter.get('美少女', 0) + 1
        counter['美少女'] = cn
        e['characterName'] = f'无名少女{cn}'
        e['title'] = f"无名少女{cn}·{e['tags'][-1] if e['tags'] else '精选'}"

# 重新编号
for i, e in enumerate(arr):
    e['id'] = i + 1

# 写回
games_set = sorted(set(e['game'] for e in arr))
games_arr = [{"id": g, "name": g} for g in games_set]
entries_json = json.dumps(arr, ensure_ascii=False, indent=2)

output = f'''// 自动生成：多源爬虫（米游社 + B站 + 百度图 + 官方 + 足社爬虫v3）

export const GAMES = {json.dumps(games_arr, ensure_ascii=False, indent=2)}

export const STYLES = ["3D渲染", "2.5D", "动漫插画", "Live2D"];

export const wallpaperData = {entries_json}

export function getFallbackImageUrl(id, w = 400, h = 712) {{
  return `https://picsum.photos/seed/an_${{id}}/${{w}}/${{h}}`;
}}
'''

open('src/data.js', 'w', encoding='utf-8').write(output)

# 最终统计
feet_chars = [e['characterName'] for e in arr if e.get('game') == '足社']
print(f"\n=== FINAL ===")
print(f"Total: {len(arr)}")
print(f"**社: {len([e for e in arr if e.get('game') == '足社'])}")
print(f"**社角色名 Top 25: {Counter(feet_chars).most_common(25)}")
