"""
本地图片扫描器 — 把手动下载的图自动写入 data.js
用法：
1. 把 .jpg/.png/.webp 丢进 public/images/
2. python scan_local.py
3. npm run dev

支持：按文件名前缀自动分组、手动维护元数据
"""

import os
import re
import json
from pathlib import Path

DOWNLOAD_DIR = "public/images"
META_PATH = "public/images/meta.json"  # 手动维护角色信息
DATA_JS_PATH = "src/data.js"

# 游戏名称正则匹配
GAME_PATTERNS = [
    ("原神", ["原神", "genshin", "雷电将军", "胡桃", "纳西妲", "芙宁娜", "甘雨", "宵宫", "绫华", "八重", "妮露", "心海", "优菈", "申鹤", "夜兰", "迪希雅", "千织", "娜维娅", "克洛琳德", "希诺宁", "玛薇卡", "茜特菈莉", "恰斯卡"]),
    ("崩坏3", ["崩坏3", "崩三", "布洛妮娅", "琪亚娜", "芽衣", "希儿", "爱莉希雅", "符华", "丽塔", "幽兰黛尔", "德丽莎", "姬子"]),
    ("崩坏：星穹铁道", ["星穹铁道", "崩铁", "黄泉", "流萤", "黑天鹅", "花火", "知更鸟", "阮梅", "镜流", "藿藿", "银狼", "卡芙卡", "三月七", "停云", "青雀", "佩拉"]),
    ("绝区零", ["绝区零", "艾莲", "星见雅", "朱鸢", "简", "青衣", "柏妮思", "凯撒", "耀嘉音", "妮可", "安比", "可琳", "格莉丝"]),
    ("明日方舟", ["明日方舟", "arknights", "阿米娅", "德克萨斯", "能天使", "斯卡蒂", "银灰", "棘刺", "山", "傀影", "流明", "澄闪"]),
    ("蔚蓝档案", ["蔚蓝档案", "碧蓝档案", "白子", "优香", "星野", "日奈", "未花", "爱露", "阿露", "睦月", "小春", "梓"]),
    ("碧蓝航线", ["碧蓝航线", "信浓", "企业", "贝尔法斯特", "光辉", "可畏", "埃塞克斯", "长门", "天城", "赤城"]),
    ("少女前线", ["少女前线", "HK416", "UMP45", "M4A1", "AR15", "AK12", "AN94"]),
    ("战双帕弥什", ["战双", "帕弥什", "露西亚", "丽芙", "露娜", "阿尔法", "薇拉"]),
    ("FGO", ["FGO", "阿尔托莉雅", "呆毛", "贞德", "玛修", "摩根", "斯卡哈", "伽摩"]),
    ("赛马娘", ["赛马娘", "东海帝皇", "特别周", "目白麦昆", "北部玄驹", "里见光钻"]),
    ("其他", []),
]


def log(msg):
    print(msg)


def guess_game_and_char(filename):
    """从文件名猜游戏和角色"""
    name_lower = filename.lower()
    for game, keywords in GAME_PATTERNS:
        for kw in keywords:
            if kw.lower() in name_lower:
                return game, kw
    return "其他", "未知角色"


def load_meta():
    """读取手动维护的 meta.json"""
    if os.path.exists(META_PATH):
        with open(META_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def scan_images():
    """扫描目录，返回 [(idx, filename, game, char, title), ...]"""
    exts = (".jpg", ".jpeg", ".png", ".webp", ".gif")
    files = sorted([f for f in os.listdir(DOWNLOAD_DIR) if f.lower().endswith(exts)])

    meta = load_meta()
    items = []
    idx = 1

    for fname in files:
        if fname == "meta.json":
            continue

        # 优先用 meta.json 里的信息
        if fname in meta:
            info = meta[fname]
            game = info.get("game", "其他")
            char = info.get("character", "未知角色")
            title = info.get("title", f"{char}·壁纸")
            style = info.get("style", "动漫插画")
            tags = info.get("tags", [char, game])
        else:
            game, char = guess_game_and_char(fname)
            # 去掉扩展名和后缀的 hash
            clean = re.sub(r"_?[a-f0-9]{8,}$", "", Path(fname).stem)
            clean = re.sub(r"^\d+_", "", clean)  # 去掉序号前缀
            title = clean.replace("_", "·").replace("-", "·") or f"{char}·壁纸"
            style = "动漫插画"
            tags = [char, game]

        items.append({
            "id": idx,
            "title": title[:55],
            "characterName": char,
            "game": game,
            "gender": "女",
            "style": style,
            "tags": tags[:6],
            "likes": 0,
            "rarity": "SSR",
            "source": "本地",
            "nsfw": False,
            "imageFile": fname,
        })
        idx += 1

    return items


def write_data_js(items):
    # 统计各游戏数量
    game_counts = {}
    for item in items:
        g = item["game"]
        game_counts[g] = game_counts.get(g, 0) + 1

    # 动态生成 GAMES 列表
    all_games = list(game_counts.keys())
    games_list = []
    for g in ["原神", "崩坏3", "崩坏：星穹铁道", "绝区零", "明日方舟", "蔚蓝档案", "碧蓝航线", "少女前线", "战双帕弥什", "FGO", "赛马娘"]:
        if g in all_games:
            games_list.append({"id": g.lower().replace(":", "").replace(" ", ""), "name": g})
    for g in all_games:
        if g not in [x["name"] for x in games_list] and g != "其他":
            games_list.append({"id": g.lower().replace(":", "").replace(" ", ""), "name": g})
    if "其他" in all_games:
        games_list.append({"id": "other", "name": "其他"})

    with open(DATA_JS_PATH, "w", encoding="utf-8") as f:
        f.write("// 自动生成：python scan_local.py\n")
        f.write("// 本地图源：把图丢进 public/images/ 再跑这个脚本\n")
        f.write("// gender 强制='女'\n\n")

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
    items = scan_images()
    write_data_js(items)
    log(f"✅ 扫描完成：{len(items)} 张图")
    log(f"✅ data.js 已覆写")

    # 统计
    game_counts = {}
    for item in items:
        g = item["game"]
        game_counts[g] = game_counts.get(g, 0) + 1
    log("\n📊 各游戏分布：")
    for g, c in sorted(game_counts.items(), key=lambda x: -x[1]):
        log(f"  {g}: {c} 张")


if __name__ == "__main__":
    main()
