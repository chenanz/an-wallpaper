@echo off
chcp 65001 >nul
:: ============================================
:: 安 — 一键构建APK + 上传到GitHub Release
:: 用法：build-and-release.bat
:: ============================================
echo.
echo  ╔══════════════════════════════════════╗
echo  ║  安 — 一键构建APK + 发布下载链接     ║
echo  ╚══════════════════════════════════════╝
echo.

:: --- 环境检查 ---
echo [1/7] 检查环境...
where java >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ 未检测到 Java！安装 JDK 17：https://adoptium.net/
    pause && exit /b 1
)
echo   ✅ Java

if not defined ANDROID_HOME if not defined ANDROID_SDK_ROOT (
    echo ❌ 未检测到 Android SDK！安装 Android Studio：https://developer.android.com/studio
    pause && exit /b 1
)
echo   ✅ Android SDK

where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ 未检测到 Node.js！
    pause && exit /b 1
)
echo   ✅ Node.js

:: --- 构建前端（APK模式，不带子路径） ---
echo.
echo [2/7] 安装前端依赖...
call npm install --prefer-offline 2>nul

echo.
echo [3/7] 构建前端（APK模式）...
set GH_PAGES=
call npm run build
if %ERRORLEVEL% neq 0 (
    echo ❌ 前端构建失败！
    pause && exit /b 1
)

:: --- 同步 Capacitor ---
echo.
echo [4/7] 同步 Capacitor...
call npx cap sync android
if %ERRORLEVEL% neq 0 (
    echo ❌ Capacitor 同步失败！
    pause && exit /b 1
)

:: --- 编译 APK ---
echo.
echo [5/7] 编译 release APK（约3-5分钟）...
cd android
call .\gradlew.bat assembleRelease
if %ERRORLEVEL% neq 0 (
    echo ⚠️ Release 签名失败，改用 debug APK...
    call .\gradlew.bat assembleDebug
    set APK_PATH=android\app\build\outputs\apk\debug\app-debug.apk
) else (
    set APK_PATH=android\app\build\outputs\apk\release\app-release.apk
)
cd ..

:: --- 上传到 GitHub Release ---
echo.
echo [6/7] 上传 APK 到 GitHub Release...
python upload_release.py %APK_PATH%
if %ERRORLEVEL% neq 0 (
    echo ❌ 上传失败！
    echo 💡 你可以手动上传 APK：
    echo    打开 https://github.com/chenanz/an-wallpaper/releases
    echo    点 "Create a new release" → 拖入 APK
    pause && exit /b 1
)

:: --- 同时更新 GitHub Pages ---
echo.
echo [7/7] 更新 GitHub Pages...
set GH_PAGES=1
call npm run build
if %ERRORLEVEL% neq 0 (
    echo ⚠️ Pages 构建失败，但 APK 已上传
)
python deploy_api.py 2>nul

echo.
echo  ╔══════════════════════════════════════╗
echo  ║           全部完成！                 ║
echo  ╚══════════════════════════════════════╝
echo.
echo  📱 APK 下载：https://github.com/chenanz/an-wallpaper/releases
echo  🌐 网页版：  https://chenanz.github.io/an-wallpaper/
echo.

explorer android\app\build\outputs\apk\
pause
