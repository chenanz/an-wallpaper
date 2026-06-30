@echo off
chcp 65001 >nul
:: ============================================
:: 安 — GitHub Pages 一键部署
:: 用法：deploy-gh-pages.bat
:: ============================================
echo.
echo  🚀 安 — 部署到 GitHub Pages...
echo.

:: 设置环境变量（区分 GitHub Pages 构建 vs 本地/Android 构建）
set GH_PAGES=1

:: 构建前端（带 /an-wallpaper/ base 路径）
echo [1/3] 构建前端（GitHub Pages 模式）...
call npm run build
if %ERRORLEVEL% neq 0 (
    echo ❌ 构建失败！
    pause
    exit /b 1
)

:: 上传到 GitHub
echo.
echo [2/3] 上传到 GitHub...
python deploy_api.py
if %ERRORLEVEL% neq 0 (
    echo ❌ 上传失败！
    pause
    exit /b 1
)

echo.
echo [3/3] ✅ 部署完成！
echo.
echo  🔗 https://chenanz.github.io/an-wallpaper/
echo  (1-3分钟生效)
echo.
pause
