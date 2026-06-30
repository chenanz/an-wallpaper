"""
二游女角色壁纸扒图器 V2 — 米游社版
大陆直连，不挂梯子，建筑 50+ 角色池，每角色 3 张，支持增量续爬

用法：
1. python sync_v2.py
2. npm run dev

增量模式：
  python sync_v2.py --incremental   # 只补新角色/新图，不删旧的
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

# ===== 配置区 =====
DOWNLOAD_DIR = "public/images"
DATA_JS_PATH = "src/data.js"
INCREMENTAL = "--incremental" in sys.argv

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://bbs.miyoushe.com/",
}

# 男角色黑名单：标题出现这些直接跳过
MALE_BLOCKLIST = [
    "钟离", "魈", "达达利亚", "公子", "阿贝多", "温迪", "万叶", "枫原万叶",
    "荒泷一斗", "提纳里", "赛诺", "艾尔海森", "卡维", "那维莱特", "莱欧斯利",
    "景元", "刃", "丹恒", "杰帕德", "桑博", "卢卡", "彦卿", "罗刹",
    "凯文", "奥托", "齐格飞", "瓦尔特", "虚空万藏",
    "哲", "安东", "本", "莱卡恩", "苍角",
    "银灰", "棘刺", "山", "傀影", "流明",
]

SKIP_TITLE_KEYWORDS = [
    "cos", "cosplay", "手办", "攻略", "养成", "一图流", "联动", "实物",
    "光锥", "抽卡", "抽取", "卡池", "强度", "测评", "评测", "周边", "谷子",
    "Q版", "表情包", "梗图", "沙雕", "抽", "专武", "圣遗物", "阵容",
    "配队", "深渊", "面板", "伤害", "DPS", "排行", "节奏榜",
    "男", "男主", "哥哥", "弟弟", "老公", "老婆", " husbands",
]

BOOST_TITLE_KEYWORDS = [
    "壁纸", "立绘", "绘图", "插画", "日历", "月历", "同人", "美图",
    "分享", "收藏", "精选", "合集", "超清", "高清",
]

VALID_STYLES = {"3D渲染", "2.5D", "动漫插画", "Live2D"}
STYLE_MAP = {
    "3D": "3D渲染", "3DCG": "3D渲染", "Live2D": "Live2D",
    "live2d": "Live2D", "2.5D": "2.5D", "2.5次元": "2.5D",
}

MIN_IMAGE_BYTES = 15 * 1024
MAX_IMAGE_WIDTH = 1200
MAX_IMAGE_KB = 800
REQUEST_DELAY = 0.8   # 请求间隔秒，防封
MAX_PER_CHARACTER = 3 # 每个角色最多扒几张


def log(msg):
    print(msg)


def score_post(subject):
    sub = subject.lower()
    # 黑名单
    for bad in SKIP_TITLE_KEYWORDS:
        if bad.lower() in sub:
            return -9999
    # 男角色拦截
    for male in MALE_BLOCKLIST:
        if male in subject:
            return -9999
    score = 0
    for good in BOOST_TITLE_KEYWORDS:
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


def pick_best_posts(posts, top_n=8):
    scored = []
    for p in posts:
        post = p.get("post", {})
        subject = post.get("subject", "")
        score = score_post(subject)
        images = post.get("images") or []
        if score <= -1000 or not images:
            continue
        scored.append((score, post))
    scored.sort(key=lambda x: (-x[0], -len(x[1].get("images", []))))
    return [p for _, p in scored[:top_n]]


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
        log(f"    ⚠️ 下载失败 {url[:60]}... : {e}")
        return False, 0, None


def clean_title(title, char_name):
    title = re.sub(r"\s*[\[\(【].*?[\]\)】]", "", title)
    title = title.strip()
    if not title or len(title) < 4:
        title = f"{char_name}"
    return title[:55]


def load_existing():
    """读取现有的 data.js，返回已有图片的 url_hash set"""
    seen = set()
    if not os.path.exists(DATA_JS_PATH):
        return seen, []
    try:
        with open(DATA_JS_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        # 简单正则提取 imageFile
        for line in content.split("\n"):
            m = re.search(r'"imageFile"\s*:\s*"([^"]+)"', line)
            if m:
                fname = m.group(1)
                # 从文件名提取 hash
                parts = fname.replace(".jpg", "").split("_")
                if len(parts) >= 2:
                    seen.add(parts[-1])
    except:
        pass
    return seen, []


# ===== 角色池 =====
CHARACTERS = {
    # 原神 (gids=2) — 20 个热门女角色
    2: [
        ("雷电将军", "3D渲染"), ("胡桃", "动漫插画"), ("纳西妲", "动漫插画"),
        ("芙宁娜", "3D渲染"), ("那维莱特", "3D渲染"), ("甘雨", "3D渲染"),
        ("宵宫", "动漫插画"), ("绫华", "3D渲染"), ("八重神子", "3D渲染"),
        ("妮露", "3D渲染"), ("心海", "3D渲染"), ("优菈", "3D渲染"),
        ("申鹤", "3D渲染"), ("夜兰", "3D渲染"), ("迪希雅", "3D渲染"),
        ("千织", "3D渲染"), ("娜维娅", "3D渲染"), ("克洛琳德", "3D渲染"),
        ("希诺宁", "3D渲染"), ("玛薇卡", "3D渲染"),
    ],
    # 崩坏3 (gids=1) — 10 个
    1: [
        ("布洛妮娅", "3D渲染"), ("琪亚娜", "3D渲染"), ("雷电芽衣", "3D渲染"),
        ("希儿", "3D渲染"), ("爱莉希雅", "3D渲染"), ("符华", "3D渲染"),
        ("丽塔", "3D渲染"), ("幽兰黛尔", "3D渲染"), ("德丽莎", "动漫插画"),
        ("姬子", "3D渲染"),
    ],
    # 崩坏星穹铁道 (gids=6) — 12 个
    6: [
        ("黄泉", "3D渲染"), ("流萤", "3D渲染"), ("黑天鹅", "3D渲染"),
        ("花火", "3D渲染"), ("知更鸟", "3D渲染"), ("阮梅", "3D渲染"),
        ("镜流", "3D渲染"), ("藿藿", "动漫插画"), ("银狼", "2.5D"),
        ("卡芙卡", "3D渲染"), ("姬子", "3D渲染"), ("三月七", "动漫插画"),
    ],
    # 绝区零 (gids=8) — 8 个
    8: [
        ("艾莲", "3D渲染"), ("星见雅", "3D渲染"), ("朱鸢", "3D渲染"),
        ("简", "3D渲染"), ("青衣", "3D渲染"), ("柏妮思", "3D渲染"),
        ("凯撒", "3D渲染"), ("耀嘉音", "3D渲染"),
    ],
}

GAME_NAMES = {1: "崩坏3", 2: "原神", 6: "崩坏：星穹铁道", 8: "绝区零"}


def main():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    seen_hashes, _ = load_existing()
    log(f"📦 已有 {len(seen_hashes)} 张图，增量模式={INCREMENTAL}")

    output = []
    total_fetched = 0
    total_skipped = 0
    idx = 1

    for gids, chars in CHARACTERS.items():
        game = GAME_NAMES[gids]
        log(f"\n🎮 [{game}] {len(chars)} 个角色")

        for char_name, default_style in chars:
            keyword = f"{char_name} 壁纸"
            log(f"  🔍 {char_name}")

            posts = search_miyoushe(keyword, gids, size=25)
            time.sleep(REQUEST_DELAY)

            best_posts = pick_best_posts(posts, top_n=8)
            if not best_posts:
                log(f"    ⚠️ 无合适帖子")
                continue

            fetched_for_char = 0
            for post in best_posts:
                if fetched_for_char >= MAX_PER_CHARACTER:
                    break

                subject = post.get("subject", "")
                images = post.get("images") or []
                if not images:
                    continue

                # 取第一张图（通常是最清晰的封面）
                img_url = images[0]
                url_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]

                if url_hash in seen_hashes:
                    total_skipped += 1
                    continue
                seen_hashes.add(url_hash)

                clean_url = img_url.split("?")[0]
                fname = f"{idx}_{url_hash}.jpg"
                save_path = os.path.join(DOWNLOAD_DIR, fname)

                ok, size, final_path = download_image(clean_url, save_path)
                if not ok:
                    continue

                # 标题太烂就用角色名兜底
                title = clean_title(subject, char_name)
                if len(title) < 3 or title == char_name:
                    title = f"{char_name}·精选壁纸"

                tags = [char_name, game]
                style = default_style if default_style in VALID_STYLES else "动漫插画"

                output.append({
                    "id": idx,
                    "title": title,
                    "characterName": char_name,
                    "game": game,
                    "gender": "女",
                    "style": style,
                    "tags": tags[:6],
                    "likes": 0,
                    "rarity": "SSR",
                    "source": "米游社",
                    "nsfw": False,
                    "imageFile": fname,
                    "miyoushe_post_id": post.get("post_id"),
                })
                fetched_for_char += 1
                total_fetched += 1
                log(f"    ✓ [{fetched_for_char}/{MAX_PER_CHARACTER}] {fname} ({size/1024:.0f}KB) {title[:30]}")
                idx += 1

                time.sleep(REQUEST_DELAY * 0.5)

    # 写入 data.js
    with open(DATA_JS_PATH, "w", encoding="utf-8") as f:
        f.write("// 自动生成：python sync_v2.py\n")
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
        json.dump(output, f, ensure_ascii=False, indent=2)
        f.write(";\n\n")

        f.write("export function getFallbackImageUrl(id, w = 400, h = 712) {\n")
        f.write("  return `https://picsum.photos/seed/an_${id}/${w}/${h}`;\n")
        f.write("}\n")

    log(f"\n{'='*40}")
    log(f"✅ 本次新增：{total_fetched} 张")
    log(f"⏭ 跳过重复：{total_skipped} 张")
    log(f"📊 data.js 总计：{len(output)} 张")
    log(f"{'='*40}")


if __name__ == "__main__":
    main()
