#!/usr/bin/env python3
"""
**社数据大修：
1. 修正角色名（英文→中文映射）
2. 修正 title 格式
3. 丰富 tags（从 barefoot 单一标签 → 按实际内容补充）
4. SSL分类隔离（确保足社图 game="足社"）
"""
import re, os

# 角色英文名→中文映射 (从 booru 标签提取的常见角色)
CHAR_MAP = {
    # 原神
    "nahida": "纳西妲", "hu_tao": "胡桃", "ganyu": "甘雨", "keqing": "刻晴",
    "raiden_shogun": "雷电将军", "yoimiya": "宵宫", "yae_miko": "八重神子",
    "nilou": "妮露", "fischl": "菲谢尔", "lumine": "荧", "ayaka": "绫华",
    "kamisato_ayaka": "绫华", "shenhe": "申鹤", "eula": "优菈",
    "rosaria": "罗莎莉亚", "beidou": "北斗", "ningguang": "凝光",
    "yelan": "夜兰", "shinobu": "久岐忍", "collei": "柯莱",
    "furina": "芙宁娜", "navia": "娜维娅", "chevreuse": "夏沃蕾",
    "arlecchino": "阿蕾奇诺", "clorinde": "克洛琳德", "sigewinne": "希格雯",
    "emilie": "艾梅莉埃", "mualani": "玛拉妮", "kachina": "卡齐娜",
    "xilonen": "希诺宁", "citlali": "茜特菈莉", "lan_yan": "蓝砚",
    "yanfei": "烟绯", "xiangling": "香菱", "xinyan": "辛焱",
    "sayu": "早柚", "kuki_shinobu": "久岐忍", "kirara": "绮良良",
    "diona": "迪奥娜", "qiqi": "七七", "sucrose": "砂糖",
    "barbara": "芭芭拉", "noelle": "诺艾尔", "lisa": "丽莎",
    "amber": "安柏", "mona": "莫娜", "jean": "琴",
    "razdihina": "拉兹蒂娜",
    # 星穹铁道
    "kafka": "卡芙卡", "himeko": "姬子", "seele": "希儿",
    "bronya": "布洛妮娅", "natasha": "娜塔莎", "tuurz": "图尔兹",
    "asta": "艾丝妲", "herta": "黑塔", "silver_wolf": "银狼",
    "firefly": "流萤", "robin": "知更鸟", "sparkle": "花火",
    "acheron": "黄泉", "ruan_mei": "阮梅", "black_swan": "黑天鹅",
    "topaz": "托帕", "dr_ratio": "真理医生",
    # 明日方舟
    "amiya": "阿米娅", "texas": "德克萨斯", "exusiai": "能天使",
    "sora": "空", "angelina": "安洁莉娜", "specter": "幽灵鲨",
    "skadi": "斯卡蒂", "ch'en": "陈", "kal'tsit": "凯尔希",
    "mudrock": "泥岩", "surtr": "澄闪", "swire": "诗怀雅",
    "liskarm": "雷蛇", "siege": "推进之王",
    # 蔚蓝档案
    "alice": "爱丽丝", "aru": "阿露", "mika": "米卡",
    "iroha": "伊吕波", "miyako": "都子", "saki": "纱纪",
    "hoshino": "星野", "nonomi": "野宫", "tsubaki": "椿",
    # 绝区零
    "anby": "安比", "nicole": "妮可", "ellen": "艾莲",
    "zhu_yuan": "朱鸢", "qingyi": "青衣", "jane_doe": "简·杜",
    # 通用
    "kinako": "金阁", "iris": "爱丽丝", "squeezable": "美少女",
}

# 标签修正映射
TAG_MAP = {
    "barefoot": "裸足", "soles": "脚底", "toes": "脚趾",
    "foot_focus": "足特写", "feet": "裸足",
    "stockings": "黑丝", "black_thighhighs": "黑丝",
    "white_thighhighs": "白丝", "thighhighs": "过膝袜",
    "pantyhose": "连裤袜", "kneesocks": "膝上袜",
    "socks": "短袜", "legwear": "腿部装饰",
    "bare_legs": "裸腿", "legs": "美腿",
    "skindentation": "绝对领域",
}

def normalize_char(raw_name):
    """将 booru 英文角色名转为中文名"""
    if not raw_name or raw_name == '美少女':
        return '美少女'
    
    key = raw_name.lower().replace(' ', '_').replace('(', '').replace(')', '')
    
    # 直接匹配
    if key in CHAR_MAP:
        return CHAR_MAP[key]
    
    # 模糊匹配
    for en, cn in CHAR_MAP.items():
        if en in key or key in en:
            return cn
    
    # 没匹配到，保持原名（因为是真角色名）
    name = raw_name.replace('_', ' ').title()
    # 但如果是明显非角色名，标为美少女
    non_char = {'squeezable', 'unknown', 'original', '1girl', '2girls'}
    if key in non_char:
        return '美少女'
    return name

def enrich_tags(raw_tags_str, image_file):
    """从原始标签字符串丰富中文标签"""
    raw_lower = raw_tags_str.lower()
    tags = []
    
    # 从原始标签推断
    for en_tag, cn_tag in TAG_MAP.items():
        if en_tag in raw_lower and cn_tag not in tags:
            tags.append(cn_tag)
    
    # 确保至少有"足社"标签
    if '足社' not in tags:
        tags.append('足社')
    
    # 如果没有任何关键词标签，默认加"裸足"
    specific = [t for t in tags if t != '足社']
    if not specific:
        tags.insert(0, '裸足')
    
    return tags

def build_title(char_name, tags):
    """构建标题：角色名·关键词"""
    specific_tags = [t for t in tags if t != '足社']
    keyword = specific_tags[0] if specific_tags else '精选'
    return f'{char_name}·{keyword}'

# ===== 主逻辑 =====
data_path = 'src/data.js'
data = open(data_path, 'r', encoding='utf-8').read()

# 找到 wallpaperData 数组内容
start_marker = 'export const wallpaperData = ['
start_idx = data.index(start_marker) + len(start_marker)
end_idx = data.rindex(']')  # 最后一个 ] 是数组结尾
header = data[:start_idx]
footer = data[end_idx:]

# 解析每个条目
array_content = data[start_idx:end_idx]
# 用正则提取每个完整 JSON 对象
entry_pattern = re.compile(r'\{\s*"id":\s*\d+.*?"imageFile":\s*"[^"]*"\s*\}', re.DOTALL)
entries = entry_pattern.findall(array_content)

print(f'总条目: {len(entries)}')

modified = 0
new_entries = []
char_names = set()

for entry in entries:
    # 提取关键字段
    game_m = re.search(r'"game":\s*"(.*?)"', entry)
    char_m = re.search(r'"characterName":\s*"(.*?)"', entry)
    tags_m = re.search(r'"tags":\s*\[(.*?)\]', entry, re.DOTALL)
    title_m = re.search(r'"title":\s*"(.*?)"', entry)
    image_m = re.search(r'"imageFile":\s*"(.*?)"', entry)
    
    game = game_m.group(1) if game_m else ''
    char = char_m.group(1) if char_m else '美少女'
    raw_tags = tags_m.group(1) if tags_m else ''
    image_file = image_m.group(1) if image_m else ''
    
    if game == '足社':
        # 修正角色名
        new_char = normalize_char(char)
        
        # 丰富标签
        new_tags = enrich_tags(raw_tags, image_file)
        
        # 构建标题
        new_title = build_title(new_char, new_tags)
        
        if new_char != char or new_title != (title_m.group(1) if title_m else ''):
            modified += 1
        
        # 替换字段
        entry = re.sub(r'"characterName":\s*"[^"]*"', f'"characterName": "{new_char}"', entry)
        entry = re.sub(r'"title":\s*"[^"]*"', f'"title": "{new_title}"', entry)
        
        # 替换 tags
        tags_json = ', '.join(f'"{t}"' for t in new_tags)
        entry = re.sub(r'"tags":\s*\[.*?\]', f'"tags": [{tags_json}]', entry, flags=re.DOTALL)
        
        char_names.add(new_char)
    
    new_entries.append(entry)

# 重新编号
for i, entry in enumerate(new_entries):
    entry = re.sub(r'"id":\s*\d+', f'"id": {i+1}', entry, count=1)
    new_entries[i] = entry

# 写回
output = header + ',\n  '.join(new_entries) + footer
open(data_path, 'w', encoding='utf-8').write(output)

print(f'修正了 {modified} 条**社条目')
print(f'**社角色名: {sorted(char_names)}')
