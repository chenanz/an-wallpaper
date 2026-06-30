#!/usr/bin/env python3
"""
数据恢复脚本：从 public/images/ 文件名反推角色信息，重建 data.js
"""
import os
import json
import re
from pathlib import Path

DOWNLOAD_DIR = "public/images"
DATA_JS_PATH = "src/data.js"

# 根据爬虫V2的输出日志，id范围→角色映射
ID_MAP = {}

# 原神 24角色 × 3张 = 72张 (id 1-72)
genshin_chars = [
    ("雷电将军","3D渲染"),("胡桃","动漫插画"),("纳西妲","动漫插画"),("芙宁娜","3D渲染"),
    ("甘雨","3D渲染"),("宵宫","动漫插画"),("绫华","3D渲染"),("八重神子","3D渲染"),
    ("妮露","3D渲染"),("心海","3D渲染"),("优菈","3D渲染"),("申鹤","3D渲染"),
    ("夜兰","3D渲染"),("迪希雅","3D渲染"),("千织","3D渲染"),("娜维娅","3D渲染"),
    ("克洛琳德","3D渲染"),("希诺宁","3D渲染"),("玛薇卡","3D渲染"),("茜特菈莉","动漫插画"),
    ("恰斯卡","3D渲染"),("艾梅莉埃","3D渲染"),("闲云","3D渲染"),("夏洛蒂","动漫插画"),
]
for i, (char, style) in enumerate(genshin_chars, 0):
    for j in range(3):
        ID_MAP[i*3 + j + 1] = ("原神", char, style)

# 崩坏3 10角色 × 3张 = 30张 (id 73-102)
hi3_chars = [
    ("布洛妮娅","3D渲染"),("琪亚娜","3D渲染"),("雷电芽衣","3D渲染"),("希儿","3D渲染"),
    ("爱莉希雅","3D渲染"),("符华","3D渲染"),("丽塔","3D渲染"),("幽兰黛尔","3D渲染"),
    ("德丽莎","动漫插画"),("姬子","3D渲染"),
]
for i, (char, style) in enumerate(hi3_chars, 0):
    for j in range(3):
        ID_MAP[72 + i*3 + j + 1] = ("崩坏3", char, style)

# 崩铁 12角色 × 3张 = 36张 (id 103-138)
hsr_chars = [
    ("黄泉","3D渲染"),("流萤","3D渲染"),("黑天鹅","3D渲染"),("花火","3D渲染"),
    ("知更鸟","3D渲染"),("阮梅","3D渲染"),("镜流","3D渲染"),("藿藿","动漫插画"),
    ("银狼","2.5D"),("卡芙卡","3D渲染"),("三月七","动漫插画"),("布洛妮娅","3D渲染"),
]
for i, (char, style) in enumerate(hsr_chars, 0):
    for j in range(3):
        ID_MAP[102 + i*3 + j + 1] = ("崩坏：星穹铁道", char, style)

# 绝区零 8角色 × 3张 = 24张 (id 139-162)
zzz_chars = [
    ("艾莲","3D渲染"),("星见雅","3D渲染"),("朱鸢","3D渲染"),("简","3D渲染"),
    ("青衣","3D渲染"),("柏妮思","3D渲染"),("凯撒","3D渲染"),("耀嘉音","3D渲染"),
]
for i, (char, style) in enumerate(zzz_chars, 0):
    for j in range(3):
        ID_MAP[138 + i*3 + j + 1] = ("绝区零", char, style)


def main():
    files = sorted([f for f in os.listdir(DOWNLOAD_DIR) if f.lower().endswith((".jpg",".jpeg",".png",".webp"))])

    items = []
    for fname in files:
        # 解析 id
        m = re.match(r"(\d+)_.*", fname)
        if not m:
            continue
        idx = int(m.group(1))

        game, char, style = ID_MAP.get(idx, ("其他", "未知角色", "动漫插画"))

        items.append({
            "id": idx,
            "title": f"{char}·精选壁纸" if game != "其他" else f"壁纸 #{idx}",
            "characterName": char,
            "game": game,
            "gender": "女",
            "style": style,
            "tags": [char, game][:6],
            "likes": 0,
            "rarity": "SSR",
            "source": "米游社" if game != "其他" else "本地",
            "nsfw": False,
            "imageFile": fname,
        })

    # 去重按 id
    seen = set()
    uniq = []
    for it in items:
        if it["id"] not in seen:
            seen.add(it["id"])
            uniq.append(it)

    # 排序
    uniq.sort(key=lambda x: x["id"])
    # 重新编号
    for i, it in enumerate(uniq, 1):
        it["id"] = i

    # 写 data.js
    games_list = [
        {"id": "genshin", "name": "原神"},
        {"id": "hi3", "name": "崩坏3"},
        {"id": "hsr", "name": "崩坏：星穹铁道"},
        {"id": "zzz", "name": "绝区零"},
        {"id": "arknights", "name": "明日方舟"},
        {"id": "ba", "name": "蔚蓝档案"},
    ]

    with open(DATA_JS_PATH, "w", encoding="utf-8") as f:
        f.write("// 自动生成：python recovery.py\n")
        f.write("// 从图片文件名反推角色信息\n\n")
        f.write("export const GAMES = ")
        json.dump(games_list, f, ensure_ascii=False, indent=2)
        f.write(";\n\n")
        f.write("export const STYLES = [\"3D渲染\", \"2.5D\", \"动漫插画\", \"Live2D\"];\n\n")
        f.write("export const wallpaperData = ")
        json.dump(uniq, f, ensure_ascii=False, indent=2)
        f.write(";\n\n")
        f.write("export function getFallbackImageUrl(id, w = 400, h = 712) {\n")
        f.write("  return `https://picsum.photos/seed/an_${id}/${w}/${h}`;\n")
        f.write("}\n")

    print(f"✅ 已恢复 {len(uniq)} 条记录 → {DATA_JS_PATH}")
    # 统计
    from collections import Counter
    c = Counter([it["game"] for it in uniq])
    for g, n in c.most_common():
        print(f"  {g}: {n} 张")


if __name__ == "__main__":
    main()
