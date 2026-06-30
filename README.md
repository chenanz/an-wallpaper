# 安 — 二游少女壁纸馆

> 只收录二次元手游女角色壁纸，男角色一律过滤。大陆直连，无需梯子。

---

## 📱 两种使用方式

### 方式 A：局域网手机浏览（最快，5 秒搞定）

电脑上运行：

```bash
cd "你的路径/an-app"
npm install
npm run dev
```

然后手机浏览器访问：
- `http://<电脑局域网IP>:5173`

> 获取电脑 IP：`ipconfig`（Windows）或 `ifconfig`（Mac/Linux）

同 WiFi 下直接打开，无需任何安装。

---

### 方式 B：打包成 Android APK（Native 体验）

需要：
- Android Studio（官网下载）
- JDK 17（Android Studio 自带）
- 手机开 USB 调试

**Windows 一键脚本：**

```bash
build-apk.bat
```

**Mac/Linux 一键脚本：**

```bash
bash build-apk.sh
```

脚本会自动：
1. 跑米游社爬虫（下拉壁纸）
2. 构建前端
3. 同步到 Android 工程
4. 编译 APK

编译完成后：
```bash
adb install android/app/build/outputs/apk/debug/app-debug.apk
```

手机上出现 App 图标「安」，点开即用。

---

## 🕷 壁纸爬虫（不挂梯子）

### 米游社版（推荐，大陆直接跑）

```bash
pip install -r requirements.txt
python sync_miyoushe.py
```

**会自动：**
- 搜索米游社「角色名 壁纸」
- 过滤 cos/手办/攻略/联动等低质量帖
- 下载原图并压缩到 ≤1200px 宽、≤800KB
- 生成 `src/data.js`

**改搜哪些角色：**

编辑 `sync_miyoushe.py` 里的 `QUERIES`：

```python
QUERIES = [
    ("雷电将军 壁纸", 2, "原神", "3D渲染", "雷电将军"),
    ("胡桃 壁纸",     2, "原神", "动漫插画", "胡桃"),
    # (搜索词, gids, 游戏名, 默认风格, 角色名)
]
```

gids 对应：
- `1` = 崩坏3
- `2` = 原神
- `6` = 崩坏：星穹铁道
- `8` = 绝区零

> ⚠️ 米游社没有明日方舟/蔚蓝档案的专区，这两个游戏的角色建议手动补充图或用小红书下载。

### Pixiv 版（需要梯子和 Token）

```bash
python sync.py
```

需要填 `REFRESH_TOKEN`，获取方式见脚本内注释。

---

## ⚙️ 硬性内容规则

1. **gender 只允许 "女"** — 男角色（钟离/魈/达达利亚/景元/刃等）一律不收录
2. **风格限定** — 只认 3D渲染 / 2.5D / 动漫插画 / Live2D
3. **源标注** — 每张图标 `source`（米游社 / Pixiv / 手动）
4. **NSFW 默认关闭** — 开启需年龄确认

---

## 📂 文件结构

```
an-app/
├── public/
│   └── images/                    ← 米游社爬虫下载的真图
├── src/
│   ├── data.js                    ← 壁纸数据（爬虫自动生成）
│   ├── App.jsx                    ← 5 Tab 主界面
│   ├── main.jsx
│   ├── hooks/
│   │   ├── useLocalStorage.js
│   │   └── useWallpaperImages.js
│   └── utils/
│       └── capacitor.js           ← 手机端壁纸/相册 Native 调用
├── android/                       ← Capacitor Android 工程
├── sync_miyoushe.py               ← ★ 米游社爬虫（不挂梯子）
├── sync.py                        ← Pixiv 爬虫（需梯子+Token）
├── requirements.txt
├── package.json
├── build-apk.bat                  ← Windows 一键打包
├── build-apk.sh                   ← Mac/Linux 一键打包
└── README.md                      ← 本文件
```

---

## 🚀 快速开始（第一次）

```bash
# 1. 装依赖
npm install
pip install -r requirements.txt

# 2. 爬壁纸（米游社，不挂梯子）
python sync_miyoushe.py

# 3. 本地预览
npm run dev
# 浏览器打开 http://localhost:5173

# 4. （可选）打包 APK
bash build-apk.sh   # Mac/Linux
# 或
build-apk.bat       # Windows
```

---

## 📋 验收清单

| 用例 | 状态 |
|---|---|
| 搜索「雷电将军」出结果 | ✅ |
| 搜索「达达利亚」空结果（男角色过滤） | ✅ |
| 风格「3D渲染」只出 3D | ✅ |
| 米游社爬虫大陆直连不挂梯子 | ✅ |
| 图片自动压缩 ≤1200px / ≤800KB | ✅ |
| 全屏预览 + 收藏 + 设为壁纸 + 下载 | ✅ |
| APK 构建脚本就绪 | ✅ |

---

## ⚠️ 版权提示

- 米游社图源为米哈游官方/用户社区公开内容
- Pixiv 图源需确认画师授权
- **仅供个人收藏学习，公开分发需自行确认版权**
