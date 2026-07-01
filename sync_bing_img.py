"""
Bing图片搜索爬虫 — 补二游同人壁纸（Lofter API已死，改用Bing搜索）
Bing国内可直连，竖图过滤支持好，图片质量比百度高

用法：python sync_bing_img.py
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

MIN_DELAY = 4.0
MAX_DELAY = 10.0
MAX_PER_RUN = 25
MAX_IMGS_PER_QUERY = 8

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
]

SKIP_KEYWORDS = [
    "cos","cosplay","手办","攻略","联动","实物","周边","谷子",
    "抽卡","强度","测评","节奏榜","配队","模组",
    "男","男主","男角色","男性","哥哥","弟弟","老公",
    "表情包","梗图","沙雕","Q版","头像","ICON",
]

BING_QUERIES = [
    ("原神同人壁纸 女角色", "原神", ["雷电将军","胡桃","纳西妲","芙宁娜","甘雨","绫华","宵宫","八重神子","妮露","心海","优菈","申鹤","夜兰"]),
    ("崩坏星穹铁道同人 女角色", "崩坏：星穹铁道", ["黄泉","流萤","黑天鹅","花火","知更鸟","阮梅","镜流","藿藿","银狼","卡芙卡"]),
    ("明日方舟同人 女角色 壁纸", "明日方舟", ["阿米娅","德克萨斯","能天使","斯卡蒂","陈","凯尔希","澄闪","琴柳","令","夕","年","W","浊心斯卡蒂"]),
    ("蔚蓝档案同人 壁纸", "蔚蓝档案", ["白子","优香","星野","日奈","未花","爱露","阿露","小春","梓","爱丽丝","花凛","晴奈"]),
    ("碧蓝航线同人 女角色", "碧蓝航线", ["信浓","企业","贝尔法斯特","光辉","可畏","埃塞克斯","长门","天城","赤城","加贺"]),
    ("第七史诗 女角色 壁纸", "第七史诗", ["塔玛林德","华伦薇","洁馥薇","维瑞德","兰蒂","塞西莉亚"]),
    ("战双帕弥什 女角色 壁纸", "战双帕弥什", ["露西亚","丽芙","露娜","阿尔法","薇拉","比安卡","赛琳娜"]),
    ("FGO 女角色 壁纸", "FGO", ["阿尔托莉雅","贞德","玛修","摩根","斯卡哈","伽摩","伊什塔尔","远坂凛"]),
]


def log(msg):
    ts = datetime.now().strftime("%m-%d %H:%M:%S")
    line = f"[{ts}][Bing图] {msg}"
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


def guess_char(title, keyword, char_pool):
    for char in sorted(char_pool, key=len, reverse=True):
        if char in title or char in keyword:
            return char
    return random.choice(char_pool) if char_pool else "精选角色"


def bing_image_search(keyword, count=35, portrait=True):
    """Bing图片异步搜索API，返回 [{url, width, height, title, source}, ...]"""
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": "https://cn.bing.com/images/",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    base_url = "https://cn.bing.com/images/async"
    qft = "+filterui:aspect-tall" if portrait else ""
    params = {
        "q": keyword,
        "count": str(count),
        "first": "0",
        "qft": qft,
        "mmasync": "1",
    }

    try:
        resp = requests.get(base_url, headers=headers, params=params, timeout=20)
        if resp.status_code != 200:
            return [], resp.status_code

        html = resp.text
        results = []

        # Bing async 返回HTML，图片信息在 m="..." JSON块内
        # 注意：Bing用 " 编码JSON，需要先HTML解码
        import html as html_module
        m_blocks = re.findall(r'm="([^"]+)"', html)
        for block in m_blocks:
            try:
                # HTML实体解码
                block = html_module.unescape(block)
                data = json.loads(block)
                murl = data.get("murl", "")
                if not murl or not murl.startswith("http"):
                    continue
                results.append({
                    "url": murl,
                    "width": data.get("mw", 0),
                    "height": data.get("mh", 0),
                    "title": data.get("t", ""),
                    "source": data.get("surl", ""),
                })
            except:
                continue

        return results, 0
    except Exception as e:
        return [], str(e)


def download_image(url, save_path):
    try:
        from PIL import Image
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Referer": "https://cn.bing.com/",
        }
        resp = requests.get(url, headers=headers, timeout=25)
        if resp.status_code != 200:
            return False, 0

        data = resp.content
        if len(data) < 20 * 1024:
            return False, 0

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
        return True, out.tell()
    except Exception as e:
        return False, 0


def read_data_js():
    if not os.path.exists(DATA_JS_PATH):
        return []
    try:
        with open(DATA_JS_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        m = re.search(r'export const wallpaperData = (\[.*\])\s*\r?\n', content, re.DOTALL)
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


def get_games_list():
    return [
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


def write_data_js(items):
    existing_games = set(it["game"] for it in items)
    games_list = [g for g in get_games_list() if g["name"] in existing_games]
    for g in existing_games:
        if g not in [x["name"] for x in games_list]:
            games_list.append({"id": g.lower().replace(" ", ""), "name": g})

    with open(DATA_JS_PATH, "w", encoding="utf-8") as f:
        f.write("// 自动生成：多源爬虫（米游社 + B站 + 百度图 + Bing + 官方）\n\n")
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

    log(f"=== Bing图爬虫启动 | 已有 {len(existing_items)} 张 | 最多 +{MAX_PER_RUN} ===")

    for keyword, game, char_pool in BING_QUERIES:
        if fetched >= MAX_PER_RUN:
            break

        log(f"🔍 搜索(竖图): {keyword}")
        results, code = bing_image_search(keyword, portrait=True)
        random_delay()

        # 竖图不够就补充搜索不带过滤的
        if len(results) < 3:
            log(f"  竖图不足，补搜横图")
            results2, _ = bing_image_search(keyword, portrait=False)
            results = results + results2
            random_delay()

        if not results:
            log(f"  ⚠️ 无结果 (code={code})")
            continue

        log(f"  找到 {len(results)} 张候选图，开始下载…")

        for img_info in results[:MAX_IMGS_PER_QUERY]:
            if fetched >= MAX_PER_RUN:
                break

            img_url = img_info["url"]
            title_raw = img_info.get("title", "")

            if is_blocked(title_raw):
                continue

            url_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
            if url_hash in seen_hashes:
                continue
            seen_hashes.add(url_hash)

            ok, size = download_image(img_url, os.path.join(DOWNLOAD_DIR, f"{idx}_{url_hash}.jpg"))
            if not ok:
                continue

            char_name = guess_char(title_raw, keyword, char_pool)
            title = re.sub(r"\s*[\[\(【].*?[\]\)】]", "", title_raw).strip() if title_raw else ""
            if len(title) < 4:
                title = f"{char_name}·同人壁纸"

            total_items.append({
                "id": idx,
                "title": title[:55],
                "characterName": char_name,
                "game": game,
                "gender": "女",
                "style": "动漫插画",
                "tags": [char_name, game, "同人"][:6],
                "likes": 0,
                "rarity": "SSR",
                "source": "Bing搜索",
                "nsfw": False,
                "imageFile": f"{idx}_{url_hash}.jpg",
            })
            fetched += 1
            idx += 1
            log(f"    ✓ {char_name} ({size//1024}KB) [+{fetched}/{MAX_PER_RUN}]")
            random_delay()

    log(f"=== Bing图爬虫结束 | 新增 {fetched} 张 | 总计 {len(total_items)} ===")

    if fetched > 0:
        write_data_js(total_items)
        log("📦 data.js 已覆写 + 触发构建")
        os.system("npm run build")


if __name__ == "__main__":
    main()
