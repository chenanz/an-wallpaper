"""
B站专栏壁纸爬虫 — 补非米游游戏的图（明日方舟/蔚蓝档案/碧蓝航线等）
大陆直连，无需梯子

用法：
  python sync_bilibili.py              # 单轮
  python sync_bilibili.py --incremental # 增量续爬
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

# 自动定位到项目根目录（无论从哪里运行）
_SCRIPT_DIR = Path(__file__).resolve().parent
if (_SCRIPT_DIR / "src" / "data.js").exists():
    PROJECT_ROOT = str(_SCRIPT_DIR)
elif (_SCRIPT_DIR.parent / "an-app" / "src" / "data.js").exists():
    PROJECT_ROOT = str(_SCRIPT_DIR.parent / "an-app")
else:
    # 兜底：硬编码
    PROJECT_ROOT = r"D:\风\hermes\an-app"
os.chdir(PROJECT_ROOT)

DOWNLOAD_DIR = "public/images"
DATA_JS_PATH = "src/data.js"
LOG_PATH = "public/images/.crawl_log.txt"

MIN_DELAY = 3.0
MAX_DELAY = 8.0
MAX_PER_QUERY = 5       # 每个搜索词最多取5篇专栏
MAX_IMGS_PER_ARTICLE = 4  # 每篇专栏最多取4张图
MAX_PER_RUN = 20          # 每轮最多下载20张
MIN_IMAGE_BYTES = 20 * 1024
MAX_IMAGE_WIDTH = 1200
MAX_IMAGE_KB = 800

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
]

MALE_BLOCKLIST = [
    "博士男","男博士","男MC","男主","哥哥","弟弟","老公",
    "银灰","山","傀影","流明","棘刺","送葬人","号角",
]

SKIP_KEYWORDS = [
    "cos","cosplay","手办","攻略","养成","联动","实物","周边",
    "抽卡","强度","测评","评测","节奏榜","配队","模组",
    "男","男主","男角色","男性",
]

# B站搜索词 → 游戏名 → 默认角色池
BILI_QUERIES = [
    # 明日方舟
    ("明日方舟 女角色 壁纸", "明日方舟", ["阿米娅","德克萨斯","能天使","斯卡蒂","陈"," 凯尔希","迷迭香","澄闪","琴柳","焰尾","令","夕","年","W","浊心斯卡蒂","假日威龙陈"]),
    ("明日方舟 壁纸 高清", "明日方舟", ["阿米娅","德克萨斯","斯卡蒂","陈","澄闪"]),
    ("arknights wallpaper", "明日方舟", ["阿米娅","德克萨斯","斯卡蒂"]),
    # 蔚蓝档案
    ("蔚蓝档案 壁纸", "蔚蓝档案", ["白子","优香","星野","日奈","未花","爱露","阿露","睦月","小春","梓","爱丽丝","花凛","晴奈","芹香","知世"]),
    ("碧蓝档案 壁纸", "蔚蓝档案", ["白子","优香","星野","日奈","未花"]),
    ("Blue Archive wallpaper", "蔚蓝档案", ["白子","星野"]),
    # 碧蓝航线
    ("碧蓝航线 壁纸", "碧蓝航线", ["信浓","企业","贝尔法斯特","光辉","可畏","埃塞克斯","长门","天城","赤城","加贺","约克城","胡蜂"]),
    ("碧蓝航线 女角色 壁纸", "碧蓝航线", ["信浓","企业","光辉"]),
    # 第七史诗
    ("第七史诗 女角色 壁纸", "第七史诗", ["塔玛林德","华伦薇","洁馥薇","维瑞德","兰蒂","塞西莉亚"]),
    # 少女前线
    ("少女前线 壁纸", "少女前线", ["HK416","UMP45","M4A1","AR15","AK12","AN94","SPAS12","内格夫"]),
    # 战双帕弥什
    ("战双帕弥什 壁纸", "战双帕弥什", ["露西亚","丽芙","露娜","阿尔法","薇拉","比安卡","赛琳娜"]),
    # FGO
    ("FGO 壁纸 女角色", "FGO", ["阿尔托莉雅","贞德","玛修","摩根","斯卡哈","伽摩","太岁","伊什塔尔","远坂凛"]),
    # 通用补充
    ("原神 女角色 壁纸 高清", "原神", ["雷电将军","胡桃","纳西妲","芙宁娜","甘雨","绫华","宵宫"]),
    ("崩坏星穹铁道 女角色 壁纸", "崩坏：星穹铁道", ["黄泉","流萤","黑天鹅","花火","知更鸟","阮梅","镜流"]),
]


def log(msg):
    ts = datetime.now().strftime("%m-%d %H:%M:%S")
    line = f"[{ts}][B站] {msg}"
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


def guess_article_char(title, char_pool):
    """从标题猜角色名"""
    for char in sorted(char_pool, key=len, reverse=True):
        if char in title:
            return char
    # 标题没有角色名，随机选一个
    return random.choice(char_pool) if char_pool else "精选角色"


def search_bilibili(keyword, page=1, page_size=10):
    """搜索B站专栏"""
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": "https://search.bilibili.com/",
        "Accept": "application/json",
    }
    url = f"https://api.bilibili.com/x/web-interface/search/type"
    params = {
        "keyword": keyword,
        "search_type": "article",
        "page": page,
        "page_size": page_size,
    }
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        if resp.status_code != 200:
            return None, resp.status_code
        data = resp.json()
        items = (data.get("data") or {}).get("result") or []
        return items, 0
    except Exception as e:
        return None, str(e)


def get_article_images(cvid):
    """读取专栏内容，提取所有图片URL和尺寸"""
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": "https://www.bilibili.com/",
        "Accept": "application/json",
    }
    url = f"https://api.bilibili.com/x/article/view?gm=0&id={cvid}"
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            return [], resp.status_code
        data = resp.json().get("data", {})
        content = data.get("content", "")
        
        # 提取图片URL（//i0.hdslb.com/...格式）
        img_urls = re.findall(r'src="//(i\d+\.hdslb\.com/[^"]+)"', content)
        img_urls = [f"https://{u}" for u in img_urls]
        
        # 提取对应尺寸
        widths = [int(x) for x in re.findall(r'width="(\d+)"', content)]
        heights = [int(x) for x in re.findall(r'height="(\d+)"', content)]
        
        # 配对
        results = []
        for i, img_url in enumerate(img_urls):
            w = widths[i] if i < len(widths) else 0
            h = heights[i] if i < len(heights) else 0
            ratio = h / w if w > 0 else 0
            is_portrait = ratio >= 1.2  # 竖图或方图
            results.append({
                "url": img_url,
                "width": w,
                "height": h,
                "is_portrait": is_portrait,
            })
        
        return results, 0
    except Exception as e:
        return [], str(e)


def download_image(url, save_path):
    try:
        from PIL import Image
        resp = requests.get(url, headers={
            "User-Agent": random.choice(USER_AGENTS),
            "Referer": "https://www.bilibili.com/",
        }, timeout=30)
        resp.raise_for_status()
        data = resp.content
        if len(data) < MIN_IMAGE_BYTES:
            return False, 0

        img = Image.open(BytesIO(data))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        w, h = img.size
        if w > MAX_IMAGE_WIDTH:
            ratio = MAX_IMAGE_WIDTH / w
            img = img.resize((MAX_IMAGE_WIDTH, int(h * ratio)), Image.Resampling.LANCZOS)

        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        quality = 90
        out = BytesIO()
        while quality >= 60:
            out.seek(0)
            out.truncate()
            img.save(out, format="JPEG", quality=quality, optimize=True)
            if out.tell() <= MAX_IMAGE_KB * 1024:
                break
            quality -= 5

        save_path = str(Path(save_path).with_suffix(".jpg"))
        with open(save_path, "wb") as f:
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
        # 找到最后一个 ; 之前的 ]，即数组结尾
        # 先定位 "export const wallpaperData = " 的起始位置
        marker = "export const wallpaperData = "
        start = content.find(marker)
        if start < 0:
            return []
        start += len(marker)
        # 从 start 位置找到匹配括号的结束
        depth = 0
        end = start
        for i in range(start, len(content)):
            if content[i] == '[':
                depth += 1
            elif content[i] == ']':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        arr_text = content[start:end]
        return json.loads(arr_text)
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
            # 从文件名提取hash
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


def read_games_js():
    """读取现有 data.js 中的 GAMES 列表"""
    if not os.path.exists(DATA_JS_PATH):
        return []
    try:
        with open(DATA_JS_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        marker = "export const GAMES = "
        start = content.find(marker)
        if start < 0:
            return []
        start += len(marker)
        depth = 0
        end = start
        for i in range(start, len(content)):
            if content[i] == '[':
                depth += 1
            elif content[i] == ']':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        return json.loads(content[start:end])
    except:
        return []


def write_data_js(items):
    # 优先从现有 data.js 读取 GAMES 列表，保留已有的（如足社）
    existing_games_list = read_games_js()
    existing_game_names = set(g["name"] for g in existing_games_list)
    
    # 统计 items 中出现的游戏
    items_game_names = set(it["game"] for it in items)
    
    # 把 items 中有但 GAMES 列表里没有的游戏补上
    preset = get_games_list()
    for g in preset:
        if g["name"] in items_game_names and g["name"] not in existing_game_names:
            existing_games_list.append(g)
            existing_game_names.add(g["name"])
    # 不在预设列表里的也补上
    for gname in items_game_names:
        if gname not in existing_game_names:
            existing_games_list.append({"id": gname.lower().replace(" ", ""), "name": gname})
            existing_game_names.add(gname)
    
    # 保留不在 items 中的已有游戏（如足社）
    games_list = existing_games_list

    with open(DATA_JS_PATH, "w", encoding="utf-8") as f:
        f.write("// 自动生成：多源爬虫（米游社 + B站 + 百度图 + 官方 + 足社爬虫v3）\n\n")
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

    log(f"=== B站爬虫启动 | 已有 {len(existing_items)} 张 | 最多 +{MAX_PER_RUN} ===")

    for keyword, game, char_pool in BILI_QUERIES:
        if fetched >= MAX_PER_RUN:
            break

        log(f"🔍 搜索: {keyword}")

        # 搜索专栏
        articles, code = search_bilibili(keyword)
        random_delay()

        if articles is None:
            log(f"  ⚠️ 搜索失败: {code}")
            continue

        if not articles:
            log(f"  ⚠️ 无结果")
            continue

        article_count = 0
        for art in articles[:MAX_PER_QUERY]:
            if fetched >= MAX_PER_RUN:
                break
            if article_count >= MAX_PER_QUERY:
                break

            cvid = str(art.get("id", ""))
            title_raw = art.get("title", "").replace('<em class="keyword">', '').replace('</em>', '')
            
            # 过滤
            if is_blocked(title_raw):
                log(f"  ⏭ 跳过(标题过滤): {title_raw[:30]}")
                continue

            log(f"  📖 专栏 cv{cvid}: {title_raw[:35]}")

            # 获取专栏图片
            images, code = get_article_images(cvid)
            random_delay()

            if not images:
                log(f"    ⚠️ 无图或获取失败")
                continue

            article_count += 1
            char_name = guess_article_char(title_raw, char_pool)
            style = "动漫插画"  # B站同人图归动漫插画类

            # 优先取竖图
            portraits = [img for img in images if img["is_portrait"]]
            candidates = (portraits + images)[:MAX_IMGS_PER_ARTICLE]  # 竖图优先，不够补横图

            for img_info in candidates:
                if fetched >= MAX_PER_RUN:
                    break

                img_url = img_info["url"]
                url_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
                if url_hash in seen_hashes:
                    continue
                seen_hashes.add(url_hash)

                ok, size = download_image(img_url, os.path.join(DOWNLOAD_DIR, f"{idx}_{url_hash}.jpg"))
                if not ok:
                    continue

                title = re.sub(r"\s*[\[\(【].*?[\]\)】]", "", title_raw).strip()
                if len(title) < 4:
                    title = f"{char_name}·精选壁纸"

                orientation = "竖图" if img_info["is_portrait"] else "横图"

                total_items.append({
                    "id": idx,
                    "title": title[:55],
                    "characterName": char_name,
                    "game": game,
                    "gender": "女",
                    "style": style,
                    "tags": [char_name, game, "B站"][:6],
                    "likes": 0,
                    "rarity": "SSR",
                    "source": "Bilibili",
                    "nsfw": False,
                    "imageFile": f"{idx}_{url_hash}.jpg",
                    "bili_cvid": cvid,
                })
                fetched += 1
                idx += 1
                log(f"    ✓ [{orientation}] {char_name} ({size//1024}KB) [+{fetched}/{MAX_PER_RUN}]")

                random_delay()

    log(f"=== B站爬虫结束 | 新增 {fetched} 张 | 总计 {len(total_items)} ===")
    
    if fetched > 0:
        write_data_js(total_items)
        log("📦 data.js 已覆写 + 触发构建")
        os.system("npm run build")


if __name__ == "__main__":
    main()
