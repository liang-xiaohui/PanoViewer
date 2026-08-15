#!/usr/bin/env python3
"""
生成带地标的测试全景图（等距圆柱投影 2048×1024）。

地标包括：经纬网格、四个方位角标注（0°/90°/180°/270° + 方向词）、
不同形状的地标图形、天顶 Z / 天底 N 标记、左右边缘拼缝标记线
（左缘白色 / 右缘洋红——用于肉眼检查拼缝是否连续、是否镜像、是否有脏楔形带）。

依赖：Pillow（pip install pillow）
用法：python3 tools/make_test_pano.py [输出路径，默认 tools/test_pano.png]
"""
import sys
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 2048, 1024


def main() -> None:
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "test_pano.png")
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)

    # 天空渐变（上 1/2）与地面渐变（下 1/2），地平线在 v = 0.5
    for y in range(H):
        v = y / H
        if v < 0.5:
            t = v / 0.5
            c = (int(90 + 100 * t), int(140 + 80 * t), 235)
        else:
            t = (v - 0.5) / 0.5
            c = (int(60 + 120 * t), int(120 - 40 * t), int(70 + 60 * t))
        d.line([(0, y), (W, y)], fill=c)

    # 经纬网格：每 30°
    for lon in range(0, 360, 30):
        x = int(lon / 360 * W)
        d.line([(x, 0), (x, H)], fill=(255, 255, 255), width=2)
    for lat in range(-90, 91, 30):
        y = int((0.5 - lat / 180) * H)
        d.line([(0, y), (W, y)], fill=(220, 220, 220), width=2)

    try:
        f_mid = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
    except OSError:
        f_mid = ImageFont.load_default()

    # 四个方位角：标注文字 + 地标图形（不同形状便于识别）
    col = {0: (255, 60, 60), 90: (255, 200, 0), 180: (0, 220, 120), 270: (80, 150, 255)}
    txt = {0: "0 FRONT", 90: "90 RIGHT", 180: "180 BACK", 270: "270 LEFT"}
    shape = {0: "tri", 90: "sq", 180: "diamond", 270: "circle"}
    for lon in (0, 90, 180, 270):
        x = int(lon / 360 * W)
        d.text((x + 10, int(H * 0.38)), txt[lon], fill=col[lon], font=f_mid)
        y = int(H * 0.62)
        s = shape[lon]
        if s == "tri":
            d.polygon([(x, y - 60), (x - 55, y + 45), (x + 55, y + 45)], outline=col[lon], width=8)
        elif s == "sq":
            d.rectangle([x - 50, y - 50, x + 50, y + 50], outline=col[lon], width=8)
        elif s == "diamond":
            d.polygon([(x, y - 65), (x - 55, y), (x, y + 65), (x + 55, y)], outline=col[lon], width=8)
        else:
            d.ellipse([x - 50, y - 50, x + 50, y + 50], outline=col[lon], width=8)

    # 天顶 / 天底标记（极点内容会被投影压缩成放射状，用于检查极射投影）
    for i in range(24):
        x = int(i / 24 * W)
        d.text((x, 8), "Z", fill=(30, 30, 30), font=f_mid)
        d.text((x, H - 80), "N", fill=(15, 15, 15), font=f_mid)
    d.line([(0, 0), (W, 0)], fill=(30, 30, 30), width=6)
    d.line([(0, H - 1), (W, H - 1)], fill=(15, 15, 15), width=6)

    # 拼缝标记：左缘白线 / 右缘洋红线（正常渲染下两者应无缝贴合）
    d.line([(0, 0), (0, H)], fill=(255, 255, 255), width=4)
    d.line([(W - 1, 0), (W - 1, H)], fill=(255, 0, 255), width=4)

    img.save(out)
    print("saved", out, img.size)


if __name__ == "__main__":
    main()
