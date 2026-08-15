#!/bin/zsh
# Build the self-contained macOS app and disk image.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="$(tr -d '[:space:]' < "$ROOT/VERSION")"
APP_NAME="PanoViewer"
APP="$ROOT/dist/$APP_NAME.app"
DMG="$ROOT/dist/PanoViewer-macOS.dmg"
STAGING="$(mktemp -d -t panoviewer-dmg)"
trap 'rm -rf "$STAGING"' EXIT

python3 "$ROOT/scripts/build.py"
rm -rf "$APP" "$DMG"
osacompile -o "$APP" "$ROOT/scripts/pano_applet.applescript"

RESOURCES="$APP/Contents/Resources"
cp "$ROOT/scripts/pano.sh" "$RESOURCES/pano.sh"
cp "$ROOT/dist/template.html" "$RESOURCES/template.html"
cp "$ROOT/assets/PanoViewer.icns" "$RESOURCES/applet.icns"
chmod +x "$RESOURCES/pano.sh"

/usr/libexec/PlistBuddy -c "Set :CFBundleName $APP_NAME" "$APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Add :CFBundleDisplayName string $APP_NAME" "$APP/Contents/Info.plist" 2>/dev/null || \
  /usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName $APP_NAME" "$APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Add :CFBundleIdentifier string com.liangxiaohui.panoviewer" "$APP/Contents/Info.plist" 2>/dev/null || \
  /usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier com.liangxiaohui.panoviewer" "$APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Add :CFBundleShortVersionString string $VERSION" "$APP/Contents/Info.plist" 2>/dev/null || \
  /usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString $VERSION" "$APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Add :CFBundleVersion string $VERSION" "$APP/Contents/Info.plist" 2>/dev/null || \
  /usr/libexec/PlistBuddy -c "Set :CFBundleVersion $VERSION" "$APP/Contents/Info.plist"

codesign --force --deep --sign - "$APP"
codesign --verify --deep --strict --verbose=2 "$APP"

cp -R "$APP" "$STAGING/"
ln -s /Applications "$STAGING/Applications"
hdiutil create -volname "$APP_NAME" -srcfolder "$STAGING" -ov -format UDZO "$DMG"
shasum -a 256 "$DMG"
