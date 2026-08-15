#!/usr/bin/env python3
"""Generate matching Windows, browser, and macOS application icons."""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"
ICO_OUTPUT = ASSETS / "PanoViewer.ico"
PNG_OUTPUT = ASSETS / "PanoViewer-favicon.png"
ICNS_OUTPUT = ASSETS / "PanoViewer.icns"
SIZE = 1024


def main() -> None:
    image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Dark rounded app tile with a subtle cyan rim.
    draw.rounded_rectangle((48, 48, 976, 976), radius=220, fill="#101827", outline="#243b55", width=22)

    # Panorama globe.
    globe = (205, 205, 819, 819)
    draw.ellipse(globe, fill="#087ea4", outline="#67e8f9", width=34)
    draw.arc((310, 205, 714, 819), 90, 270, fill="#a5f3fc", width=24)
    draw.arc((310, 205, 714, 819), 270, 90, fill="#22d3ee", width=24)
    draw.arc((205, 348, 819, 676), 0, 180, fill="#a5f3fc", width=22)
    draw.arc((205, 348, 819, 676), 180, 360, fill="#22d3ee", width=22)
    draw.line((222, 512, 802, 512), fill="#ecfeff", width=27)

    # Orbit and viewpoint dot make the 360-degree purpose legible at small sizes.
    draw.arc((118, 362, 906, 790), 18, 340, fill="#f8fafc", width=30)
    draw.ellipse((805, 604, 887, 686), fill="#f8fafc")

    ASSETS.mkdir(parents=True, exist_ok=True)
    image.save(
        ICO_OUTPUT,
        format="ICO",
        sizes=[(16, 16), (20, 20), (24, 24), (32, 32), (40, 40), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    image.resize((64, 64), Image.Resampling.LANCZOS).save(PNG_OUTPUT, format="PNG", optimize=True)
    image.save(ICNS_OUTPUT, format="ICNS")
    print(ICO_OUTPUT)
    print(PNG_OUTPUT)
    print(ICNS_OUTPUT)


if __name__ == "__main__":
    main()
