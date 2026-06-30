"""
二游女角色壁纸扒图器 — 米游社版（大陆直接跑，无需梯子）
跑完自动覆写 src/data.js，Vite 侧刷新即见

用法：
1. 改下面的 QUERIES 配置
2. python sync_miyoushe.py
3. npm run dev
"""

import os
import re
import json
import hashlib
import requests
from PIL import Image
from urllib.parse import quote
from pathlib import Path

# ===== 配置区 =====
DOWNLOAD_DIR = "public/images"
DATA_JS_PATH = "src/data.js"

# 用户代理，必须加 Referer，否则接口可能 403
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://bbs.miyoushe.com/",
}

# (搜索词, gids, 游戏名, 默认style, 角色名)
# gids: 1=崩坏3, 2=原神, 6=崩坏星穹铁道, 8=绝区零
QUERIES = [
    ("雷电将军 壁纸", 2, "原神", "3D渲染", "雷电将军"),
    ("胡桃 壁纸", 2, "原神", "动漫插画", "胡桃"),
    ("纳西妲 壁纸", 2, "原神", "动漫插画", "纳西妲"),
    ("芙宁娜 壁纸", 2, "原神", "3D渲染", "芙宁娜"),
    ("布洛妮娅 壁纸", 1, "崩坏3", "3D渲染", "布洛妮娅"),
    ("琪亚娜 壁纸", 1, "崩坏3", "3D渲染", "琪亚娜"),
    ("黄泉 壁纸", 6, "崩坏：星穹铁道", "3D渲染", "黄泉"),
    ("流萤 壁纸", 6, "崩坏：星穹铁道", "3D渲染", "流萤"),
    ("艾莲 壁纸", 8, "绝区零", "3D渲染", "艾莲"),
    ("星见雅 壁纸", 8, "绝区零", "3D渲染", "星见雅"),
]

# 黑名单：标题或 tag 出现这些就跳过
SKIP_TITLE_KEYWORDS = [
    "cos", "手办", "攻略", "养成", "一图流", "联动", "实物", "光锥",
    "抽卡", "抽取", "卡池", "强度", "测评", "评测", "周边", "谷子",
    "Q版", "表情包", "梗图", "沙雕", "抽", "专武", "圣遗物"
]

# 白名单：标题出现这些优先靠前
BOOST_TITLE_KEYWORDS = [
    "壁纸", "立绘", "绘图", "插画", "日历", "月历", "同人", "美图"
]

VALID_STYLES = {"3D渲染", "2.5D", "动漫插画", "Live2D"}
STYLE_MAP = {
    "3D": "3D渲染",
    "3DCG": "3D渲染",
    "Live2D": "Live2D",
    "live2d": "Live2D",
    "2.5D": "2.5D",
    "2.5次元": "2.5D",
}

MIN_IMAGE_BYTES = 15 * 1024   # 小于 15KB 认为不是壁纸
MAX_IMAGES_PER_POST = 5       # 每个帖子最多取几张
MAX_IMAGE_WIDTH = 1200        # 压缩后最大宽度
MAX_IMAGE_KB = 800            # 压缩后最大体积 KB


def log(msg):
    print(msg)


def score_post(subject):
    """标题质量分：白名单加分，黑名单直接判负"""
    sub = subject.lower()
    for bad in SKIP_TITLE_KEYWORDS:
        if bad.lower() in sub:
            return -1000
    score = 0
    for good in BOOST_TITLE_KEYWORDS:
        if good.lower() in sub:
            score += 10
    return score


def search_miyoushe(keyword, gids, size=20):
    url = f"https://bbs-api.miyoushe.com/post/wapi/searchPosts?gids={gids}&keyword={quote(keyword)}&size={size}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        if data.get("retcode") != 0:
            log(f"  ⚠️ API 错误: {data.get('message')}")
            return []
        return data.get("data", {}).get("posts", [])
    except Exception as e:
        log(f"  ⚠️ 请求失败: {e}")
        return []


def pick_best_posts(posts, top_n=3):
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


def guess_style(default_style, tags):
    if not tags:
        return default_style if default_style in VALID_STYLES else "动漫插画"
    for t in tags:
        if t in STYLE_MAP:
            return STYLE_MAP[t]
    return default_style if default_style in VALID_STYLES else "动漫插画"


def download_image(url, save_path):
    """下载并压缩图片，统一输出为 .jpg"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.content
        if len(data) < MIN_IMAGE_BYTES:
            return False, 0, None

        from io import BytesIO
        img = Image.open(BytesIO(data))
        # 转 RGB，去透明通道
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # 缩放
        w, h = img.size
        if w > MAX_IMAGE_WIDTH:
            ratio = MAX_IMAGE_WIDTH / w
            img = img.resize((MAX_IMAGE_WIDTH, int(h * ratio)), Image.LANCZOS)

        Path(save_path).parent.mkdir(parents=True, exist_ok=True)

        # 质量循环压缩，直到体积达标
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
        log(f"    ⚠️ 下载失败 {url[:60]}: {e}")
        return False, 0, None


def clean_title(title, char_name):
    title = re.sub(r"\s*[\[\(【].*?[\]\)】]", "", title)
    title = title.strip() or f"{char_name}"
    return title[:60]


def main():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    output = []
    seen_ids = set()
    idx = 1

    for keyword, gids, game, default_style, char_name in QUERIES:
        log(f"[{idx}/{len(QUERIES)}] 搜: {keyword} (game={game})")

        posts = search_miyoushe(keyword, gids, size=20)
        best_posts = pick_best_posts(posts, top_n=3)

        if not best_posts:
            log(f"  ⚠️ 没有合适的帖子")
            continue

        downloaded_any = False
        for post in best_posts:
            subject = post.get("subject", "")
            images = post.get("images") or []
            log(f"  📌 {subject[:50]} | {len(images)} 张图")

            for img_url in images[:MAX_IMAGES_PER_POST]:
                # 用 url hash 防重
                url_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
                if url_hash in seen_ids:
                    continue
                seen_ids.add(url_hash)

                # 米游社图通常带 o 参数的原图，去掉 @ 后面的缩略图参数
                clean_url = img_url.split("?")[0]
                ext = ".jpg"  # 压缩后统一 jpg
                fname = f"{idx}_{url_hash}.jpg"
                save_path = os.path.join(DOWNLOAD_DIR, fname)

                ok, size, final_path = download_image(clean_url, save_path)
                if not ok or not final_path:
                    continue

                tags = [char_name, game, default_style]
                style = guess_style(default_style, tags)

                output.append({
                    "id": idx,
                    "title": clean_title(subject, char_name),
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
                downloaded_any = True
                idx += 1
                log(f"    ✓ {fname} ({size/1024:.1f} KB)")
                # 每个角色只取一张最优的（若想要多张，可注释 break）
                break

            if downloaded_any:
                break

    # 覆写 data.js
    with open(DATA_JS_PATH, "w", encoding="utf-8") as f:
        f.write("// 自动生成：python sync_miyoushe.py\n")
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

    log(f"\\n✅ 完成：{len(output)} 张图 -> {DOWNLOAD_DIR}/")
    log(f"✅ data.js 已覆写 -> {DATA_JS_PATH}")


if __name__ == "__main__":
    main()
