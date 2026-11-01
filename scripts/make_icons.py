#!/usr/bin/env python3
"""Generate launcher icon assets (legacy PNG + adaptive foreground) from assets/music.png."""
import sys, os
from PIL import Image

SRC = sys.argv[1]
OUT = sys.argv[2]
BG = (251, 231, 227)          # background colour sampled from music.png (#FBE7E3)
DENSITY = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}

im = Image.open(SRC).convert("RGBA")

# legacy icon: crop to the rounded square, pad to a square canvas
bbox = im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
sq = im.crop(bbox)
side = max(sq.size)
canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
canvas.paste(sq, ((side - sq.width) // 2, (side - sq.height) // 2))

# adaptive foreground: keep only the glyph (pixels that are not the background colour)
px = im.load()
glyph = Image.new("RGBA", im.size, (0, 0, 0, 0))
gp = glyph.load()
for y in range(im.height):
    for x in range(im.width):
        r, g, b, a = px[x, y]
        if a > 200 and max(abs(r - BG[0]), abs(g - BG[1]), abs(b - BG[2])) > 10:
            gp[x, y] = (r, g, b, 255)
glyph = glyph.crop(glyph.getbbox())

def fg_layer(size):
    target_h = int(size * 0.46)
    scale = target_h / glyph.height
    g = glyph.resize((max(1, round(glyph.width * scale)), target_h), Image.LANCZOS)
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    layer.paste(g, ((size - g.width) // 2, (size - g.height) // 2), g)
    return layer

for name, d in DENSITY.items():
    folder = os.path.join(OUT, f"mipmap-{name}")
    os.makedirs(folder, exist_ok=True)
    canvas.resize((round(48 * d),) * 2, Image.LANCZOS).save(os.path.join(folder, "legacy.png"))
    fg_layer(round(108 * d)).save(os.path.join(folder, "yts_icon_fg.png"))

canvas.resize((512, 512), Image.LANCZOS).save(os.path.join(OUT, "playstore_512.png"))
print("icons written to", OUT)
