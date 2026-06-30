"""
二游女角色壁纸扒图器 — Pixiv 版
跑完自动覆写 src/data.js，Vite 侧刷新即见

用法：
1. 把你的 pixiv refresh_token 填到下面的 REFRESH_TOKEN
2. (可选) PROXY 填 http://127.0.0.1:7890
3. python sync.py
4. npm run dev
"""

import os
import json
import re
from pixivpy3 import AppPixivAPI

# ===== 配置区 =====
REFRESH_TOKEN = ""
PROXY = None  # 例："http://127.0.0.1:7890"
DOWNLOAD_DIR = "public/images"
DATA_JS_PATH = "src/data.js"

QUERY_CHARACTERS = [
    # (Pixiv 搜索词, 游戏名, 默认 style, 指定角色名（可选）)
    ("原神 雷电将军 10000users入り", "原神", "3D渲染", "雷电将军"),
    ("原神 胡桃 10000users入り", "原神", "动漫插画", "胡桃"),
    ("崩坏：星穹铁道 银狼 10000users入り", "崩坏：星穹铁道", "2.5D", "银狼"),
    ("崩坏3 布洛妮娅 10000users入り", "崩坏3", "3D渲染", "布洛妮娅"),
    ("明日方舟 德克萨斯 10000users入り", "明日方舟", "动漫插画", "德克萨斯"),
    ("蔚蓝档案 白子 10000users入り", "蔚蓝档案", "动漫插画", "砂狼白子"),
    ("绝区零 艾莲 10000users入り", "绝区零", "3D渲染", "艾莲"),
    ("原神 纳西妲 10000users入り", "原神", "动漫插画", "纳西妲"),
    ("崩坏：星穹铁道 黄泉 10000users入り", "崩坏：星穹铁道", "3D渲染", "黄泉"),
    ("崩坏3 琪亚娜 10000users入り", "崩坏3", "3D渲染", "琪亚娜"),
]

STYLE_MAP = {
    "3D": "3D渲染",
    "3DCG": "3D渲染",
    "Live2D": "Live2D",
    "live2d": "Live2D",
}

VALID_STYLES = {"3D渲染", "2.5D", "动漫插画", "Live2D"}

# 男性关键词过滤（安全网，标题/tag 里出现就跳过）
MALE_KEYWORDS = {
    "钟离", "达达利亚", "魈", "艾尔海森", "卡维", "提纳里",
    "赛诺", "莱欧斯利", "那维莱特", "景元", "刃", "丹恒", "砂金",
    "真理医生", "穹", "空", "林尼", "五郎"
}


def guess_style(manual_style, tags):
    for t in tags:
        if t in STYLE_MAP:
            return STYLE_MAP[t]
    if any(s in tags for s in ["2.5D", "2.5次元"]):
        return "2.5D"
    if manual_style in VALID_STYLES:
        return manual_style
    return "动漫插画"


def has_male_content(ill, keyword_name):
    text_pool = ill.title.lower()
    for t in ill.tags:
        text_pool += " " + t.name.lower()
    for male in MALE_KEYWORDS:
        if male.lower() in text_pool:
            return True
    # 角色名自己都在黑名单里
    if keyword_name in MALE_KEYWORDS:
        return True
    return False


def clean_title(title):
    # 去掉 Pixiv 常见的水印/标签尾缀
    title = re.sub(r"\s*#.*$", "", title)
    return title.strip()[:80]


def main():
    if not REFRESH_TOKEN:
        print("请先填写 sync.py 里的 REFRESH_TOKEN")
        return

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    api = AppPixivAPI(proxy=PROXY)
    api.set_auth(access_token=None)
    api.login(refresh_token=REFRESH_TOKEN)

    data = []

    for idx, (keyword, game, default_style, char_name) in enumerate(QUERY_CHARACTERS, 1):
        print(f"[{idx}/{len(QUERY_CHARACTERS)}] 搜: {keyword}")

        try:
            res = api.search_illust(
                keyword,
                search_target="partial_match_for_tags",
                search_ai_type=1,       # 排除 AI
                sort="popular_desc",    # 人气降序
                req_auth=True
            )
        except Exception as e:
            print(f"  ⚠️ 搜索失败: {e}")
            continue

        picked = None
        for ill in res.illusts or []:
            if has_male_content(ill, char_name):
                continue
            # 优先单图大图
            if ill.type in ("illust", "ugoira"):
                picked = ill
                break

        if not picked:
            print(f"  ⚠️ 没搜到合适结果，跳过")
            continue

        if picked.meta_single_page and picked.meta_single_page.get("original_image_url"):
            url = picked.meta_single_page["original_image_url"]
        else:
            url = picked.image_urls.large

        fname = f"{idx}.jpg"
        local_path = os.path.join(DOWNLOAD_DIR, fname)

        try:
            api.download(url, path=DOWNLOAD_DIR, name=fname)
            print(f"  ✓ {fname} <- {picked.title} (pixiv_id={picked.id})")
        except Exception as e:
            print(f"  ⚠️ 下载失败: {e}，跳过")
            continue

        tags = [t.name for t in picked.tags if not t.name.startswith('#')][:8]
        style = guess_style(default_style, tags)

        data.append({
            "id": idx,
            "title": clean_title(picked.title) or f"{char_name}·{game}",
            "characterName": char_name,
            "game": game,
            "gender": "女",
            "style": style,
            "tags": tags,
            "likes": picked.total_bookmarks or 0,
            "rarity": "SSR" if (picked.total_bookmarks or 0) > 10000 else "SR",
            "source": "Pixiv",
            "nsfw": picked.x_restrict > 0 or picked.sanity_level < 4,
            "pixiv_id": picked.id,
            "pixiv_url": f"https://www.pixiv.net/artworks/{picked.id}",
        })

    # 写入 data.js
    with open(DATA_JS_PATH, "w", encoding="utf-8") as f:
        f.write("// 自动生成：python sync.py\\n")
        f.write("// gender 强制='女'；男角色/AI图/R18已过滤\\n\\n")
        f.write("export const GAMES = ")
        json.dump([
            {"id": "genshin", "name": "原神"},
            {"id": "hsr", "name": "崩坏：星穹铁道"},
            {"id": "hi3", "name": "崩坏3"},
            {"id": "arknights", "name": "明日方舟"},
            {"id": "ba", "name": "蔚蓝档案"},
            {"id": "zzz", "name": "绝区零"},
        ], f, ensure_ascii=False, indent=2)
        f.write(";\\n\\n")
        f.write("export const STYLES = [\\\"3D渲染\\\", \\\"2.5D\\\", \\\"动漫插画\\\", \\\"Live2D\\\"];\\n\\n")
        f.write("export const wallpaperData = ")
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write(";\\n")

    print(f"\\n✅ 完成：{len(data)} 张图 -> {DOWNLOAD_DIR}/")
    print(f"✅ data.js 已覆写 -> {DATA_JS_PATH}")
    if any(d.get("nsfw") for d in data):
        print("⚠️ 检测到 NSFW 标记项，请在 App 设置中确认是否显示")


if __name__ == "__main__":
    main()
