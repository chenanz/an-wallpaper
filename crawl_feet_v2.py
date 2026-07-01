"""
足社爬虫 v2 - 解决三问题：
1. 角色名中文化（完整映射表）
2. 隔离足社（feet_图片game="足社"）
3. 量大（足社200+，总量400+）
"""
import os, re, json, time, random, hashlib, requests
from pathlib import Path
from datetime import datetime
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed

# ═══ 配置 ═══
DOWNLOAD_DIR = "public/images"
DATA_JS_PATH = "src/data.js"
LOG_PATH = "public/images/.crawl_feet.log.txt"
TARGET_FEET = 200
TARGET_OTHER = 200
MIN_HEIGHT = 800
MIN_WIDTH = 500
MAX_CONCURRENT = 4
PAGE_SIZE = 100

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
]
MALE_BLOCKS = {"1boy", "2boys", "multiple_boys", "male_focus", "boy"}
SKIP_TAGS = {"cosplay", "3d_cg", "photorealistic", "photo_(medium)", "monochrome", "comic", "4koma", "chibi", "sd_character"}
NSFW_TAGS = {"nude", "topless", "bottomless", "underwear", "panties", "bra", "nipples", "areolae", "pussy", "sex", "oral", "cum", "tentacle", "bondage", "guro"}

# ═══ 角色名映射表 ═══
CHAR_DB = {}

def _reg(mapping, suffix=""):
    for eng, cn in mapping.items():
        k = eng.lower().strip()
        CHAR_DB[k] = cn
        if suffix:
            CHAR_DB[f"{k}_{suffix}"] = cn

# ── 原神 80+ ──
_reg({
    "aether": "空", "lumine": "荧", "jean": "琴", "lisa": "丽莎",
    "amber": "安柏", "barbara": "芭芭拉", "razor": "雷泽", "kaeya": "凯亚",
    "diluc": "迪卢克", "venti": "温迪", "xiangling": "香菱", "beidou": "北斗",
    "xingqiu": "行秋", "ningguang": "凝光", "fischl": "菲谢尔",
    "bennett": "班尼特", "noelle": "诺艾尔", "qiqi": "七七",
    "chongyun": "重云", "sucrose": "砂糖", "mona": "莫娜", "keqing": "刻晴",
    "diona": "迪奥娜", "albedo": "阿贝多", "ganyu": "甘雨", "xiao": "魈",
    "hu_tao": "胡桃", "rosaria": "罗莎莉亚", "yanfei": "烟绯", "eula": "优菈",
    "kazuha": "枫原万叶", "kamisato_ayaka": "神里绫华", "yoimiya": "宵宫",
    "sayu": "早柚", "raiden_shogun": "雷电将军",
    "sangonomiya_kokomi": "珊瑚宫心海", "thoma": "托马", "gorou": "五郎",
    "itto": "荒泷一斗", "shenhe": "申鹤", "yun_jin": "云堇",
    "yae_miko": "八重神子", "ayato": "神里绫人", "kuki_shinobu": "久岐忍",
    "shinobu": "久岐忍", "heizou": "鹿野院平藏", "tighnari": "提纳里",
    "collei": "柯莱", "dori": "多莉", "cyno": "赛诺", "candace": "坎蒂丝",
    "nilou": "妮露", "nahida": "纳西妲", "layla": "莱依拉",
    "faruzan": "珐露珊", "wanderer": "流浪者", "alhaitham": "艾尔海森",
    "yaoyao": "瑶瑶", "dehya": "迪希雅", "mika": "米卡", "baizhu": "白术",
    "kaveh": "卡维", "kirara": "绮良良", "lyney": "林尼", "lynette": "琳妮特",
    "freminet": "菲米尼", "furina": "芙宁娜", "navia": "娜维娅",
    "chevreuse": "夏沃蕾", "clorinde": "克洛琳德", "sigewinne": "希格雯",
    "emilie": "艾梅莉埃", "chiori": "千织", "arlecchino": "仆人",
    "sethos": "塞索斯", "xilonen": "希诺宁", "citlali": "茜特菈莉",
    "mavuika": "玛薇卡", "ororon": "欧洛伦", "lan_yan": "蓝砚",
    "mizuki": "梦月", "ayaka": "神里绫华", "kokomi": "珊瑚宫心海",
    "raiden": "雷电将军", "yae": "八重神子", "shogun": "雷电将军",
    "hutao": "胡桃", "shinobu": "久岐忍",
    "charlotte": "夏洛特", "wriothasley": "莱欧斯利",
    "neuvillette": "那维莱特", "wriothesley": "莱欧斯利",
    "chiori": "千织", "sethos": "塞索斯",
}, "_(genshin_impact)")

# ── 星穹铁道 50+ ──
_reg({
    "himeko": "姬子", "bronya": "布洛妮娅", "seele": "希儿",
    "tingyun": "停云", "kafka": "卡芙卡", "silver_wolf": "银狼",
    "bailu": "白露", "serval": "希露瓦", "pela": "佩拉",
    "natasha": "娜塔莎", "asta": "艾丝妲", "herta": "黑塔",
    "qingque": "青雀", "yukong": "驭空", "luocha": "罗刹",
    "jing_yuan": "景元", "sushang": "素裳", "yanqing": "彦卿",
    "fu_xuan": "符玄", "jingliu": "镜流", "topaz": "托帕",
    "guinaifen": "桂乃芬", "huohuo": "藿藿", "ruan_mei": "阮梅",
    "sparkle": "花火", "black_swan": "黑天鹅", "march_7th": "三月七",
    "danheng": "丹恒", "trailblazer": "开拓者", "sampo": "桑博",
    "arlan": "阿兰", "firefly": "流萤", "robin": "知更鸟",
    "acheron": "黄泉", "jade": "翡翠", "yunli": "云璃",
    "jiaoqiu": "椒丘", "feixiao": "飞霄", "lingsha": "灵砂",
    "aglaea": "阿格莱雅", "mydei": "迈德", "tribbie": "提宝",
    "castorice": "卡斯特莉斯", "misha": "米沙",
    "dr_ratio": "真理医生", "aventurine": "砂金",
    "sunday": "星期日", "mothlan": "飞霄",
    "mokoshi": "梦月", "rappa": "乱破",
    # 简写
    "sw": "银狼", "bs": "黑天鹅",
}, "_(honkai:_star_rail)")

# ── 明日方舟 60+ ──
_reg({
    "amiya": "阿米娅", "texas": "德克萨斯", "exusiai": "能天使",
    "saria": "塞雷娅", "franka": "芙兰卡", "liskarm": "雷蛇",
    "croissant": "可颂", "shamare": "巫恋", "mostima": "莫斯提马",
    "angelina": "安洁莉娜", "magallan": "麦哲伦", "skadi": "斯卡蒂",
    "grani": "格拉尼", "specter": "幽灵鲨", "surtr": "史尔特尔",
    "chen": "陈", "kal'tsit": "凯尔希", "mountain": "山",
    "saga": "令", "dusk": "夕", "nian": "年", "rosa": "迷迭香",
    "lappland": "拉普兰德", "pramanix": "初雪", "mayer": "梅尔",
    "weedy": "温蒂", "elegy": "歌蕾蒂娅",
    "skadi_the_corrupting_heart": "浊心斯卡蒂", "mizuki": "水子",
    "suzuran": "铃兰", "archetto": "远牙", "ash": "灰烬",
    "lee": "老鲤", "blacknight": "夜半", "thorns": "棘刺",
    "penance": "斥罪", "virtuosa": "但书", "ling": "令",
    "chong_yue": "重岳", "lin": "林", "muelsyse": "缪尔赛思",
    "hoederer": "赫德雷", "inez": "伊内丝", "typhon": "提丰",
    "viviana": "薇薇安娜", "mlynar": "玛恩纳", "w": "W",
    "ifrit": "伊芙利特", "eyjafjalla": "艾雅法拉",
    "siege": "推进之王", "zima": "真理", "istina": "真理",
    "talia": "塔露拉", "talulah": "塔露拉",
    "schwarz": "黑", "hellagur": "赫拉格",
    "ceylon": "锡兰", "reed": "苇草", "flamebringer": "炎客",
    "magallan": "麦哲伦", "manticore": "曼提柯",
    "phantom": "幽灵", "w": "W",
    "rosmontis": "迷迭香", "amiya_(guard)": "阿米娅(近卫)",
    "kaltsit": "凯尔希", "kalsit": "凯尔希",
    "kirin_r_yato": "麒麟R夜刀", "pozem": "能天使",
    "预备干员": "预备干员",
}, "_(arknights)")

# ── 蔚蓝档案 40+ ──
_reg({
    "shiroko": "白子", "hoshino": "星野", "nonomi": "野宫",
    "serika": "黑子", "ayane": "绫音", "alice": "爱丽丝",
    "aris": "爱丽丝", "mika": "美嘉", "miyako": "宫子",
    "saki": "咲", "miyu": "美游", "reisa": "蕾莎",
    "koyuki": "小雪", "noa": "诺亚", "hanae": "花绘",
    "haruka": "遥", "izumi": "泉", "junko": "纯子",
    "koharu": "小春", "kokona": "心奈", "marina": "玛丽娜",
    "midori": "翠", "momoi": "桃井", "natsu": "夏",
    "neru": "妮露", "tsubaki": "椿", "hifumi": "日富美",
    "kozue": "梢", "utaha": "诗花", "shun": "瞬",
    "toki": "时", "arisu": "有栖", "ein": "爱因",
    "sia": "夏", "chihiro": "千寻", "yuzu": "柚子",
    "haruna": "春奈", "izuna": "伊织", "kanna": "神奈",
    "hanna": "汉娜", "kagami": "镜", "mimori": "三森",
    "seia": "星绪", "kirino": "桐乃", "mari": "玛丽",
    "hasumi": "莲见", "tsubaki_(blue_archive)": "椿",
}, "_(blue_archive)")

# ── 绝区零 20+ ──
_reg({
    "ellen_joe": "艾莲", "zhu_yuan": "朱鸢", "jane_doe": "简",
    "miyabi": "星见雅", "nicole": "妮可", "grace": "格莉丝",
    "anby": "安比", "nekomata": "猫又", "lycaon": "莱卡恩",
    "rina": "丽娜", "alexandrina": "丽娜", "soldier_11": "11号",
    "corin": "珂蕾妲", "koleida": "珂蕾妲", "lucy": "露西",
    "burnice": "伯妮斯", "lighter": "莱特", "caesar": "凯撒",
    "yanagi": "柳", "harumasa": "晴雅", "asaba_harumasa": "浅羽晴雅",
    "miyako": "宫子", "trigger": "扳机", "pulchra": "普拉切拉",
}, "_(zenless_zone_zero)")

# ── 其他热门角色 ──
_reg({
    "rem": "雷姆", "ram": "拉姆", "emilia": "艾米莉亚",
    "zero_two": "02", "megumin": "惠惠", "aqua": "阿库娅",
    "darkness": "达克妮丝", "mikasa": "三笠", "saber": "Saber",
    "rin_tohsaka": "远坂凛", "sakura_matou": "间桐樱",
    "asuna": "亚丝娜", "sinon": "诗乃", "leafa": "莉法",
    "rei": "绫波丽", "asuka": "明日香", "hatsune_miku": "初音未来",
    "miku_hatsune": "初音未来", "kanna_kamui": "康娜",
    "tohru": "托尔", "lucoa": "露科亚", "elaina": "伊蕾娜",
    "holo": "赫萝", "roxy": "洛琪希",
    "marin_kitagawa": "喜多川海梦", "nico": "妮可",
    "stocking": "史朵克", "panty": "潘蒂",
    "miku": "初音未来", "hatsune": "初音未来",
    "ishtar": "伊什塔尔", "rin": "远坂凛",
    "illya": "伊莉雅", "illyasviel": "伊莉雅",
    "kuroka": "黑歌", "touka": "灯", "natsuki": "夏树",
})

# ═══ 游戏→中文映射 ═══
GAME_CN = {
    "genshin_impact": "原神",
    "honkai:_star_rail": "崩坏：星穹铁道",
    "honkai_star_rail": "崩坏：星穹铁道",
    "star_rail": "崩坏：星穹铁道",
    "arknights": "明日方舟",
    "blue_archive": "蔚蓝档案",
    "zenless_zone_zero": "绝区零",
    "honkai_impact_3rd": "崩坏3",
    "girls'_frontline": "少女前线",
    "azur_lane": "碧蓝航线",
    "fate/grand_order": "Fate/GO",
    "fate": "Fate",
    "nikke": "胜利女神：妮姬",
}

# ═══ 足相关TAG→中文 ═══
FEET_TAG_CN = {
    "feet": "玉足", "foot_focus": "足部特写", "barefoot": "裸足",
    "soles": "足底", "toes": "脚趾", "heels": "脚后跟",
    "stockings": "丝袜", "thighhighs": "过膝袜",
    "black_thighhighs": "黑丝", "white_thighhighs": "白丝",
    "pantyhose": "连裤袜", "kneesocks": "膝袜",
    "bare_legs": "裸腿", "legs": "美腿",
    "anklet": "脚踝饰", "ankle_boots": "踝靴",
    "striped_thighhighs": "条纹袜", "footwear_focus": "足装饰",
    "high_heels": "高跟", "platform_heels": "厚底鞋",
    "thigh_boots": "过膝靴", "white_pantyhose": "白丝连裤",
    "black_pantyhose": "黑丝连裤", "fishnets": "渔网袜",
    "socks": "袜子", "garter_belt": "吊袜带",
    "between_thighs": "腿间", "crossed_legs": "交叠腿",
    "one_leg_up": "单腿抬", "spread_legs": "张腿",
}

# ═══ 安全检查 - 删除旧的.feet_url缓存以免冲突 ═══

def log(msg):
    ts = datetime.now().strftime("%m-%d %H:%M:%S")
    line = f"[{ts}][足社] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def get_ua():
    return random.choice(USER_AGENTS)

def random_delay(a=0.3, b=1.0):
    time.sleep(random.uniform(a, b))

# ═══ 角色名提取 ═══
def extract_character_cn(tags_str):
    """从 Safebooru tags 提取角色中文名 + 所属游戏"""
    tags_list = tags_str.split()
    char_name = "美少女"
    game_name = ""
    candidates = []

    for t in tags_list:
        # 匹配 character_(series) 格式
        m = re.match(r'^([a-z0-9_\']+)_\(([^)]+)\)$', t, re.IGNORECASE)
        if m:
            ctag = m.group(1).lower()
            stag = m.group(2).lower()
            full = f"{ctag}_({stag})".lower()
            if full in CHAR_DB:
                candidates.append((CHAR_DB[full], stag))
            elif ctag in CHAR_DB:
                candidates.append((CHAR_DB[ctag], stag))
            else:
                ctag2 = ctag.replace("'", "")
                if ctag2 in CHAR_DB:
                    candidates.append((CHAR_DB[ctag2], stag))

    if not candidates:
        for t in tags_list:
            tl = t.lower().strip()
            if tl in CHAR_DB and len(tl) > 2 and tl not in SKIP_TAGS:
                candidates.append((CHAR_DB[tl], ""))

    if candidates:
        with_game = [c for c in candidates if c[1]]
        if with_game:
            char_name, gtag = with_game[0]
            game_name = GAME_CN.get(gtag, "")
        else:
            char_name = candidates[0][0]

    if not game_name:
        for t in tags_list:
            tl = t.lower()
            if tl in GAME_CN:
                game_name = GAME_CN[tl]
                break

    return char_name, game_name


def extract_feet_tags_cn(tags_str):
    """提取足相关中文标签"""
    result = []
    for t in tags_str.split():
        tl = t.lower()
        if tl in FEET_TAG_CN:
            cn = FEET_TAG_CN[tl]
            if cn not in result:
                result.append(cn)
    return result


def has_nsfw(tags_str):
    return any(t in NSFW_TAGS for t in tags_str.lower().split())


# ═══ 图片下载/保存 ═══
def download_image(url, referer="", timeout=30):
    try:
        headers = {"User-Agent": get_ua()}
        if referer:
            headers["Referer"] = referer
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        if resp.status_code != 200:
            return None
        data = resp.content
        if len(data) < 10 * 1024:
            return None
        try:
            from PIL import Image
            img = Image.open(BytesIO(data))
            w, h = img.size
            img.load()
            return data, w, h
        except ImportError:
            return data, 0, 0
    except:
        return None


def save_image(data, filename):
    save_path = os.path.join(DOWNLOAD_DIR, filename)
    try:
        from PIL import Image
        img = Image.open(BytesIO(data))
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        w, h = img.size
        if h > w:
            if w > 1200:
                r = 1200 / w
                img = img.resize((1200, int(h * r)), Image.Resampling.LANCZOS)
        else:
            if h > 2000:
                r = 2000 / h
                img = img.resize((int(w * r), 2000), Image.Resampling.LANCZOS)
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        quality = 90
        out = BytesIO()
        while quality >= 55:
            out.seek(0); out.truncate()
            img.save(out, format="JPEG", quality=quality, optimize=True)
            if out.tell() <= 900 * 1024:
                break
            quality -= 5
        with open(save_path, "wb") as f:
            f.write(out.getvalue())
        w2, h2 = img.size
        return True, out.tell(), (w2, h2)
    except ImportError:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(data)
        return True, len(data), (0, 0)
    except:
        return False, 0, (0, 0)


# ═══ Safebooru 爬取 ═══
FEET_QUERIES = [
    ("foot_focus 1girl", "foot_focus", "足特写"),
    ("feet 1girl", "feet", "玉足"),
    ("barefoot 1girl", "barefoot", "裸足"),
    ("soles 1girl", "soles", "足底"),
    ("toes 1girl", "toes", "脚趾"),
    ("stockings 1girl", "stockings", "丝袜"),
    ("thighhighs 1girl", "thighhighs", "过膝袜"),
    ("pantyhose 1girl", "pantyhose", "连裤袜"),
    ("bare_legs 1girl", "bare_legs", "裸腿"),
    ("legs 1girl", "legs", "美腿"),
    ("black_thighhighs 1girl", "black_thighhighs", "黑丝"),
    ("white_thighhighs 1girl", "white_thighhighs", "白丝"),
    ("kneesocks 1girl", "kneesocks", "膝袜"),
    ("striped_thighhighs 1girl", "striped_thighhighs", "条纹袜"),
    ("anklet 1girl", "anklet", "脚踝饰"),
    ("high_heels 1girl", "high_heels", "高跟"),
    ("garter_belt 1girl", "garter_belt", "吊袜带"),
    ("thigh_boots 1girl", "thigh_boots", "过膝靴"),
    ("fishnets 1girl", "fishnets", "渔网袜"),
    ("white_pantyhose 1girl", "white_pantyhose", "白连裤袜"),
    ("black_pantyhose 1girl", "black_pantyhose", "黑连裤袜"),
    ("crossed_legs 1girl", "crossed_legs", "交叠腿"),
    ("between_thighs 1girl", "between_thighs", "腿间"),
]
OTHER_QUERIES = [
    ("nahida_(genshin_impact)", "genshin_impact", "原神"),
    ("furina_(genshin_impact)", "genshin_impact", "原神"),
    ("raiden_shogun_(genshin_impact)", "genshin_impact", "原神"),
    ("yae_miko_(genshin_impact)", "genshin_impact", "原神"),
    ("kamisato_ayaka_(genshin_impact)", "genshin_impact", "原神"),
    ("hu_tao_(genshin_impact)", "genshin_impact", "原神"),
    ("ganyu_(genshin_impact)", "genshin_impact", "原神"),
    ("nilou_(genshin_impact)", "genshin_impact", "原神"),
    ("eula_(genshin_impact)", "genshin_impact", "原神"),
    ("shenhe_(genshin_impact)", "genshin_impact", "原神"),
    ("mona_(genshin_impact)", "genshin_impact", "原神"),
    ("kafka_(honkai:_star_rail)", "honkai:_star_rail", "崩铁"),
    ("firefly_(honkai:_star_rail)", "honkai:_star_rail", "崩铁"),
    ("black_swan_(honkai:_star_rail)", "honkai:_star_rail", "崩铁"),
    ("ruan_mei_(honkai:_star_rail)", "honkai:_star_rail", "崩铁"),
    ("sparkle_(honkai:_star_rail)", "honkai:_star_rail", "崩铁"),
    ("jingliu_(honkai:_star_rail)", "honkai:_star_rail", "崩铁"),
    ("himeko_(honkai:_star_rail)", "honkai:_star_rail", "崩铁"),
    ("seele_(honkai:_star_rail)", "honkai:_star_rail", "崩铁"),
    ("skadi_(arknights)", "arknights", "方舟"),
    ("texas_(arknights)", "arknights", "方舟"),
    ("exusiai_(arknights)", "arknights", "方舟"),
    ("lappland_(arknights)", "arknights", "方舟"),
    ("surtr_(arknights)", "arknights", "方舟"),
    ("amiya_(arknights)", "arknights", "方舟"),
    ("shiroko_(blue_archive)", "blue_archive", "蔚蓝档案"),
    ("hoshino_(blue_archive)", "blue_archive", "蔚蓝档案"),
    ("alice_(blue_archive)", "blue_archive", "蔚蓝档案"),
    ("mika_(blue_archive)", "blue_archive", "蔚蓝档案"),
    ("ellen_joe_(zenless_zone_zero)", "zenless_zone_zero", "绝区零"),
    ("zhu_yuan_(zenless_zone_zero)", "zenless_zone_zero", "绝区零"),
    ("jane_doe_(zenless_zone_zero)", "zenless_zone_zero", "绝区零"),
    ("miyabi_(zenless_zone_zero)", "zenless_zone_zero", "绝区零"),
]


def fetch_safebooru(tag_query, pid):
    """通用 Safebooru API 调用"""
    url = "https://safebooru.org/index.php"
    params = {
        "page": "dapi", "s": "post", "q": "index",
        "json": "1", "tags": tag_query,
        "limit": str(PAGE_SIZE), "pid": str(pid),
    }
    try:
        resp = requests.get(url, params=params, timeout=20,
            headers={"User-Agent": get_ua(), "Referer": "https://safebooru.org/"})
        if resp.status_code != 200:
            return []
        return json.loads(resp.text) or []
    except:
        return []


def crawl_feet(seen, need):
    """爬取足社候选"""
    results = []
    for tq, tk, kw in FEET_QUERIES:
        if len(results) >= need * 2:
            break
        for pid in range(0, 15):
            if len(results) >= need * 2:
                break
            posts = fetch_safebooru(tq, pid)
            if not posts:
                break
            for p in posts:
                w, h = p.get("width", 0), p.get("height", 0)
                if w < MIN_WIDTH or h < MIN_HEIGHT:
                    continue
                furl = p.get("file_url", "") or p.get("sample_url", "")
                if not furl:
                    continue
                uh = hashlib.md5(furl.encode()).hexdigest()[:6]
                if uh in seen:
                    continue
                ts = p.get("tags", "")
                tl = ts.split()
                if any(t in MALE_BLOCKS for t in tl):
                    continue
                if any(t in SKIP_TAGS for t in tl):
                    continue
                if has_nsfw(ts):
                    continue
                cn, gn = extract_character_cn(ts)
                ft = extract_feet_tags_cn(ts) or [kw]
                results.append({
                    "url": furl, "url_hash": uh,
                    "referer": "https://safebooru.org/",
                    "source": "Safebooru",
                    "char_name": cn, "game_cn": gn,
                    "keyword": kw, "feet_tags": ft,
                    "width": w, "height": h,
                })
                seen.add(uh)
            log(f"  足社[{tk}] pid={pid}: {len(posts)}post, 累计{len(results)}")
            random_delay()
    return results


def crawl_other(seen, need):
    """爬取其他分类候选"""
    results = []
    for tq, gk, gn in OTHER_QUERIES:
        if len(results) >= need * 2:
            break
        for pid in range(0, 8):
            if len(results) >= need * 2:
                break
            posts = fetch_safebooru(tq, pid)
            if not posts:
                break
            for p in posts:
                w, h = p.get("width", 0), p.get("height", 0)
                if w < MIN_WIDTH or h < MIN_HEIGHT:
                    continue
                furl = p.get("file_url", "") or p.get("sample_url", "")
                if not furl:
                    continue
                uh = hashlib.md5(furl.encode()).hexdigest()[:6]
                if uh in seen:
                    continue
                ts = p.get("tags", "")
                tl = ts.split()
                if any(t in MALE_BLOCKS for t in tl):
                    continue
                if any(t in SKIP_TAGS for t in tl):
                    continue
                if has_nsfw(ts):
                    continue
                cn, game_cn = extract_character_cn(ts)
                game_cn = game_cn or gn
                ft = extract_feet_tags_cn(ts)
                results.append({
                    "url": furl, "url_hash": uh,
                    "referer": "https://safebooru.org/",
                    "source": "Safebooru",
                    "char_name": cn, "game_cn": game_cn,
                    "keyword": gn, "feet_tags": ft,
                    "width": w, "height": h,
                })
                seen.add(uh)
            log(f"  其他[{gk}] pid={pid}: {len(posts)}post, 累计{len(results)}")
            random_delay()
    return results


# ═══ 去重 ═══
def load_existing_hashes():
    seen = set()
    if os.path.exists(DOWNLOAD_DIR):
        for f in os.listdir(DOWNLOAD_DIR):
            if f.startswith("feet_") and f.endswith(".jpg"):
                parts = f.replace(".jpg", "").split("_")
                if len(parts) >= 2:
                    seen.add(parts[-1])
    return seen

def load_url_hashes():
    seen = set()
    lf = os.path.join(DOWNLOAD_DIR, ".crawl_feet_urls.txt")
    if os.path.exists(lf):
        with open(lf, "r", encoding="utf-8") as f:
            for line in f:
                l = line.strip()
                if l:
                    seen.add(l)
    return seen

def save_url_hash(uh):
    lf = os.path.join(DOWNLOAD_DIR, ".crawl_feet_urls.txt")
    with open(lf, "a", encoding="utf-8") as f:
        f.write(uh + "\n")


# ═══ data.js 读写 ═══
def read_data_js():
    if not os.path.exists(DATA_JS_PATH):
        return []
    try:
        with open(DATA_JS_PATH, "r", encoding="utf-8") as f:
            c = f.read()
        m = re.search(r'export const wallpaperData = (\[.*\]);', c, re.DOTALL)
        if m:
            return json.loads(m.group(1))
    except Exception as e:
        log(f"读取 data.js 失败: {e}")
    return []

def read_games_js():
    if os.path.exists(DATA_JS_PATH):
        try:
            with open(DATA_JS_PATH, "r", encoding="utf-8") as f:
                c = f.read()
            m = re.search(r'export const GAMES = (\[.*?\]);', c, re.DOTALL)
            if m:
                return json.loads(m.group(1))
        except:
            pass
    return []

def write_data_js(items, games_list):
    gids = set(g.get("id", "") for g in games_list)
    if "足社" not in gids:
        games_list.append({"id": "足社", "name": "足社"})
    with open(DATA_JS_PATH, "w", encoding="utf-8") as f:
        f.write("// 自动生成：多源爬虫（米游社 + B站 + 百度图 + 官方 + 足社爬虫v2）\n\n")
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


# ═══ 下载处理 ═══
def download_one(cand, seen):
    url = cand["url"]
    uh = cand["url_hash"]
    if uh in seen:
        return False, None
    result = download_image(url, referer=cand.get("referer", ""))
    if result is None:
        return False, None
    data, w, h = result
    if w > 0 and h > 0 and h < MIN_HEIGHT and w < MIN_HEIGHT:
        return False, None
    fn = f"feet_{uh}.jpg"
    ok, sz, (sw, sh) = save_image(data, fn)
    if not ok:
        return False, None
    seen.add(uh)
    save_url_hash(uh)
    return True, {"filename": fn, "size": sz, "width": sw or w, "height": sh or h, "candidate": cand}


def process_batch(candidates, seen, max_count):
    new_items = []
    fetched = 0
    failed = 0
    seen_local = set(seen)
    # 优先竖图
    candidates.sort(key=lambda c: 0 if c["height"] > c["width"] else 1)
    bs = MAX_CONCURRENT * 3
    for start in range(0, len(candidates), bs):
        if fetched >= max_count:
            break
        batch = candidates[start:start + bs]
        with ThreadPoolExecutor(max_workers=MAX_CONCURRENT) as ex:
            futures = {ex.submit(download_one, c, seen_local): c for c in batch}
            for f in as_completed(futures):
                if fetched >= max_count:
                    break
                try:
                    ok, res = f.result()
                    if not ok or res is None:
                        failed += 1
                        continue
                    cand = res["candidate"]
                    cn = cand["char_name"]
                    ft = cand.get("feet_tags", [cand["keyword"]])
                    kw = cand["keyword"]
                    main_tag = ft[0] if ft else kw
                    title = f"{cn}·{main_tag}"
                    if len(title) > 40:
                        title = title[:40]
                    tags = [cn]
                    for t in ft[:3]:
                        if t and t not in tags:
                            tags.append(t)
                    # 决定game
                    is_feet = any(t in FEET_TAG_CN for t in cand.get("feet_tags_raw", [])) or cand.get("keyword", "") in [v for v in FEET_TAG_CN.values()]
                    # feet_开头的文件一定是足社
                    cat = cand.get("category", "feet")
                    game = "足社" if cat == "feet" else (cand.get("game_cn") or kw)

                    item = {
                        "title": title,
                        "characterName": cn,
                        "game": game,
                        "source": cand["source"],
                        "imageFile": res["filename"],
                        "tags": tags[:6],
                    }
                    new_items.append(item)
                    fetched += 1
                    log(f"    ✓ {title} ({res['size']//1024}KB) [{game}] [+{fetched}]")
                except:
                    failed += 1
    seen.update(seen_local)
    log(f"  下载: 成功={fetched}, 失败={failed}")
    return new_items


# ═══ 主流程 ═══
def main():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    seen_hashes = load_existing_hashes()
    url_seen = load_url_hashes()
    all_seen = seen_hashes | url_seen

    existing = read_data_js()
    games_list = read_games_js()

    # 修复现有数据
    fixed_existing = []
    for item in existing:
        # 问题2: feet_图片必须归入足社
        if item.get("imageFile", "").startswith("feet_"):
            item["game"] = "足社"
        # 问题1: 英文角色名→中文
        if item.get("game") == "足社":
            cn = item.get("characterName", "")
            if cn and not any('\u4e00' <= c <= '\u9fff' for c in cn):
                item["characterName"] = "美少女"
                old = item.get("title", "")
                if "·" in old:
                    item["title"] = f"美少女·{old.split('·')[-1]}"
                else:
                    item["title"] = "美少女·精选"
        fixed_existing.append(item)

    # 分类统计
    old_feet = [x for x in fixed_existing if x.get("game") == "足社"]
    old_feet_files = set(x.get("imageFile", "") for x in old_feet if x.get("imageFile", "").startswith("feet_"))
    old_other = [x for x in fixed_existing if x.get("game") != "足社"]

    need_feet = max(0, TARGET_FEET - len(old_feet_files))
    need_other = max(0, TARGET_OTHER - len(old_other))

    log(f"=== 足社爬虫v2 ===")
    log(f"  现有: 总{len(fixed_existing)}, 足社{len(old_feet)}, 其他{len(old_other)}")
    log(f"  目标: 足社+{need_feet}, 其他+{need_other}")

    # 阶段1: 收集足社候选
    log("── 收集足社候选 ──")
    feet_cands = crawl_feet(all_seen, need_feet)
    log(f"  足社候选: {len(feet_cands)}")

    # 阶段2: 收集其他候选
    other_cands = []
    if need_other > 0:
        log("── 收集其他分类候选 ──")
        other_cands = crawl_other(all_seen, need_other)
        log(f"  其他候选: {len(other_cands)}")

    # 给候选打category标记
    for c in feet_cands:
        c["category"] = "feet"
    for c in other_cands:
        c["category"] = "other"

    # 阶段3: 下载足社
    new_feet = []
    if feet_cands and need_feet > 0:
        log("── 下载足社图片 ──")
        new_feet = process_batch(feet_cands, all_seen, need_feet)

    # 阶段4: 下载其他
    new_other = []
    if other_cands and need_other > 0:
        log("── 下载其他分类图片 ──")
        new_other = process_batch(other_cands, all_seen, need_other)

    # 强制所有feet_文件的条目game="足社"
    for item in new_feet:
        item["game"] = "足社"

    # 阶段5: 重建data.js
    log("── 重建 data.js ──")
    # 合并: 旧(非足社) + 旧足社(修复后) + 新足社 + 新其他
    all_items = old_other + old_feet + new_other + new_feet

    # ID重新编号 + 确保字段完整
    for i, item in enumerate(all_items):
        item["id"] = i + 1
        item.setdefault("gender", "女")
        item.setdefault("style", "二次元")
        item.setdefault("tags", [])
        item.setdefault("likes", 0)
        item.setdefault("rarity", "SSR")
        item.setdefault("nsfw", False)
        # 最终安全检查: feet_文件→足社
        if item.get("imageFile", "").startswith("feet_"):
            item["game"] = "足社"

    write_data_js(all_items, games_list)

    # 统计
    gc = {}
    for x in all_items:
        g = x.get("game", "?")
        gc[g] = gc.get(g, 0) + 1
    feet_items = [x for x in all_items if x.get("game") == "足社"]
    feet_chars = sorted(set(x.get("characterName", "") for x in feet_items))

    log(f"\n{'='*50}")
    log(f"=== 最终统计 ===")
    log(f"  总条目: {len(all_items)}")
    log(f"  足社: {len(feet_items)}, 其他: {len(all_items) - len(feet_items)}")
    log(f"  分游戏: {gc}")
    log(f"  足社角色({len(feet_chars)}): {', '.join(feet_chars[:30])}")
    log(f"  新增足社: {len(new_feet)}, 新增其他: {len(new_other)}")
    img_count = len([f for f in os.listdir(DOWNLOAD_DIR) if f.startswith("feet_") and f.endswith(".jpg")])
    log(f"  图片目录feet_*.jpg: {img_count}")
    log(f"=== 完成 ===")


if __name__ == "__main__":
    main()
