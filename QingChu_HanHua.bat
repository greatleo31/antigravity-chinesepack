@echo off
setlocal
chcp 65001 >nul
:: ========================================================
:: Antigravity 中文语言包还原工具
:: ========================================================
title Antigravity 中文语言包还原工具

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
echo [2/3] 正在还原官方文件...
%PYTHON_CMD% "%~dp0AntigravityHanHua_GongJu.py" --huifu %*
set "status=%errorlevel%"

echo.
if not "%status%"=="0" (
    echo [3/3] 还原失败，请检查上方输出信息。
) else (
    echo [3/3] 还原完成。
    echo.
    echo [提示] Antigravity 已恢复为官方原始状态。
)

echo.
pause
exit /b %status%
