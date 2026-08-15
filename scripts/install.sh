#!/bin/zsh
# 一键安装/更新 Mac 端入口：
#   1. 构建离线单文件查看器（dist/）
#   2. 部署注入脚本与模板到 ~/Library/Application Support/PanoViewer/
#   3. 编译拖放 App 到 ~/Applications/360°全景查看.app（osacompile）
#   4. 同步独立版到 iCloud Drive（供 iPhone 快捷指令使用，若目录存在）
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP_SUPPORT="$HOME/Library/Application Support/PanoViewer"
APPLET_SRC="$ROOT/scripts/pano_applet.applescript"
APP_OUT="$HOME/Applications/360°全景查看.app"
ICLOUD="$HOME/Library/Mobile Documents/com~apple~CloudDocs"

# 1. 构建
python3 "$ROOT/scripts/build.py"

# 2. 部署注入脚本与模板（拖放 App 的运行时依赖）
mkdir -p "$APP_SUPPORT"
cp "$ROOT/scripts/pano.sh" "$APP_SUPPORT/pano.sh"
chmod +x "$APP_SUPPORT/pano.sh"
cp "$ROOT/dist/template.html" "$APP_SUPPORT/template.html"
echo "OK  $APP_SUPPORT"

# 3. 编译拖放 App
osacompile -o "$APP_OUT" "$APPLET_SRC"
cp "$ROOT/assets/PanoViewer.icns" "$APP_OUT/Contents/Resources/applet.icns"
touch "$APP_OUT"
echo "OK  $APP_OUT"

# 4. iCloud 同步（可选）
if [[ -d "$ICLOUD" ]]; then
  cp "$ROOT/dist/全景查看器-独立版.html" "$ICLOUD/全景查看器-独立版.html"
  echo "OK  $ICLOUD/全景查看器-独立版.html"
fi

echo ""
echo "安装完成。用法："
echo "  - 拖全景图到 Dock 中的「360°全景查看」图标"
echo "  - 或 Finder 右键 → 打开方式 → 360°全景查看"
echo "  - 或双击 App 后点选图片"
