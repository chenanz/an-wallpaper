@echo off
chcp 65001 >nul
:: ============================================
:: 安 — 二游少女壁纸馆 APK 一键构建
:: ============================================
echo.
echo  ╔══════════════════════════════════════╗
echo  ║    安 — 二游少女壁纸馆 APK 构建      ║
echo  ╚══════════════════════════════════════╝
echo.

:: --- 环境检查 ---
echo [1/6] 检查环境...

where java >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ 未检测到 Java！请先安装 JDK 17：
    echo    https://adoptium.net/temurin/releases/?version=17
    echo    安装后重跑此脚本
    pause
    exit /b 1
)
echo   ✅ Java OK

if not defined ANDROID_HOME (
    if not defined ANDROID_SDK_ROOT (
        echo ❌ 未检测到 Android SDK！请安装 Android Studio：
        echo    https://developer.android.com/studio
        echo    安装后设置环境变量 ANDROID_HOME
        pause
        exit /b 1
    )
)
echo   ✅ Android SDK OK

where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ 未检测到 Node.js！
    pause
    exit /b 1
)
echo   ✅ Node.js OK

:: --- 安装依赖 ---
echo.
echo [2/6] 安装前端依赖...
call npm install --prefer-offline 2>nul

:: --- 构建前端 ---
echo.
echo [3/6] 构建前端...
call npm run build
if %ERRORLEVEL% neq 0 (
    echo ❌ 前端构建失败！
    pause
    exit /b 1
)

:: --- 同步到 Android ---
echo.
echo [4/6] 同步 Capacitor...
call npx cap sync android
if %ERRORLEVEL% neq 0 (
    echo ❌ Capacitor 同步失败！
    pause
    exit /b 1
)

:: --- 编译 APK ---
echo.
echo [5/6] 编译 APK（首次较慢，约3-5分钟）...
cd android
call .\gradlew.bat assembleDebug
if %ERRORLEVEL% neq 0 (
    echo ❌ APK 编译失败！
    pause
    exit /b 1
)
cd ..

:: --- 输出结果 ---
echo.
echo [6/6] ✅ 构建成功！
echo.
echo  ╔══════════════════════════════════════╗
echo  ║          APK 已生成！                ║
echo  ╚══════════════════════════════════════╝
echo.
echo  📦 APK 位置：
dir /b android\app\build\outputs\apk\debug\app-debug.apk 2>nul
echo.
echo  📱 安装方式：
echo     手机开 USB 调试 → 连电脑 → 运行：
echo     adb install android\app\build\outputs\apk\debug\app-debug.apk
echo.
echo  💡 要生成签名版 APK（用来上架应用商店）：
echo     cd android ^&^& .\gradlew.bat assembleRelease
echo.

:: 自动打开 APK 所在文件夹
explorer android\app\build\outputs\apk\debug\

pause
