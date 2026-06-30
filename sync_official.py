"""
Official art crawler - fetch official high-res character art from game APIs
Zero ban risk: uses public CDN/API endpoints

Usage:
  python sync_official.py              # single run (max 30)
  python sync_official.py --max 50     # custom max per run
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

# ===== Config =====
DOWNLOAD_DIR = "public/images"
DATA_JS_PATH = "src/data.js"
LOG_PATH = "public/images/.crawl_official_log.txt"
MAX_PER_RUN = 30
MIN_DELAY = 2
MAX_DELAY = 5
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

MALE_BLOCKLIST = [
    "钟离","魈","达达利亚","公子","阿贝多","温迪","万叶","枫原万叶",
    "荒泷一斗","提纳里","赛诺","艾尔海森","卡维","那维莱特","莱欧斯利",
    "景元","刃","丹恒","哲","安东","本","莱卡恩","苍角",
    "旅行者","空","Aether","Caelus",
]

# ===== Character pools =====
GENSHIN_CHARS = [
    ("raiden","雷电将军"),("hu-tao","胡桃"),("nahida","纳西妲"),
    ("furina","芙宁娜"),("ganyu","甘雨"),("yoimiya","宵宫"),
    ("ayaka","绫华"),("yae-miko","八重神子"),("nilou","妮露"),
    ("kokomi","心海"),("eula","优菈"),("shenhe","申鹤"),
    ("yelan","夜兰"),("dehya","迪希雅"),("chiori","千织"),
    ("navia","娜维娅"),("clorinde","克洛琳德"),("shinobu","久岐忍"),
    ("arlecchino","阿蕾奇诺"),("mavuika","玛薇卡"),
    ("mona","莫娜"),("keqing","刻晴"),("klee","可莉"),
    ("jean","琴"),("ningguang","凝光"),("beidou","北斗"),
    ("yanfei","烟绯"),("yun-jin","云堇"),("faruzan","珐露珊"),
    ("charlotte","夏洛蒂"),("fischl","菲谢尔"),
]

AK_CHARS = [
    "迷迭香","凯尔希","史尔特尔","陈","能天使","W",
    "推进之王","艾雅法拉","伊芙利特","星熊","塞雷娅",
    "闪灵","夜莺","澄闪","夕","令","铃兰","傀影",
    "温蒂","风笛","棘刺","银灰","焰尾","远牙","空弦",
    "嵯峨","水月","玛恩纳","灰喉","赫德",
]

BA_CHARS = [
    ("aru","阿露"),("hina","日奈"),("iori","伊织"),
    ("haruna","晴奈"),("mutsuki","六花"),("nonomi","诺诺美"),
    ("shiroko","白子"),("serika","芹香"),("hoshino","星野"),
    ("tsubaki","椿"),("izuna","泉奈"),("miyako","宫子"),
    ("hanako","花子"),("ako","亚子"),("yuzu","柚子"),
    ("midori","翠"),("hasumi","莲见"),("koharu","小春"),
    ("saki","咲"),("hifumi","妃叶"),
]


def log(msg):
    ts = datetime.now().strftime("%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def random_delay():
    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))


def download_and_compress(url, save_path, referer=""):
    """Download image and compress with Pillow: <=1200px, <=800KB"""
    try:
        from PIL import Image
        from io import BytesIO
        headers = {"User-Agent": USER_AGENT}
        if referer:
            headers["Referer"] = referer
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.content
        if len(data) < 20 * 1024:
            return False, 0, "too_small"
        img = Image.open(BytesIO(data))
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        w, h = img.size
        if w > 1200:
            ratio = 1200 / w
            img = img.resize((1200, int(h * ratio)), Image.Resampling.LANCZOS)
        save_path = str(Path(save_path).with_suffix(".jpg"))
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        quality = 92
        out = BytesIO()
        while quality >= 55:
            out.seek(0)
            out.truncate()
            img.save(out, format="JPEG", quality=quality, optimize=True)
            if out.tell() <= 800 * 1024:
                break
            quality -= 5
        with open(save_path, "wb") as f:
            f.write(out.getvalue())
        return True, out.tell(), "ok"
    except Exception as e:
        return False, 0, str(e)[:80]


def url_hash8(s):
    return hashlib.md5(s.encode()).hexdigest()[:8]


def read_data_js_items():
    if not os.path.exists(DATA_JS_PATH):
        return []
    try:
        with open(DATA_JS_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        m = re.search(r'wallpaperData\s*=\s*(\[.*\]);', content, re.DOTALL)
        if m:
            return json.loads(m.group(1))
    except Exception as e:
        log(f"读data.js失败: {e}")
    return []


def load_existing_hashes():
    seen = set()
    for it in read_data_js_items():
        fname = it.get("imageFile", "")
        parts = fname.replace(".jpg", "").split("_")
        if len(parts) >= 2:
            seen.add(parts[-1])
    return seen


def load_existing_pairs():
    pairs = set()
    for it in read_data_js_items():
        pairs.add((it.get("characterName", ""), it.get("game", "")))
    return pairs


def write_data_js(items):
    """Write the complete data.js file"""
    with open(DATA_JS_PATH, "w", encoding="utf-8") as f:
        f.write("// 自动生成：python sync_official.py / sync_auto.py\n")
        f.write("// 官方立绘 + 多源自动爬虫\n\n")
        f.write("export const GAMES = ")
        json.dump([
            {"id": "genshin", "name": "原神"},
            {"id": "hi3", "name": "崩坏3"},
            {"id": "hsr", "name": "崩坏：星穹铁道"},
            {"id": "zzz", "name": "绝区零"},
            {"id": "arknights", "name": "明日方舟"},
            {"id": "ba", "name": "蔚蓝档案"},
            {"id": "azur", "name": "碧蓝航线"},
        ], f, ensure_ascii=False, indent=2)
        f.write(";\n\n")
        f.write('export const STYLES = ["3D渲染", "2.5D", "动漫插画", "Live2D"];\n\n')
        f.write("export const wallpaperData = ")
        json.dump(items, f, ensure_ascii=False, indent=2)
        f.write(";\n\n")
        f.write("export function getFallbackImageUrl(id, w = 400, h = 712) {\n")
        f.write("  return `https://picsum.photos/seed/an_${id}/${w}/${h}`;\n")
        f.write("}\n")

# ===== Fetch sources =====

def fetch_genshin(char_list, seen_hashes, seen_pairs, idx, fetched, max_fetch):
    """Fetch Genshin official art from genshin.jmp.blue"""
    log("  >>> [原神] genshin.jmp.blue fetching...")
    results = []
    for slug, cn_name in char_list:
        if fetched >= max_fetch:
            break
        if any(m in cn_name for m in MALE_BLOCKLIST):
            continue
        if (cn_name, "原神") in seen_pairs:
            log(f"    >> {cn_name} already exists, skip")
            continue
        for art_type in ["portrait", "gacha-splash"]:
            if fetched >= max_fetch:
                break
            url = f"https://genshin.jmp.blue/characters/{slug}/{art_type}"
            h = url_hash8(url)
            if h in seen_hashes:
                continue
            seen_hashes.add(h)
            save_path = os.path.join(DOWNLOAD_DIR, f"{idx}_{h}.jpg")
            ok, size, status = download_and_compress(url, save_path, referer="https://genshin.jmp.blue/")
            if ok:
                title = f"{cn_name}·官方立绘"
                if art_type == "gacha-splash":
                    title = f"{cn_name}·角色祈愿立绘"
                results.append({
                    "id": idx, "title": title, "characterName": cn_name,
                    "game": "原神", "gender": "女", "style": "3D渲染",
                    "tags": [cn_name, "原神", "官方立绘"],
                    "likes": 0, "rarity": "SSR", "source": "官方", "nsfw": False,
                    "imageFile": f"{idx}_{h}.jpg",
                    "official_slug": slug, "official_art_type": art_type,
                })
                idx += 1; fetched += 1
                log(f"    OK [{cn_name}] {art_type} ({size//1024}KB) [+{fetched}/{max_fetch}]")
                seen_pairs.add((cn_name, "原神"))
                random_delay()
                break
            else:
                if art_type == "portrait":
                    continue
                log(f"    ERR [{cn_name}] {art_type} failed: {status}")
    return results, idx, fetched


def fetch_arknights(char_list, seen_hashes, seen_pairs, idx, fetched, max_fetch):
    """Fetch Arknights official art from prts.wiki MediaWiki API"""
    log("  >>> [明日方舟] prts.wiki fetching...")
    results = []
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    for cn_name in char_list:
        if fetched >= max_fetch:
            break
        if (cn_name, "明日方舟") in seen_pairs:
            log(f"    >> {cn_name} already exists, skip")
            continue
        try:
            api_url = "https://prts.wiki/api.php"
            params = {"action": "query", "titles": cn_name, "prop": "images", "imlimit": "30", "format": "json"}
            resp = session.get(api_url, params=params, timeout=15)
            data = resp.json()
            pages = data.get("query", {}).get("pages", {})
            images = []
            for page_id, page_data in pages.items():
                if "missing" in page_data:
                    continue
                images = page_data.get("images", [])
                break
            if not images:
                log(f"    WARN [{cn_name}] no images on page")
                continue
            img_title = None
            for img_info in images:
                t = img_info.get("title", "")
                if "精二" in t or "精英 2" in t:
                    img_title = t; break
            if not img_title:
                for img_info in images:
                    t = img_info.get("title", "")
                    if "精一" in t or "精英 1" in t:
                        img_title = t; break
            if not img_title:
                for img_info in images:
                    t = img_info.get("title", "")
                    if "立绘" in t:
                        img_title = t; break
            if not img_title:
                for img_info in images:
                    t = img_info.get("title", "")
                    if (t.endswith(".png") or t.endswith(".jpg")) and "档案" not in t and "密录" not in t and "图标" not in t:
                        img_title = t; break
            if not img_title:
                log(f"    WARN [{cn_name}] no art found")
                continue
            params2 = {"action": "query", "titles": img_title, "prop": "imageinfo", "iiprop": "url|size", "format": "json"}
            resp2 = session.get(api_url, params=params2, timeout=15)
            data2 = resp2.json()
            pages2 = data2.get("query", {}).get("pages", {})
            img_url = None
            for pid, pdata in pages2.items():
                iis = pdata.get("imageinfo", [])
                if iis:
                    img_url = iis[0].get("url", "")
                    w = iis[0].get("width", 0)
                    if w < 200:
                        img_url = None
                    break
            if not img_url:
                log(f"    WARN [{cn_name}] no image URL")
                continue
            h = url_hash8(img_url)
            if h in seen_hashes:
                log(f"    >> [{cn_name}] image already exists")
                continue
            seen_hashes.add(h)
            save_path = os.path.join(DOWNLOAD_DIR, f"{idx}_{h}.jpg")
            ok, size, status = download_and_compress(img_url, save_path, referer="https://prts.wiki/")
            if ok:
                art_label = "精英二立绘" if "精二" in (img_title or "") else "官方立绘"
                results.append({
                    "id": idx, "title": f"{cn_name}·{art_label}", "characterName": cn_name,
                    "game": "明日方舟", "gender": "女", "style": "2.5D",
                    "tags": [cn_name, "明日方舟", "官方立绘"],
                    "likes": 0, "rarity": "SSR", "source": "官方", "nsfw": False,
                    "imageFile": f"{idx}_{h}.jpg", "official_char_page": cn_name,
                })
                idx += 1; fetched += 1
                log(f"    OK [{cn_name}] ({size//1024}KB) [+{fetched}/{max_fetch}]")
                seen_pairs.add((cn_name, "明日方舟"))
                random_delay()
            else:
                log(f"    ERR [{cn_name}] download failed: {status}")
        except Exception as e:
            log(f"    ERR [{cn_name}] exception: {str(e)[:60]}")
            continue
    return results, idx, fetched

def fetch_ba(char_list, seen_hashes, seen_pairs, idx, fetched, max_fetch):
    """Fetch Blue Archive official art from schaledb.com"""
    log("  >>> [蔚蓝档案] schaledb.com fetching...")
    results = []
    for path_name, cn_name in char_list:
        if fetched >= max_fetch:
            break
        if (cn_name, "蔚蓝档案") in seen_pairs:
            log(f"    >> {cn_name} already exists, skip")
            continue
        for img_type in ["portrait", "collection"]:
            if fetched >= max_fetch:
                break
            url = f"https://schaledb.com/images/student/{img_type}/{path_name}.png"
            h = url_hash8(url)
            if h in seen_hashes:
                continue
            seen_hashes.add(h)
            save_path = os.path.join(DOWNLOAD_DIR, f"{idx}_{h}.jpg")
            ok, size, status = download_and_compress(url, save_path, referer="https://schaledb.com/")
            if ok:
                results.append({
                    "id": idx, "title": f"{cn_name}·官方立绘", "characterName": cn_name,
                    "game": "蔚蓝档案", "gender": "女", "style": "动漫插画",
                    "tags": [cn_name, "蔚蓝档案", "官方立绘"],
                    "likes": 0, "rarity": "SSR", "source": "官方", "nsfw": False,
                    "imageFile": f"{idx}_{h}.jpg", "official_slug": path_name,
                })
                idx += 1; fetched += 1
                log(f"    OK [{cn_name}] {img_type} ({size//1024}KB) [+{fetched}/{max_fetch}]")
                seen_pairs.add((cn_name, "蔚蓝档案"))
                random_delay()
                break
            else:
                if img_type == "portrait":
                    continue
                log(f"    ERR [{cn_name}] download failed: {status}")
    return results, idx, fetched


def fetch_mihoyo_local(seen_hashes, seen_pairs, idx, fetched, max_fetch):
    """Try to scan miHoYo local cache for official assets"""
    log("  >>> [米哈游本地缓存] scanning...")
    results = []
    cache_dirs = [
        "C:/Users/Administrator/AppData/Local/miHoYo",
        "C:/Users/Administrator/AppData/Local/HoYoverse",
        "C:/Users/Administrator/AppData/LocalLow/miHoYo",
        "C:/Users/Administrator/AppData/LocalLow/HoYoverse",
    ]
    for cache_base in cache_dirs:
        if not os.path.isdir(cache_base):
            continue
        log(f"    DIR {cache_base}")
        try:
            for root, dirs, files in os.walk(cache_base):
                for fname in files:
                    if fetched >= max_fetch:
                        break
                    if not fname.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        continue
                    fpath = os.path.join(root, fname)
                    try:
                        fsize = os.path.getsize(fpath)
                    except OSError:
                        continue
                    if fsize < 100 * 1024 or fsize > 20 * 1024 * 1024:
                        continue
                    rl = root.lower().replace("\\", "/")
                    game, style = "", ""
                    if "genshin" in rl or "原神" in root:
                        game, style = "原神", "3D渲染"
                    elif any(k in rl for k in ["starrail", "星铁", "hkrpg"]):
                        game, style = "崩坏：星穹铁道", "3D渲染"
                    elif "nap" in rl or "绝区零" in root:
                        game, style = "绝区零", "3D渲染"
                    elif "bh3" in rl or "崩坏3" in root:
                        game, style = "崩坏3", "3D渲染"
                    if not game:
                        continue
                    with open(fpath, "rb") as f:
                        fh = hashlib.md5(f.read()).hexdigest()[:8]
                    if fh in seen_hashes:
                        continue
                    seen_hashes.add(fh)
                    char_guess = Path(fname).stem.split("_")[0].split("-")[0]
                    save_path = os.path.join(DOWNLOAD_DIR, f"{idx}_{fh}.jpg")
                    try:
                        from PIL import Image
                        from io import BytesIO
                        img = Image.open(fpath)
                        if img.mode in ("RGBA", "P", "LA"):
                            img = img.convert("RGB")
                        w, h = img.size
                        if w > 1200:
                            ratio = 1200 / w
                            img = img.resize((1200, int(h * ratio)), Image.Resampling.LANCZOS)
                        q = 92; out = BytesIO()
                        while q >= 55:
                            out.seek(0); out.truncate()
                            img.save(out, format="JPEG", quality=q, optimize=True)
                            if out.tell() <= 800 * 1024:
                                break
                            q -= 5
                        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
                        with open(save_path, "wb") as of:
                            of.write(out.getvalue())
                        results.append({
                            "id": idx, "title": f"{char_guess}·官方立绘",
                            "characterName": char_guess, "game": game,
                            "gender": "女", "style": style,
                            "tags": [char_guess, game, "官方立绘"],
                            "likes": 0, "rarity": "SSR", "source": "官方", "nsfw": False,
                            "imageFile": f"{idx}_{fh}.jpg", "local_path": fpath,
                        })
                        idx += 1; fetched += 1
                        log(f"    OK [local] {fpath} [{fetched}/{max_fetch}]")
                    except Exception as e:
                        log(f"    ERR [local] {fpath}: {str(e)[:40]}")
        except Exception as e:
            log(f"    ERR scan {cache_base}: {str(e)[:40]}")
    if not results:
        log("    INFO No local cache assets found (normal)")
    return results, idx, fetched

# ===== Main =====

def run_crawl(max_per_run=MAX_PER_RUN):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    existing_items = read_data_js_items()
    seen_hashes = load_existing_hashes()
    seen_pairs = load_existing_pairs()
    max_id = max([it["id"] for it in existing_items] or [0])
    idx = max_id + 1
    fetched = 0
    new_items = []

    log(f"=== 官方立绘爬虫启动 | 已有 {len(existing_items)} 张 | 本轮目标 +{max_per_run} ===")

    # 1. miHoYo local cache (zero network)
    results, idx, fetched = fetch_mihoyo_local(seen_hashes, seen_pairs, idx, fetched, max_per_run)
    new_items.extend(results)

    # 2. Genshin (genshin.jmp.blue)
    if fetched < max_per_run:
        results, idx, fetched = fetch_genshin(GENSHIN_CHARS, seen_hashes, seen_pairs, idx, fetched, max_per_run)
        new_items.extend(results)

    # 3. Arknights (prts.wiki)
    if fetched < max_per_run:
        results, idx, fetched = fetch_arknights(AK_CHARS, seen_hashes, seen_pairs, idx, fetched, max_per_run)
        new_items.extend(results)

    # 4. Blue Archive (schaledb.com)
    if fetched < max_per_run:
        results, idx, fetched = fetch_ba(BA_CHARS, seen_hashes, seen_pairs, idx, fetched, max_per_run)
        new_items.extend(results)

    # Merge and write
    all_items = existing_items + new_items
    if new_items:
        write_data_js(all_items)

    log(f"=== 本轮完成 | 新增 {len(new_items)} 张 | 总计 {len(all_items)} 张 ===")
    return new_items


def main():
    max_per_run = MAX_PER_RUN
    for i, arg in enumerate(sys.argv):
        if arg == "--max" and i + 1 < len(sys.argv):
            try:
                max_per_run = int(sys.argv[i + 1])
            except ValueError:
                pass

    results = run_crawl(max_per_run)

    if results:
        by_game = {}
        for r in results:
            game = r.get("game", "?")
            by_game[game] = by_game.get(game, 0) + 1
        summary = ", ".join(f"{g}:{c}" for g, c in by_game.items())
        log(f"新增分布: {summary}")

    log("sync_official.py 完成!")


if __name__ == "__main__":
    main()
