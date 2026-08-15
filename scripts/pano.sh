#!/bin/zsh
# 360°全景查看 - 图片注入查看器并打开浏览器
# 用法: pano.sh <图片路径>...  或从 stdin 读路径

TEMPLATE="$HOME/Library/Application Support/PanoViewer/template.html"
LOG="$HOME/Library/Application Support/PanoViewer/last_run.log"
exec 2>"$LOG"

process() {
  local f="$1"
  # 处理 file:// URL
  case "$f" in
    file://*)
      f="${f#file://}"
      f=$(python3 -c "import sys,urllib.parse;print(urllib.parse.unquote(sys.argv[1]))" "$f" 2>>"$LOG")
      ;;
  esac
  [[ -z "$f" || ! -f "$f" ]] && return 1
  local ext="${f##*.}" mime
  case "${ext:l}" in
    png)  mime="image/png" ;;
    webp) mime="image/webp" ;;
    gif)  mime="image/gif" ;;
    *)    mime="image/jpeg" ;;
  esac
  local b64 tmp
  b64=$(base64 -i "$f" | tr -d '\n') || return 1
  tmp="$(mktemp -t pano).html"
  {
    while IFS= read -r line; do
      if [[ "$line" == *"__EMBEDDED_IMAGE__"* ]]; then
        print -r -- "${line//__EMBEDDED_IMAGE__/data:$mime;base64,$b64}"
      else
        print -r -- "$line"
      fi
    done < "$TEMPLATE"
  } > "$tmp" || return 1
  open "$tmp"
  echo "OK: $f -> $tmp" >> "$LOG"
  return 0
}

if [[ $# -gt 0 ]]; then
  for f in "$@"; do
    process "$f" && exit 0
  done
  exit 1
else
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    process "$f" && exit 0
  done
  exit 1
fi
