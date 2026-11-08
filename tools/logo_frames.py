"""Make small site copies of hand-drawn logo frames.

Usage: python3 tools/logo_frames.py SRC_DIR OUT_DIR HEIGHT_PX   (needs Pillow)
e.g.   python3 tools/logo_frames.py images/logos/moon images/logos/moon/site 96
Reads SRC_DIR/1.png, 2.png, 3.png (any size, transparent background), crops
each to its drawing, puts all of them on one shared canvas (centered, same
scale, so the frames line up and keep their relative sizes), then scales the
canvas to HEIGHT_PX tall and writes OUT_DIR/1.png ...
"""
import sys, glob, os
from PIL import Image

src, out, height = sys.argv[1], sys.argv[2], int(sys.argv[3])
paths = sorted(p for p in glob.glob(os.path.join(src, '[0-9].*')))
frames = []
for p in paths:
    im = Image.open(p).convert('RGBA')
    im = im.crop(im.getchannel('A').getbbox())
    frames.append((os.path.splitext(os.path.basename(p))[0], im))
W = max(im.width for _, im in frames)
H = max(im.height for _, im in frames)
scale = height / H
size = (round(W * scale), height)
for name, im in frames:
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    canvas.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
    small = canvas.resize(size, Image.LANCZOS)
    dest = os.path.join(out, name + '.png')
    small.save(dest, optimize=True)
    print(dest, small.size, os.path.getsize(dest), 'bytes')
