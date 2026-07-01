#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
足社数据重建脚本 v4 - 修复版
- 从 git 恢复原始非足社条目
- 从 feet_meta.json 生成新足社条目  
- 正确生成 data.js
"""

import os
import sys
import json
import re
import subprocess
from pathlib import Path

BASE_DIR = Path(r"D:\风\hermes\an-app")
DATA_JS = BASE_DIR / "src" / "data.js"
META_PATH = BASE_DIR / "feet_meta.json"

# 角色名映射
CHAR_MAP = {
    "nahida": "纳西妲", "hu_tao": "胡桃", "hutao": "胡桃",
    "ganyu": "甘雨", "keqing": "刻晴",
    "raiden_shogun": "雷电将军", "yoimiya": "宵宫",
    "yae_miko": "八重神子", "nilou": "妮露", "fischl": "菲谢尔",
    "shenhe": "申鹤", "eula": "优菈", "yelan": "夜兰", "furina": "芙宁娜",
    "arlecchino": "阿蕾奇诺", "lumine": "荧", "ayaka": "绫华",
    "kamisato_ayaka": "绫华", "rosaria": "罗莎莉亚", "barbara": "芭芭拉",
    "mona": "莫娜", "sayu": "早柚", "ningguang": "凝光", "diona": "迪奥娜",
    "qiqi": "七七", "sucrose": "砂糖", "noelle": "诺艾尔", "lisa": "丽莎",
    "amber": "安柏", "jean": "琴", "xiangling": "香菱", "yanfei": "烟绯",
    "collei": "柯莱", "kirara": "绮良良", "kuki_shinobu": "久岐忍",
    "beidou": "北斗", "klee": "可莉",
    "sangonomiya_kokomi": "心海", "kokomi": "心海",
    "lynette": "琳妮特", "charlotte": "夏洛蒂",
    "navia": "娜维娅", "clorinde": "克洛琳德", "chlorinde": "克洛琳德",
    "chiori": "千织", "shinobu": "久岐忍",
    "miko": "八重神子", "paimon": "派蒙",
    "diluc": "迪卢克", "kaeya": "凯亚",
    "aether": "空", "sara": "九条裟罗", "kujo_sara": "九条裟罗",
    "thoma": "托马", "faruzan": "珐露珊", "layla": "莱依拉",
    "tighnari": "提纳里", "dehya": "迪希雅",
    "alhaitham": "艾尔海森", "baizhu": "白术",
    "lyney": "林尼", "neuvillette": "那维莱特",
    "wriothesley": "莱欧斯利", "xianyun": "闲云",
    "sigewinne": "希格雯", "emilie": "艾梅莉埃",
    "venti": "温迪", "zhongli": "钟离", "xiao": "魈",
    "tartaglia": "达达利亚",
    # 星铁
    "kafka": "卡芙卡", "himeko": "姬子", "seele": "希儿",
    "bronya": "布洛妮娅", "silver_wolf": "银狼", "firefly": "流萤",
    "robin": "知更鸟", "sparkle": "花火", "acheron": "黄泉",
    "ruan_mei": "阮梅", "black_swan": "黑天鹅", "topaz": "托帕",
    "hanya": "寒鸦", "yukong": "驭空", "tingyun": "停云",
    "huohuo": "藿藿", "pela": "佩拉",
    "asta": "艾丝妲", "herta": "黑塔", "march_7th": "三月七",
    "stelle": "星", "bailu": "白露", "jingyuan": "景元",
    "yanqing": "彦卿", "sushang": "素裳", "fuxuan": "符玄",
    "qingque": "青雀", "luocha": "罗刹", "jade": "翡翠",
    # 方舟
    "amiya": "阿米娅", "texas": "德克萨斯", "exusiai": "能天使",
    "angelina": "安洁莉娜", "skadi": "斯卡蒂", "specter": "幽灵鲨",
    "mudrock": "泥岩", "surtr": "澄闪",
    "kal'tsit": "凯尔希", "kaltst": "凯尔希",
    "siege": "推进之王", "saria": "塞雷娅",
    "dusk": "夕", "nian": "年", "ling": "令",
    # BA
    "hoshino": "星野", "nonomi": "野宫", "iroha": "伊吕波",
    "aru": "阿露", "saki": "纱纪", "tsubaki": "椿", "miyako": "都子",
    "shiroko": "白子", "hasumi": "莲见", "hanako": "花子",
    "asuna": "明日奈", "karin": "花凛", "hina": "日奈",
    "alice_(blue_archive)": "爱丽丝", "alice": "爱丽丝",
    "mika_(blue_archive)": "米卡",
    # 绝区零
    "anby": "安比", "nicole": "妮可", "ellen": "艾莲",
    "zhu_yuan": "朱鸢", "qingyi": "青衣", "jane_doe": "简·杜",
    "belle": "铃", "corin": "可琳", "miyabi": "雅",
    "astra_yao": "星见雅",
    # FGO
    "artoria": "阿尔托莉雅", "saber": "阿尔托莉雅",
    "rin_tohsaka": "远坂凛", "sakura_matou": "间桐樱",
    "ishtar": "伊什塔尔", "ereshkigal": "埃列什基伽勒",
    # 其他
    "miku": "初音", "hatsune_miku": "初音",
    "zero_two": "零二", "02_(darling_in_the_franxx)": "零二",
    "marin_kitagawa": "喜多川海梦",
    "power_(chainsaw_man)": "帕瓦", "makima": "玛奇玛",
    "rem_(re:zero)": "雷姆", "ram_(re:zero)": "拉姆",
    "emilia": "艾米莉亚",
    "yor_forger": "约尔",
}

# 标签中文映射
TAG_MAP = {
    "barefoot": "裸足", "soles": "脚底", "toes": "脚趾",
    "foot_focus": "足特写", "feet": "裸足",
    "stockings": "黑丝", "black_thighhighs": "黑丝",
    "white_thighhighs": "白丝", "thighhighs": "过膝袜",
    "pantyhose": "连裤袜", "kneesocks": "膝上袜",
    "socks": "短袜", "bare_legs": "裸腿", "legs": "美腿",
    "skindentation": "绝对领域",
    "white_pantyhose": "白丝连裤袜",
    "black_pantyhose": "黑丝连裤袜",
    "striped_thighhighs": "条纹过膝袜",
    "striped_pantyhose": "条纹连裤袜",
    "asymmetrical_legwear": "不对称腿饰",
    "garter": "吊袜带", "garter_straps": "吊袜带",
    "loafers": "乐福鞋", "heels": "高跟鞋",
    "sandals": "凉鞋", "no_shoes": "赤脚",
}


def extract_character_from_tags(tags_str):
    """从 tags 字符串提取角色名并转为中文"""
    tags = tags_str.split()
    characters = []
    
    for tag in tags:
        if "_(" in tag and tag.endswith(")"):
            char_part = tag.split("_(")[0]
            characters.append(char_part)
    
    for char_part in characters:
        char_lower = char_part.lower()
        if char_lower in CHAR_MAP:
            return CHAR_MAP[char_lower]
        char_nound = char_lower.replace("_", "")
        for key, val in CHAR_MAP.items():
            if key.replace("_", "") == char_nound:
                return val
    
    for tag in tags:
        tag_lower = tag.lower().strip()
        if tag_lower in CHAR_MAP:
            return CHAR_MAP[tag_lower]
    
    return None


def generate_cn_tags(tags_str):
    """从 booru tags 生成中文标签列表"""
    tags = tags_str.split()
    cn_tags = []
    seen = set()
    
    for tag in tags:
        tag_lower = tag.lower().strip()
        if tag_lower in TAG_MAP:
            cn = TAG_MAP[tag_lower]
            if cn not in seen:
                cn_tags.append(cn)
                seen.add(cn)
    
    if "裸腿" in cn_tags and "裸足" in cn_tags:
        cn_tags.remove("裸腿")
    
    return cn_tags[:6]


def get_primary_keyword(cn_tags):
    """从中文标签中提取主要关键词用于标题"""
    priority = ["裸足", "黑丝", "白丝", "连裤袜", "过膝袜", "膝上袜",
                "足特写", "脚趾", "脚底", "吊袜带", "绝对领域",
                "短袜", "美腿", "裸腿", "赤脚"]
    for kw in priority:
        if kw in cn_tags:
            return kw
    return cn_tags[0] if cn_tags else "裸足"


def extract_non_feet_from_git():
    """从 git 恢复原始 data.js 并提取非足社条目"""
    # 获取 git 中的原始版本
    result = subprocess.run(
        ["git", "show", "HEAD:src/data.js"],
        capture_output=True, text=True,
        cwd=str(BASE_DIR)
    )
    if result.returncode != 0:
        print(f"[错误] git show 失败: {result.stderr}")
        sys.exit(1)
    
    content = result.stdout
    
    # 提取 wallpaperData 数组
    match = re.search(r'export const wallpaperData = \[', content)
    if not match:
        print("[错误] 找不到 wallpaperData!")
        sys.exit(1)
    
    start = match.end()
    bracket_count = 1
    pos = start
    while bracket_count > 0 and pos < len(content):
        if content[pos] == '[':
            bracket_count += 1
        elif content[pos] == ']':
            bracket_count -= 1
        pos += 1
    
    array_text = content[start:pos-1]
    
    # 提取每个 { ... } 块并用 json5-like 解析
    entries = []
    depth = 0
    entry_start = -1
    
    for i, ch in enumerate(array_text):
        if ch == '{':
            if depth == 0:
                entry_start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and entry_start >= 0:
                entry_text = array_text[entry_start:i+1]
                # 修复为合法 JSON
                fixed = entry_text
                # nsfw: false -> "nsfw": false
                fixed = re.sub(r'(?<=[,"{\s])nsfw\s*:', '"nsfw":', fixed)
                # yuzu: true -> "yuzu": true
                fixed = re.sub(r'(?<=[,"{\s])yuzu\s*:', '"yuzu":', fixed)
                # 移除尾随逗号
                fixed = re.sub(r',\s*}', '}', fixed)
                fixed = re.sub(r',\s*]', ']', fixed)
                
                try:
                    obj = json.loads(fixed)
                    entries.append(obj)
                except json.JSONDecodeError as e:
                    print(f"  [警告] 跳过: {entry_text[:60]}... err={e}")
                entry_start = -1
    
    # 分离非足社条目
    non_feet = []
    for e in entries:
        game = e.get("game", "")
        image_file = e.get("imageFile", "")
        
        # 跳过足社条目
        if game == "足社":
            continue
        
        # 检查泄露（非足社但图片是feet_开头）
        if image_file.startswith("feet_"):
            print(f"  [修复泄露] {image_file}: game={game} -> 移除(将被新足社条目覆盖)")
            continue
        
        non_feet.append(e)
    
    return non_feet


def generate_feet_entries(meta):
    """从爬取的元数据生成足社条目"""
    feet_entries = []
    char_count = {}
    
    for item in meta:
        filename = item["filename"]
        tags_str = item.get("tags", "")
        
        char_name = extract_character_from_tags(tags_str)
        if char_name is None:
            char_name = "美少女"
        
        char_count[char_name] = char_count.get(char_name, 0) + 1
        
        cn_tags = generate_cn_tags(tags_str)
        if "足社" not in cn_tags:
            cn_tags.append("足社")
        
        keyword = get_primary_keyword(cn_tags)
        title = f"{char_name}·{keyword}"
        
        entry = {
            "title": title,
            "characterName": char_name,
            "game": "足社",
            "gender": "女",
            "style": "二次元",
            "tags": cn_tags,
            "likes": 0,
            "rarity": "SSR",
            "source": "Safebooru",
            "nsfw": False,
            "imageFile": filename,
        }
        feet_entries.append(entry)
    
    return feet_entries, char_count


def write_data_js(non_feet, feet_entries, char_count):
    """生成完整的 data.js"""
    
    all_entries = non_feet + feet_entries
    
    # 重新编号
    for i, entry in enumerate(all_entries):
        entry["id"] = i + 1
    
    # GAMES 数组
    games_set = set()
    for e in all_entries:
        games_set.add(e.get("game", ""))
    
    games_list = []
    game_order = ["原神", "崩坏：星穹铁道", "绝区零", "明日方舟", "蔚蓝档案", "足社"]
    for g in game_order:
        if g in games_set:
            games_list.append({"id": g, "name": g})
    for g in sorted(games_set):
        if g not in game_order:
            games_list.append({"id": g, "name": g})
    
    # 用 json.dumps 生成，确保合法
    lines = []
    lines.append("// 自动生成：多源爬虫（米游社 + B站 + 百度图 + 官方 + 足社爬虫v3）")
    lines.append("")
    
    # GAMES
    lines.append("export const GAMES = [")
    for g in games_list:
        lines.append(f'  {json.dumps(g, ensure_ascii=False)}')
    lines.append("];")
    lines.append("")
    
    # STYLES
    lines.append('export const STYLES = ["3D渲染", "2.5D", "动漫插画", "Live2D"];')
    lines.append("")
    
    # wallpaperData - 用 json.dumps 生成整个数组，然后手动格式化
    lines.append("export const wallpaperData = [")
    
    for i, entry in enumerate(all_entries):
        # 确保字段顺序: id, title, characterName, game, gender, style, tags, likes, rarity, source, nsfw, imageFile[, yuzu]
        ordered = {}
        for key in ["id", "title", "characterName", "game", "gender", "style", "tags", "likes", "rarity", "source", "nsfw", "imageFile"]:
            if key in entry:
                ordered[key] = entry[key]
        if "yuzu" in entry:
            ordered["yuzu"] = entry["yuzu"]
        
        entry_json = json.dumps(ordered, ensure_ascii=False, indent=2)
        # 缩进
        entry_lines = entry_json.split("\n")
        for j, line in enumerate(entry_lines):
            if j == 0:
                lines.append("  " + line)
            else:
                lines.append("  " + line)
        
        if i < len(all_entries) - 1:
            # 最后一行是 }，改成 },
            lines[-1] = lines[-1].rstrip() + ","
    
    lines.append("];")
    lines.append("")
    lines.append("export function getFallbackImageUrl(id, w = 400, h = 712) {")
    lines.append("  return `https://picsum.photos/seed/an_${id}/${w}/${h}`;")
    lines.append("}")
    
    content = "\n".join(lines) + "\n"
    
    with open(DATA_JS, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return len(all_entries), len(feet_entries)


def main():
    print("=" * 60)
    print("足社数据重建 v4")
    print("=" * 60)
    
    # 1. 从 git 恢复非足社条目
    print("\n从 git 恢复原始非足社条目...")
    non_feet = extract_non_feet_from_git()
    
    game_counts = {}
    for e in non_feet:
        g = e.get("game", "未知")
        game_counts[g] = game_counts.get(g, 0) + 1
    
    print(f"保留非足社条目: {len(non_feet)}")
    for g, c in sorted(game_counts.items()):
        print(f"  {g}: {c}")
    
    # 2. 从元数据生成足社条目
    print("\n从爬取元数据生成足社条目...")
    with open(META_PATH, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    
    feet_entries, char_count = generate_feet_entries(meta)
    
    print(f"新足社条目: {len(feet_entries)}")
    print(f"角色名分布:")
    for char, count in sorted(char_count.items(), key=lambda x: -x[1])[:20]:
        print(f"  {char}: {count}")
    
    # 3. 写入 data.js
    print("\n写入 data.js...")
    total, feet_total = write_data_js(non_feet, feet_entries, char_count)
    
    print(f"\n完成!")
    print(f"总条目数: {total}")
    print(f"足社条目: {feet_total}")
    print(f"非足社条目: {len(non_feet)}")
    
    # 验证 data.js 是否合法 JS
    print("\n验证 data.js 语法...")
    content = DATA_JS.read_text(encoding='utf-8')
    # 检查是否有明显的 JSON 语法错误
    # 提取数组部分并验证
    try:
        match = re.search(r'export const wallpaperData = (\[.*\]);', content, re.DOTALL)
        if match:
            # 移除尾随逗号
            array_text = match.group(1)
            array_text = re.sub(r',\s*}', '}', array_text)
            array_text = re.sub(r',\s*]', ']', array_text)
            data = json.loads(array_text)
            print(f"  JSON 验证通过: {len(data)} 条")
    except json.JSONDecodeError as e:
        print(f"  [警告] JSON 验证失败: {e}")


if __name__ == "__main__":
    main()
