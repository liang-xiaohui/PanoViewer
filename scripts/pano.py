#!/usr/bin/env python3
"""Cross-platform launcher for PanoViewer."""

from __future__ import annotations

import argparse
import base64
import mimetypes
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import webbrowser


ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "dist" / "template.html"
BUILD_SCRIPT = ROOT / "scripts" / "build.py"
SUPPORTED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


def choose_image() -> Path | None:
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        return None

    root = tk.Tk()
    root.withdraw()
    root.update()
    selected = filedialog.askopenfilename(
        title="选择 360° 全景图片",
        filetypes=[
            ("全景图片", "*.jpg *.jpeg *.png *.webp *.gif"),
            ("所有文件", "*.*"),
        ],
    )
    root.destroy()
    return Path(selected) if selected else None


def ensure_template() -> None:
    if TEMPLATE.is_file():
        return
    subprocess.run([sys.executable, str(BUILD_SCRIPT)], cwd=ROOT, check=True)


def make_viewer(image: Path) -> Path:
    image = image.expanduser().resolve()
    if not image.is_file():
        raise FileNotFoundError(f"图片不存在：{image}")

    mime = mimetypes.guess_type(image.name)[0] or "image/jpeg"
    if mime not in SUPPORTED_TYPES:
        raise ValueError(f"不支持的图片格式：{image.suffix or '(无扩展名)'}")

    ensure_template()
    template = TEMPLATE.read_text(encoding="utf-8")
    encoded = base64.b64encode(image.read_bytes()).decode("ascii")
    html = template.replace("__EMBEDDED_IMAGE__", f"data:{mime};base64,{encoded}")

    output_dir = Path(tempfile.gettempdir()) / "PanoViewer"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "viewer.html"
    output.write_text(html, encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="跨平台 360° 全景图片查看器")
    parser.add_argument("image", nargs="?", type=Path, help="全景图片路径；省略时弹出选择框")
    parser.add_argument("--no-open", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    image = args.image or choose_image()
    if image is None:
        if args.image is None:
            print("未选择图片。", file=sys.stderr)
        else:
            print("当前 Python 没有 tkinter，请在命令行传入图片路径。", file=sys.stderr)
        return 1

    try:
        viewer = make_viewer(image)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1

    print(viewer)
    if not args.no_open and not webbrowser.open(viewer.as_uri()):
        print("无法自动打开浏览器，请手动打开上面的 HTML 文件。", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
