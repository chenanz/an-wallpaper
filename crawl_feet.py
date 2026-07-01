"""
足社多源爬虫 - 足相关壁纸
多源并发爬取，专门抓取足/丝袜/裸足/腿相关二次元女角色壁纸
图源：Safebooru + Zerochan + Bing CN
用法：python crawl_feet.py
"""

import os
import re
import json
import time
import random
import hashlib
import requests
from pathlib import Path
from datetime import datetime
from io import BytesIO
from urllib.parse import unquote, quote
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── 配置 ──────────────────────────────────────────
DOWNLOAD_DIR = "public/images"
DATA_JS_PATH = "src/data.js"
LOG_PATH = "public/images/.crawl_feet.log.txt"

TARGET_COUNT = 70              # 目标爬取数量
MIN_HEIGHT = 1080               # 最小高度（竖图≥1080p）
MAX_CONCURRENT_DOWNLOADS = 3    # 并发下载数
SAFEBOORU_PAGE_SIZE = 100       # Safebooru 每页请求数
ZEROCHAN_PAGES = 5              # Zerochan 每个tag翻页数
BING_PAGES = 3                  # Bing 每个keyword翻页数

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
]

# 男角色屏蔽列表
MALE_BLOCKLIST = set([
    "男", "男性", "male", "1boy", "2boys", "multiple_boys",
    "钟离", "魈", "达达利亚", "阿贝多", "温迪", "万叶",
    "荒泷一斗", "提纳里", "赛诺", "艾尔海森", "卡维", "那维莱特",
    "景元", "刃", "丹恒", "杰帕德", "罗刹",
])

# 非目标内容过滤
SKIP_TAGS = set([
    "cosplay", "3d_cg", "photorealistic", "photo_(medium)",
    "monochrome", "comic", "4koma", "strip", "sketch",
    "chibi", "sd_character", "super_deformed",
])

# ── Safebooru 搜索配置 ─────────────────────────
# (tag_query, tag_for_metadata, display_keyword)
SAFEBOORU_QUERIES = [
    ("foot_focus+1girl",                    "foot_focus",  "足特写"),
    ("feet+1girl",                          "feet",        "足"),
    ("barefoot+1girl",                      "barefoot",    "裸足"),
    ("soles+1girl",                         "soles",       "足底"),
    ("toes+1girl",                          "toes",        "脚趾"),
    ("stockings+1girl",                      "stockings",   "丝袜"),
    ("thighhighs+1girl",                     "thighhighs",  "过膝袜"),
    ("pantyhose+1girl",                      "pantyhose",   "连裤袜"),
    ("bare_legs+1girl",                     "bare_legs",   "裸腿"),
    ("legs+1girl",                          "legs",        "美腿"),
    ("footwear_focus+1girl",                 "footwear_focus", "足装"),
    ("black_thighhighs+1girl",              "black_thighhighs", "黑丝"),
    ("white_thighhighs+1girl",              "white_thighhighs", "白丝"),
    ("ankle_boots+1girl",                   "ankle_boots", "踝靴"),
    ("kneesocks+1girl",                     "kneesocks",   "膝袜"),
    ("striped_thighhighs+1girl",            "striped_thighhighs", "条纹袜"),
]

# ── Zerochan 搜索配置 ─────────────────────────
ZEROCHAN_QUERIES = [
    ("Feet,Anime",          "feet",       "足"),
    ("Barefoot,Anime",      "barefoot",   "裸足"),
    ("Stockings,Anime",     "stockings",  "丝袜"),
    ("Pantyhose,Anime",     "pantyhose",  "连裤袜"),
    ("Socks,Anime",         "socks",      "短袜"),
    ("Thigh+Highs,Anime",   "thighhighs", "过膝袜"),
    ("Bare+Legs,Anime",     "bare_legs",  "裸腿"),
    ("Anklet,Anime",        "anklet",     "脚踝"),
]

# ── Bing CN 搜索配置 ─────────────────────────
BING_QUERIES = [
    ("anime feet wallpaper 1080p",          "feet",     "足"),
    ("anime barefoot girl wallpaper",       "barefoot", "裸足"),
    ("anime stockings wallpaper vertical",  "stockings", "丝袜"),
    ("anime pantyhose wallpaper",           "pantyhose", "连裤袜"),
    ("anime legs wallpaper phone",          "legs",      "美腿"),
    ("anime thigh high socks wallpaper",    "thighhighs", "过膝袜"),
    ("anime soles wallpaper hd",            "soles",     "足底"),
    ("anime toes wallpaper",                "toes",      "脚趾"),
]


def log(msg):
    ts = datetime.now().strftime("%m-%d %H:%M:%S")
    line = f"[{ts}][足社] {msg}"
    print(line, flush=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def get_ua():
    return random.choice(USER_AGENTS)


def random_delay(min_s=0.8, max_s=2.5):
    time.sleep(random.uniform(min_s, max_s))


# ── 图片下载 ──────────────────────────────────
def download_image(url, referer="", timeout=30):
    """下载图片，返回 (bytes, width, height, format) 或 None"""
    try:
        headers = {"User-Agent": get_ua()}
        if referer:
            headers["Referer"] = referer
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        if resp.status_code != 200:
            return None
        data = resp.content
        if len(data) < 15 * 1024:  # < 15KB 太小
            return None
        # 用 PIL 验证图片和获取尺寸
        try:
            from PIL import Image
            img = Image.open(BytesIO(data))
            w, h = img.size
            fmt = img.format or "JPEG"
            # 验证是有效图片
            img.load()
            return data, w, h, fmt
        except ImportError:
            # 没有 PIL，从字节头推断
            if data[:3] == b'\xff\xd8\xff':
                return data, 0, 0, "JPEG"
            elif data[:8] == b'\x89PNG\r\n':
                return data, 0, 0, "PNG"
            return None
    except Exception as e:
        return None


def save_image(data, filename):
    """保存图片到 public/images/，自动转换和压缩"""
    save_path = os.path.join(DOWNLOAD_DIR, filename)
    try:
        from PIL import Image
        img = Image.open(BytesIO(data))
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        # 调整大小：竖图保持，横图裁剪为9:16
        w, h = img.size
        if h > w:
            # 竖图，保持
            max_w = 1200
            if w > max_w:
                ratio = max_w / w
                img = img.resize((max_w, int(h * ratio)), Image.Resampling.LANCZOS)
        else:
            # 横图也保存（有些横图也不错）
            max_h = 2000
            if h > max_h:
                ratio = max_h / h
                img = img.resize((int(w * ratio), max_h), Image.Resampling.LANCZOS)
        
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        quality = 90
        out = BytesIO()
        while quality >= 55:
            out.seek(0)
            out.truncate()
            img.save(out, format="JPEG", quality=quality, optimize=True)
            if out.tell() <= 900 * 1024:  # < 900KB
                break
            quality -= 5
        with open(save_path, "wb") as f:
            f.write(out.getvalue())
        w2, h2 = img.size
        return True, out.tell(), (w2, h2)
    except ImportError:
        # 没有 PIL，直接保存原始数据
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(data)
        return True, len(data), (0, 0)
    except Exception as e:
        return False, 0, (0, 0)


# ── Safebooru 爬取 ─────────────────────────────
def crawl_safebooru(seen_hashes):
    """从 Safebooru 爬取足相关图片"""
    results = []
    
    for tag_query, tag_key, display_kw in SAFEBOORU_QUERIES:
        if len(results) >= TARGET_COUNT:
            break
        
        for pid in range(0, 10):  # 最多翻10页
            if len(results) >= TARGET_COUNT:
                break
            
            try:
                url = "https://safebooru.org/index.php"
                params = {
                    "page": "dapi",
                    "s": "post",
                    "q": "index",
                    "json": "1",
                    "tags": tag_query,
                    "limit": str(SAFEBOORU_PAGE_SIZE),
                    "pid": str(pid),
                }
                resp = requests.get(url, params=params, timeout=20,
                    headers={"User-Agent": get_ua(), "Referer": "https://safebooru.org/"})
                if resp.status_code != 200:
                    break
                
                posts = json.loads(resp.text)
                if not posts:
                    break
                
                for post in posts:
                    if len(results) >= TARGET_COUNT:
                        break
                    
                    # 尺寸过滤：竖图且高度≥1080
                    w = post.get("width", 0)
                    h = post.get("height", 0)
                    if w == 0 or h == 0:
                        continue
                    if h < MIN_HEIGHT:
                        continue
                    # 优先竖图，但横图也接受（>=1080p）
                    
                    # 提取文件 URL
                    file_url = post.get("file_url", "")
                    if not file_url:
                        # 尝试从sample_url获取
                        file_url = post.get("sample_url", "")
                    if not file_url:
                        continue
                    
                    # URL 去重
                    url_hash = hashlib.md5(file_url.encode()).hexdigest()[:6]
                    if url_hash in seen_hashes:
                        continue
                    
                    # 标签分析：提取角色名和过滤
                    tags_str = post.get("tags", "")
                    tags_list = tags_str.split()
                    
                    # 过滤男性
                    if any(t in MALE_BLOCKLIST for t in tags_list):
                        continue
                    # 过滤不想要的内容
                    if any(t in SKIP_TAGS for t in tags_list):
                        continue
                    
                    # 提取角色名 (带_(xxx)后缀的是角色tag)
                    char_name = ""
                    char_tags = []
                    for t in tags_list:
                        # 角色tag格式: name_(series) 或 series:name
                        if "(" in t and ")" in t:
                            char_tags.append(t.split("(")[0].replace("_", " ").strip())
                        elif ":" in t and not t.startswith(":"):
                            char_tags.append(t.split(":")[-1].replace("_", " ").strip())
                    # 提取知名角色
                    known_chars = extract_character_name(tags_str)
                    if known_chars:
                        char_name = known_chars
                    elif char_tags:
                        char_name = char_tags[0]
                    else:
                        char_name = "精选角色"
                    
                    # 收集相关tag
                    feet_related = []
                    for t in tags_list:
                        t_lower = t.lower()
                        if any(k in t_lower for k in [
                            "foot", "feet", "barefoot", "sole", "toe", "heel",
                            "stocking", "pantyhose", "thighhigh", "kneesock",
                            "sock", "leg", "anklet", "bare_leg",
                        ]):
                            feet_related.append(t.replace("_", " "))
                    
                    results.append({
                        "source": "Safebooru",
                        "url": file_url,
                        "referer": "https://safebooru.org/",
                        "url_hash": url_hash,
                        "char_name": char_name,
                        "keyword": display_kw,
                        "key_tag": tag_key,
                        "extra_tags": feet_related[:3],
                        "width": w,
                        "height": h,
                    })
                
                log(f"  Safebooru [{tag_query}] pid={pid}: {len(posts)} posts, 累计 {len(results)}")
                random_delay(1.0, 2.0)
                
            except Exception as e:
                log(f"  Safebooru [{tag_query}] pid={pid} 失败: {e}")
                break
    
    return results


# ── Zerochan 爬取 ───────────────────────────────
def crawl_zerochan(seen_hashes):
    """从 Zerochan 爬取足相关图片"""
    results = []
    session = requests.Session()
    
    for tag, tag_key, display_kw in ZEROCHAN_QUERIES:
        if len(results) >= TARGET_COUNT:
            break
        
        for page in range(1, ZEROCHAN_PAGES + 1):
            if len(results) >= TARGET_COUNT:
                break
            
            try:
                url = f"https://www.zerochan.net/{tag}?json=1&p={page}"
                resp = session.get(url, timeout=20, headers={
                    "User-Agent": get_ua(),
                    "Accept": "application/json",
                    "Referer": "https://www.zerochan.net/",
                })
                if resp.status_code != 200:
                    break
                
                data = json.loads(resp.text)
                items = data.get("items", [])
                if not items:
                    break
                
                for item in items:
                    if len(results) >= TARGET_COUNT:
                        break
                    
                    w = item.get("width", 0)
                    h = item.get("height", 0)
                    if w == 0 or h == 0:
                        continue
                    if h < MIN_HEIGHT and w < 1920:
                        continue
                    
                    item_id = item.get("id")
                    char_tag = item.get("tag", "Unknown")
                    
                    # 获取完整图片URL（需要访问具体页面）
                    try:
                        page_url = f"https://www.zerochan.net/{item_id}"
                        page_resp = session.get(page_url, timeout=15, headers={
                            "User-Agent": get_ua(),
                            "Referer": "https://www.zerochan.net/",
                        })
                        if page_resp.status_code != 200:
                            continue
                        
                        full_match = re.search(
                            r'https://static\.zerochan\.net/[^"]+\.full\.\d+\.jpg',
                            page_resp.text
                        )
                        if not full_match:
                            # 尝试 PNG
                            full_match = re.search(
                                r'https://static\.zerochan\.net/[^"]+\.full\.\d+\.png',
                                page_resp.text
                            )
                        if not full_match:
                            continue
                        
                        img_url = full_match.group()
                        url_hash = hashlib.md5(img_url.encode()).hexdigest()[:6]
                        if url_hash in seen_hashes:
                            continue
                        
                        # 提取角色名
                        char_name = char_tag.replace("+", " ").strip()
                        if not char_name or char_name == "Unknown":
                            # 从URL中提取
                            url_name = re.search(r'zerochan\.net/([^.]+)\.full', img_url)
                            if url_name:
                                char_name = url_name.group(1).replace(".", " ").replace("+", " ").strip()
                            else:
                                char_name = "精选角色"
                        
                        results.append({
                            "source": "Zerochan",
                            "url": img_url,
                            "referer": "https://www.zerochan.net/",
                            "url_hash": url_hash,
                            "char_name": char_name,
                            "keyword": display_kw,
                            "key_tag": tag_key,
                            "extra_tags": [display_kw],
                            "width": w,
                            "height": h,
                        })
                        
                    except Exception as e:
                        continue
                
                log(f"  Zerochan [{tag}] p={page}: {len(items)} items, 累计 {len(results)}")
                random_delay(1.5, 3.0)
                
            except Exception as e:
                log(f"  Zerochan [{tag}] p={page} 失败: {e}")
                break
    
    return results


# ── Bing CN 爬取 ───────────────────────────────
def crawl_bing(seen_hashes):
    """从 Bing CN 爬取足相关图片"""
    results = []
    session = requests.Session()
    
    for keyword, tag_key, display_kw in BING_QUERIES:
        if len(results) >= TARGET_COUNT:
            break
        
        for page_idx in range(BING_PAGES):
            if len(results) >= TARGET_COUNT:
                break
            
            try:
                first = page_idx * 35 + 1
                url = "https://cn.bing.com/images/async"
                params = {
                    "q": keyword,
                    "first": str(first),
                    "count": "35",
                    "qft": "+filterui:aspect-tall+filterui:photo-photo",
                }
                resp = session.get(url, params=params, timeout=20, headers={
                    "User-Agent": get_ua(),
                    "Referer": "https://cn.bing.com/images/search",
                })
                if resp.status_code != 200:
                    break
                
                # 提取 mediaurl（URL编码的源图链接）
                encoded_urls = re.findall(r'mediaurl=(https?%3[Aa]%2[Ff][^&"]+)', resp.text)
                
                for enc_url in encoded_urls:
                    if len(results) >= TARGET_COUNT:
                        break
                    
                    try:
                        img_url = unquote(enc_url)
                        # 只接受看起来像图片的URL
                        if not any(img_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                            # 也接受包含image/pic/img等关键词的URL
                            if not any(k in img_url.lower() for k in ['image', 'img', 'pic', 'photo', 'wallpaper', 'upload']):
                                continue
                        
                        url_hash = hashlib.md5(img_url.encode()).hexdigest()[:6]
                        if url_hash in seen_hashes:
                            continue
                        
                        results.append({
                            "source": "Bing图片",
                            "url": img_url,
                            "referer": "https://cn.bing.com/",
                            "url_hash": url_hash,
                            "char_name": "",  # Bing无法提取角色名
                            "keyword": display_kw,
                            "key_tag": tag_key,
                            "extra_tags": [display_kw],
                            "width": 0,  # 待下载后获取
                            "height": 0,
                        })
                    except Exception:
                        continue
                
                log(f"  Bing [{keyword}] page={page_idx}: {len(encoded_urls)} urls, 累计 {len(results)}")
                random_delay(1.0, 2.0)
                
            except Exception as e:
                log(f"  Bing [{keyword}] page={page_idx} 失败: {e}")
                break
    
    return results


# ── 角色名提取 ──────────────────────────────────
CHAR_DB = {
    # 原神
    "raiden_shogun": "雷电将军", "yae_miko": "八重神子", "furina": "芙宁娜",
    "yelan": "夜兰", "keqing": "刻晴", "ganyu": "甘雨", "eula": "优菈",
    "shenhe": "申鹤", "mona": "莫娜", "navia": "娜维娅", "clorinde": "克洛琳德",
    "jean": "琴", "lisa": "丽莎", "ningguang": "凝光", "hu_tao": "胡桃",
    "nahida": "纳西妲", "nilou": "妮露", "yoimiya": "宵宫", "shinobu": "绮良良",
    "chiori": "千织", "kamisato_ayaka": "神里绫华", "sangonomiya_kokomi": "珊瑚宫心海",
    "barbara": "芭芭拉", "noelle": "诺艾尔", "fischl": "菲谢尔",
    "faruzan": "珐露珊", "candace": "坎蒂丝", "layla": "莱依拉",
    "shenhe_(genshin_impact)": "申鹤", "raiden_shogun_(genshin_impact)": "雷电将军",
    # 崩铁
    "kafka": "卡芙卡", "himeko": "姬子", "black_swan": "黑天鹅",
    "ruan_mei": "阮梅", "march_7th": "三月七", "bronya": "布洛妮娅",
    "tingyun": "停云", "pela": "佩拉", "akingyon": "知更鸟",
    "huohuo": "藿藿", "klarafa": "克拉拉", "qingque": "青雀",
    "aki": "黄泉", "firefly": "流萤", "huoxin": "花火",
    "jingliu": "镜流", "fugue": "忘归人",
    "kafka_(honkai:_star_rail)": "卡芙卡",
    # 绝区零
    "ellen_joe": "艾莲", "zhu_yuan": "朱鸢", "jane_doe": "简",
    "miyabi": "星见雅", "nicole": "妮可", "grace": "格莉丝",
    # 明日方舟
    "amiya": "阿米娅", "texas": "德克萨斯", "exusiai": "能天使",
    "skadi": "斯卡蒂", "chen": "陈", "kal'tsit": "凯尔希",
    "saga": "令", "dusk": "夕", "nian": "年",
    "surtr": "史尔特尔", "lappland": "拉普兰德",
    # 蔚蓝档案
    "alice": "爱丽丝", "shiroko": "白子", "hoshino": "星野",
    "sunlight": "日奈", "aris": "爱丽丝",
    # 少女前线
    "m4a1": "M4A1", "ump45": "UMP45", "ump9": "UMP9",
    # 通用
    "rem": "雷姆", "ram": "拉姆", "emilia": "艾米莉亚",
    "zero_two": "02", "megumin": "惠惠", "aqua": "阿库娅",
    "darkness": "达克妮丝", "mikasa": "三笠", "saber": "Saber",
    "rin_tohsaka": "远坂凛", "sakura_matou": "间桐樱",
    "asuna": "亚丝娜", "sinon": "诗乃",
}

def extract_character_name(tags_str):
    """从标签字符串中提取角色名"""
    tags_lower = tags_str.lower()
    for eng_name, cn_name in CHAR_DB.items():
        if eng_name in tags_lower:
            return cn_name
    return ""


# ── 去重 ──────────────────────────────────────
def load_existing_hashes():
    """从已下载文件和 data.js 加载已有 hash"""
    seen = set()
    # 从 data.js 中的 imageFile 提取
    if os.path.exists(DATA_JS_PATH):
        try:
            with open(DATA_JS_PATH, "r", encoding="utf-8") as f:
                content = f.read()
            # 提取所有 imageFile 中的 hash 部分
            for m in re.finditer(r'"imageFile"\s*:\s*"([^"]+)"', content):
                fname = m.group(1)
                # feet_xxxxxx.jpg 格式
                parts = fname.replace(".jpg", "").replace(".png", "").split("_")
                if len(parts) >= 2:
                    seen.add(parts[-1])
        except Exception:
            pass
    
    # 从已下载文件名提取
    if os.path.exists(DOWNLOAD_DIR):
        for f in os.listdir(DOWNLOAD_DIR):
            if f.startswith("feet_"):
                parts = f.replace(".jpg", "").replace(".png", "").split("_")
                if len(parts) >= 2:
                    seen.add(parts[-1])
    
    return seen


def load_all_image_hashes():
    """加载所有已有图片的 URL hash（用于URL级别去重）"""
    seen = set()
    log_file = os.path.join(DOWNLOAD_DIR, ".crawl_feet_urls.txt")
    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        seen.add(line)
        except Exception:
            pass
    return seen


def save_url_hash(url_hash):
    """保存 URL hash 到日志文件"""
    log_file = os.path.join(DOWNLOAD_DIR, ".crawl_feet_urls.txt")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(url_hash + "\n")


# ── data.js 读写 ───────────────────────────────
def read_data_js():
    """读取现有 wallpaperData"""
    if not os.path.exists(DATA_JS_PATH):
        return []
    try:
        with open(DATA_JS_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        m = re.search(r'export const wallpaperData = (\[.*\]);', content, re.DOTALL)
        if m:
            return json.loads(m.group(1))
    except Exception as e:
        log(f"读取 data.js 失败: {e}")
    return []


def write_data_js(items):
    """写回 wallpaperData"""
    # 收集已有的 game 列表
    existing_games = set(it["game"] for it in items)
    games_list = []
    seen_game_ids = set()
    # 保留原有 GAMES 定义，添加新的
    if os.path.exists(DATA_JS_PATH):
        try:
            with open(DATA_JS_PATH, "r", encoding="utf-8") as f:
                content = f.read()
            m = re.search(r'export const GAMES = (\[.*?\]);', content, re.DOTALL)
            if m:
                games_list = json.loads(m.group(1))
                seen_game_ids = set(g.get("id", "") for g in games_list)
        except Exception:
            pass
    
    for game_name in existing_games:
        if game_name not in seen_game_ids:
            games_list.append({"id": game_name, "name": game_name})
            seen_game_ids.add(game_name)
    
    with open(DATA_JS_PATH, "w", encoding="utf-8") as f:
        f.write("// 自动生成：多源爬虫（米游社 + B站 + 百度图 + 官方 + 玉足社补图 + 足社爬虫）\n\n")
        f.write("export const GAMES = ")
        json.dump(games_list, f, ensure_ascii=False, indent=2)
        f.write(";\n\n")
        f.write('export const STYLES = ["3D渲染", "2.5D", "动漫插画", "Live2D"];\n\n')
        f.write("export const wallpaperData = ")
        json.dump(items, f, ensure_ascii=False, indent=2)
        f.write(";\n\n")
        f.write("export function getFallbackImageUrl(id, w = 400, h = 712) {\n")
        f.write("  return `https://picsum.photos/seed/an_${id}/${w}/${h}`;\n")
        f.write("}\n")


# ── 并发下载 + 入库 ────────────────────────────
def download_and_save(candidate, seen_hashes):
    """下载单张图片并保存，返回 (success, item_dict)"""
    url = candidate["url"]
    referer = candidate.get("referer", "")
    url_hash = candidate["url_hash"]
    
    if url_hash in seen_hashes:
        return False, None
    
    result = download_image(url, referer=referer)
    if result is None:
        return False, None
    
    data, w, h, fmt = result
    
    # 尺寸验证（下载后二次确认）
    if w > 0 and h > 0:
        if h < MIN_HEIGHT and w < MIN_HEIGHT:
            return False, None
    
    # 保存
    filename = f"feet_{url_hash}.jpg"
    ok, size, (sw, sh) = save_image(data, filename)
    if not ok:
        return False, None
    
    seen_hashes.add(url_hash)
    save_url_hash(url_hash)
    
    return True, {
        "filename": filename,
        "size": size,
        "width": sw or w,
        "height": sh or h,
        "candidate": candidate,
    }


def process_candidates(all_candidates, seen_hashes, existing_items, max_id):
    """并发下载候选图片，返回新增条目"""
    new_items = []
    fetched = 0
    failed = 0
    next_id = max_id + 1
    
    log(f"  开始下载 {len(all_candidates)} 个候选图片，并发={MAX_CONCURRENT_DOWNLOADS}")
    
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_DOWNLOADS) as executor:
        futures = {}
        for i, cand in enumerate(all_candidates):
            if fetched >= TARGET_COUNT:
                break
            future = executor.submit(download_and_save, cand, seen_hashes)
            futures[future] = (i, cand)
        
        for future in as_completed(futures):
            if fetched >= TARGET_COUNT:
                break
            
            idx, cand = futures[future]
            try:
                ok, result = future.result()
                if not ok or result is None:
                    failed += 1
                    continue
                
                cand = result["candidate"]
                filename = result["filename"]
                w, h = result["width"], result["height"]
                size = result["size"]
                
                is_portrait = (h > w) if w > 0 else True
                
                char_name = cand["char_name"] or "精选角色"
                keyword = cand["keyword"]
                key_tag = cand["key_tag"]
                extra_tags = cand.get("extra_tags", [])
                source = cand["source"]
                
                # 构建title
                title = f"{char_name}·{keyword}"
                if len(title) > 55:
                    title = title[:55]
                
                # 构建tags
                tags = [char_name]
                if keyword and keyword not in tags:
                    tags.append(keyword)
                for et in extra_tags:
                    if et and et not in tags:
                        tags.append(et)
                if "足社" not in tags:
                    tags.append("足社")
                # 确保足相关关键词
                feet_keywords = ["足", "脚", "腿", "foot", "leg", "feet", "stocking",
                                "pantyhose", "裸足", "丝袜", "玉足", "脚趾", "美腿",
                                "长腿", "黑丝", "白丝", "过膝袜", "thigh", "soles",
                                "踝", "连裤袜", "足底"]
                if not any(k in " ".join(tags).lower() for k in feet_keywords):
                    tags.append(key_tag.replace("_", " "))
                tags = tags[:6]
                
                item = {
                    "id": next_id,
                    "title": title,
                    "characterName": char_name,
                    "game": "足社",
                    "gender": "女",
                    "style": "二次元",
                    "tags": tags,
                    "likes": 0,
                    "rarity": "SSR",
                    "source": source,
                    "nsfw": False,
                    "imageFile": filename,
                }
                new_items.append(item)
                next_id += 1
                fetched += 1
                
                orientation = "竖" if is_portrait else "横"
                log(f"    ✓ [{orientation}] {title} ({size//1024}KB) [{source}] [+{fetched}/{TARGET_COUNT}]")
                
            except Exception as e:
                failed += 1
                log(f"    ✗ 下载失败 #{idx}: {e}")
    
    log(f"  下载完成: 成功={fetched}, 失败={failed}")
    return new_items


# ── 主流程 ──────────────────────────────────────
def main():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    seen_hashes = load_existing_hashes()
    url_seen = load_all_image_hashes()
    # 合并两种去重
    all_seen = seen_hashes | url_seen
    
    existing_items = read_data_js()
    max_id = max([it["id"] for it in existing_items] or [0])
    
    log(f"=== 足社爬虫启动 | 已有 {len(existing_items)} 张 | 目标 +{TARGET_COUNT} ===")
    log(f"  已有hash: {len(seen_hashes)} 个 (文件级) + {len(url_seen)} 个 (URL级)")
    
    # ── 并行收集候选 ──
    all_candidates = []
    
    log("── 阶段1: 收集 Safebooru 候选 ──")
    safebooru_candidates = crawl_safebooru(all_seen)
    for c in safebooru_candidates:
        all_seen.add(c["url_hash"])
    all_candidates.extend(safebooru_candidates)
    log(f"  Safebooru: {len(safebooru_candidates)} 个候选")
    
    log("── 阶段2: 收集 Zerochan 候选 ──")
    zerochan_candidates = crawl_zerochan(all_seen)
    for c in zerochan_candidates:
        all_seen.add(c["url_hash"])
    all_candidates.extend(zerochan_candidates)
    log(f"  Zerochan: {len(zerochan_candidates)} 个候选")
    
    log("── 阶段3: 收集 Bing CN 候选 ──")
    bing_candidates = crawl_bing(all_seen)
    for c in bing_candidates:
        all_seen.add(c["url_hash"])
    all_candidates.extend(bing_candidates)
    log(f"  Bing CN: {len(bing_candidates)} 个候选")
    
    # 打乱候选顺序，确保来源多样性
    random.shuffle(all_candidates)
    
    # 限制候选数量避免过多
    if len(all_candidates) > TARGET_COUNT * 3:
        all_candidates = all_candidates[:TARGET_COUNT * 3]
    
    log(f"── 总候选: {len(all_candidates)} 个 ──")
    
    # ── 阶段4: 并发下载 ──
    log("── 阶段4: 并发下载图片 ──")
    new_items = process_candidates(all_candidates, all_seen, existing_items, max_id)
    
    # ── 阶段5: 写入 data.js ──
    if new_items:
        total_items = existing_items + new_items
        write_data_js(total_items)
        log(f"📦 data.js 已更新: {len(existing_items)} → {len(total_items)} (+{len(new_items)})")
    else:
        log("⚠️ 未获取任何新图片")
    
    log(f"=== 足社爬虫结束 | 新增 {len(new_items)} 张 ===")


if __name__ == "__main__":
    main()
