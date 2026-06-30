"""
玉足社补图爬虫
专门抓带足/腿/丝袜/黑丝/白丝/裸足等元素的二游女角色图
跑完追加到 src/data.js，tags 里带关键词，App 玉足社就能识别
用法：python add_yuzu.py
"""

import os
import re
import sys
import json
import time
import random
import hashlib
import requests
from pathlib import Path
from datetime import datetime
from io import BytesIO

DOWNLOAD_DIR = "public/images"
DATA_JS_PATH = "src/data.js"
LOG_PATH = "public/images/.crawl_log.txt"

MIN_DELAY = 3.5
MAX_DELAY = 7.0
MAX_PER_RUN = 40          # 每轮最多补40张
MAX_IMGS_PER_QUERY = 8
PREFER_PORTRAIT = True

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
]

MALE_BLOCKLIST = [
    "钟离","魈","达达利亚","公子","阿贝多","温迪","万叶","枫原万叶",
    "荒泷一斗","提纳里","赛诺","艾尔海森","卡维","那维莱特","莱欧斯利",
    "景元","刃","丹恒","杰帕德","桑博","卢卡","彦卿","罗刹",
    "凯文","奥托","齐格飞","瓦尔特","虚空万藏",
    "哲","安东","本","莱卡恩","苍角",
    "银灰","棘刺","山","傀影","流明","送葬人","号角","博士男","赫德雷",
    "男","男性","男主","哥哥","弟弟","老公",
]

SKIP_KEYWORDS = [
    "cos","cosplay","手办","攻略","联动","实物","周边","谷子",
    "抽卡","强度","测评","节奏榜","配队","模组",
    "表情包","梗图","沙雕","Q版","头像",
]

# 玉足社专用搜索词：关键词 + 要打进 tags 的标记
YUZU_QUERIES = [
    # 原神
    ("原神 女角色 黑丝 壁纸", "原神", ["雷电将军","八重神子","芙宁娜","夜兰","刻晴","甘雨","优菈","申鹤","莫娜","娜维娅","克洛琳德","琴","丽莎","凝光"], ["黑丝","丝袜"]),
    ("原神 女角色 白丝 壁纸", "原神", ["雷电将军","神里绫华","芙宁娜","珊瑚宫心海","可莉","七七","芭芭拉","诺艾尔","琳妮特","菲谢尔","夏洛蒂"], ["白丝","丝袜"]),
    ("原神 女角色 裸足 壁纸", "原神", ["雷电将军","胡桃","纳西妲","芙宁娜","妮露","宵宫","绮良良","千织"], ["裸足","玉足"]),
    ("原神 女角色 美腿  wallpaper", "原神", ["雷电将军","八重神子","夜兰","刻晴","优菈","申鹤","莫娜","克洛琳德"], ["美腿","腿"]),
    # 崩铁
    ("崩坏星穹铁道 女角色 黑丝 壁纸", "崩坏：星穹铁道", ["卡芙卡","姬子","黑天鹅","阮梅","三月七","布洛妮娅","停云","佩拉"], ["黑丝","丝袜"]),
    ("崩坏星穹铁道 女角色 白丝 壁纸", "崩坏：星穹铁道", ["知更鸟","三月七","藿藿","克拉拉","青雀"], ["白丝","丝袜"]),
    ("崩坏星穹铁道 女角色 裸足 壁纸", "崩坏：星穹铁道", ["黄泉","流萤","花火","镜流","藿藿"], ["裸足","玉足"]),
    # 绝区零
    ("绝区零 女角色 黑丝 壁纸", "绝区零", ["星见雅","朱鸢","简","耀嘉音","妮可","格莉丝","丽娜"], ["黑丝","丝袜"]),
    ("绝区零 女角色 白丝 壁纸", "绝区零", ["艾莲","柏妮思","安比","可琳"], ["白丝","丝袜"]),
    # 明日方舟
    ("明日方舟 女角色 黑丝 壁纸", "明日方舟", ["阿米娅","德克萨斯","能天使","斯卡蒂","陈","凯尔希","澄闪","琴柳"], ["黑丝","丝袜"]),
    ("明日方舟 女角色 白丝 壁纸", "明日方舟", ["阿米娅","澄闪","琴柳","令","夕","年"], ["白丝","丝袜"]),
    # 蔚蓝档案
    ("蔚蓝档案 女角色 黑丝 壁纸", "蔚蓝档案", ["优香","星野","日奈","未花","黑见茜香","羽川莲见","花凛","晴奈"], ["黑丝","丝袜"]),
    ("蔚蓝档案 女角色 白丝 壁纸", "蔚蓝档案", ["白子","爱丽丝","小春","梓","芹香","知世"], ["白丝","丝袜"]),
    # 通用
    ("二次元 美少女 裸足 壁纸", "原神", ["少女","女角色"], ["裸足","玉足"]),
    ("二次元 美少女 黑丝 壁纸", "原神", ["少女","女角色"], ["黑丝","丝袜"]),
    ("二次元 美少女 白丝 壁纸", "原神", ["少女","女角色"], ["白丝","丝袜"]),
    ("二次元 美少女 美腿 壁纸", "原神", ["少女","女角色"], ["美腿","腿"]),
]

GAMES_LIST = [
    {"id": "genshin", "name": "原神"},
    {"id": "hi3", "name": "崩坏3"},
    {"id": "hsr", "name": "崩坏：星穹铁道"},
    {"id": "zzz", "name": "绝区零"},
    {"id": "arknights", "name": "明日方舟"},
    {"id": "ba", "name": "蔚蓝档案"},
    {"id": "azur", "name": "碧蓝航线"},
    {"id": "gfl", "name": "少女前线"},
    {"id": "epic7", "name": "第七史诗"},
    {"id": "pgr", "name": "战双帕弥什"},
    {"id": "fgo", "name": "FGO"},
]


def log(msg):
    ts = datetime.now().strftime("%m-%d %H:%M:%S")
    line = f"[{ts}][玉足社] {msg}"
    print(line)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def random_delay():
    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))


def is_blocked(title):
    t = title.lower()
    for bad in SKIP_KEYWORDS:
        if bad.lower() in t:
            return True
    for male in MALE_BLOCKLIST:
        if male in title:
            return True
    return False


def guess_char(title, char_pool):
    for char in sorted(char_pool, key=len, reverse=True):
        if char in title:
            return char
    return random.choice(char_pool) if char_pool else "精选角色"


def baidu_image_search(keyword, page=0, per_page=30):
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": "https://image.baidu.com/",
    }
    url = "https://image.baidu.com/search/flip"
    params = {
        "tn": "baiduimage",
        "word": keyword,
        "rn": str(per_page),
        "pn": str(page * per_page),
        "ie": "utf-8",
        "oe": "utf-8",
    }
    if PREFER_PORTRAIT:
        params["z"] = "0"
        params["height"] = "1280"
        params["width"] = "720"
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=20)
        if resp.status_code != 200:
            return [], resp.status_code
        html = resp.text
        obj_urls = re.findall(r'"objURL"\s*:\s*"([^"]+)"', html)
        img_data_list = re.findall(r'data-imgurl="([^"]+)"', html)
        all_urls = list(set(obj_urls + img_data_list))
        results = []
        for img_url in all_urls:
            img_url = img_url.replace("\\/", "/")
            if not img_url.startswith("http"):
                continue
            results.append({"url": img_url, "title": "", "source_url": ""})
        return results, 0
    except Exception as e:
        return [], str(e)


def download_image(url, save_path):
    try:
        from PIL import Image
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Referer": "https://image.baidu.com/",
        }
        resp = requests.get(url, headers=headers, timeout=25, allow_redirects=True)
        if resp.status_code != 200:
            return False, 0, (0, 0)
        data = resp.content
        if len(data) < 20 * 1024:
            return False, 0, (0, 0)
        img = Image.open(BytesIO(data))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        w, h = img.size
        if w > 1200:
            ratio = 1200 / w
            img = img.resize((1200, int(h * ratio)), Image.Resampling.LANCZOS)
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        quality = 90
        out = BytesIO()
        while quality >= 55:
            out.seek(0)
            out.truncate()
            img.save(out, format="JPEG", quality=quality, optimize=True)
            if out.tell() <= 800 * 1024:
                break
            quality -= 5
        save_path_jpg = str(Path(save_path).with_suffix(".jpg"))
        with open(save_path_jpg, "wb") as f:
            f.write(out.getvalue())
        return True, out.tell(), (w, h)
    except Exception as e:
        return False, 0, (0, 0)


def read_data_js():
    if not os.path.exists(DATA_JS_PATH):
        return []
    try:
        with open(DATA_JS_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        m = re.search(r'export const wallpaperData = (\[.*?\]);', content, re.DOTALL)
        if m:
            return json.loads(m.group(1))
    except Exception as e:
        log(f"读取 data.js 失败: {e}")
    return []


def load_existing_hashes():
    seen = set()
    if not os.path.exists(DATA_JS_PATH):
        return seen
    try:
        with open(DATA_JS_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        for m in re.finditer(r'"imageFile"\s*:\s*"([^"]+)"', content):
            fname = m.group(1)
            parts = fname.replace(".jpg", "").replace(".png", "").replace(".webp", "").split("_")
            if len(parts) >= 2:
                seen.add(parts[-1])
    except:
        pass
    return seen


def write_data_js(items):
    existing_games = set(it["game"] for it in items)
    games_list = [g for g in GAMES_LIST if g["name"] in existing_games]
    for g in existing_games:
        if g not in [x["name"] for x in games_list]:
            games_list.append({"id": g.lower().replace(" ", ""), "name": g})
    with open(DATA_JS_PATH, "w", encoding="utf-8") as f:
        f.write("// 自动生成：多源爬虫（米游社 + B站 + 百度图 + 官方 + 玉足社补图）\n\n")
        f.write("export const GAMES = ")
        json.dump(games_list, f, ensure_ascii=False, indent=2)
        f.write(";\n\n")
        f.write("export const STYLES = [\"3D渲染\", \"2.5D\", \"动漫插画\", \"Live2D\"];\n\n")
        f.write("export const wallpaperData = ")
        json.dump(items, f, ensure_ascii=False, indent=2)
        f.write(";\n\n")
        f.write("export function getFallbackImageUrl(id, w = 400, h = 712) {\n")
        f.write("  return `https://picsum.photos/seed/an_${id}/${w}/${h}`;\n")
        f.write("}\n")


def main():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    seen_hashes = load_existing_hashes()
    existing_items = read_data_js()
    max_id = max([it["id"] for it in existing_items] or [0])
    idx = max_id + 1
    total_items = existing_items.copy()
    fetched = 0
    used_keyword_count = {}

    log(f"=== 玉足社补图启动 | 已有 {len(existing_items)} 张 | 最多 +{MAX_PER_RUN} ===")

    for keyword, game, char_pool, yuzu_tags in YUZU_QUERIES:
        if fetched >= MAX_PER_RUN:
            break
        if used_keyword_count.get(keyword, 0) >= MAX_IMGS_PER_QUERY:
            continue

        log(f"🔍 搜索: {keyword}")
        results, code = baidu_image_search(keyword)
        random_delay()

        if not results:
            log(f"  ⚠️ 无结果 (code={code})")
            continue

        log(f"  找到 {len(results)} 张候选图")

        for img_info in results:
            if fetched >= MAX_PER_RUN:
                break
            if used_keyword_count.get(keyword, 0) >= MAX_IMGS_PER_QUERY:
                break

            img_url = img_info["url"]
            url_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
            if url_hash in seen_hashes:
                continue
            seen_hashes.add(url_hash)

            ok, size, (w, h) = download_image(img_url, os.path.join(DOWNLOAD_DIR, f"{idx}_{url_hash}.jpg"))
            if not ok:
                continue

            is_portrait = (h / w) >= 1.2 if w > 0 else True
            char_name = guess_char(img_info.get("title", ""), char_pool)
            main_tag = random.choice(yuzu_tags)
            title = f"{char_name}·{main_tag}"

            tags = [char_name, game, main_tag] + [t for t in yuzu_tags if t != main_tag]
            tags = tags[:6]
            # 确保 tags 里一定有玉足社能匹配到的关键词
            yuzu_matchers = ["足", "脚", "腿", "foot", "leg", "feet", "stocking", "pantyhose", "裸足", "丝袜", "玉足", "脚趾", "美腿", "长腿", "黑丝", "白丝", "过膝袜", "thigh", "soles", "踝"]
            if not any(k in " ".join(tags).lower() for k in yuzu_matchers):
                tags.append(yuzu_tags[-1])  # 兜底加一个

            total_items.append({
                "id": idx,
                "title": title[:55],
                "characterName": char_name,
                "game": game,
                "gender": "女",
                "style": "动漫插画",
                "tags": tags,
                "likes": 0,
                "rarity": "SSR",
                "source": "百度图片",
                "nsfw": False,
                "imageFile": f"{idx}_{url_hash}.jpg",
                "yuzu": True,
            })
            fetched += 1
            used_keyword_count[keyword] = used_keyword_count.get(keyword, 0) + 1
            orientation = "竖图" if is_portrait else "横图"
            log(f"    ✓ [{orientation}] {title} ({size//1024}KB) [+{fetched}/{MAX_PER_RUN}]")
            random_delay()

    log(f"=== 玉足社补图结束 | 新增 {fetched} 张 | 总计 {len(total_items)} ===")
    if fetched > 0:
        write_data_js(total_items)
        log("📦 data.js 已覆写")


if __name__ == "__main__":
    main()
