#!/usr/bin/env python3
"""news-image-20261119: one poster that sums up Thursday 19 November 2026.

Pure Python 3.13 standard library, no network, fully deterministic.
Draws a bold poster (giant date masthead, six story panels, footer) into
an RGB framebuffer and encodes it as a PNG written to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- font
# A hand-drawn 5x7 block font. Each glyph is 7 rows of 5 characters;
# '#' is a lit pixel. Chunky on purpose: scaled up it stays legible
# when the whole poster is shrunk to ~300 px across.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", ".#.#.", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "'": (".##..", ".##..", ".#...", ".....", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "€": ("..###", ".#...", "#....", "####.", "#....", ".#...", "..###"),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    "•": (".....", ".....", ".###.", ".###.", ".###.", ".....", "....."),
}


def text_width(s, scale, tracking=1):
    """Pixel width of a string in the block font."""
    if not s:
        return 0
    return len(s) * (5 + tracking) * scale - tracking * scale


# ---------------------------------------------------------------- canvas
class Canvas:
    """A flat RGB framebuffer with simple bold-shape primitives."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bytes(bg) * (w * h))

    def px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + len(row)] = row

    def disc(self, cx, cy, r, color):
        r2 = r * r
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            span = int((r2 - dy * dy) ** 0.5)
            self.rect(cx - span, yy, 2 * span + 1, 1, color)

    def ring(self, cx, cy, r, thick, color):
        """Filled circle outline: pixels whose distance is in [r-thick, r]."""
        lo = (r - thick) * (r - thick)
        hi = r * r
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if lo <= d2 <= hi:
                    self.px(xx, yy, color)

    def poly(self, pts, color):
        """Scanline-filled polygon from a list of (x, y) points."""
        ys = [p[1] for p in pts]
        for yy in range(min(ys), max(ys) + 1):
            nodes = []
            n = len(pts)
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= yy < y2) or (y2 <= yy < y1):
                    nodes.append(x1 + (yy - y1) * (x2 - x1) // (y2 - y1))
            nodes.sort()
            for i in range(0, len(nodes) - 1, 2):
                self.rect(nodes[i], yy, nodes[i + 1] - nodes[i] + 1, 1, color)

    def line(self, x1, y1, x2, y2, color, thick=3):
        steps = max(abs(x2 - x1), abs(y2 - y1), 1)
        r = max(1, thick // 2)
        for i in range(steps + 1):
            x = x1 + (x2 - x1) * i // steps
            y = y1 + (y2 - y1) * i // steps
            self.disc(x, y, r, color)

    def text(self, s, x, y, scale, color, tracking=1):
        cx = x
        for ch in s.upper():
            glyph = FONT.get(ch, FONT[" "])
            for gy, row in enumerate(glyph):
                for gx, cell in enumerate(row):
                    if cell == "#":
                        self.rect(cx + gx * scale, y + gy * scale,
                                  scale, scale, color)
            cx += (5 + tracking) * scale
        return cx - tracking * scale

    def text_c(self, s, cx, y, scale, color, tracking=1):
        x = cx - text_width(s, scale, tracking) // 2
        return self.text(s, x, y, scale, color, tracking)


# ---------------------------------------------------------------- png out
def _chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def save_png(canvas, path):
    raw = bytearray()
    stride = canvas.w * 3
    for yy in range(canvas.h):
        raw.append(0)
        raw += canvas.buf[yy * stride:(yy + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n"
           + _chunk(b"IHDR", ihdr)
           + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + _chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)
    return len(png)


# ---------------------------------------------------------------- palette
INK = (10, 14, 26)          # poster background, near-black navy
PAPER = (244, 241, 234)     # off-white
YELLOW = (255, 205, 40)
RED = (226, 43, 32)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SKY = (168, 205, 232)
SEA = (38, 96, 160)
GREY = (120, 128, 138)
DARKGREY = (52, 58, 66)
OLIVE = (96, 108, 62)
TAN = (216, 188, 138)
GOLD = (198, 148, 44)
TEAL = (16, 92, 102)
PINK = (240, 90, 160)
ORANGE = (248, 140, 40)
PURPLE = (104, 60, 160)
GREEN = (46, 140, 72)
BROWN = (110, 72, 40)


def _star(c, cx, cy, r, color):
    """Chunky five-point star made of stamped discs along its outline."""
    import math
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + int(rad * math.cos(ang)), cy + int(rad * math.sin(ang))))
    c.poly(pts, color)


# ---------------------------------------------------------------- scenes
# Each scene draws inside the box (x, y, w, h): the picture area of a
# panel, above its black headline strip. Shapes are kept big and flat
# so the scene still reads when the poster is thumbnail-sized.

def scene_summit(c, x, y, w, h):
    """Three national flags side by side: US, China, Russia."""
    c.rect(x, y, w, h, (196, 216, 232))
    c.rect(x, y + h - 18, w, 18, DARKGREY)  # ground
    fw, fh = 118, 66
    tops = [y + 26, y + 18, y + 26]
    xs = [x + 28, x + w // 2 - fw // 2, x + w - 28 - fw]
    for fx in xs:
        c.rect(fx - 4, y + 14, 5, h - 30, DARKGREY)  # pole
    # United States: stripes, blue canton, dot stars
    fx, fy = xs[0], tops[0]
    c.rect(fx, fy, fw, fh, WHITE)
    for i in range(0, 7, 2):
        c.rect(fx, fy + i * 10, fw, 9, RED)
    c.rect(fx, fy, 52, 36, (40, 60, 150))
    for r in range(3):
        for col in range(4):
            c.rect(fx + 6 + col * 12, fy + 6 + r * 11, 5, 5, WHITE)
    # China: red field, one big star and a small arc of stars
    fx, fy = xs[1], tops[1]
    c.rect(fx, fy, fw, fh, (214, 38, 32))
    _star(c, fx + 26, fy + 22, 13, YELLOW)
    for dx, dy in ((48, 8), (54, 22), (52, 36), (44, 47)):
        _star(c, fx + dx, fy + dy, 5, YELLOW)
    # Russia: white / blue / red horizontal thirds
    fx, fy = xs[2], tops[2]
    c.rect(fx, fy, fw, fh // 3 + 1, WHITE)
    c.rect(fx, fy + fh // 3, fw, fh // 3, (40, 90, 180))
    c.rect(fx, fy + 2 * fh // 3, fw, fh - 2 * fh // 3, RED)


def scene_bridge(c, x, y, w, h):
    """A bridge over the sea with its middle span down and a burst."""
    c.rect(x, y, w, h, (176, 208, 226))
    c.rect(x, y + h - 34, w, 34, SEA)
    deck_y = y + 62
    c.rect(x + 70, y + 20, 12, deck_y - y - 14, DARKGREY)    # tower L
    c.rect(x + w - 82, y + 20, 12, deck_y - y - 14, DARKGREY)  # tower R
    c.rect(x, deck_y, 190, 10, DARKGREY)                     # deck L
    c.rect(x + w - 190, deck_y, 190, 10, DARKGREY)           # deck R
    # fallen span, tilted into the water
    c.poly([(x + 196, deck_y + 4), (x + 292, deck_y + 4),
            (x + 306, deck_y + 40), (x + 210, deck_y + 40)], RED)
    # explosion burst where the span broke
    _star(c, x + 200, deck_y - 6, 26, ORANGE)
    _star(c, x + 200, deck_y - 6, 15, YELLOW)
    c.disc(x + 300, deck_y - 16, 13, GREY)   # smoke
    c.disc(x + 322, deck_y - 24, 10, GREY)
    # cables
    c.line(x + 76, y + 22, x + 8, deck_y, DARKGREY, 2)
    c.line(x + w - 76, y + 22, x + w - 8, deck_y, DARKGREY, 2)


def scene_gaza(c, x, y, w, h):
    """A tank on the left, aid tents on the right, flood water in front."""
    c.rect(x, y, w, h, (226, 204, 164))
    c.disc(x + 60, y + 26, 15, YELLOW)  # sun
    # tank: tracks, hull, turret, barrel
    tx, ty = x + 36, y + h - 58
    c.rect(tx, ty + 26, 150, 22, DARKGREY)
    for i in range(5):
        c.disc(tx + 16 + i * 30, ty + 37, 8, BLACK)
    c.poly([(tx - 6, ty + 28), (tx + 10, ty + 6), (tx + 140, ty + 6),
            (tx + 156, ty + 28)], OLIVE)
    c.rect(tx + 46, ty - 14, 62, 20, OLIVE)
    c.line(tx + 108, ty - 6, tx + 196, ty - 16, DARKGREY, 7)
    # tents
    for bx in (x + 268, x + 372):
        c.poly([(bx, y + h - 34), (bx + 44, y + h - 84),
                (bx + 88, y + h - 34)], PAPER)
        c.poly([(bx + 34, y + h - 34), (bx + 44, y + h - 62),
                (bx + 54, y + h - 34)], BROWN)
    # flood water across the foreground
    c.rect(x, y + h - 26, w, 26, SEA)
    for i in range(9):
        c.disc(x + 30 + i * 54, y + h - 26, 9, SEA)


def scene_cyclone(c, x, y, w, h):
    """A spiral storm over the sea, land and a bent palm at the edge."""
    c.rect(x, y, w, h, TEAL)
    cx, cy = x + 190, y + h // 2
    import math
    for arm in range(3):
        base = arm * 2.1
        for t in range(46):
            ang = base + t * 0.16
            rad = 8 + t * 1.9
            px = cx + int(rad * math.cos(ang))
            py = cy + int(rad * math.sin(ang) * 0.72)
            if x <= px < x + w and y <= py < y + h:
                c.disc(px, py, 7, WHITE)
    c.disc(cx, cy, 11, (180, 225, 235))  # eye
    # landmass bottom-right with a palm bent by the wind
    c.poly([(x + w - 170, y + h), (x + w, y + h - 52),
            (x + w, y + h)], TAN)
    px, py = x + w - 66, y + h - 40
    c.line(px, py, px - 16, py - 44, BROWN, 6)
    for dx, dy in ((-34, -58), (-14, -66), (8, -62), (24, -48)):
        c.line(px - 16, py - 44, px - 16 + dx, py - 44 + dy + 18, GREEN, 5)
    # rain streaks
    for i in range(7):
        rx = x + 26 + i * 34
        c.line(rx, y + 12, rx - 10, y + 34, (180, 225, 235), 3)


def scene_vangogh(c, x, y, w, h):
    """A framed painting: blossom tree under a swirling night sky."""
    c.rect(x, y, w, h, (88, 76, 66))
    fx, fy, fw, fh = x + 52, y + 6, w - 104, h - 12
    c.rect(fx, fy, fw, fh, GOLD)
    ix, iy, iw, ih = fx + 10, fy + 10, fw - 20, fh - 20
    c.rect(ix, iy, iw, ih, (24, 34, 96))
    c.ring(ix + 52, iy + 30, 15, 5, (240, 230, 170))   # moon swirl
    c.ring(ix + iw - 44, iy + 24, 10, 4, WHITE)
    c.disc(ix + 30, iy + 16, 4, WHITE)
    c.disc(ix + iw - 70, iy + 44, 4, WHITE)
    # tree trunk and dark green canopy with white blossom clusters
    c.line(ix + iw // 2, iy + ih, ix + iw // 2 - 4, iy + 32, BROWN, 8)
    for dx, dy, r in ((-34, 40, 20), (0, 29, 24), (34, 40, 20),
                      (-17, 49, 17), (18, 49, 17)):
        c.disc(ix + iw // 2 + dx, iy + dy, r, (26, 84, 44))
    for dx, dy in ((-38, 32), (-14, 22), (12, 24), (38, 34),
                   (-22, 44), (24, 46), (0, 38)):
        c.disc(ix + iw // 2 + dx, iy + dy, 6, WHITE)
        c.disc(ix + iw // 2 + dx + 2, iy + dy + 2, 3, (250, 240, 200))


def scene_gta(c, x, y, w, h):
    """Vice City sunset: sun, palms and a sports car silhouette."""
    bands = [(250, 120, 90), (244, 96, 130), (196, 74, 158),
             (140, 62, 168), (84, 52, 140)]
    band_h = (h - 30) // len(bands)
    for i, col in enumerate(bands):
        c.rect(x, y + i * band_h, w, band_h + 1, col)
    c.disc(x + w // 2, y + h - 44, 40, YELLOW)
    c.rect(x, y + h - 30, w, 30, (24, 18, 44))  # road
    # palms, left and right
    for px, flip in ((x + 62, 1), (x + w - 62, -1)):
        py = y + h - 28
        c.line(px, py, px + flip * 10, py - 58, BLACK, 7)
        top_x, top_y = px + flip * 10, py - 58
        for dx, dy in ((-40, -12), (-22, -24), (0, -28), (24, -22), (40, -8)):
            c.line(top_x, top_y, top_x + dx, top_y + dy + 16, BLACK, 5)
    # sports car
    cx, cy = x + w // 2, y + h - 30
    c.poly([(cx - 88, cy), (cx - 78, cy - 20), (cx - 30, cy - 24),
            (cx + 34, cy - 24), (cx + 80, cy - 16), (cx + 90, cy)], BLACK)
    c.poly([(cx - 34, cy - 24), (cx - 18, cy - 40), (cx + 26, cy - 40),
            (cx + 40, cy - 24)], BLACK)
    c.rect(cx - 20, cy - 38, 42, 12, (120, 200, 235))
    for wx in (cx - 56, cx + 56):
        c.disc(wx, cy - 2, 13, BLACK)
        c.disc(wx, cy - 2, 6, GREY)


# ---------------------------------------------------------------- poster
# Headlines are kept to <=15 block-font characters per line so they can
# run at scale 6 (42 px tall) inside a panel 491 px wide: at a 300 px
# thumbnail they are still ~13 px tall and readable.
PANELS = [
    (scene_summit, "TRUMP XI PUTIN", "SHENZHEN SUMMIT",
     "FIRST TRILATERAL TALKS"),
    (scene_bridge, "CRIMEAN BRIDGE", "HIT THIRD TIME",
     "TRAFFIC SUSPENDED"),
    (scene_gaza, "TANKS ENTER", "CENTRAL GAZA",
     "AID PLEA AS FLOODS HIT"),
    (scene_cyclone, "CYCLONE AKVAN", "NEARS INDIA",
     "50,000 EVACUATED"),
    (scene_vangogh, "VAN GOGH SELLS", "FOR $190.4M",
     "RECORD AT SOTHEBY'S"),
    (scene_gta, "GTA VI LAUNCHES", "WORLDWIDE",
     "BACK TO VICE CITY"),
]


def build():
    c = Canvas(W, H, INK)
    # Masthead: the day, named as large as the canvas allows.
    c.text_c("THURSDAY", W // 2, 18, 14, PAPER)
    c.rect(32, 128, W - 64, 7, RED)
    c.text_c("19 NOVEMBER 2026", W // 2, 146, 9, YELLOW)
    # Six panels in a 2x3 grid.
    grid_top, grid_bot = 224, 960
    margin, gap = 16, 10
    pw = (W - 2 * margin - gap) // 2
    ph = (grid_bot - grid_top - 2 * gap) // 3
    strip_h = 128
    for i, (scene, l1, l2, sub) in enumerate(PANELS):
        px = margin + (i % 2) * (pw + gap)
        py = grid_top + (i // 2) * (ph + gap)
        c.rect(px, py, pw, ph, (26, 36, 54))
        scene(c, px + 4, py + 4, pw - 8, ph - strip_h - 8)
        sy = py + ph - strip_h
        c.rect(px + 4, sy, pw - 8, strip_h - 4, BLACK)
        c.text_c(l1, px + pw // 2, sy + 5, 6, WHITE, tracking=0)
        c.text_c(l2, px + pw // 2, sy + 50, 6, WHITE, tracking=0)
        c.text_c(sub, px + pw // 2, sy + 94, 4, YELLOW, tracking=0)
    # Footer: the rest of the day, one breath.
    c.text_c("ANTHROPIC'S RECORD $81.3BN IPO • EU PROPOSES €45BN UKRAINE LOAN",
             W // 2, 968, 3, PAPER, tracking=0)
    c.text_c("EU APPROVES INDONESIA TRADE PACT", W // 2, 993, 3, GREY,
             tracking=0)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    n = save_png(build(), path)
    print(f"entry.png written: {n} bytes, {W}x{H}")


if __name__ == "__main__":
    main()
