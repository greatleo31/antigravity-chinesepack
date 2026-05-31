@echo off
setlocal
chcp 65001 >nul
:: ========================================================
:: Antigravity 中文语言包安装工具
:: ========================================================
title Antigravity 中文语言包安装工具

where python >nul 2>nul
if errorlevel 1 (
    py -3 -V >nul 2>nul
    if errorlevel 1 (
        echo.
        echo [错误] 未检测到 Python，请先安装 Python 3 并确保已加入 PATH。
        echo.
        pause
        exit /b 1
    ) else (
        set "PYTHON_CMD=py -3"
    )
) else (
    set "PYTHON_CMD=python"
)

echo.
echo [1/3] 正在检测并关闭 Antigravity 进程...
taskkill /f /im Antigravity.exe /t >nul 2>nul
timeout /t 2 /nobreak >nul

echo.
echo [2/3] 正在注入汉化核心...
%PYTHON_CMD% "%~dp0AntigravityHanHua_GongJu.py" %*
set "status=%errorlevel%"

echo.
if not "%status%"=="0" (
    echo [3/3] 安装失败，请检查上方输出信息。
) else (
    echo [3/3] 安装完成。
    echo.
    echo [提示] 请重新启动 Antigravity 查看汉化效果。
)

echo.
pause
exit /b %status%
