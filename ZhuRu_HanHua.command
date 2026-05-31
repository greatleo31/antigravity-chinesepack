#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

echo
if command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD="python"
else
  echo "[错误] 未检测到 Python 3，请先安装 Python。"
  echo
  echo "按回车键退出..."
  read -r _
  exit 1
fi

echo "[1/3] 正在检测并关闭 Antigravity 进程..."
osascript -e 'tell application "Antigravity" to quit' >/dev/null 2>&1 || true
pkill -f "Antigravity" >/dev/null 2>&1 || true
sleep 1

echo
echo "[2/3] 正在注入汉化核心..."
"$PYTHON_CMD" "$SCRIPT_DIR/AntigravityHanHua_GongJu.py" "$@"
status=$?

echo
if [ "$status" -ne 0 ]; then
  echo "[3/3] 安装失败，请检查上方输出信息。"
else
  echo "[3/3] 安装完成。"
  echo
  echo "[提示] 请重新启动 Antigravity 查看汉化效果。"
fi

echo
echo "按回车键退出..."
read -r _
exit $status
