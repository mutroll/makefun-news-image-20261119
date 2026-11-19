#!/usr/bin/env python3
"""news-image-20261119 entry: one image that sums up the world news of
Thursday 19 November 2026, written to /output/entry.png.

The front page is drawn from scratch with the Python 3.13 standard
library only: a small RGB framebuffer, a hand-made 5x7 bitmap typeface
and a minimal PNG writer (struct + zlib). No network, no randomness,
no clock: two runs produce byte-identical output.

When run outside the grading sandbox, MAKEFUN_OUTPUT_DIR overrides
the /output directory.
"""

import math
import os
import struct
import zlib

SIZE = 1024

# ------------------------------------------------------------------ palette
PAPER = (243, 238, 226)      # warm newsprint
CARD = (252, 250, 243)       # panel paper
INK = (26, 24, 22)           # near-black
NAVY = (23, 34, 64)          # masthead band
GOLD = (186, 138, 44)
CRIMSON = (158, 36, 32)
TEAL = (18, 102, 110)
SKYBLUE = (44, 96, 152)
OLIVE = (84, 110, 44)
PLUM = (96, 52, 110)
SAND = (214, 196, 158)
SEA = (62, 118, 168)
PINK = (232, 168, 188)
BLOSSOM = (250, 244, 238)
WHITE = (255, 255, 255)
GREY = (110, 106, 98)

# ------------------------------------------------------------------ typeface
# 5 columns x 7 rows per glyph; '#' is a filled cell.

GLYPHS = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#....", "#....", "#....", "#....", "#....", ".###."),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#.#.#", "#..##", "#...#", "#...#"),
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
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "2": (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
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
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".....", ".##..", ".##.."),
    "'": (".##..", ".##..", ".#...", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": (".##..", "..#..", "...#.", "...#.", "...#.", "..#..", ".##.."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#..##"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
}


def measure(s, scale, bold=False):
    """Pixel width of a string in the bitmap typeface."""
    if not s:
        return 0
    extra = max(1, scale // 3) if bold else 0
    return len(s) * 6 * scale - scale + extra


def wrap(s, scale, max_px, bold=False):
    """Split s into lines that each fit within max_px."""
    out = []
    line = ""
    for word in s.split(" "):
        trial = word if not line else line + " " + word
        if measure(trial, scale, bold) <= max_px:
            line = trial
        else:
            if line:
                out.append(line)
            line = word
    if line:
        out.append(line)
    return out


# ------------------------------------------------------------------ canvas

class Page:
    """A SIZE x SIZE RGB framebuffer with simple drawing tools."""

    def __init__(self, bg):
        self.pix = bytearray(bg) * (SIZE * SIZE)

    def dot(self, x, y, col):
        if 0 <= x < SIZE and 0 <= y < SIZE:
            i = (y * SIZE + x) * 3
            self.pix[i] = col[0]
            self.pix[i + 1] = col[1]
            self.pix[i + 2] = col[2]

    def box(self, x, y, w, h, col):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(SIZE, x + w), min(SIZE, y + h)
        if x0 >= x1 or y0 >= y1:
            return
        row = bytes(col) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * SIZE + x0) * 3
            self.pix[i:i + len(row)] = row

    def outline(self, x, y, w, h, col, t=2):
        self.box(x, y, w, t, col)
        self.box(x, y + h - t, w, t, col)
        self.box(x, y, t, h, col)
        self.box(x + w - t, y, t, h, col)

    def seg(self, x0, y0, x1, y1, col, t=3):
        """Thick line via Bresenham with a square brush."""
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        r = max(0, t // 2)
        while True:
            self.box(x0 - r, y0 - r, 2 * r + 1, 2 * r + 1, col)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, col):
        for yy in range(cy - r, cy + r + 1):
            span = math.isqrt(max(0, r * r - (yy - cy) ** 2))
            self.box(cx - span, yy, 2 * span + 1, 1, col)

    def tri(self, pts, col):
        """Filled polygon by scanline (works for any simple polygon)."""
        lo = min(p[1] for p in pts)
        hi = max(p[1] for p in pts)
        n = len(pts)
        for yy in range(lo, hi + 1):
            hits = []
            for i in range(n):
                ax, ay = pts[i]
                bx, by = pts[(i + 1) % n]
                if (ay <= yy < by) or (by <= yy < ay):
                    hits.append(ax + (yy - ay) * (bx - ax) // (by - ay))
            hits.sort()
            for i in range(0, len(hits) - 1, 2):
                self.box(hits[i], yy, hits[i + 1] - hits[i] + 1, 1, col)

    def txt(self, x, y, s, scale, col, bold=False):
        dx = max(1, scale // 3) if bold else 0
        cx = x
        for ch in s:
            glyph = GLYPHS.get(ch, GLYPHS[" "])
            for r in range(7):
                for c in range(5):
                    if glyph[r][c] == "#":
                        self.box(cx + c * scale, y + r * scale,
                                 scale, scale, col)
                        if dx:
                            self.box(cx + c * scale + dx, y + r * scale,
                                     scale, scale, col)
            cx += 6 * scale
        return cx - x

    def centered(self, y, s, scale, col, bold=False):
        self.txt((SIZE - measure(s, scale, bold)) // 2, y, s, scale,
                 col, bold)

    def block(self, x, y, s, scale, col, max_px, line_h, bold=False,
              limit=None):
        lines = wrap(s, scale, max_px, bold)
        if limit is not None:
            lines = lines[:limit]
        for i, ln in enumerate(lines):
            self.txt(x, y + i * line_h, ln, scale, col, bold)
        return len(lines)


# ------------------------------------------------------------------ icons
# Grid icons live in a ~92 x 62 box at (x, y); the lead and wide icons
# get their own larger stages.

def icon_bridge(pg, x, y):
    # Kerch bridge: a great arch over the fairway, its middle span
    # dropped into the sea.
    cx, cy = x + 46, y + 38                    # arch centre, deck level
    for a in range(33):
        ang = math.pi * a / 32
        px = int(cx + 27 * math.cos(ang))
        py = int(cy - 25 * math.sin(ang))
        pg.disc(px, py, 2, INK)
    for hx in (cx - 18, cx + 18):              # hangers arch -> deck
        top = int(cy - 25 * math.sqrt(max(0.0, 1 - (18 / 27) ** 2)))
        pg.seg(hx, top, hx, cy, GREY, 2)
    pg.box(x + 0, y + 36, 37, 6, INK)          # deck, left of the gap
    pg.box(x + 55, y + 36, 37, 6, INK)         # deck, right of the gap
    pg.box(x + 8, y + 42, 5, 10, INK)          # piers
    pg.box(x + 79, y + 42, 5, 10, INK)
    pg.seg(x + 38, y + 39, x + 54, y + 53, CRIMSON, 6)  # fallen span
    for i, wx in enumerate(range(x + 0, x + 86, 14)):
        wy = y + 56 + (3 if i % 2 else 0)
        pg.seg(wx, wy, wx + 9, wy - 3, SEA, 3)


def icon_tank_tent(pg, x, y):
    # a tank beside a flooded refugee tent, rain coming down
    for rx in (x + 62, x + 72, x + 82, x + 90):
        pg.seg(rx, y + 2, rx - 3, y + 10, SKYBLUE, 2)
    # tank: tracks, hull, turret, barrel pointing right
    pg.box(x + 2, y + 42, 46, 11, INK)
    for wx in (x + 9, x + 22, x + 35):
        pg.disc(wx, y + 47, 4, GREY)
    pg.tri([(x + 6, y + 42), (x + 13, y + 31), (x + 42, y + 31),
            (x + 48, y + 42)], INK)
    pg.box(x + 19, y + 22, 20, 10, INK)
    pg.seg(x + 39, y + 26, x + 56, y + 22, INK, 4)
    # tent: triangle with a door, standing in flood water
    pg.tri([(x + 58, y + 53), (x + 75, y + 26), (x + 92, y + 53)], TEAL)
    pg.tri([(x + 70, y + 53), (x + 75, y + 40), (x + 80, y + 53)], CARD)
    pg.box(x + 56, y + 55, 38, 3, SEA)
    pg.box(x + 60, y + 59, 32, 3, SEA)


def icon_cyclone(pg, x, y):
    # a spiral storm over waves
    cx, cy = x + 45, y + 26
    steps = 90
    for i in range(steps):
        t = i / steps
        ang = t * 4.4 * math.pi
        rad = 3 + t * 24
        px = int(cx + rad * math.cos(ang))
        py = int(cy + rad * math.sin(ang) * 0.72)
        pg.disc(px, py, 3, TEAL if i % 3 else NAVY)
    pg.disc(cx, cy, 4, CARD)
    for i, wx in enumerate(range(x + 2, x + 86, 14)):
        wy = y + 54 + (3 if i % 2 else 0)
        pg.seg(wx, wy, wx + 9, wy - 3, SEA, 3)


def icon_painting(pg, x, y):
    # a framed blossoming chestnut tree, and the auctioneer's gavel
    pg.box(x + 6, y + 0, 62, 52, GOLD)
    pg.box(x + 10, y + 4, 54, 44, (196, 220, 235))
    pg.seg(x + 37, y + 48, x + 37, y + 30, (90, 64, 40), 4)
    pg.seg(x + 37, y + 36, x + 26, y + 24, (90, 64, 40), 3)
    pg.seg(x + 37, y + 34, x + 48, y + 22, (90, 64, 40), 3)
    for (bx, by, r) in [(30, 20, 7), (44, 16, 8), (36, 10, 6),
                        (24, 28, 5), (50, 27, 5), (42, 26, 5)]:
        pg.disc(x + bx, y + by, r, BLOSSOM)
        pg.disc(x + bx, y + by, max(2, r - 3), PINK)
    pg.box(x + 10, y + 42, 54, 6, OLIVE)
    # gavel, bottom right
    pg.seg(x + 76, y + 34, x + 88, y + 48, (90, 64, 40), 4)
    pg.box(x + 68, y + 26, 16, 9, INK)


def icon_summit(pg, x, y):
    # three leaders under their flags, shaking hands over one table
    for i, col in enumerate([CRIMSON, GOLD, SKYBLUE]):
        fx = x + 30 + i * 52
        pg.box(fx + 12, y + 0, 3, 24, INK)         # flag pole
        pg.box(fx + 15, y + 0, 22, 13, col)        # flag
    for i, col in enumerate([CRIMSON, NAVY, SKYBLUE]):
        fx = x + 30 + i * 52
        pg.disc(fx + 12, y + 40, 10, INK)          # head
        pg.box(fx, y + 52, 24, 36, col)            # body
    # arms reaching in to a shared handshake at the centre
    pg.seg(x + 52, y + 62, x + 88, y + 74, INK, 5)
    pg.seg(x + 150, y + 62, x + 104, y + 74, INK, 5)
    pg.seg(x + 107, y + 58, x + 97, y + 74, INK, 5)
    pg.disc(x + 96, y + 75, 6, INK)
    pg.box(x + 12, y + 90, 166, 6, INK)            # table line


def icon_vicecity(pg, x, y):
    # Vice City: skyline, a big sun and two palms (wide panel stage)
    pg.disc(x + 118, y + 26, 20, (240, 160, 60))
    heights = [26, 40, 32, 48, 36, 44, 28]
    for i, hh in enumerate(heights):
        bx = x + 6 + i * 17
        pg.box(bx, y + 62 - hh, 14, hh, NAVY)
        pg.box(bx + 3, y + 62 - hh + 6, 3, 3, GOLD)
        pg.box(bx + 9, y + 62 - hh + 14, 3, 3, GOLD)
    pg.box(x + 0, y + 62, 150, 4, INK)
    for base_x, lean in [(x + 132, 6), (x + 20, -5)]:
        top_x = base_x + lean
        pg.seg(base_x, y + 62, top_x, y + 24, (90, 64, 40), 4)
        for ang in (-0.9, -0.4, 0.1, 0.6, 1.1):
            ex = int(top_x + 17 * math.cos(ang - 1.2))
            ey = int(y + 24 + 10 * math.sin(ang - 1.2)) + 4
            pg.seg(top_x, y + 24, ex, ey, OLIVE, 3)


# ------------------------------------------------------------------ stories

LEAD = (
    "SHENZHEN SUMMIT", CRIMSON, icon_summit,
    "TRUMP, XI AND PUTIN SIT DOWN TOGETHER",
    "THE FIRST TRILATERAL MEETING OF THE US, CHINESE AND RUSSIAN "
    "PRESIDENTS, AT THE APEC SUMMIT IN SHENZHEN.",
)

PANELS = [
    ("UKRAINE", SKYBLUE, icon_bridge,
     "CRIMEAN BRIDGE HIT A 3RD TIME",
     "TRAFFIC HALTED AFTER THE LATEST STRIKE. TUESDAY'S BLAST FELLED "
     "A 227M ROAD SPAN INTO THE SEA."),
    ("GAZA", TEAL, icon_tank_tent,
     "GAZA TRUCE LINE CROSSED",
     "FIRST BIG GROUND PUSH SINCE THE TRUCE: NUSEIRAT, BUREIJ. "
     "FLOODS WRECK 6,000 SHELTERS."),
    ("INDIA", OLIVE, icon_cyclone,
     "CYCLONE AKVAN BEARS DOWN",
     "50,000 PEOPLE EVACUATED IN ODISHA. LANDFALL DUE FRIDAY NOON "
     "BETWEEN NARSAPUR AND PURI."),
    ("ARTS", PLUM, icon_painting,
     "VAN GOGH SETS A RECORD",
     "'BLOSSOMING CHESTNUT TREES' FETCHES $190.4M AT SOTHEBY'S NEW "
     "YORK; NAZI-ERA CLAIM SETTLED."),
]

WIDE = (
    "GAMES", PLUM, icon_vicecity,
    "GTA VI RETURNS TO VICE CITY",
    "A 13-YEAR WAIT ENDS AS IT UNLOCKS FROM NEW ZEALAND WESTWARD; "
    "REVIEWS: 99/100.",
)

FOOTER = ("ALSO TODAY: ANTHROPIC IPO RAISES A RECORD $81.3BN - EU "
          "PROPOSES A 45BN-EURO UKRAINE LOAN - EU SEALS INDONESIA "
          "TRADE PACT")


# ------------------------------------------------------------------ layout

def masthead(pg):
    pg.box(0, 0, SIZE, SIZE, PAPER)
    pg.outline(10, 10, SIZE - 20, SIZE - 20, INK, 3)
    pg.outline(17, 17, SIZE - 34, SIZE - 34, INK, 1)
    pg.box(24, 24, SIZE - 48, 150, NAVY)
    pg.centered(32, "THE DAILY PICTURE OF THE WORLD'S NEWS", 3, SAND,
                bold=True)
    pg.centered(56, "ONE DAY, ONE WORLD", 9, WHITE, bold=True)
    pg.box(120, 126, SIZE - 240, 3, GOLD)
    pg.centered(134, "THURSDAY 19 NOVEMBER 2026", 5, GOLD, bold=True)


def lead_panel(pg, x, y, w, h, story):
    cat, col, icon, head, cap = story
    pg.box(x, y, w, h, CARD)
    pg.outline(x, y, w, h, INK, 2)
    pg.box(x, y, measure(cat, 3, True) + 26, 26, col)
    pg.txt(x + 12, y + 4, cat, 3, WHITE, bold=True)
    icon(pg, x + 16, y + 38)
    pg.block(x + 224, y + 30, head, 5, INK, w - 224 - 16, 40, bold=True,
             limit=2)
    pg.block(x + 224, y + 110, cap, 3, INK, w - 224 - 16, 24, limit=3)


def grid_panel(pg, x, y, w, h, story):
    cat, col, icon, head, cap = story
    pg.box(x, y, w, h, CARD)
    pg.outline(x, y, w, h, INK, 2)
    pg.box(x, y, w, 24, col)
    pg.txt(x + 10, y + 3, cat, 3, WHITE, bold=True)
    icon(pg, x + 12, y + 32)
    pg.block(x + 116, y + 30, head, 4, INK, w - 116 - 12, 31, bold=True,
             limit=2)
    pg.block(x + 12, y + 98, cap, 3, INK, w - 24, 25, limit=4)


def wide_panel(pg, x, y, w, h, story):
    cat, col, icon, head, cap = story
    pg.box(x, y, w, h, CARD)
    pg.outline(x, y, w, h, INK, 2)
    pg.box(x, y, 120, 24, col)
    pg.txt(x + 10, y + 3, cat, 3, WHITE, bold=True)
    icon(pg, x + 806, y + 28)
    pg.block(x + 14, y + 30, head, 4, INK, 780, 31, bold=True, limit=1)
    pg.block(x + 14, y + 60, cap, 3, INK, 780, 25, limit=2)


def build():
    pg = Page(PAPER)
    masthead(pg)
    lead_panel(pg, 24, 184, 976, 184, LEAD)
    pw, ph = 482, 202
    for i, story in enumerate(PANELS):
        x = 24 + (i % 2) * (pw + 12)
        y = 380 + (i // 2) * (ph + 10)
        grid_panel(pg, x, y, pw, ph, story)
    wide_panel(pg, 24, 806, 976, 110, WIDE)
    fy = 926
    pg.box(24, fy, SIZE - 48, 74, INK)
    pg.block(38, fy + 5, FOOTER, 3, WHITE, SIZE - 76, 23, limit=3)
    return pg


# ------------------------------------------------------------------ png out

def png_bytes(pg):
    def chunk(tag, data):
        body = tag + data
        return (struct.pack(">I", len(data)) + body
                + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF))

    raw = bytearray()
    stride = SIZE * 3
    for yy in range(SIZE):
        raw.append(0)
        raw += pg.pix[yy * stride:(yy + 1) * stride]
    out = b"\x89PNG\r\n\x1a\n"
    out += chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8, 2, 0, 0, 0))
    out += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    out += chunk(b"IEND", b"")
    return out


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "entry.png"), "wb") as fh:
        fh.write(png_bytes(build()))


if __name__ == "__main__":
    main()
