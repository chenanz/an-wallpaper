export const GAMES_R18 = [
  { id: "原神", name: "原神" },
  { id: "崩坏：星穹铁道", name: "崩坏：星穹铁道" },
  { id: "明日方舟", name: "明日方舟" },
  { id: "碧蓝航线", name: "碧蓝航线" },
  { id: "绝区零", name: "绝区零" },
  { id: "蔚蓝档案", name: "蔚蓝档案" },
];

export const STYLES_R18 = ["3D渲染", "2.5D", "动漫插画", "Live2D"];

export const wallpaperDataR18 = [
  {
    id: "r18_1",
    title: "示例 R18 壁纸 - 1",
    characterName: "示例角色",
    game: "原神",
    gender: "女",
    style: "动漫插画",
    tags: ["R18", "示例"],
    likes: 0,
    rarity: "SSR",
    source: "限定",
    nsfw: true,
    imageFile: "r18_1.jpg"
  },
  {
    id: "r18_2",
    title: "示例 R18 壁纸 - 2",
    characterName: "示例角色",
    game: "崩坏：星穹铁道",
    gender: "女",
    style: "3D渲染",
    tags: ["R18", "示例"],
    likes: 0,
    rarity: "SSR",
    source: "限定",
    nsfw: true,
    imageFile: "r18_2.jpg"
  },
  {
    id: "r18_3",
    title: "示例 R18 壁纸 - 3",
    characterName: "示例角色",
    game: "明日方舟",
    gender: "女",
    style: "动漫插画",
    tags: ["R18", "示例"],
    likes: 0,
    rarity: "SSR",
    source: "限定",
    nsfw: true,
    imageFile: "r18_3.jpg"
  }
];

export function getFallbackImageUrl(id, w = 400, h = 712) {
  return `https://picsum.photos/seed/an_${id}/${w}/${h}`;
}
