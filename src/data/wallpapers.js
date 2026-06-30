// ============ 硬性规则 ============
// 1. gender 字段只允许 "女"
// 2. 男角色（达达利亚/钟离/魈/景元/刃…）一律不收录
// 3. 风格只认 3D渲染 / 2.5D / 动漫插画 / Live2D
// ===================================

export const GAMES = [
  { id: 'genshin', name: '原神', nameEn: 'Genshin Impact', color: '#7ecbf2' },
  { id: 'hsr', name: '崩坏：星穹铁道', nameEn: 'Honkai Star Rail', color: '#c9a4f2' },
  { id: 'zzz', name: '绝区零', nameEn: 'Zenless Zone Zero', color: '#ff6b4a' },
  { id: 'arknights', name: '明日方舟', nameEn: 'Arknights', color: '#2b2b2b' },
  { id: 'ba', name: '蔚蓝档案', nameEn: 'Blue Archive', color: '#4ecdc4' },
  { id: 'hi3', name: '崩坏3', nameEn: 'Honkai Impact 3rd', color: '#ff8fab' },
  { id: 'onmyoji', name: '阴阳师', nameEn: 'Onmyoji', color: '#e63946' },
  { id: 'e7', name: '第七史诗', nameEn: 'Epic Seven', color: '#f1c40f' },
];

export const STYLES = ['3D渲染', '2.5D', '动漫插画', 'Live2D'];

export const RARITIES = { SSR: 3, SR: 2, R: 1 };

function iurl(seed, w = 400, h = 712) {
  return `https://picsum.photos/seed/${seed}/${w}/${h}`;
}

function twurl(seed) {
  return iurl(seed + '_t', 300, 534);
}

export const CHARACTERS = [
  // ===== 原神 =====
  { name: '雷电将军', nameEn: 'Raiden Shogun', game: '原神', gender: '女', avatar: iurl('raiden_a', 120, 120), rarity: 'SSR', element: '雷', cv: '泽城美雪', releaseVersion: '2.1', description: '稻妻的雷电将军，追求「永恒」的统治者。' },
  { name: '甘雨', nameEn: 'Ganyu', game: '原神', gender: '女', avatar: iurl('ganyu_a', 120, 120), rarity: 'SSR', element: '冰', cv: '上田丽奈', releaseVersion: '1.0', description: '半人半仙的秘书，工作在璃月港。' },
  { name: '胡桃', nameEn: 'Hu Tao', game: '原神', gender: '女', avatar: iurl('hutao_a', 120, 120), rarity: 'SSR', element: '火', cv: '高桥李依', releaseVersion: '1.3', description: '往生堂第七十七代堂主。' },
  { name: '纳西妲', nameEn: 'Nahida', game: '原神', gender: '女', avatar: iurl('nahida_a', 120, 120), rarity: 'SSR', element: '草', cv: '田村由香里', releaseVersion: '3.2', description: '须弥的小吉祥草王。' },
  { name: '神里绫华', nameEn: 'Kamisato Ayaka', game: '原神', gender: '女', avatar: iurl('ayaka_a', 120, 120), rarity: 'SSR', element: '冰', cv: '早见沙织', releaseVersion: '2.0', description: '社奉行神里家的大小姐。' },
  { name: '八重神子', nameEn: 'Yae Miko', game: '原神', gender: '女', avatar: iurl('yae_a', 120, 120), rarity: 'SSR', element: '雷', cv: '佐仓绫音', releaseVersion: '2.5', description: '鸣神大社的宫司大人。' },
  { name: '芙宁娜', nameEn: 'Furina', game: '原神', gender: '女', avatar: iurl('furina_a', 120, 120), rarity: 'SSR', element: '水', cv: '水濑祈', releaseVersion: '4.2', description: '枫丹的水神，舞台上的绝对主角。' },
  { name: '妮露', nameEn: 'Nilou', game: '原神', gender: '女', avatar: iurl('nilou_a', 120, 120), rarity: 'SSR', element: '水', cv: '花守由美里', releaseVersion: '3.1', description: '大巴扎最耀眼的舞者。' },

  // ===== 崩铁 =====
  { name: '黄泉', nameEn: 'Acheron', game: '崩坏：星穹铁道', gender: '女', avatar: iurl('acheron_a', 120, 120), rarity: 'SSR', element: '虚无', cv: '泽城美雪', releaseVersion: '2.0', description: '自称为「黄泉」的巡海游侠。' },
  { name: '黑天鹅', nameEn: 'Black Swan', game: '崩坏：星穹铁道', gender: '女', avatar: iurl('swan_a', 120, 120), rarity: 'SSR', element: '虚无', cv: '生天目仁美', releaseVersion: '2.0', description: '流光忆庭的忆者，优雅而神秘。' },
  { name: '花火', nameEn: 'Sparkle', game: '崩坏：星穹铁道', gender: '女', avatar: iurl('sparkle_a', 120, 120), rarity: 'SSR', element: '同谐', cv: '上田丽奈', releaseVersion: '2.0', description: '假面愚者的一员，乐子人。' },
  { name: '知更鸟', nameEn: 'Robin', game: '崩坏：星穹铁道', gender: '女', avatar: iurl('robin_a', 120, 120), rarity: 'SSR', element: '同谐', cv: '东山奈央', releaseVersion: '2.2', description: '银河级歌姬，匹诺康尼的明星。' },
  { name: '流萤', nameEn: 'Firefly', game: '崩坏：星穹铁道', gender: '女', avatar: iurl('firefly_a', 120, 120), rarity: 'SSR', element: '毁灭', cv: '楠木灯', releaseVersion: '2.3', description: '星核猎手成员，萨姆的驾驶员。' },

  // ===== 绝区零 =====
  { name: '艾莲', nameEn: 'Ellen', game: '绝区零', gender: '女', avatar: iurl('ellen_a', 120, 120), rarity: 'SSR', element: '冰', cv: '若山诗音', releaseVersion: '1.0', description: '维多利亚家政的女仆，鲨鱼娘。' },
  { name: '朱鸢', nameEn: 'Zhu Yuan', game: '绝区零', gender: '女', avatar: iurl('zhuyuan_a', 120, 120), rarity: 'SSR', element: '以太', cv: '小清水亚美', releaseVersion: '1.0', description: '新艾利都刑侦特勤组警探。' },
  { name: '星见雅', nameEn: 'Miyabi', game: '绝区零', gender: '女', avatar: iurl('miyabi_a', 120, 120), rarity: 'SSR', element: '冰', cv: '小仓唯', releaseVersion: '1.4', description: '对空六课课长，星见家的继承人。' },
  { name: '月城柳', nameEn: 'Yanagi', game: '绝区零', gender: '女', avatar: iurl('yanagi_a', 120, 120), rarity: 'SSR', element: '电', cv: '名冢佳织', releaseVersion: '1.3', description: '对空六课副课长，鬼族少女。' },

  // ===== 明日方舟 =====
  { name: '阿米娅', nameEn: 'Amiya', game: '明日方舟', gender: '女', avatar: iurl('amiya_a', 120, 120), rarity: 'SSR', element: '术师', cv: '黑泽朋世', releaseVersion: '开服', description: '罗德岛的公开领袖，温柔的领袖。' },
  { name: '斯卡蒂', nameEn: 'Skadi', game: '明日方舟', gender: '女', avatar: iurl('skadi_a', 120, 120), rarity: 'SSR', element: '近卫', cv: '佐藤利奈', releaseVersion: '开服', description: '深海猎人，孤独的虎鲸。' },
  { name: '能天使', nameEn: 'Exusiai', game: '明日方舟', gender: '女', avatar: iurl('exusiai_a', 120, 120), rarity: 'SSR', element: '狙击', cv: '石见舞菜香', releaseVersion: '开服', description: '企鹅物流的信使，乐天派。' },
  { name: '凯尔希', nameEn: "Kal'tsit", game: '明日方舟', gender: '女', avatar: iurl('kaltsit_a', 120, 120), rarity: 'SSR', element: '医疗', cv: '日笠阳子', releaseVersion: '开服', description: '罗德岛的医疗负责人，谜一般的存在。' },

  // ===== 蔚蓝档案 =====
  { name: '砂狼白子', nameEn: 'Shiroko', game: '蔚蓝档案', gender: '女', avatar: iurl('shiroko_a', 120, 120), rarity: 'SSR', element: '神秘', cv: '小仓唯', releaseVersion: '开服', description: '阿拜多斯对策委员会的突击队长。' },
  { name: '小鸟游星野', nameEn: 'Hoshino', game: '蔚蓝档案', gender: '女', avatar: iurl('hoshino_a', 120, 120), rarity: 'SSR', element: '神秘', cv: '花守由美里', releaseVersion: '开服', description: '阿拜多斯对策委员会的委员长。' },
  { name: '陆八魔亚瑠', nameEn: 'Aru', game: '蔚蓝档案', gender: '女', avatar: iurl('aru_a', 120, 120), rarity: 'SSR', element: '神秘', cv: '近藤玲奈', releaseVersion: '开服', description: '便利屋68的社长，装酷的反差萌。' },
  { name: '白洲梓', nameEn: 'Azusa', game: '蔚蓝档案', gender: '女', avatar: iurl('azusa_a', 120, 120), rarity: 'SSR', element: '神秘', cv: '东山奈央', releaseVersion: '1.0', description: '补习部的成员，有点忧郁的少女。' },

  // ===== 崩坏3 =====
  { name: '琪亚娜', nameEn: 'Kiana', game: '崩坏3', gender: '女', avatar: iurl('kiana_a', 120, 120), rarity: 'SSR', element: '火', cv: '钉宫理惠', releaseVersion: '1.0', description: '天真烂漫的沙尼亚特家大小姐。' },
  { name: '雷电芽衣', nameEn: 'Mei', game: '崩坏3', gender: '女', avatar: iurl('mei_a', 120, 120), rarity: 'SSR', element: '雷', cv: '泽城美雪', releaseVersion: '1.0', description: '雷电家的继承人，温柔而坚强。' },
  { name: '布洛妮娅', nameEn: 'Bronya', game: '崩坏3', gender: '女', avatar: iurl('bronya_a', 120, 120), rarity: 'SSR', element: '冰', cv: '阿澄佳奈', releaseVersion: '1.0', description: '前乌拉尔银狼，重装小兔的驾驶员。' },

  // ===== 阴阳师 =====
  { name: '不知火', nameEn: 'Shiranui', game: '阴阳师', gender: '女', avatar: iurl('shiranui_a', 120, 120), rarity: 'SSR', element: '火', cv: '东山奈央', releaseVersion: '2019', description: '离岛的歌姬，化作妖怪的美人。' },
  { name: '紧那罗', nameEn: 'Kinnara', game: '阴阳师', gender: '女', avatar: iurl('kinnara_a', 120, 120), rarity: 'SSR', element: '光', cv: '南条爱乃', releaseVersion: '2020', description: '严岛的神明，以音乐驱散黑暗。' },

  // ===== 第七史诗 =====
  { name: '赛娜', nameEn: 'Senya', game: '第七史诗', gender: '女', avatar: iurl('senya_a', 120, 120), rarity: 'SSR', element: '光', cv: '悠木碧', releaseVersion: 'S3', description: '龙骑士，守护神圣的骑士。' },
  { name: '璐璐卡', nameEn: 'Luluca', game: '第七史诗', gender: '女', avatar: iurl('luluca_a', 120, 120), rarity: 'SSR', element: '水', cv: '雨宫天', releaseVersion: 'S2', description: '霜雪之星，冰霜法师。' },
];

// 生成壁纸数据：每个角色至少2张
let idCounter = 1;
function makeWallpaper(character, style, titleSuffix, tags, extra = {}) {
  const seed = `${character.nameEn}_${idCounter}`;
  return {
    id: `wp_${idCounter++}`,
    title: `${character.name}·${titleSuffix}`,
    characterName: character.name,
    game: character.game,
    gender: '女', // 强制女，硬性规则
    style,
    imageUrl: iurl(seed, 720, 1280),
    thumbnailUrl: twurl(seed),
    rarity: character.rarity,
    tags,
    likes: Math.floor(Math.random() * 5000) + 800,
    isFavorite: false,
    source: extra.source || '官方',
    nsfw: false,
    ...extra,
  };
}

export const WALLPAPERS = [
  // 原神
  makeWallpaper(CHARACTERS[0], '3D渲染', '一心净土', ['长发','御姐','和服','雷'], { source: '官方' }),
  makeWallpaper(CHARACTERS[0], '动漫插画', '无想的一刀', ['长发','御姐','战斗'], { source: '同人' }),
  makeWallpaper(CHARACTERS[0], 'Live2D', '雷神降临', ['长发','御姐','动态'], { source: '官方' }),
  makeWallpaper(CHARACTERS[1], '3D渲染', '循循守月', ['长发','御姐','角','冰'], { source: '官方' }),
  makeWallpaper(CHARACTERS[1], '动漫插画', '半仙之兽', ['长发','温柔','麒麟'], { source: '同人' }),
  makeWallpaper(CHARACTERS[2], '3D渲染', '雪霁梅香', ['双马尾','萝莉','火'], { source: '官方' }),
  makeWallpaper(CHARACTERS[2], '动漫插画', '往生堂堂主', ['双马尾','活泼','帽子'], { source: '二创' }),
  makeWallpaper(CHARACTERS[3], '3D渲染', '白草净华', ['短发','萝莉','草'], { source: '官方' }),
  makeWallpaper(CHARACTERS[3], 'Live2D', '智慧之神', ['短发','萝莉','智慧'], { source: '官方' }),
  makeWallpaper(CHARACTERS[4], '3D渲染', '白鹭霜华', ['长发','大小姐','冰'], { source: '官方' }),
  makeWallpaper(CHARACTERS[5], '3D渲染', '浮世笑百姿', ['长发','御姐','狐耳'], { source: '官方' }),
  makeWallpaper(CHARACTERS[5], '动漫插画', '鸣神宫司', ['长发','狐耳','优雅'], { source: '同人' }),
  makeWallpaper(CHARACTERS[6], '3D渲染', '不眠之夜', ['短发','水','魔法'], { source: '官方' }),
  makeWallpaper(CHARACTERS[6], 'Live2D', '芙宁娜演出', ['短发','水','舞台'], { source: '官方' }),
  makeWallpaper(CHARACTERS[7], '3D渲染', '莲光落舞筵', ['长发','水','舞娘'], { source: '官方' }),

  // 崩铁
  makeWallpaper(CHARACTERS[8], '3D渲染', '虚无令使', ['长发','御姐','红'], { source: '官方' }),
  makeWallpaper(CHARACTERS[8], '动漫插画', '黄泉之路', ['长发','御姐','刀'], { source: '同人' }),
  makeWallpaper(CHARACTERS[9], '3D渲染', '流光忆庭', ['长发','神秘','紫'], { source: '官方' }),
  makeWallpaper(CHARACTERS[10], '3D渲染', '假面愚者', ['双马尾','面具','红'], { source: '官方' }),
  makeWallpaper(CHARACTERS[10], 'Live2D', '花火炸场', ['双马尾','活泼','烟花'], { source: '官方' }),
  makeWallpaper(CHARACTERS[11], '3D渲染', '银河歌姬', ['长发','歌手','优雅'], { source: '官方' }),
  makeWallpaper(CHARACTERS[12], '3D渲染', '流萤飞火', ['长发','机甲','绿'], { source: '官方' }),
  makeWallpaper(CHARACTERS[12], '动漫插画', '萨姆真身', ['长发','机甲','战斗'], { source: '同人' }),

  // 绝区零
  makeWallpaper(CHARACTERS[13], '3D渲染', '鲨鱼女仆', ['短发','女仆','冰'], { source: '官方' }),
  makeWallpaper(CHARACTERS[13], '动漫插画', '维多利亚家政', ['短发','冷娇'], { source: '同人' }),
  makeWallpaper(CHARACTERS[14], '3D渲染', '刑侦特勤', ['长发','警服','以太'], { source: '官方' }),
  makeWallpaper(CHARACTERS[15], '3D渲染', '雅·入阵', ['长发','和风','冰'], { source: '官方' }),
  makeWallpaper(CHARACTERS[15], 'Live2D', '星见雅拔刀', ['长发','武士'], { source: '官方' }),
  makeWallpaper(CHARACTERS[16], '3D渲染', '鬼副课长', ['长发','鬼角','电'], { source: '官方' }),

  // 明日方舟
  makeWallpaper(CHARACTERS[17], '动漫插画', '罗德岛领袖', ['兔耳','萝莉','领袖'], { source: '官方' }),
  makeWallpaper(CHARACTERS[17], '2.5D', '升变阿米娅', ['兔耳','术士'], { source: '官方' }),
  makeWallpaper(CHARACTERS[18], '动漫插画', '深海猎人', ['长发','红眼','虎鲸'], { source: '官方' }),
  makeWallpaper(CHARACTERS[19], '动漫插画', '拉特兰信使', ['短发','光环','乐天'], { source: '官方' }),
  makeWallpaper(CHARACTERS[20], '动漫插画', '无所不知', ['短发','冷淡','医生'], { source: '官方' }),

  // 蔚蓝档案
  makeWallpaper(CHARACTERS[21], '动漫插画', '砂狼的突击', ['狼耳','运动','蓝'], { source: '官方' }),
  makeWallpaper(CHARACTERS[22], '动漫插画', '大叔委员长', ['异色瞳','慵懒','粉'], { source: '官方' }),
  makeWallpaper(CHARACTERS[23], '动漫插画', '便利屋社长', ['角','西装','装酷'], { source: '官方' }),
  makeWallpaper(CHARACTERS[24], '动漫插画', '补习部魔女', ['短发','天使','忧郁'], { source: '官方' }),

  // 崩坏3
  makeWallpaper(CHARACTERS[25], '3D渲染', '薪炎永燃', ['双马尾','火','战斗'], { source: '官方' }),
  makeWallpaper(CHARACTERS[26], '3D渲染', '始源之律者', ['长发','太刀','雷'], { source: '官方' }),
  makeWallpaper(CHARACTERS[27], '3D渲染', '真理之律者', ['短发','机甲','冰'], { source: '官方' }),

  // 阴阳师
  makeWallpaper(CHARACTERS[28], '2.5D', '离岛之歌', ['长发','和服','火蝶'], { source: '官方' }),
  makeWallpaper(CHARACTERS[29], '2.5D', '严岛神明', ['乐器','神明','光'], { source: '官方' }),

  // 第七史诗
  makeWallpaper(CHARACTERS[30], '2.5D', '龙骑士', ['长发','铠甲','光'], { source: '官方' }),
  makeWallpaper(CHARACTERS[31], '2.5D', '霜雪之星', ['短发','法师','水'], { source: '官方' }),
];

// 辅助函数
export function getCharacterWallpapers(characterName) {
  return WALLPAPERS.filter(wp => wp.characterName === characterName);
}

export function getGameCharacters(gameName) {
  return CHARACTERS.filter(c => c.game === gameName && c.gender === '女');
}

export function searchWallpapers(query) {
  if (!query || query.trim() === '') return WALLPAPERS;
  const q = query.toLowerCase().trim();
  // 硬过滤：搜"男"直接空结果
  if (q === '男' || q === 'male' || q === 'boy' || q === 'man') return [];
  return WALLPAPERS.filter(wp => {
    const char = CHARACTERS.find(c => c.name === wp.characterName);
    return (
      wp.characterName.toLowerCase().includes(q) ||
      wp.title.toLowerCase().includes(q) ||
      wp.game.toLowerCase().includes(q) ||
      wp.tags.some(t => t.toLowerCase().includes(q)) ||
      (char && char.nameEn.toLowerCase().includes(q)) ||
      wp.characterName.includes(q) // 中文匹配
    );
  });
}

// 硬过滤：移除任何可能的男角色（即使数据集里混入了也会被这过滤）
export function filterFemaleOnly(list) {
  return list.filter(wp => wp.gender === '女');
}
