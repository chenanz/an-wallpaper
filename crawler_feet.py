#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
足社批量爬取 + 数据重建脚本 v3
- 从 Safebooru 爬取足部相关图片
- 下载竖图 (w>500, h>800)
- 提取角色名并映射中文
- 重建 data.js，保留非足社条目，替换所有足社条目
"""

import os
import sys
import json
import hashlib
import time
import re
import requests
from pathlib import Path

# === 配置 ===
BASE_DIR = Path(r"D:\风\hermes\an-app")
IMAGE_DIR = BASE_DIR / "public" / "images"
DATA_JS = BASE_DIR / "src" / "data.js"

# Safebooru API
SAFEBOORU_API = "https://safebooru.org/index.php"
SAFEBOORU_IMAGE_BASE = "https://safebooru.org/images/"

# 目标数量
TARGET_FEET_COUNT = 220

# 搜索标签组合
TAG_COMBOS = [
    "feet barefoot",
    "feet stockings",
    "foot_focus",
    "feet pantyhose",
    "soles barefoot",
    "thighhighs barefoot",
    "feet toes",
    "black_thighhighs feet",
    "white_thighhighs feet",
    "kneesocks feet",
]

# 角色名映射 (英文 -> 中文)
CHAR_MAP = {
    # 原神
    "nahida": "纳西妲", "hu_tao": "胡桃", "ganyu": "甘雨", "keqing": "刻晴",
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
    "hutao": "胡桃", "lynette": "琳妮特", "charlotte": "夏洛蒂",
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
    "mualani": "玛拉妮", "xilonen": "希诺宁",
    "chasca": "恰斯卡", "ororon": "欧洛伦",
    "citlali": "茜特菈莉", "kinich": "基尼奇",
    "chevreuse": "夏沃蕾", "gaming": "嘉明",
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
    "aru": "阿露", "mika_(blue_archive)": "米卡",
    "alice_(blue_archive)": "爱丽丝", "alice": "爱丽丝",
    "saki": "纱纪", "tsubaki": "椿", "miyako": "都子",
    "shiroko": "白子", "hasumi": "莲见", "hanako": "花子",
    "asuna": "明日奈", "karin": "花凛", "hina": "日奈",
    # 绝区零
    "anby": "安比", "nicole": "妮可", "ellen": "艾莲",
    "zhu_yuan": "朱鸢", "qingyi": "青衣", "jane_doe": "简·杜",
    "belle": "铃", "corin": "可琳", "miyabi": "雅",
    "astra_yao": "星见雅",
    # FGO
    "artoria": "阿尔托莉雅", "saber": "阿尔托莉雅",
    "rin_tohsaka": "远坂凛", "sakura_matou": "间桐樱",
    "ishtar": "伊什塔尔", "ereshkigal": "埃列什基伽勒",
    "meltlilith": "溶解莉莉丝", "bb_(fate)": "BB",
    # Generic anime
    "miku": "初音", "hatsune_miku": "初音",
    "zero_two": "零二", "02_(darling_in_the_franxx)": "零二",
    "marin_kitagawa": "喜多川海梦",
    "power_(chainsaw_man)": "帕瓦", "makima": "玛奇玛",
    "rem_(re:zero)": "雷姆", "ram_(re:zero)": "拉姆",
    "emilia": "艾米莉亚",
    "nico_yazawa": "矢泽妮可",
    "yor_forger": "约尔", "anya_forger": "阿尼亚",
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


def fetch_safebooru(tags_str, pid=0, limit=100):
    """从 Safebooru 获取帖子列表"""
    params = {
        "page": "dapi",
        "s": "post",
        "q": "index",
        "tags": tags_str + " rating:safe",
        "limit": limit,
        "pid": pid,
        "json": "1",
    }
    try:
        resp = requests.get(SAFEBOORU_API, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            return data
        return []
    except Exception as e:
        print(f"  [错误] 获取失败 pid={pid} tags={tags_str}: {e}")
        return []


def download_image(url, filepath, retries=2):
    """下载图片到指定路径"""
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, timeout=30, stream=True,
                              headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
            return True
        except Exception as e:
            if attempt < retries:
                time.sleep(1)
            else:
                print(f"  [错误] 下载失败 {url}: {e}")
    return False


def extract_character_from_tags(tags_str):
    """从 tags 字符串提取角色名并转为中文"""
    tags = tags_str.split()
    characters = []
    
    for tag in tags:
        # 角色标签格式: name_(series)
        if "_(" in tag and tag.endswith(")"):
            char_part = tag.split("_(")[0]
            characters.append(char_part)
    
    # 查找匹配的角色
    for char_part in characters:
        char_lower = char_part.lower()
        # 直接匹配
        if char_lower in CHAR_MAP:
            return CHAR_MAP[char_lower]
        # 去下划线匹配
        char_nound = char_lower.replace("_", "")
        for key, val in CHAR_MAP.items():
            if key.replace("_", "") == char_nound:
                return val
    
    # 如果没匹配到角色标签，检查 tags 中是否有任何已知的角色标签
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
    
    # 去重和清理
    if "裸腿" in cn_tags and "裸足" in cn_tags:
        cn_tags.remove("裸腿")
    
    return cn_tags[:6]


def get_primary_keyword(cn_tags):
    """从中文标签中提取主要关键词用于标题"""
    priority = ["裸足", "黑丝", "白丝", "连裤袜", "过膝袜", "膝上袜",
                "脚底特写", "脚趾", "脚底", "吊袜带", "绝对领域",
                "短袜", "美腿", "裸腿", "赤脚"]
    for kw in priority:
        if kw in cn_tags:
            return kw
    return cn_tags[0] if cn_tags else "裸足"


def get_image_url(post):
    """从 post 数据中获取图片 URL"""
    file_url = post.get("file_url")
    if file_url:
        return file_url
    
    directory = post.get("directory")
    image = post.get("image")
    if directory and image:
        return f"{SAFEBOORU_IMAGE_BASE}{directory}/{image}"
    
    sample_url = post.get("sample_url")
    if sample_url:
        return sample_url
    
    return None


# ========== 第一步：爬取图片 ==========

def main_crawl():
    print("=" * 60)
    print("第一步：从 Safebooru 爬取足社图片")
    print("=" * 60)
    
    existing_files = set()
    if IMAGE_DIR.exists():
        for f in IMAGE_DIR.iterdir():
            if f.name.startswith("feet_"):
                existing_files.add(f.name)
    
    print(f"现有足社图片: {len(existing_files)} 张")
    
    all_posts = []
    seen_ids = set()
    
    for combo in TAG_COMBOS:
        print(f"\n搜索标签: {combo}")
        for pid in range(5):
            posts = fetch_safebooru(combo, pid=pid, limit=100)
            new_count = 0
            for post in posts:
                post_id = post.get("id")
                if post_id and post_id not in seen_ids:
                    seen_ids.add(post_id)
                    all_posts.append((post, combo))
                    new_count += 1
            print(f"  pid={pid}: 获取 {len(posts)} 条, 新增 {new_count}")
            
            if len(posts) < 20:
                break
            time.sleep(0.5)
    
    print(f"\n总计获取 {len(all_posts)} 条不重复帖子")
    
    # 过滤竖图
    vertical_posts = []
    for post, combo in all_posts:
        try:
            w = int(post.get("width", 0) or 0)
            h = int(post.get("height", 0) or 0)
        except (ValueError, TypeError):
            continue
        if w > 500 and h > 800 and h > w:
            vertical_posts.append((post, combo))
    
    print(f"过滤竖图 (w>500, h>800, h>w): {len(vertical_posts)} 条")
    
    # 去重（基于图片URL）
    seen_urls = set()
    unique_posts = []
    for post, combo in vertical_posts:
        img_url = get_image_url(post)
        if img_url and img_url not in seen_urls:
            seen_urls.add(img_url)
            unique_posts.append((post, combo))
    
    print(f"去重后: {len(unique_posts)} 条")
    
    # 下载图片
    downloaded = []
    success = 0
    fail = 0
    skip = 0
    
    for i, (post, combo) in enumerate(unique_posts):
        if success >= TARGET_FEET_COUNT:
            print(f"\n已达到目标数量 {TARGET_FEET_COUNT}, 停止下载")
            break
        
        img_url = get_image_url(post)
        if not img_url:
            skip += 1
            continue
        
        # 生成文件名: feet_<hash6>.jpg
        url_hash = hashlib.md5(img_url.encode()).hexdigest()[:6]
        ext = os.path.splitext(img_url)[1] or ".jpg"
        if ext.lower() not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            ext = '.jpg'
        filename = f"feet_{url_hash}{ext}"
        
        # 跳过已存在的文件
        if (IMAGE_DIR / filename).exists():
            downloaded.append((filename, post, combo))
            success += 1
            skip += 1
            continue
        
        filepath = IMAGE_DIR / filename
        
        if download_image(img_url, filepath):
            downloaded.append((filename, post, combo))
            success += 1
            if success % 20 == 0:
                print(f"  下载进度: {success}/{TARGET_FEET_COUNT}")
        else:
            fail += 1
            if filepath.exists():
                filepath.unlink()
        
        time.sleep(0.3)
    
    print(f"\n下载完成: 成功 {success}, 失败 {fail}, 跳过(已存在) {skip}")
    
    # 保存下载元数据
    meta_path = BASE_DIR / "feet_meta.json"
    meta = []
    for filename, post, combo in downloaded:
        meta.append({
            "filename": filename,
            "tags": post.get("tags", ""),
            "combo": combo,
            "width": post.get("width", 0),
            "height": post.get("height", 0),
            "id": post.get("id", 0),
        })
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    
    print(f"元数据已保存到: {meta_path}")
    return meta


# ========== 第二步：重建 data.js ==========

def parse_existing_data_js():
    """解析现有 data.js 提取非足社条目"""
    with open(DATA_JS, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到 wallpaperData 数组内容
    match = re.search(r'export const wallpaperData = \[', content)
    if not match:
        print("[错误] 找不到 wallpaperData 数组!")
        sys.exit(1)
    
    # 找到数组结尾
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
    
    # 尝试用正则提取每个条目
    # 用一种更可靠的方式: 提取 { ... } 块
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
                try:
                    # 尝试解析为 JSON
                    obj = json.loads(entry_text)
                    entries.append(obj)
                except json.JSONDecodeError:
                    # 尝试修复常见问题
                    fixed = entry_text
                    # 移除尾随逗号
                    fixed = re.sub(r',\s*}', '}', fixed)
                    fixed = re.sub(r',\s*]', ']', fixed)
                    try:
                        obj = json.loads(fixed)
                        entries.append(obj)
                    except:
                        print(f"  [警告] 跳过无法解析的条目: {entry_text[:80]}...")
                entry_start = -1
    
    return entries


def rebuild_data_js(meta):
    print("\n" + "=" * 60)
    print("第二步：重建 data.js")
    print("=" * 60)
    
    # 解析现有条目
    entries = parse_existing_data_js()
    print(f"解析到总条目: {len(entries)}")
    
    # 分离: 保留非足社+修复泄露条目
    non_feet_entries = []
    for e in entries:
        game = e.get("game", "")
        image_file = e.get("imageFile", "")
        
        # 跳过所有足社条目（会被新爬取的替换）
        if game == "足社":
            continue
        
        # 检查泄露：非足社但文件名是 feet_ 开头
        if image_file.startswith("feet_"):
            print(f"  [修复] 泄露条目 {image_file}: game {game} -> 足社 (不保留，将被新条目覆盖)")
            continue
        
        # 清理不需要的字段
        entry = {}
        for key in ["id", "title", "characterName", "game", "gender", "style",
                     "tags", "likes", "rarity", "source", "nsfw", "imageFile"]:
            if key in e:
                entry[key] = e[key]
        # 保留 yuzu 字段如果存在
        if "yuzu" in e:
            entry["yuzu"] = e["yuzu"]
        
        non_feet_entries.append(entry)
    
    # 统计
    game_counts = {}
    for e in non_feet_entries:
        g = e.get("game", "未知")
        game_counts[g] = game_counts.get(g, 0) + 1
    
    print(f"保留非足社条目: {len(non_feet_entries)}")
    for g, c in sorted(game_counts.items()):
        print(f"  {g}: {c}")
    
    # 生成新的足社条目
    new_feet_entries = []
    char_count = {}
    
    for item in meta:
        filename = item["filename"]
        tags_str = item.get("tags", "")
        combo = item.get("combo", "")
        
        # 提取角色名
        char_name = extract_character_from_tags(tags_str)
        if char_name is None:
            char_name = "美少女"
        
        char_count[char_name] = char_count.get(char_name, 0) + 1
        
        # 生成中文标签
        cn_tags = generate_cn_tags(tags_str)
        
        # 确保标签中有 "足社"
        if "足社" not in cn_tags:
            cn_tags.append("足社")
        
        # 获取主要关键词
        keyword = get_primary_keyword(cn_tags)
        
        # 生成标题
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
        new_feet_entries.append(entry)
    
    print(f"\n新足社条目: {len(new_feet_entries)}")
    print(f"角色名分布 (前20):")
    for char, count in sorted(char_count.items(), key=lambda x: -x[1])[:20]:
        print(f"  {char}: {count}")
    
    # 合并所有条目
    all_entries = non_feet_entries + new_feet_entries
    
    # 重新编号 ID
    for i, entry in enumerate(all_entries):
        entry["id"] = i + 1
    
    # 生成 GAMES 数组
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
    
    # 生成 data.js
    js_parts = []
    js_parts.append("// 自动生成：多源爬虫（米游社 + B站 + 百度图 + 官方 + 足社爬虫v3）")
    js_parts.append("")
    
    # GAMES
    js_parts.append("export const GAMES = [")
    for g in games_list:
        js_parts.append(f'  {{"id": "{g["id"]}", "name": "{g["name"]}"}}')
    js_parts.append("];")
    js_parts.append("")
    
    # STYLES
    js_parts.append('export const STYLES = ["3D渲染", "2.5D", "动漫插画", "Live2D"];')
    js_parts.append("")
    
    # wallpaperData
    js_parts.append("export const wallpaperData = [")
    for i, entry in enumerate(all_entries):
        lines = ["  {"]
        for key, val in entry.items():
            if key == "id":
                lines.append(f'    "id": {val},')
            elif isinstance(val, bool):
                lines.append(f'    "{key}: {str(val).lower()},')
            elif isinstance(val, int):
                lines.append(f'    "{key}": {val},')
            elif isinstance(val, list):
                lines.append(f'    "{key}": {json.dumps(val, ensure_ascii=False)},')
            else:
                lines.append(f'    "{key}": {json.dumps(val, ensure_ascii=False)},')
        # 移除最后一行的逗号
        lines[-1] = lines[-1].rstrip(",")
        lines.append("  }")
        if i < len(all_entries) - 1:
            lines[-1] += ","
        js_parts.extend(lines)
    js_parts.append("];")
    js_parts.append("")
    js_parts.append("export function getFallbackImageUrl(id, w = 400, h = 712) {")
    js_parts.append("  return `https://picsum.photos/seed/an_${id}/${w}/${h}`;")
    js_parts.append("}")
    
    content = "\n".join(js_parts) + "\n"
    
    with open(DATA_JS, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\ndata.js 已重写: {DATA_JS}")
    print(f"总条目: {len(all_entries)}")
    print(f"足社条目: {len(new_feet_entries)}")
    print(f"非足社条目: {len(non_feet_entries)}")
    
    # 清理旧 feet 图片文件（不在新元数据中的）
    if IMAGE_DIR.exists():
        new_filenames = {item["filename"] for item in meta}
        for f in IMAGE_DIR.iterdir():
            if f.name.startswith("feet_") and f.name not in new_filenames:
                print(f"  [清理] 删除旧图片: {f.name}")
                f.unlink()
    
    return len(all_entries), len(new_feet_entries), char_count


# ========== 主流程 ==========

if __name__ == "__main__":
    print("足社批量爬取+数据重建 开始!")
    print(f"工作目录: {BASE_DIR}")
    print(f"图片目录: {IMAGE_DIR}")
    print()
    
    # 第一步：爬取
    meta = main_crawl()
    
    # 限制到目标数量
    if len(meta) > TARGET_FEET_COUNT:
        meta = meta[:TARGET_FEET_COUNT]
        print(f"\n截取前 {TARGET_FEET_COUNT} 条足社条目")
    
    if len(meta) < 50:
        print(f"\n[警告] 只爬到 {len(meta)} 张，少于50张")
    
    # 第二步：重建
    total, feet_count, char_dist = rebuild_data_js(meta)
    
    print("\n" + "=" * 60)
    print("完成！")
    print(f"总条目数: {total}")
    print(f"足社条目: {feet_count}")
    print(f"角色名分布:")
    for char, count in sorted(char_dist.items(), key=lambda x: -x[1]):
        print(f"  {char}: {count}")
