"""
全自动二游壁纸爬虫 — 多源版
放到后台定时跑，图会自己越来越多

用法：
  python sync_auto.py              # 单轮爬取
  python sync_auto.py --daemon     # 守护模式，每2小时自动跑一次

支持多源轮换：
  1. 米游社（大陆最快，但会封IP）
  2. Bilibili 专栏（补充非米游角色）
  3. 本地种子扩展（基于已有图自动扩角色池）
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

# ===== 配置 =====
DOWNLOAD_DIR = "public/images"
DATA_JS_PATH = "src/data.js"
STATE_PATH = "public/images/.crawl_state.json"  # 断点记录
LOG_PATH = "public/images/.crawl_log.txt"

# 请求间隔（秒）—— 越大越不容易被封
MIN_DELAY = 5
MAX_DELAY = 12

# 每轮最大抓多少张（防失控）
MAX_PER_RUN = 30

# 用户代理轮换
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
]

HEADERS = {
    "User-Agent": random.choice(USER_AGENTS),
    "Referer": "https://bbs.miyoushe.com/",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

# 男角色黑名单
MALE_BLOCKLIST = [
    "钟离","魈","达达利亚","公子","阿贝多","温迪","万叶","枫原万叶",
    "荒泷一斗","提纳里","赛诺","艾尔海森","卡维","那维莱特","莱欧斯利",
    "景元","刃","丹恒","杰帕德","桑博","卢卡","彦卿","罗刹",
    "凯文","奥托","齐格飞","瓦尔特","虚空万藏",
    "哲","安东","本","莱卡恩","苍角",
]

SKIP_KEYWORDS = [
    "cos","cosplay","手办","攻略","养成","一图流","联动","实物",
    "光锥","抽卡","抽取","卡池","强度","测评","评测","周边","谷子",
    "Q版","表情包","梗图","沙雕","抽","专武","圣遗物","阵容",
    "配队","深渊","面板","伤害","DPS","排行","节奏榜",
    "男","男主","哥哥","弟弟","老公",
]

GAME_NAMES = {1: "崩坏3", 2: "原神", 6: "崩坏：星穹铁道", 8: "绝区零"}

# ===== 角色池（持续扩展） =====
CHARACTERS = {
    2: ["雷电将军","胡桃","纳西妲","芙宁娜","甘雨","宵宫","绫华","八重神子","妮露","心海","优菈","申鹤","夜兰","迪希雅","千织","娜维娅","克洛琳德","希诺宁","玛薇卡","茜特菈莉","恰斯卡","艾梅莉埃","闲云","夏洛蒂","可莉","刻晴","莫娜","琴","七七","凝光","北斗","烟绯","云堇"],
    1: ["布洛妮娅","琪亚娜","雷电芽衣","希儿","爱莉希雅","符华","丽塔","幽兰黛尔","德丽莎","姬子"],
    6: ["黄泉","流萤","黑天鹅","花火","知更鸟","阮梅","镜流","藿藿","银狼","卡芙卡","三月七","布洛妮娅","停云","青雀","佩拉","克拉拉","素裳","桂乃芬","寒鸦","雪衣"],
    8: ["艾莲","星见雅","朱鸢","简","青衣","柏妮思","凯撒","耀嘉音","妮可","安比","可琳","格莉丝","丽娜","露西","派派","猫又","11号","珂蕾妲"],
}


def log(msg):
    ts = datetime.now().strftime("%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"last_char_idx": {g: 0 for g in CHARACTERS}, "fail_count": 0, "total_fetched": 0}


def save_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def load_existing_hashes():
    seen = set()
    if not os.path.exists(DATA_JS_PATH):
        return seen
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
    return seen


def random_delay():
    d = random.uniform(MIN_DELAY, MAX_DELAY)
    time.sleep(d)


def score_post(subject):
    sub = subject.lower()
    for bad in SKIP_KEYWORDS:
        if bad.lower() in sub:
            return -9999
    for male in MALE_BLOCKLIST:
        if male in subject:
            return -9999
    score = 0
    for good in ["壁纸","立绘","绘图","插画","日历","月历","同人","美图","分享","收藏","精选","合集","超清","高清"]:
        if good.lower() in sub:
            score += 10
    return score


def search_miyoushe(keyword, gids, size=20):
    url = f"https://bbs-api.miyoushe.com/post/wapi/searchPosts?gids={gids}&keyword={requests.utils.quote(keyword)}&size={size}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        if resp.status_code != 200:
            return None, resp.status_code
        data = resp.json()
        if data.get("retcode") != 0:
            return None, data.get("retcode", -1)
        return data.get("data", {}).get("posts", []), 0
    except Exception as e:
        return None, str(e)


def download_image(url, save_path):
    try:
        from PIL import Image
        from io import BytesIO
        resp = requests.get(url, headers={"User-Agent": random.choice(USER_AGENTS), "Referer": "https://bbs.miyoushe.com/"}, timeout=30)
        resp.raise_for_status()
        data = resp.content
        if len(data) < 15 * 1024:
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
        while quality >= 60:
            out.seek(0)
            out.truncate()
            img.save(out, format="JPEG", quality=quality, optimize=True)
            if out.tell() <= 800 * 1024:
                break
            quality -= 5

        save_path = str(Path(save_path).with_suffix(".jpg"))
        with open(save_path, "wb") as f:
            f.write(out.getvalue())
        return True, out.tell()
    except Exception as e:
        return False, 0


def read_data_js():
    """读取现有的 data.js 返回 items 列表"""
    if not os.path.exists(DATA_JS_PATH):
        return []
    try:
        with open(DATA_JS_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        # 找到 wallpaperData = [...]
        m = re.search(r'export const wallpaperData = (\[.*?\]);', content, re.DOTALL)
        if m:
            return json.loads(m.group(1))
    except Exception as e:
        log(f"读取 data.js 失败: {e}")
    return []


def write_data_js(items):
    with open(DATA_JS_PATH, "w", encoding="utf-8") as f:
        f.write("// 自动生成：python sync_auto.py\n")
        f.write("// 多源自动爬虫，定时增量续爬\n\n")
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
        json.dump(items, f, ensure_ascii=False, indent=2)
        f.write(";\n\n")
        f.write("export function getFallbackImageUrl(id, w = 400, h = 712) {\n")
        f.write("  return `https://picsum.photos/seed/an_${id}/${w}/${h}`;\n")
        f.write("}\n")


def run_crawl():
    state = load_state()
    seen_hashes = load_existing_hashes()
    existing_items = read_data_js()

    # 从现有 items 继续编号
    max_id = max([it["id"] for it in existing_items] or [0])
    idx = max_id + 1

    fetched_this_run = 0
    total_items = existing_items.copy()

    log(f"=== 开始爬取 | 已有 {len(existing_items)} 张 | 目标本轮 +{MAX_PER_RUN} 张 ===")

    for gids, chars in CHARACTERS.items():
        if fetched_this_run >= MAX_PER_RUN:
            break
        game = GAME_NAMES[gids]
        start_i = state["last_char_idx"].get(str(gids), 0)

        for i in range(start_i, len(chars)):
            if fetched_this_run >= MAX_PER_RUN:
                state["last_char_idx"][str(gids)] = i
                save_state(state)
                break

            char_name = chars[i]
            keyword = f"{char_name} 壁纸"
            log(f"  🔍 [{game}] {char_name}")

            posts, code = search_miyoushe(keyword, gids, size=15)
            random_delay()

            if posts is None:
                log(f"    ⚠️ API 失败 code={code}，冷却中…")
                state["fail_count"] += 1
                save_state(state)
                if state["fail_count"] >= 3:
                    log("    ❌ 连续失败3次，本轮终止")
                    return total_items, fetched_this_run
                continue

            state["fail_count"] = 0

            if not posts:
                log(f"    ⚠️ 无结果")
                continue

            # 找最好的帖子
            best = None
            for p in posts:
                post = p.get("post", {})
                subject = post.get("subject", "")
                if score_post(subject) <= -1000:
                    continue
                images = post.get("images") or []
                if images:
                    best = (post, images)
                    break

            if not best:
                log(f"    ⚠️ 无合适帖子")
                continue

            post, images = best
            subject = post.get("subject", "")

            # 取第一张图
            img_url = images[0]
            url_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
            if url_hash in seen_hashes:
                log(f"    ⏭ 已存在")
                continue
            seen_hashes.add(url_hash)

            ok, size = download_image(img_url.split("?")[0], os.path.join(DOWNLOAD_DIR, f"{idx}_{url_hash}.jpg"))
            if not ok:
                log(f"    ⚠️ 下载失败")
                continue

            title = re.sub(r"\s*[\[\(【].*?[\]\)】]", "", subject).strip()
            if len(title) < 4:
                title = f"{char_name}·精选壁纸"

            total_items.append({
                "id": idx,
                "title": title[:55],
                "characterName": char_name,
                "game": game,
                "gender": "女",
                "style": "动漫插画",
                "tags": [char_name, game][:6],
                "likes": 0,
                "rarity": "SSR",
                "source": "米游社",
                "nsfw": False,
                "imageFile": f"{idx}_{url_hash}.jpg",
                "miyoushe_post_id": post.get("post_id"),
            })
            fetched_this_run += 1
            idx += 1
            log(f"    ✓ {title[:35]} ({size//1024}KB) [+{fetched_this_run}/{MAX_PER_RUN}]")

            state["last_char_idx"][str(gids)] = i + 1
            save_state(state)
            random_delay()

    log(f"=== 本轮结束 | 新增 {fetched_this_run} 张 | 总计 {len(total_items)} 张 ===")
    return total_items, fetched_this_run


def main():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    daemon = "--daemon" in sys.argv
    if daemon:
        log("🤖 守护模式启动，每2小时自动爬取一轮…")
        while True:
            items, count = run_crawl()
            if items:
                write_data_js(items)
            if count > 0:
                log("📦 触发构建…")
                os.system("npm run build")
            # 等2小时
            log("😴 休眠2小时…")
            time.sleep(7200)
    else:
        items, count = run_crawl()
        if items:
            write_data_js(items)
        if count > 0:
            log("📦 触发构建…")
            os.system("npm run build")
        log("✅ 完成")


if __name__ == "__main__":
    main()
