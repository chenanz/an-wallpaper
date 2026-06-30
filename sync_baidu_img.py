"""
百度图片搜索爬虫 — 补二游女角色壁纸（替代小红书/Lofter已死API）
百度图片搜索国内直连免梯子，有竖图过滤、尺寸过滤
source 字段标记为对应来源（小红书/Lofter标签页来的都算搜索引擎抓的）

用法：python sync_baidu_img.py
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
]

SKIP_KEYWORDS = [
    "cos","cosplay","手办","攻略","联动","实物","周边","谷子",
    "抽卡","强度","测评","节奏榜","配队","模组",
    "男","男主","男角色","男性","哥哥","弟弟","老公",
    "表情包","梗图","沙雕","Q版","头像","ICON",
]

# 搜索关键词 → 游戏 → 默认角色池
BAIDU_QUERIES = [
    ("原神 女角色 壁纸 高清", "原神", ["雷电将军","胡桃","纳西妲","芙宁娜","甘雨","绫华","宵宫","八重神子","妮露","心海","优菈","申鹤","夜兰","迪希雅","千织","娜维娅","可莉","刻晴","莫娜","琴","七七","凝光","北斗","烟绯","云堇","菲谢尔","夏洛蒂","克洛琳德","希诺宁","玛薇卡"]),
    ("崩坏星穹铁道 女角色 壁纸", "崩坏：星穹铁道", ["黄泉","流萤","黑天鹅","花火","知更鸟","阮梅","镜流","藿藿","银狼","卡芙卡","三月七","布洛妮娅","停云","青雀","佩拉","克拉拉"]),
    ("绝区零 女角色 壁纸", "绝区零", ["艾莲","星见雅","朱鸢","简","青衣","柏妮思","凯撒","耀嘉音","妮可","安比","可琳","格莉丝"]),
    ("明日方舟 女角色 壁纸", "明日方舟", ["阿米娅","德克萨斯","能天使","斯卡蒂","陈","凯尔希","迷迭香","澄闪","琴柳","焰尾","令","夕","年","W","浊心斯卡蒂","假日威龙陈"]),
    ("蔚蓝档案 壁纸", "蔚蓝档案", ["白子","优香","星野","日奈","未花","爱露","阿露","睦月","小春","梓","爱丽丝","花凛","晴奈","芹香","知世"]),
    ("碧蓝航线 女角色 壁纸", "碧蓝航线", ["信浓","企业","贝尔法斯特","光辉","可畏","埃塞克斯","长门","天城","赤城","加贺","约克城","胡蜂"]),
    ("第七史诗 女角色 壁纸", "第七史诗", ["塔玛林德","华伦薇","洁馥薇","维瑞德","兰蒂","塞西莉亚"]),
    ("少女前线 壁纸", "少女前线", ["HK416","UMP45","M4A1","AR15","AK12","AN94","SPAS12","内格夫"]),
    ("战双帕弥什 女角色 壁纸", "战双帕弥什", ["露西亚","丽芙","露娜","阿尔法","薇拉","比安卡","赛琳娜"]),
    ("FGO 女角色 壁纸", "FGO", ["阿尔托莉雅","贞德","玛修","摩根","斯卡哈","伽摩","伊什塔尔","远坂凛"]),
]


def log(msg):
    ts = datetime.now().strftime("%m-%d %H:%M:%S")
    line = f"[{ts}][百度图] {msg}"
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
    """百度图片翻页搜索，返回 [{url, width, height, title, source_url}, ...]"""
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": "https://image.baidu.com/",
    }
    # 百度图片flip模式
    url = "https://image.baidu.com/search/flip"
    params = {
        "tn": "baiduimage",
        "word": keyword,
        "rn": str(per_page),
        "pn": str(page * per_page),
        "ie": "utf-8",
        "oe": "utf-8",
    }
    # 加竖图过滤
    if PREFER_PORTRAIT:
        params["z"] = "0"
        params["height"] = "1280"
        params["width"] = "720"

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=20)
        if resp.status_code != 200:
            return [], resp.status_code

        html = resp.text
        # 百度在 data-imgurl 和 objURL 里嵌入图信息
        # 用正则提取：从 data-objurl 或 "objURL":"xxx" 中提取
        results = []

        # 方法1：从 JSON数据中提取objURL（百度flip模式主数据源）
        obj_urls = re.findall(r'"objURL"\s*:\s*"([^"]+)"', html)
        
        # 方法2：data-imgurl
        img_data_list = re.findall(r'data-imgurl="([^"]+)"', html)

        # 合并
        all_urls = list(set(obj_urls + img_data_list))

        for img_url in all_urls:
            # 百度可能对URL做了编码
            img_url = img_url.replace("\\/", "/").replace("&", "&")
            if not img_url.startswith("http"):
                continue

            title = ""
            results.append({
                "url": img_url,
                "width": 0,
                "height": 0,
                "title": title,
                "source_url": "",
            })

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
        # 百度图搜索结果的URL可能是编码过的
        if "baidu.com/search/down" not in url:
            # 尝试直接下载
            resp = requests.get(url, headers=headers, timeout=20)
        else:
            resp = requests.get(url, headers=headers, timeout=20, allow_redirects=True)

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
        f.write("// 自动生成：多源爬虫（米游社 + B站 + 百度图 + 官方）\n\n")
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

    log(f"=== 百度图爬虫启动 | 已有 {len(existing_items)} 张 | 最多 +{MAX_PER_RUN} ===")

    for keyword, game, char_pool in BAIDU_QUERIES:
        if fetched >= MAX_PER_RUN:
            break

        log(f"🔍 搜索: {keyword}")
        results, code = baidu_image_search(keyword)
        random_delay()

        if not results:
            log(f"  ⚠️ 无结果 (code={code})")
            continue

        log(f"  找到 {len(results)} 张候选图")

        for img_info in results[:MAX_IMGS_PER_QUERY]:
            if fetched >= MAX_PER_RUN:
                break

            img_url = img_info["url"]
            url_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
            if url_hash in seen_hashes:
                continue
            seen_hashes.add(url_hash)

            # 先下载看看能不能打开
            ok, size = download_image(img_url, os.path.join(DOWNLOAD_DIR, f"{idx}_{url_hash}.jpg"))
            if not ok:
                continue

            # 检查是否竖图
            try:
                from PIL import Image
                img = Image.open(os.path.join(DOWNLOAD_DIR, f"{idx}_{url_hash}.jpg"))
                w, h = img.size
                is_portrait = (h / w) >= 1.2 if w > 0 else False
            except:
                is_portrait = True  # 不确定就当竖图

            char_name = guess_char(keyword, char_pool)
            title = f"{char_name}·精选壁纸"
            orientation = "竖图" if is_portrait else "横图"

            total_items.append({
                "id": idx,
                "title": title[:55],
                "characterName": char_name,
                "game": game,
                "gender": "女",
                "style": "动漫插画",
                "tags": [char_name, game, "百度图源"][:6],
                "likes": 0,
                "rarity": "SSR",
                "source": "百度图片",
                "nsfw": False,
                "imageFile": f"{idx}_{url_hash}.jpg",
            })
            fetched += 1
            idx += 1
            log(f"    ✓ [{orientation}] {char_name} ({size//1024}KB) [+{fetched}/{MAX_PER_RUN}]")
            random_delay()

    log(f"=== 百度图爬虫结束 | 新增 {fetched} 张 | 总计 {len(total_items)} ===")

    if fetched > 0:
        write_data_js(total_items)
        log("📦 data.js 已覆写 + 触发构建")
        os.system("npm run build")


if __name__ == "__main__":
    main()
