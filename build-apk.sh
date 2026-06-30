#!/bin/bash
# build-apk.sh — 一键构建 Android APK
# 前提：已安装 Android Studio + JDK 17 + 环境变量 $ANDROID_HOME

set -e

echo "=== 安 — 二游少女壁纸馆 APK 构建 ==="
echo ""

# 1. 爬取壁纸（可选）
if [ "$1" = "--skip-crawl" ]; then
    echo "⏭ 跳过爬虫"
else
    echo "🕷 运行米游社爬虫..."
    pip install -r requirements.txt -q
    python sync_miyoushe.py
fi

# 2. 构建前端
echo ""
echo "📦 构建前端..."
npm ci 2>/dev/null || npm install
npm run build

# 3. 同步到 Android 工程
echo ""
echo "📲 同步 Capacitor..."
npx cap sync android

# 4. 编译 APK
echo ""
echo "🔨 编译 APK..."
cd android
./gradlew assembleDebug --quiet

echo ""
echo "✅ APK 已生成："
ls -lh app/build/outputs/apk/debug/app-debug.apk

echo ""
echo "📱 安装到手机："
echo "  1. 手机开 USB 调试，连电脑"
echo "  2. adb install app/build/outputs/apk/debug/app-debug.apk"
