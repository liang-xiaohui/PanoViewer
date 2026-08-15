#!/usr/bin/env python3
"""
构建脚本：把 src/viewer_source.html 与 vendor/three.min.js 组装为离线单文件查看器。

产物（输出到 dist/）：
  - 全景查看器-独立版.html : 独立版，无内嵌图片，打开后手动选图/拖图
  - template.html          : 拖放 App 注入模板，保留 __EMBEDDED_IMAGE__ 标记
                              （pano.sh 会把 base64 图片注入该标记处）

用法：
  python3 scripts/build.py                    # 仅构建
  python3 scripts/build.py --install          # 构建并部署到系统安装位置
  python3 scripts/build.py --embed <图片路径>  # 额外产出内嵌指定图片的测试版
"""
import argparse
import base64
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src", "viewer_source.html")
VENDOR = os.path.join(ROOT, "vendor", "three.min.js")
ICON = os.path.join(ROOT, "assets", "PanoViewer-favicon.png")
DIST = os.path.join(ROOT, "dist")

STANDALONE_NAME = "全景查看器-独立版.html"
TEMPLATE_NAME = "template.html"

MIME = {
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}


def build() -> tuple[str, str]:
    """返回 (template_content, standalone_content)。"""
    src = open(SRC, encoding="utf-8").read()
    three = open(VENDOR, encoding="utf-8").read()
    icon = base64.b64encode(open(ICON, "rb").read()).decode()
    out = src.replace("__THREE_JS__", three)
    out = out.replace("__APP_ICON__", f"data:image/png;base64,{icon}")
    if "__THREE_JS__" in out:
        sys.exit("错误：__THREE_JS__ 替换失败")
    if "__APP_ICON__" in out:
        sys.exit("错误：__APP_ICON__ 替换失败")
    standalone = out.replace("__EMBEDDED_IMAGE__", "")
    if "__EMBEDDED_IMAGE__" in standalone:
        sys.exit("错误：__EMBEDDED_IMAGE__ 替换失败")

    os.makedirs(DIST, exist_ok=True)
    open(os.path.join(DIST, STANDALONE_NAME), "w", encoding="utf-8").write(standalone)
    open(os.path.join(DIST, TEMPLATE_NAME), "w", encoding="utf-8").write(out)
    print(f"OK  dist/{STANDALONE_NAME}  ({len(standalone) // 1024} KB)")
    print(f"OK  dist/{TEMPLATE_NAME}  ({len(out) // 1024} KB)")
    return out, standalone


def embed(template: str, image_path: str) -> None:
    """把图片以 base64 内嵌进模板，产出可直接打开的测试版。"""
    ext = os.path.splitext(image_path)[1].lower()
    mime = MIME.get(ext, "image/jpeg")
    b64 = base64.b64encode(open(image_path, "rb").read()).decode()
    content = template.replace("__EMBEDDED_IMAGE__", f"data:{mime};base64,{b64}")
    if "__EMBEDDED_IMAGE__" in content:
        sys.exit("错误：__EMBEDDED_IMAGE__ 替换失败")
    name = f"测试-内嵌图-{os.path.splitext(os.path.basename(image_path))[0]}.html"
    path = os.path.join(DIST, name)
    open(path, "w", encoding="utf-8").write(content)
    print(f"OK  dist/{name}  ({len(content) // 1024} KB)")


def install() -> None:
    """部署到系统安装位置（拖放 App 的模板 + iCloud 独立版）。"""
    home = os.path.expanduser("~")
    app_support = os.path.join(home, "Library", "Application Support", "PanoViewer")
    os.makedirs(app_support, exist_ok=True)
    shutil.copy(os.path.join(DIST, TEMPLATE_NAME), os.path.join(app_support, TEMPLATE_NAME))
    print(f"OK  {app_support}/{TEMPLATE_NAME}")

    icloud = os.path.join(home, "Library", "Mobile Documents", "com~apple~CloudDocs")
    if os.path.isdir(icloud):
        shutil.copy(os.path.join(DIST, STANDALONE_NAME), os.path.join(icloud, STANDALONE_NAME))
        print(f"OK  {icloud}/{STANDALONE_NAME}")
    else:
        print("跳过 iCloud（目录不存在）")


def main() -> None:
    ap = argparse.ArgumentParser(description="构建离线单文件 360° 全景查看器")
    ap.add_argument("--install", action="store_true", help="构建后部署到系统安装位置")
    ap.add_argument("--embed", metavar="图片路径", help="额外产出内嵌指定图片的测试版")
    args = ap.parse_args()

    template, _ = build()
    if args.embed:
        embed(template, args.embed)
    if args.install:
        install()


if __name__ == "__main__":
    main()
