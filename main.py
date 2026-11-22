#!/usr/bin/env python3
"""THE SUNDAY CHRONICLE - 22 November 2026. One-page broadsheet, stdlib only.
Draws a 1024x1024 PNG (zlib + struct, no PIL) summing up Sunday's world news.
Deterministic: fixed colours, fixed zlib level, no time/randomness.
"""
import os
import struct
import zlib

W, H = 1024, 1024

# --- palette ---
PAPER = (250, 246, 232)
INK = (18, 18, 20)
ACCENT = (158, 27, 32)      # deep red for masthead rule / labels
BLUE = (28, 68, 128)
TEAL = (16, 110, 96)
GOLD = (196, 138, 30)
GREY = (110, 108, 100)
LIGHT = (232, 226, 210)
SKY = (168, 200, 228)
GREEN = (34, 120, 60)
ORANGE = (214, 110, 30)
DARKBLUE = (20, 44, 84)

# --- canvas: flat bytearray, RGB ---
px = bytearray(W * H * 3)


def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i + 1], px[i + 2] = c


def rect(x, y, w, h, c):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            px[i], px[i + 1], px[i + 2] = c


def fill(c):
    rect(0, 0, W, H, c)


def hline(x, y, w, c, t=1):
    rect(x, y, w, t, c)


def vline(x, y, h, c, t=1):
    rect(x, y, t, h, c)


def circle(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                set_px(xx, yy, c)


def disc_ring(cx, cy, r, c, t=3):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d = (xx - cx) ** 2 + (yy - cy) ** 2
            if (r - t) ** 2 <= d <= r * r:
                set_px(xx, yy, c)


def line(x0, y0, x1, y1, c, t=1):
    dx, dy = x1 - x0, y1 - y0
    n = max(abs(dx), abs(dy), 1)
    for i in range(n + 1):
        x = x0 + dx * i // n
        y = y0 + dy * i // n
        rect(x - t // 2, y - t // 2, t, t, c)


def tri(x0, y0, x1, y1, x2, y2, c):
    # scanline fill of a triangle
    ys = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
    (ax, ay), (bx, by), (cx, cy) = ys
    for y in range(ay, cy + 1):
        def at(yv, p, q):
            if q[1] == p[1]:
                return p[0]
            return p[0] + (q[0] - p[0]) * (yv - p[1]) // (q[1] - p[1])
        xa = at(y, (ax, ay), (cx, cy))
        xb = at(y, (ax, ay), (bx, by)) if y <= by else at(y, (bx, by), (cx, cy))
        for x in range(min(xa, xb), max(xa, xb) + 1):
            set_px(x, y, c)


def write_png(path):
    raw = b"".join(b"\x00" + bytes(px[y * W * 3:(y + 1) * W * 3]) for y in range(H))
    comp = zlib.compress(raw, 6)

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", ihdr)
    data += chunk(b"IDAT", comp)
    data += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(data)


# --- 5x7 bitmap font: each glyph is 7 rows of 5 bits ("#" = on) ---
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
}

# accented / special letters map to plain ones
FOLD = {"É": "E", "Ä": "A", "Ö": "O", "Ü": "U", "–": "-", "—": "-", "’": "'",
        "‘": "'", "“": '"', "”": '"', "…": ".", "€": "E", "£": "L"}


def text_w(s, scale):
    return sum((6 if ch != " " else 6) for ch in s) * scale - scale


def draw_text(x, y, s, scale, c):
    """Draw text at (x, y); returns width drawn. Uppercase enforced."""
    s = "".join(FOLD.get(ch, ch) for ch in s.upper())
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT["?"])
        for r in range(7):
            row = g[r]
            for col in range(5):
                if row[col] == "1":
                    rect(cx + col * scale, y + r * scale, scale, scale, c)
        cx += 6 * scale
    return cx - x


def text_h(scale):
    return 7 * scale


def wrap(s, scale, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_w(t, scale) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(x, y, lines, scale, c, leading=None):
    lh = leading if leading is not None else 7 * scale + 2
    for i, ln in enumerate(lines):
        draw_text(x, y + i * lh, ln, scale, c)
    return y + len(lines) * lh


def draw_center(x, y, w, s, scale, c):
    tw = text_w(s, scale)
    draw_text(x + max(0, (w - tw) // 2), y, s, scale, c)


# --- 5x7 bitmap font: each glyph is 7 rows of 5 bits ("#" = on) ---
# --- pictograms: each draws into box (x, y, w, h) ---
def pic_globe(x, y, w, h, c1=TEAL, c2=BLUE):
    cx, cy, r = x + w // 2, y + h // 2, min(w, h) // 2 - 2
    circle(cx, cy, r, SKY)
    circle(cx, cy, r - 3, c1)
    # land blobs
    circle(cx - r // 3, cy - r // 4, r // 3, GREEN)
    circle(cx + r // 3, cy + r // 4, r // 4, GREEN)
    disc_ring(cx, cy, r, c2, 3)
    # crack across the globe
    line(cx - r + 4, cy - r // 3, cx, cy + r // 4, INK, 3)
    line(cx, cy + r // 4, cx + r - 6, cy - r // 2, INK, 3)
    # smoke puffs
    circle(cx - r // 2, cy - r - 2, 4, GREY)
    circle(cx + r // 4, cy - r - 4, 5, GREY)


def pic_missile(x, y, w, h, c1=ACCENT):
    cx, cy = x + w // 2, y + h // 2
    tri(cx, y + 4, cx - 10, cy - 2, cx + 10, cy - 2, c1)
    rect(cx - 10, cy - 2, 20, 26, c1)
    tri(cx - 10, cy + 8, cx - 20, cy + 22, cx - 10, cy + 18, c1)
    tri(cx + 10, cy + 8, cx + 20, cy + 22, cx + 10, cy + 18, c1)
    tri(cx - 6, cy + 24, cx, cy + 40, cx + 6, cy + 24, GOLD)
    circle(cx, cy + 8, 3, PAPER)


def pic_tanker(x, y, w, h, c1=DARKBLUE):
    cx, cy = x + w // 2, y + h // 2 + 6
    rect(x + 6, cy - 8, w - 12, 20, c1)
    rect(x + 14, cy - 22, 12, 14, ACCENT)
    rect(x + w // 2 - 4, cy - 30, 8, 22, c1)
    line(x + 6, cy + 12, x + w - 6, cy + 12, BLUE, 3)
    line(x + 12, cy + 18, x + w - 12, cy + 18, BLUE, 2)
    circle(x + w - 18, cy - 26, 7, GOLD)
    # flame on deck
    tri(x + w - 24, cy - 14, x + w - 12, cy - 14, x + w - 18, cy - 26, ORANGE)


def pic_building(x, y, w, h, c1=GREY):
    cx = x + w // 2
    rect(cx - 24, y + 8, 48, h - 16, c1)
    rect(cx - 24, y + 8, 48, 6, INK)
    for r in range(4):
        for cc in range(3):
            rect(cx - 18 + cc * 14, y + 20 + r * 12, 8, 8,
                 GOLD if (r + cc) % 2 else PAPER)
    # crack
    line(cx + 6, y + 10, cx - 2, y + h // 2, INK, 2)
    line(cx - 2, y + h // 2, cx + 8, y + h - 10, INK, 2)


def pic_court(x, y, w, h, c1=BLUE):
    cx, cy = x + w // 2, y + h // 2
    tri(x + 6, cy - 14, cx, cy - 34, x + w - 6, cy - 14, c1)
    rect(x + 8, cy - 14, w - 16, 6, c1)
    for i in range(4):
        rect(x + 12 + i * (w - 24) // 3, cy - 8, 7, 26, c1)
    rect(x + 6, cy + 18, w - 12, 6, c1)
    rect(x + 2, cy + 24, w - 4, 5, INK)


def pic_factory(x, y, w, h, c1=ORANGE):
    cx, cy = x + w // 2, y + h // 2
    rect(x + 8, cy, w - 16, h // 2 - 4, c1)
    rect(x + 8, cy - 14, 10, 18, INK)
    rect(x + 24, cy - 14, 10, 18, INK)
    tri(x + 8, cy, cx, cy - 16, x + w - 8, cy, GOLD)
    circle(x + 13, cy - 22, 4, GREY)
    circle(x + 29, cy - 28, 5, GREY)
    for i in range(3):
        rect(x + 14 + i * 14, cy + 8, 8, 8, PAPER)


def pic_boat(x, y, w, h, c1=TEAL):
    cx, cy = x + w // 2, y + h // 2 + 4
    tri(cx - 26, cy, cx + 26, cy, cx, cy + 16, c1)
    rect(cx - 2, cy - 26, 4, 26, INK)
    tri(cx + 2, cy - 26, cx + 26, cy - 6, cx + 2, cy - 6, ACCENT)
    line(x + 4, cy + 22, x + w - 4, cy + 22, BLUE, 3)
    line(x + 12, cy + 28, x + w - 12, cy + 28, BLUE, 2)


def pic_database(x, y, w, h, c1=DARKBLUE):
    cx, cy = x + w // 2, y + h // 2
    for i in range(3):
        rect(cx - 22, cy - 22 + i * 16, 44, 13, c1)
        line(cx - 16, cy - 15 + i * 16, cx + 16, cy - 15 + i * 16, PAPER, 2)
    # warning triangle
    tri(cx + 16, cy + 18, cx + 34, cy + 18, cx + 25, cy + 2, GOLD)
    rect(cx + 23, cy + 8, 4, 6, INK)
    rect(cx + 23, cy + 15, 4, 3, INK)


def pic_dove(x, y, w, h, c1=PAPER):
    cx, cy = x + w // 2, y + h // 2
    # body: plump ellipse built from stacked bars
    rect(cx - 22, cy - 4, 44, 14, c1)
    circle(cx - 8, cy + 2, 12, c1)
    circle(cx + 12, cy, 8, c1)
    disc_ring(cx - 8, cy + 2, 12, INK, 2)
    # head + beak
    circle(cx + 20, cy - 8, 7, c1)
    disc_ring(cx + 20, cy - 8, 7, INK, 2)
    circle(cx + 22, cy - 10, 2, INK)
    tri(cx + 26, cy - 9, cx + 34, cy - 6, cx + 26, cy - 4, GOLD)
    # raised wing
    tri(cx - 16, cy - 2, cx - 2, cy - 24, cx + 6, cy - 2, c1)
    line(cx - 14, cy - 4, cx - 2, cy - 22, INK, 2)
    # tail
    tri(cx - 22, cy + 2, cx - 36, cy + 12, cx - 20, cy + 10, c1)
    # olive branch
    line(cx - 30, cy + 22, cx - 6, cy + 16, GREEN, 3)
    circle(cx - 20, cy + 18, 4, GREEN)
    circle(cx - 12, cy + 16, 4, GREEN)


def pic_chart(x, y, w, h, c1=ACCENT):
    cx, cy = x + w // 2, y + h // 2
    line(x + 8, y + 8, x + 8, y + h - 8, INK, 2)
    line(x + 8, y + h - 8, x + w - 8, y + h - 8, INK, 2)
    for i, ht in enumerate((26, 20, 14, 8)):
        rect(x + 16 + i * 14, y + h - 10 - ht, 10, ht, c1 if i > 1 else BLUE)
    line(x + 14, y + 14, x + w - 10, y + h - 18, c1, 3)


def pic_game(x, y, w, h, c1=DARKBLUE):
    cx, cy = x + w // 2, y + h // 2
    rect(cx - 28, cy - 12, 56, 26, c1)
    circle(cx - 28, cy + 2, 12, c1)
    circle(cx + 28, cy + 2, 12, c1)
    rect(cx - 20, cy - 4, 12, 4, PAPER)
    rect(cx - 16, cy - 8, 4, 12, PAPER)
    for dx, dy in ((12, -6), (20, 2), (12, 6)):
        circle(cx + dx, cy + dy, 3, GOLD)
    rect(cx - 30, cy - 18, 60, 4, GOLD)


def pic_castle(x, y, w, h, c1=ACCENT):
    cx, cy = x + w // 2, y + h // 2 + 8
    rect(cx - 26, cy - 10, 52, 22, c1)
    rect(cx - 30, cy - 26, 12, 38, c1)
    rect(cx + 18, cy - 26, 12, 38, c1)
    tri(cx - 20, cy - 10, cx, cy - 30, cx + 20, cy - 10, GOLD)
    rect(cx - 32, cy - 32, 16, 6, INK)
    rect(cx + 16, cy - 32, 16, 6, INK)
    rect(cx - 4, cy + 2, 8, 10, INK)
    circle(cx, cy - 38, 6, GOLD)


def pic_ball(x, y, w, h, c1=INK):
    cx, cy = x + w // 2, y + h // 2
    circle(cx, cy, 20, PAPER)
    disc_ring(cx, cy, 20, c1, 3)
    for ang in range(5):
        import math
        a = ang * 2 * math.pi / 5 - math.pi / 2
        line(cx, cy, cx + int(20 * math.cos(a)), cy + int(20 * math.sin(a)), c1, 2)
    circle(cx, cy, 5, c1)


def pic_handcuffs(x, y, w, h, c1=GREY):
    cx, cy = x + w // 2, y + h // 2
    disc_ring(cx - 16, cy, 14, c1, 5)
    disc_ring(cx + 16, cy, 14, c1, 5)
    line(cx - 6, cy - 6, cx + 6, cy + 6, INK, 4)
    line(cx - 6, cy + 6, cx + 6, cy - 6, INK, 4)


def pic_flag(x, y, w, h, c1=BLUE):
    cx, cy = x + w // 2, y + h // 2
    rect(cx - 2, cy - 26, 4, 52, INK)
    tri(cx + 2, cy - 26, cx + 30, cy - 16, cx + 2, cy - 6, c1)
    tri(cx + 2, cy - 6, cx + 30, cy + 4, cx + 2, cy + 14, PAPER)
    circle(cx + 12, cy - 16, 3, GOLD)


def pic_map(x, y, w, h, c1=ACCENT):
    cx, cy = x + w // 2, y + h // 2
    # Poland-ish outline: simple blocky shape
    rect(cx - 22, cy - 14, 44, 24, c1)
    rect(cx - 14, cy - 22, 28, 10, c1)
    rect(cx + 8, cy + 10, 14, 8, c1)
    disc_ring(cx, cy - 2, 12, PAPER, 3)
    circle(cx, cy - 2, 3, PAPER)
    line(cx - 22, cy + 22, cx + 22, cy + 22, INK, 2)


# --- content (facts exactly as briefed) ---
LEAD_HEAD = ["COP31 TALKS", "COLLAPSE"]
LEAD_SUMMARY = ("No deal after 44 hours of overtime. The EU, Panama, the "
                "Marshall Islands, the UK and Norway rejected a draft with "
                "no mention of fossil fuels. First summit with no headline "
                "deal since Copenhagen 2009.")

# (headline, caption, picture fn) — 15 pictured stories besides the lead
GRID = [
    ("IRAN STRIKES", "BAHRAIN", "Missiles hit Sitra site; 2 hurt, one critical.", pic_missile),
    ("TANKERS HIT", "AT HORMUZ", "Iran struck three tankers near the strait.", pic_tanker),
    ("MISSILE HITS", "KRYVYI RIH", "Boy, 7, and woman, 20, killed; 60 hurt.", pic_building),
    ("KYIV FLAT", "COLLAPSES", "Drone hit a 5-storey block; 14 missing.", pic_building),
    ("MISSILES LAND", "IN POLAND", "NATO chief calls it a grave violation.", pic_map),
    ("EL CHAPO", "CAPTURED", "Cartel boss Isidro seized in Sinaloa; 11 killed.", pic_handcuffs),
    ("WORLD COURT", "GENOCIDE", "ICJ: Myanmar committed genocide in 2017.", pic_court),
    ("FACTORY FIRE", "IN INDONESIA", "Candy factory fire: 3 dead, 36 missing.", pic_factory),
    ("BOAT CAPSIZES", "IN NIGERIA", "At least 24 dead on way to a funeral.", pic_boat),
    ("FBI DATABASE", "BREACH", "NCIC crime records probed after breach.", pic_database),
    ("GAZA: FOUR", "MORE KILLED", "Israeli fire kills four in Gaza.", pic_dove),
    ("STOCKS FALL", "CORRECTION", "S&P down 3.7%, Nasdaq down 5.3% Friday.", pic_chart),
    ("GTA 6'S RECORD", "LAUNCH", "$3.79bn on launch day, a game record.", pic_game),
    ("SHURI CASTLE", "REBORN", "Okinawa hall restored, 7 years after fire.", pic_castle),
    ("LEEDS STUN", "CHELSEA", "Leeds win 4-1 at Stamford Bridge.", pic_ball),
]

# (one scale-2 line per story: headline + key fact) — 14 text-only stories
TEXT_ONLY = [
    "EU-INDONESIA DEAL: TARIFFS CUT ON 98.5%",
    "UK AND EU REBUILD TIES AFTER BREXIT",
    "HOUTHIS FIRE ON SAUDI ARABIA",
    "TRUMP: PERMANENT IRAN DEAL",
    "BLAST AT IRAQ POWER PLANT: 4 DEAD",
    "SEOUL EDUCATION CHIEF QUITS",
    "EU PROPOSES BIG TECH TAX",
    "FRANCE PROTESTS, SIXTH WEEKEND",
    "SPAIN HEADS TO THE POLLS",
    "BELGIUM FACES AIR SHUTDOWN",
    "AMAZON'S $7.5BN AI BET",
    "IBM'S 520-QUBIT CHIP",
    "MERCURY'S NEW VISITORS",
    "A LEADER REMEMBERED, AGED 71",
]


def trunc(s, scale, max_w):
    s = "".join(FOLD.get(ch, ch) for ch in s.upper())
    while s and text_w(s, scale) > max_w:
        s = s[:-1]
    return s


def draw_page():
    # ---- masthead ----
    draw_center(0, 14, W, "THE SUNDAY CHRONICLE", 5, INK)
    draw_center(0, 58, W, "SUNDAY 22 NOVEMBER 2026", 2, ACCENT)
    draw_center(0, 76, W, "ONE DAY'S WORLD NEWS, IN ONE PICTURE", 2, GREY)
    hline(16, 96, W - 32, ACCENT, 4)
    hline(16, 102, W - 32, INK, 2)

    # ---- lead panel ----
    lx, ly, lw, lh = 16, 110, W - 32, 256
    rect(lx, ly, lw, lh, LIGHT)
    rect(lx, ly, lw, 3, ACCENT)
    rect(lx, ly + lh - 3, lw, 3, ACCENT)
    # lead picture (left)
    pic_globe(lx + 14, ly + 30, 300, 190)
    draw_center(lx + 14, ly + 226, 300, "ANTALYA, TURKEY", 2, GREY)
    # lead kicker + headline + summary (right)
    tx = lx + 330
    tw = lw - 330 - 20
    draw_text(tx, ly + 14, "CLIMATE", 2, ACCENT)
    draw_text(tx, ly + 14 + 22, "LONGEST COP IN HISTORY: 44 HOURS OF OVERTIME", 1, GREY)
    y = ly + 52
    for ln in LEAD_HEAD:
        draw_text(tx, y, ln, 4, INK)
        y += 34
    y += 6
    y = draw_lines(tx, y, wrap(LEAD_SUMMARY, 2, tw), 2, INK, leading=18)
    y += 10
    draw_text(tx, y, "SAUDI ARABIA AND OIL PRODUCERS LOBBIED", 1, GREY)
    draw_text(tx, y + 10, "TO KEEP FOSSIL FUELS OUT OF THE TEXT.", 1, GREY)

    # ---- pictured grid ----
    gy = 378
    draw_text(16, gy, "THE WORLD IN BRIEF", 2, ACCENT)
    hline(16, gy + 18, W - 32, INK, 2)
    cols, rows = 5, 3
    gap = 8
    pw = (W - 32 - (cols - 1) * gap) // cols
    ph = 128
    gy0 = gy + 26
    for i, (h1, h2, cap, pic) in enumerate(GRID):
        r, c = divmod(i, cols)
        x = 16 + c * (pw + gap)
        yy = gy0 + r * (ph + gap)
        rect(x, yy, pw, ph, PAPER)
        vline(x, yy, ph, INK, 1)
        vline(x + pw - 1, yy, ph, INK, 1)
        hline(x, yy, pw, INK, 1)
        hline(x, yy + ph - 1, pw, INK, 1)
        pic(x + 8, yy + 4, pw - 16, 56)
        hy = yy + 62
        draw_text(x + 8, hy, trunc(h1, 2, pw - 16), 2, INK)
        draw_text(x + 8, hy + 15, trunc(h2, 2, pw - 16), 2, INK)
        cy2 = hy + 32
        for ln in wrap(cap, 1, pw - 16)[:2]:
            draw_text(x + 8, cy2, ln, 1, GREY)
            cy2 += 9

    # ---- text-only columns: one bold scale-2 line per story ----
    ty = gy0 + rows * (ph + gap) + 6
    draw_text(16, ty, "MORE FROM SUNDAY", 2, ACCENT)
    hline(16, ty + 18, W - 32, INK, 2)
    colw = (W - 32 - 16) // 2
    for i, line1 in enumerate(TEXT_ONLY):
        col, row = divmod(i, 7)
        x = 16 + col * (colw + 16)
        y = ty + 26 + row * 22
        rect(x, y + 2, 8, 8, ACCENT)
        draw_text(x + 14, y, trunc(line1, 2, colw - 14), 2, INK)
    # ---- footer: sources ----
    fy = ty + 26 + 7 * 22 + 6
    hline(16, fy, W - 32, INK, 2)
    draw_center(0, fy + 8, W, "SOURCES: REUTERS - AP - AFP - CNN - WION - RAPPLER - SKY SPORTS", 1, GREY)


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    fill(PAPER)
    draw_page()
    write_png(os.path.join(outdir, "entry.png"))


if __name__ == "__main__":
    main()
