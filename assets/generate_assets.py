"""
WarmKnock brand assets for the Facebook Page.

Pillow is the only image tool on this Mac (no ImageMagick / Inkscape / SVG converter),
and it has NO antialiasing, so everything here is drawn at 4x and downsampled LANCZOS.
Thick strokes also hatch at the joints, so the door outline is drawn as filled
rectangles (frame = outer rect minus inner rect) rather than a wide stroke.

Mark and palette are taken from the live warmknock.com logo SVG, not invented:
  door frame  #d6dade   handle + knock arcs  #e8703a (ember)   tile  #20252c
"""
from PIL import Image, ImageDraw, ImageFont

S = 4  # supersample factor

COAL       = (23, 26, 31)
COAL_DEEP  = (14, 17, 22)
TILE       = (32, 37, 44)
DOOR       = (214, 218, 222)
EMBER      = (232, 112, 58)
PAPER      = (247, 245, 242)
MUTED      = (150, 160, 170)

BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
REG  = "/System/Library/Fonts/Supplemental/Arial.ttf"


def door_mark(d, cx, cy, size):
    """The WarmKnock mark: a door with a handle and two knock arcs, centred on (cx, cy)."""
    u = size / 32.0                      # the SVG is on a 32x32 grid
    ox, oy = cx - 16 * u, cy - 16 * u

    def X(v): return ox + v * u
    def Y(v): return oy + v * u

    # door frame — filled outer rect, then punch the inner rect back to the background
    t = 2 * u                            # stroke width from the SVG
    d.rounded_rectangle([X(5.5), Y(6), X(18.5), Y(26)], radius=1.6 * u, fill=DOOR)
    d.rounded_rectangle([X(5.5) + t, Y(6) + t, X(18.5) - t, Y(26) - t],
                        radius=max(1, 0.8 * u), fill=None)
    return (X(5.5) + t, Y(6) + t, X(18.5) - t, Y(26) - t)


def knock(d, cx, cy, size, hole_box, bg):
    u = size / 32.0
    ox, oy = cx - 16 * u, cy - 16 * u
    def X(v): return ox + v * u
    def Y(v): return oy + v * u

    d.rounded_rectangle(hole_box, radius=max(1, 0.8 * u), fill=bg)   # door interior
    r = 1.5 * u                                                       # handle
    d.ellipse([X(15) - r, Y(17) - r, X(15) + r, Y(17) + r], fill=EMBER)

    # two knock arcs, drawn as arcs at 4x then downsampled — no joints, so no hatching
    # sweeps kept narrow on purpose: any wider and the arc ends cross the door frame
    for cxx, rr, w, sweep in ((10.0, 12.0, 2.2, 30), (10.0, 16.5, 1.8, 33)):
        d.arc([X(cxx - rr), Y(16 - rr), X(cxx + rr), Y(16 + rr)],
              start=-sweep, end=sweep, fill=EMBER, width=int(w * u))


def profile(path, px=1024):
    img = Image.new("RGB", (px * S, px * S), TILE)
    d = ImageDraw.Draw(img)
    size = px * S * 0.58   # leaves margin for Facebook's circular crop
    cx = cy = px * S / 2
    hole = door_mark(d, cx, cy, size)
    knock(d, cx, cy, size, hole, TILE)
    img.resize((px, px), Image.LANCZOS).save(path)
    print("wrote", path)


def cover(path, w=1640, h=856):
    img = Image.new("RGB", (w * S, h * S), COAL)
    d = ImageDraw.Draw(img)
    # vertical wash from coal to coal-deep
    for y in range(h * S):
        f = y / (h * S)
        d.line([(0, y), (w * S, y)],
               fill=tuple(int(COAL[i] + (COAL_DEEP[i] - COAL[i]) * f) for i in range(3)))

    size = h * S * 0.40
    mx = w * S * 0.235
    my = h * S * 0.50
    hole = door_mark(d, mx, my, size)
    knock(d, mx, my, size, hole, COAL_DEEP)

    tx = w * S * 0.42
    f1 = ImageFont.truetype(BOLD, int(h * S * 0.135))
    f2 = ImageFont.truetype(REG,  int(h * S * 0.052))
    f3 = ImageFont.truetype(REG,  int(h * S * 0.042))
    d.text((tx, my - h * S * 0.175), "WarmKnock", font=f1, fill=PAPER)
    d.text((tx, my + h * S * 0.010), "Exclusive motivated seller leads.", font=f2, fill=EMBER)
    d.text((tx, my + h * S * 0.090), "One buyer per lead. Sold once, ever.", font=f3, fill=MUTED)

    img.resize((w, h), Image.LANCZOS).save(path)
    print("wrote", path)


base = "/Users/andrewedgar/Documents/Claude/SteelVoyage/WarmKnock_Site/assets/"
profile(base + "warmknock-profile.png")
cover(base + "warmknock-cover.png")
