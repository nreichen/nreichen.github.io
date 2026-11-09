"""Make small site copies of hand-drawn logo frames.

Usage: python3 tools/logo_frames.py SRC_DIR OUT_DIR HEIGHT_PX [--same-width]
                                                              (needs Pillow)
e.g.   python3 tools/logo_frames.py images/logos/moon images/logos/moon/site 96
       python3 tools/logo_frames.py images/logos/title images/logos/title/site 120 --same-width

Reads SRC_DIR/1.png, 2.png, 3.png (any size, transparent background), crops
each to its drawing and centers them all on one shared canvas so the frames
line up, then writes OUT_DIR/1.png ... at HEIGHT_PX tall as small 64-color PNGs.

By default every frame keeps the same scale, so a frame drawn bigger shows
bigger (right for the moon, whose frames were drawn at nearly one size).
--same-width scales each frame to the same width instead, for wide drawings
like the title, where small differences in drawing size would make the
whole word grow and shrink.
"""
import sys, glob, os
from PIL import Image

args = [a for a in sys.argv[1:] if not a.startswith('--')]
same_width = '--same-width' in sys.argv
src, out, height = args[0], args[1], int(args[2])
os.makedirs(out, exist_ok=True)

frames = []
for p in sorted(glob.glob(os.path.join(src, '[0-9].*'))):
    im = Image.open(p).convert('RGBA')
    im = im.crop(im.getchannel('A').getbbox())
    frames.append((os.path.splitext(os.path.basename(p))[0], im))

if same_width:
    # Each frame at the same width; the canvas is as tall as the tallest
    aspect = max(im.height / im.width for _, im in frames)
    canvas_w = round(height / aspect)
    sizes = [(canvas_w, round(canvas_w * im.height / im.width)) for _, im in frames]
else:
    # One scale for all frames, chosen so the tallest fills HEIGHT_PX
    W = max(im.width for _, im in frames)
    H = max(im.height for _, im in frames)
    scale = height / H
    canvas_w = round(W * scale)
    sizes = [(round(im.width * scale), round(im.height * scale)) for _, im in frames]

for (name, im), size in zip(frames, sizes):
    canvas = Image.new('RGBA', (canvas_w, height), (0, 0, 0, 0))
    small = im.resize(size, Image.LANCZOS)
    canvas.paste(small, ((canvas_w - size[0]) // 2, (height - size[1]) // 2))
    # The drawings are two flat colors plus soft edges, so a 64-color
    # palette looks identical and cuts the file to about a fifth
    canvas = canvas.quantize(colors=64, method=Image.Quantize.FASTOCTREE,
                             dither=Image.Dither.NONE)
    dest = os.path.join(out, name + '.png')
    canvas.save(dest, optimize=True)
    print(dest, canvas.size, os.path.getsize(dest), 'bytes')
