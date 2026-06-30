"""
二游女角色壁纸扒图器 V3 — 米游社版（大陆直连，不挂梯子）
模式A：精准角色搜，每个角色 5 张
模式B：泛集合搜，下合集帖全部图 → 源源不断
支持增量续爬：python sync_v3.py --incremental
"""

import os
import re
import sys
import json
import time
import hashlib
import requests
from PIL import Image
from urllib.parse import quote
from pathlib import Path

DOWNLOAD_DIR = "public/images"
DATA_JS_PATH = "src/data.js"
INCREMENTAL = "--incremental" in sys.argv

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://bbs.miyoushe.com/",
}

# 硬性过滤
MALE_BLOCKLIST = [
    "钟离","魈","达达利亚","公子","阿贝多","温迪","万叶","枫原万叶",
    "荒泷一斗","提纳里","赛诺","艾尔海森","卡维","那维莱特","莱欧斯利",
    "景元","刃","丹恒","杰帕德","桑博","卢卡","彦卿","罗刹",
    "凯文","奥托","齐格飞","瓦尔特","虚空万藏",
    "哲","安东","本","莱卡恩","苍角",
    "银灰","棘刺","山","傀影","流明",
]

SKIP_KEYWORDS = [
    "cos","cosplay","手办","攻略","养成","一图流","联动","实物",
    "光锥","抽卡","抽取","卡池","强度","测评","评测","周边","谷子",
    "Q版","表情包","梗图","沙雕","抽","专武","圣遗物","阵容",
    "配队","深渊","面板","伤害","DPS","排行","节奏榜",
    "男","男主","哥哥","弟弟","老公",
]

BOOST_KEYWORDS = ["壁纸","立绘","绘图","插画","日历","月历","同人","美图","分享","收藏","精选","合集","超清","高清"]

VALID_STYLES = {"3D渲染","2.5D","动漫插画","Live2D"}
STYLE_MAP = {"3D":"3D渲染","3DCG":"3D渲染","Live2D":"Live2D","live2d":"Live2D","2.5D":"2.5D","2.5次元":"2.5D"}

MIN_IMAGE_BYTES = 15 * 1024
MAX_IMAGE_WIDTH = 1200
MAX_IMAGE_KB = 800
REQUEST_DELAY = 1.0
MAX_PER_CHAR = 5       # 每个角色最多几张
MAX_PER_POST = 5       # 每个帖子最多取几张
TARGET_TOTAL = 500     # 目标总张数（模式A+模式B）

GAME_NAMES = {1: "崩坏3", 2: "原神", 6: "崩坏：星穹铁道", 8: "绝区零"}

CHARACTERS = {
    2: [
        ("雷电将军","3D渲染"),("胡桃","动漫插画"),("纳西妲","动漫插画"),("芙宁娜","3D渲染"),
        ("甘雨","3D渲染"),("宵宫","动漫插画"),("绫华","3D渲染"),("八重神子","3D渲染"),
        ("妮露","3D渲染"),("心海","3D渲染"),("优菈","3D渲染"),("申鹤","3D渲染"),
        ("夜兰","3D渲染"),("迪希雅","3D渲染"),("千织","3D渲染"),("娜维娅","3D渲染"),
        ("克洛琳德","3D渲染"),("希诺宁","3D渲染"),("玛薇卡","3D渲染"),("茜特菈莉","动漫插画"),
        ("恰斯卡","3D渲染"),("艾梅莉埃","3D渲染"),("闲云","3D渲染"),("夏洛蒂","动漫插画"),
    ],
    1: [
        ("布洛妮娅","3D渲染"),("琪亚娜","3D渲染"),("雷电芽衣","3D渲染"),("希儿","3D渲染"),
        ("爱莉希雅","3D渲染"),("符华","3D渲染"),("丽塔","3D渲染"),("幽兰黛尔","3D渲染"),
        ("德丽莎","动漫插画"),("姬子","3D渲染"),
    ],
    6: [
        ("黄泉","3D渲染"),("流萤","3D渲染"),("黑天鹅","3D渲染"),("花火","3D渲染"),
        ("知更鸟","3D渲染"),("阮梅","3D渲染"),("镜流","3D渲染"),("藿藿","动漫插画"),
        ("银狼","2.5D"),("卡芙卡","3D渲染"),("三月七","动漫插画"),("布洛妮娅","3D渲染"),
        ("停云","动漫插画"),("青雀","动漫插画"),("佩拉","动漫插画"),("希儿","3D渲染"),
    ],
    8: [
        ("艾莲","3D渲染"),("星见雅","3D渲染"),("朱鸢","3D渲染"),("简","3D渲染"),
        ("青衣","3D渲染"),("柏妮思","3D渲染"),("凯撒","3D渲染"),("耀嘉音","3D渲染"),
        ("妮可","3D渲染"),("安比","3D渲染"),("可琳","3D渲染"),("格莉丝","3D渲染"),
    ],
}

# 泛搜关键词（不绑定具体角色）
BULK_QUERIES = {
    2: ["原神 女角色 壁纸 合集", "原神 壁纸 高清", "原神 同人 壁纸"],
    6: ["崩坏星穹铁道 女角色 壁纸", "星穹铁道 壁纸 合集", "崩铁 壁纸"],
    1: ["崩坏3 女角色 壁纸", "崩坏3 壁纸 高清"],
    8: ["绝区零 女角色 壁纸", "绝区零 壁纸 合集"],
}


def log(msg):
    print(msg)


def score_post(subject):
    sub = subject.lower()
    for bad in SKIP_KEYWORDS:
        if bad.lower() in sub:
            return -9999
    for male in MALE_BLOCKLIST:
        if male in subject:
            return -9999
    score = 0
    for good in BOOST_KEYWORDS:
        if good.lower() in sub:
            score += 10
    return score


def search_miyoushe(keyword, gids, size=30):
    url = f"https://bbs-api.miyoushe.com/post/wapi/searchPosts?gids={gids}&keyword={quote(keyword)}&size={size}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        if data.get("retcode") != 0:
            return []
        return data.get("data", {}).get("posts", [])
    except Exception as e:
        log(f"  ⚠️ 请求失败: {e}")
        return []


def download_image(url, save_path):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.content
        if len(data) < MIN_IMAGE_BYTES:
            return False, 0, None

        from io import BytesIO
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
        return True, out.tell(), save_path
    except Exception as e:
        return False, 0, None


def load_existing():
    seen = set()
    if not os.path.exists(DATA_JS_PATH):
        return seen, []
    try:
        with open(DATA_JS_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        for line in content.split("\n"):
            m = re.search(r'"imageFile"\s*:\s*"([^"]+)"', line)
            if m:
                parts = m.group(1).replace(".jpg", "").split("_")
                if len(parts) >= 2:
                    seen.add(parts[-1])
    except:
        pass
    return seen, []


def guess_char_from_title(title):
    """从标题里硬匹配角色名"""
    all_chars = []
    for g_chars in CHARACTERS.values():
        all_chars.extend([c[0] for c in g_chars])
    for char in sorted(all_chars, key=len, reverse=True):
        if char in title:
            return char
    return "精选角色"


def write_data_js(all_items):
    with open(DATA_JS_PATH, "w", encoding="utf-8") as f:
        f.write("// 自动生成：python sync_v3.py\n")
        f.write("// 米游社图源，大陆直连，无需梯子\n")
        f.write("// gender 强制='女'；男角色/低质量帖已过滤\n\n")

        f.write("export const GAMES = ")
        json.dump([
            {"id": "genshin", "name": "原神"},
            {"id": "hi3", "name": "崩坏3"},
            {"id": "hsr", "name": "崩坏：星穹铁道"},
            {"id": "zzz", "name": "绝区零"},
            {"id": "arknights", "name": "明日方舟"},
            {"id": "ba", "name": "蔚蓝档案"},
        ], f, ensure_ascii=False, indent=2)
        f.write(";\n\n")

        f.write("export const STYLES = [\"3D渲染\", \"2.5D\", \"动漫插画\", \"Live2D\"];\n\n")

        f.write("export const wallpaperData = ")
        json.dump(all_items, f, ensure_ascii=False, indent=2)
        f.write(";\n\n")

        f.write("export function getFallbackImageUrl(id, w = 400, h = 712) {\n")
        f.write("  return `https://picsum.photos/seed/an_${id}/${w}/${h}`;\n")
        f.write("}\n")


def main():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    seen_hashes, _ = load_existing()
    log(f"📦 已有 {len(seen_hashes)} 张图，增量={INCREMENTAL}")

    all_items = []
    idx = 1

    # ===== 模式 A：精准角色搜 =====
    log("\n" + "=" * 40)
    log("📌 模式 A：精准角色搜索")
    log("=" * 40)

    for gids, chars in CHARACTERS.items():
        game = GAME_NAMES[gids]
        for char_name, default_style in chars:
            keyword = f"{char_name} 壁纸"
            posts = search_miyoushe(keyword, gids, size=25)
            time.sleep(REQUEST_DELAY)

            fetched = 0
            for p in posts:
                if fetched >= MAX_PER_CHAR:
                    break
                post = p.get("post", {})
                subject = post.get("subject", "")
                if score_post(subject) <= -1000:
                    continue
                images = post.get("images") or []
                if not images:
                    continue

                # 取前3张
                for img_url in images[:3]:
                    if fetched >= MAX_PER_CHAR:
                        break
                    url_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
                    if url_hash in seen_hashes:
                        continue
                    seen_hashes.add(url_hash)

                    ok, size, _ = download_image(img_url.split("?")[0], os.path.join(DOWNLOAD_DIR, f"{idx}_{url_hash}.jpg"))
                    if not ok:
                        continue

                    title = re.sub(r"\s*[\[\(【].*?[\]\)】]", "", subject).strip()
                    if len(title) < 4:
                        title = f"{char_name}·精选壁纸"

                    all_items.append({
                        "id": idx, "title": title[:55], "characterName": char_name,
                        "game": game, "gender": "女", "style": default_style,
                        "tags": [char_name, game][:6], "likes": 0, "rarity": "SSR",
                        "source": "米游社", "nsfw": False,
                        "imageFile": f"{idx}_{url_hash}.jpg",
                        "miyoushe_post_id": post.get("post_id"),
                    })
                    fetched += 1
                    idx += 1
                    log(f"  ✓ A [{char_name}] {title[:35]} ({size//1024}KB)")
                    time.sleep(REQUEST_DELAY * 0.3)

    log(f"\n📊 模式 A 结束，共 {len(all_items)} 张")

    # ===== 模式 B：泛搜合集帖（源源不断） =====
    log("\n" + "=" * 40)
    log("📌 模式 B：泛搜合集帖补量")
    log("=" * 40)

    mode_b_count = 0
    for gids, queries in BULK_QUERIES.items():
        game = GAME_NAMES[gids]
        for bulk_kw in queries:
            if len(all_items) >= TARGET_TOTAL:
                break
            log(f"\n  🔍 [{game}] 泛搜: {bulk_kw}")
            posts = search_miyoushe(bulk_kw, gids, size=20)
            time.sleep(REQUEST_DELAY)

            for p in posts:
                if len(all_items) >= TARGET_TOTAL:
                    break
                post = p.get("post", {})
                subject = post.get("subject", "")
                if score_post(subject) <= -1000:
                    continue
                images = post.get("images") or []
                if len(images) < 2:  # 合集帖至少2张图
                    continue

                # 从标题猜角色，猜不到用"精选壁纸"
                guessed_char = guess_char_from_title(subject)
                # 合集帖淡化标题
                title = re.sub(r"\s*[\[\(【].*?[\]\)】]", "", subject).strip()
                if len(title) < 4 or title == guessed_char:
                    title = f"{guessed_char}·壁纸精选"

                # 每个合集帖下 MAX_PER_POST 张
                for img_url in images[:MAX_PER_POST]:
                    url_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
                    if url_hash in seen_hashes:
                        continue
                    seen_hashes.add(url_hash)

                    ok, size, _ = download_image(img_url.split("?")[0], os.path.join(DOWNLOAD_DIR, f"{idx}_{url_hash}.jpg"))
                    if not ok:
                        continue

                    all_items.append({
                        "id": idx, "title": title[:55], "characterName": guessed_char,
                        "game": game, "gender": "女", "style": "动漫插画",
                        "tags": [guessed_char, game, "合集"][:6], "likes": 0, "rarity": "SSR",
                        "source": "米游社", "nsfw": False,
                        "imageFile": f"{idx}_{url_hash}.jpg",
                        "miyoushe_post_id": post.get("post_id"),
                    })
                    mode_b_count += 1
                    idx += 1
                    log(f"    ✓ B+ [{game}] {title[:35]} ({size//1024}KB)")
                    time.sleep(REQUEST_DELAY * 0.3)

    log(f"\n📊 模式 B 新增: {mode_b_count} 张")

    # ===== 写入 =====
    write_data_js(all_items)

    log("\n" + "=" * 40)
    log(f"✅ 总计: {len(all_items)} 张壁纸")
    log(f"✅ data.js 已覆写")
    log("=" * 40)


if __name__ == "__main__":
    main()
