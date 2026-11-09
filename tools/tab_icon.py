"""Make the browser tab and home-screen icons from Nathan's drawn "n".

Usage: python3 tools/tab_icon.py   (from the repo root; needs Pillow)

Reads images/logos/tab/n.png (a drawing on a transparent background) and
writes, at the repo root:
  favicon.ico           16, 32 and 48px, transparent: the drawing's cream
                        fill and dark outline read on light and dark tabs
  apple-touch-icon.png  180px on a white square (iPhones fill transparency
                        with black and round the corners themselves)
"""
from PIL import Image

src = Image.open('images/logos/tab/n.png').convert('RGBA')
src = src.crop(src.getchannel('A').getbbox())


def square(im, pad):
    """Center im on a transparent square with pad (a fraction) around it."""
    side = round(max(im.size) * (1 + 2 * pad))
    sq = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    sq.paste(im, ((side - im.width) // 2, (side - im.height) // 2))
    return sq


# Tab icon: the letter fills the box, as tab icons are tiny
tab = square(src, 0.02)
sizes = [16, 32, 48]
frames = [tab.resize((s, s), Image.LANCZOS) for s in sizes]
frames[-1].save('favicon.ico', sizes=[(s, s) for s in sizes],
                append_images=frames[:-1])

# Home-screen icon: white tile with room around the letter
apple = Image.new('RGBA', (180, 180), (255, 255, 255, 255))
apple.alpha_composite(square(src, 0.2).resize((180, 180), Image.LANCZOS))
apple.convert('RGB').save('apple-touch-icon.png', optimize=True)
print('wrote favicon.ico and apple-touch-icon.png')
