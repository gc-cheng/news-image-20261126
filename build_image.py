#!/usr/bin/env python3
"""Draw the news-image-20261126 front page, with PIL.

A one-day newspaper front page, "THE WORLD IN ONE DAY", for Thursday
26 November 2026: 50 stories in 10 regions and 20 fields, every one
happened or first reported on that day (checked against Reuters, AP,
AFP, Yonhap, Xinhua, Al Jazeera, Haaretz, France24 and the wires).
Three big illustrated features, ten illustrated cards, a world map and
a numbered list of 37 more stories, plus a date check naming the
near-miss stories that were left out because they belong to other days.

No network, no clock, no randomness: two runs write byte-identical PNG.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent

W = H = 1024
PAPER = (248, 244, 236)
INK = (18, 18, 18)
SOFT = (92, 88, 80)
FAINT = (182, 176, 164)
NAVY = (14, 40, 72)
RED = (176, 30, 20)
GOLD = (255, 213, 0)
SKY = (168, 208, 224)
SEA = (46, 110, 158)
DARK = (16, 24, 38)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

REGION_COLORS = {
    "N. AMERICA": (30, 80, 140),
    "LATIN AMERICA": (176, 104, 0),
    "EUROPE": (16, 42, 74),
    "MIDDLE EAST": (176, 30, 20),
    "N. AFRICA": (150, 40, 90),
    "SUB-SAHARAN AFRICA": (36, 112, 74),
    "SOUTH ASIA": (190, 60, 110),
    "EAST & SE ASIA": (14, 92, 92),
    "OCEANIA": (96, 64, 140),
    "GLOBAL": (90, 88, 84),
}


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, max_w):
    """Greedy wrap; returns list of lines, never wider than max_w."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        cur = ""
        for w in words:
            trial = (cur + " " + w).strip()
            if d.textlength(trial, font=fnt) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    return lines


def put_lines(d, x, y, text, fnt, max_w, fill=INK, gap=1.18, limit=None):
    """Draw wrapped text; truncate the last line with ... if over limit."""
    lines = wrap(d, text, fnt, max_w)
    if limit is not None and len(lines) > limit:
        lines = lines[:limit]
        while lines and d.textlength(lines[-1] + "...", font=fnt) > max_w:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip(".,;:") + "..."
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += int(fnt.size * gap)
    return y


def one_line(d, x, y, text, fnt, max_w, fill=INK):
    """Single line, shrinking the font until it fits (min 8)."""
    size = fnt.size
    while size > 8 and d.textlength(text, font=F(fnt.path, size)) > max_w:
        size -= 1
    d.text((x, y), text, font=F(fnt.path, size), fill=fill)
    return size


def fit_text(d, text, path, max_size, max_w, min_size=8):
    """Largest font size (<= max_size) at which text fits max_w."""
    size = max_size
    while size > min_size and d.textlength(text, font=F(path, size)) > max_w:
        size -= 1
    return F(path, size)


def tagbox(d, x, y, label, color, size=10):
    """Small filled tag with white bold text; returns right edge."""
    fnt = F(SANS_B, size)
    w = int(d.textlength(label, font=fnt)) + 10
    d.rectangle([x, y, x + w, y + 14], fill=color)
    d.text((x + 5, y + 2), label, font=fnt, fill=(255, 255, 255))
    return x + w


def chip(d, x, y, w, h, label, color, size=11):
    d.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=color)
    fnt = F(SANS_B, size)
    tw = d.textlength(label, font=fnt)
    d.text((x + (w - tw) / 2, y + (h - size) / 2 - 1), label, font=fnt,
           fill=(255, 255, 255))


def num_badge(d, cx, cy, n, r=11):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    fnt = F(SANS_B, 13)
    t = str(n)
    d.text((cx - d.textlength(t, font=fnt) / 2, cy - 7), t, font=fnt,
           fill=(255, 255, 255))


# ------------------------------------------------------------- scene art
# Each scene draws inside a box (x, y, w, h) on draw object d.

def scene_ship(d, x, y, w, h, badge_top="UP TO", badge_val="35%", labels=((0, "EU"), (2, "CHINA"), (4, "INDIA"))):
    """Container ship at sea, coloured boxes, red rate badge."""
    d.rectangle([x, y, x + w, y + h], fill=(213, 231, 240))
    d.rectangle([x, y + h * .62, x + w, y + h], fill=SEA)
    d.rectangle([x, y + h * .62, x + w, y + h * .68], fill=(255, 255, 255))
    hull_y = y + h * .52
    d.polygon([(x + w * .06, hull_y), (x + w * .94, hull_y),
               (x + w * .84, hull_y + h * .14), (x + w * .16, hull_y + h * .14)],
              fill=(30, 30, 34))
    cols = [(176, 30, 20), (30, 80, 140), (220, 160, 0), (36, 112, 74),
            (150, 40, 90), (30, 80, 140)]
    bw, bh = w * .115, h * .13
    for row in range(2):
        for c in range(6):
            cx = x + w * .10 + c * (bw + 2)
            cy = hull_y - bh * (row + 1) - 2
            d.rectangle([cx, cy, cx + bw, cy + bh], fill=cols[(c + row) % 6],
                        outline=(255, 255, 255))
    # labels centred inside the bottom-row containers
    fnt_l = F(SANS_B, 10)
    for c, lab in labels:
        ccx = x + w * .10 + c * (bw + 2) + bw / 2
        d.text((ccx - d.textlength(lab, font=fnt_l) / 2, hull_y - bh + 1),
               lab, font=fnt_l, fill=(255, 255, 255))
    d.rectangle([x + w * .72, y + 6, x + w * .97, y + 34], fill=RED)
    d.text((x + w * .75, y + 8), badge_top,
           font=fit_text(d, badge_top, SANS_B, 11, w * .20),
           fill=(255, 255, 255))
    d.text((x + w * .75, y + 20), badge_val,
           font=fit_text(d, badge_val, SANS_B, 13, w * .20),
           fill=(255, 255, 255))


def scene_chart(d, x, y, w, h, lines=("KOSPI  -6.2%", "SK HYNIX  -11.1%", "SAMSUNG  -9.9%"), gold="4,697.51", chip="AI", rising=False):
    """Dark market panel: falling red line, chip square, index labels."""
    d.rectangle([x, y, x + w, y + h], fill=DARK)
    for gy in range(1, 4):
        yy = y + h * gy / 4
        d.line([(x + 8, yy), (x + w - 8, yy)], fill=(60, 70, 90), width=1)
    pts = []
    n = 24
    for i in range(n + 1):
        px = x + 14 + (w - 28) * i / n
        py = y + 16 + (h - 44) * ((1 - (i / n) ** 1.6) if rising else (i / n) ** 1.6) + (6 if i % 5 == 0 else 0)
        pts.append((px, py))
    d.line(pts, fill=(36, 112, 74) if rising else (230, 60, 40), width=3, joint="curve")
    d.rectangle([x + 26, y + 10, x + 54, y + 38], fill=(70, 80, 100),
                outline=GOLD, width=2)
    d.text((x + 33, y + 15), chip, font=F(SANS_B, 15), fill=GOLD)
    fnt = F(SANS_B, 12)
    for i, ln in enumerate(lines):
        col = ((120, 220, 140) if rising else (255, 120, 100)) if i == 0 else (255, 255, 255)
        d.text((x + w - 118, y + 8 + i * 18), ln, font=fnt, fill=col)
    d.rectangle([x + w - 128, y + h - 24, x + w - 8, y + h - 8], fill=GOLD)
    d.text((x + w - 122, y + h - 23), gold, font=F(SANS_B, 11),
           fill=(0, 0, 0))


def scene_station(d, x, y, w, h, title="TIANGONG", rocket="SHENZHOU-24", flags=True):
    """Night sky, Tiangong station with solar wings, rocket, two flags."""
    d.rectangle([x, y, x + w, y + h], fill=(10, 18, 44))
    for sx, sy, r in [(0.12, 0.15, 2), (0.3, 0.08, 1), (0.55, 0.2, 2),
                      (0.75, 0.1, 1), (0.9, 0.25, 2), (0.42, 0.3, 1),
                      (0.65, 0.35, 1)]:
        d.ellipse([x + w * sx - r, y + h * sy - r, x + w * sx + r,
                   y + h * sy + r], fill=(255, 255, 255))
    d.ellipse([x + w * .90, y + h * .04, x + w * .98, y + h * .16],
              fill=(240, 230, 200))
    # solar wings
    d.rectangle([x + w * .06, y + h * .52, x + w * .30, y + h * .60],
                fill=(40, 90, 160), outline=(160, 200, 230))
    d.rectangle([x + w * .68, y + h * .52, x + w * .92, y + h * .60],
                fill=(40, 90, 160), outline=(160, 200, 230))
    for fx in (0.10, 0.16, 0.22, 0.72, 0.78, 0.84):
        d.line([(x + w * fx, y + h * .52), (x + w * fx, y + h * .60)],
               fill=(160, 200, 230), width=1)
    # core module
    d.rounded_rectangle([x + w * .32, y + h * .44, x + w * .66, y + h * .68],
                        radius=8, fill=(200, 205, 215))
    d.ellipse([x + w * .44, y + h * .50, x + w * .54, y + h * .60],
              fill=(30, 60, 110))
    d.text((x + w * .36, y + h * .70), title, font=F(SANS_B, 11),
           fill=(255, 255, 255))
    # rocket bottom-left
    rx, ry = x + w * .10, y + h * .78
    d.polygon([(rx, ry - 16), (rx + 7, ry - 2), (rx + 7, ry + 10),
               (rx - 7, ry + 10), (rx - 7, ry - 2)], fill=(255, 255, 255))
    d.polygon([(rx - 7, ry + 6), (rx - 13, ry + 14), (rx - 4, ry + 10)],
              fill=RED)
    d.polygon([(rx + 7, ry + 6), (rx + 13, ry + 14), (rx + 4, ry + 10)],
              fill=RED)
    d.polygon([(rx - 4, ry + 10), (rx + 4, ry + 10), (rx, ry + 22)],
              fill=GOLD)
    d.text((x + w * .24, y + h * .80), rocket, font=F(SANS_B, 11),
           fill=(255, 255, 255))
    # two small flags top-right: Pakistan green, China red
    d.rectangle([x + w * .60, y + 8, x + w * .72, y + 24], fill=(20, 90, 50))
    d.ellipse([x + w * .635, y + 11, x + w * .675, y + 21],
              fill=(255, 255, 255))
    d.ellipse([x + w * .648, y + 11, x + w * .688, y + 21],
              fill=(20, 90, 50))
    d.rectangle([x + w * .74, y + 8, x + w * .86, y + 24], fill=RED)
    d.text((x + w * .77, y + 9), "*", font=F(SANS_B, 12), fill=GOLD)


def scene_power(d, x, y, w, h, label="5 REGIONS"):
    """Blackout sky, two pylons, broken line, sparks."""
    d.rectangle([x, y, x + w, y + h], fill=(24, 28, 44))
    for px in (0.22, 0.68):
        bx = x + w * px
        d.polygon([(bx - 3, y + h), (bx + 3, y + h), (bx + 1, y + h * .25),
                   (bx - 1, y + h * .25)], fill=(120, 125, 135))
        d.line([(bx - 14, y + h * .3), (bx + 14, y + h * .3)],
               fill=(120, 125, 135), width=2)
        d.line([(bx - 10, y + h * .45), (bx + 10, y + h * .45)],
               fill=(120, 125, 135), width=2)
    d.line([(x + w * .22, y + h * .3), (x + w * .5, y + h * .42),
            (x + w * .68, y + h * .3)], fill=(120, 125, 135), width=1)
    d.polygon([(x + w * .48, y + h * .30), (x + w * .54, y + h * .44),
               (x + w * .46, y + h * .44), (x + w * .52, y + h * .58)],
              fill=GOLD)
    d.text((x + w * .60, y + 4), label, font=F(SANS_B, 11),
           fill=(255, 255, 255))


def scene_port(d, x, y, w, h, label="4 DRONES"):
    """Harbour: cranes, refinery tanks, ship, drone dots, smoke."""
    d.rectangle([x, y, x + w, y + h], fill=(214, 226, 232))
    d.rectangle([x, y + h * .66, x + w, y + h], fill=(52, 110, 150))
    for tx in (0.12, 0.30):
        d.rectangle([x + w * tx, y + h * .42, x + w * (tx + .12),
                     y + h * .66], fill=(210, 210, 205),
                    outline=(120, 120, 115))
    d.polygon([(x + w * .55, y + h * .66), (x + w * .58, y + h * .18),
               (x + w * .60, y + h * .18), (x + w * .63, y + h * .66)],
              fill=(90, 90, 95))
    d.line([(x + w * .58, y + h * .20), (x + w * .78, y + h * .34)],
           fill=(90, 90, 95), width=3)
    d.line([(x + w * .78, y + h * .34), (x + w * .78, y + h * .48)],
           fill=(90, 90, 95), width=2)
    d.ellipse([x + w * .82, y + h * .10, x + w * .86, y + h * .14],
              fill=(40, 40, 40))
    d.ellipse([x + w * .88, y + h * .22, x + w * .92, y + h * .26],
              fill=(40, 40, 40))
    d.ellipse([x + w * .44, y + h * .30, x + w * .52, y + h * .38],
              fill=(150, 150, 150))
    d.ellipse([x + w * .48, y + h * .22, x + w * .56, y + h * .30],
              fill=(170, 170, 170))
    d.polygon([(x + w * .14, y + h * .78), (x + w * .40, y + h * .78),
               (x + w * .36, y + h * .90), (x + w * .18, y + h * .90)],
              fill=(40, 40, 44))
    d.text((x + w * .14, y + 4), label, font=F(SANS_B, 11),
           fill=(20, 40, 60))


def scene_house(d, x, y, w, h, pct="+26%", bill="£2,166"):
    """House with chimney, big +26% arrow and bill."""
    d.rectangle([x, y, x + w, y + h], fill=(226, 236, 244))
    d.polygon([(x + w * .14, y + h * .55), (x + w * .40, y + h * .28),
               (x + w * .66, y + h * .55)], fill=(150, 50, 40))
    d.rectangle([x + w * .20, y + h * .55, x + w * .60, y + h * .88],
                fill=(240, 225, 200), outline=(120, 110, 95))
    d.rectangle([x + w * .36, y + h * .66, x + w * .46, y + h * .88],
                fill=(90, 60, 40))
    d.rectangle([x + w * .56, y + h * .30, x + w * .62, y + h * .48],
                fill=(120, 110, 100))
    d.ellipse([x + w * .57, y + h * .16, x + w * .63, y + h * .22],
              fill=(180, 180, 180))
    d.ellipse([x + w * .60, y + h * .08, x + w * .66, y + h * .14],
              fill=(200, 200, 200))
    d.rounded_rectangle([x + w * .67, y + 3, x + w * .98, y + h - 2],
                        radius=3, fill=(255, 255, 255))
    d.text((x + w * .70, y + h * .10), pct,
           font=fit_text(d, pct, SANS_B, 22, w * .27), fill=RED)
    d.text((x + w * .70, y + h * .52), bill,
           font=fit_text(d, bill, SANS_B, 15, w * .27), fill=INK)


def scene_flags(d, x, y, w, h):
    """Two treaty flags on poles above a signed document."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 238, 240))
    # Australia: blue field, stars
    d.rectangle([x + w * .08, y + h * .12, x + w * .42, y + h * .52],
                fill=(20, 50, 110))
    for sx, sy in [(0.16, 0.22), (0.30, 0.30), (0.20, 0.42), (0.34, 0.18)]:
        d.text((x + w * sx, y + h * sy), "*", font=F(SANS_B, 12),
               fill=(255, 255, 255))
    # Solomons: blue over green with stars
    d.polygon([(x + w * .56, y + h * .12), (x + w * .90, y + h * .12),
               (x + w * .56, y + h * .52)], fill=(20, 80, 140))
    d.polygon([(x + w * .90, y + h * .12), (x + w * .90, y + h * .52),
               (x + w * .56, y + h * .52)], fill=(20, 120, 60))
    for sx, sy in [(0.62, 0.20), (0.72, 0.26), (0.82, 0.20), (0.68, 0.38),
                   (0.80, 0.42)]:
        d.text((x + w * sx, y + h * sy), "*", font=F(SANS_B, 10),
               fill=GOLD)
    d.rectangle([x + w * .30, y + h * .62, x + w * .70, y + h * .92],
                fill=(255, 255, 255), outline=(120, 120, 115))
    for i in range(3):
        d.line([(x + w * .35, y + h * (.70 + i * .07)),
                (x + w * .65, y + h * (.70 + i * .07))],
               fill=(150, 150, 145), width=1)


def scene_sewing(d, x, y, w, h, coin="Tk", value="17,500"):
    """Garment: folded shirts, spool, coin stack, wage tag."""
    d.rectangle([x, y, x + w, y + h], fill=(240, 232, 220))
    for i, col in enumerate([(30, 80, 140), (176, 30, 20), (36, 112, 74)]):
        d.rectangle([x + w * (.10 + i * .20), y + h * .30,
                     x + w * (.26 + i * .20), y + h * .78], fill=col)
        d.line([(x + w * (.10 + i * .20), y + h * .42),
                (x + w * (.26 + i * .20), y + h * .42)],
               fill=(255, 255, 255), width=2)
    d.ellipse([x + w * .74, y + h * .18, x + w * .92, y + h * .48],
              fill=GOLD, outline=(150, 110, 0))
    d.text((x + w * .79, y + h * .26), coin, font=F(SANS_B, 12),
           fill=(90, 60, 0))
    d.text((x + w * .70, y + h * .60), value, font=F(SANS_B, 15),
           fill=INK)


def scene_mine(d, x, y, w, h, depth="100 m"):
    """Flooded pit: hillside, water, helmet, depth marker."""
    d.rectangle([x, y, x + w, y + h], fill=(222, 214, 196))
    d.polygon([(x, y + h), (x + w * .30, y + h * .18),
               (x + w * .62, y + h), (x + w, y + h)], fill=(110, 88, 60))
    d.polygon([(x + w * .62, y + h), (x + w * .80, y + h * .30),
               (x + w, y + h * .55), (x + w, y + h)], fill=(90, 72, 50))
    d.rectangle([x + w * .30, y + h * .55, x + w * .70, y + h],
                fill=(70, 120, 160))
    for i in range(3):
        d.line([(x + w * (.34 + i * .10), y + h * .66),
                (x + w * (.42 + i * .10), y + h * .66)],
               fill=(200, 225, 240), width=2)
    d.pieslice([x + w * .08, y + h * .12, x + w * .26, y + h * .30], 180, 360,
               fill=GOLD)
    d.rectangle([x + w * .06, y + h * .28, x + w * .28, y + h * .32],
                fill=GOLD)
    d.text((x + w * .72, y + h * .08), depth, font=F(SANS_B, 12),
           fill=INK)
    d.line([(x + w * .78, y + h * .24), (x + w * .78, y + h * .60)],
           fill=INK, width=1)


def scene_city(d, x, y, w, h):
    """City blocks at dusk with a smoke plume."""
    d.rectangle([x, y, x + w, y + h], fill=(238, 214, 180))
    for bx, bw, bh in [(0.06, 0.16, 0.55), (0.26, 0.12, 0.72),
                       (0.42, 0.18, 0.48), (0.64, 0.14, 0.66),
                       (0.82, 0.12, 0.42)]:
        d.rectangle([x + w * bx, y + h * (1 - bh), x + w * (bx + bw),
                     y + h], fill=(90, 80, 70))
        for wy in range(3):
            d.rectangle([x + w * (bx + .03), y + h * (1 - bh + .12 + wy * .14),
                         x + w * (bx + .07), y + h * (1 - bh + .20 + wy * .14)],
                        fill=GOLD)
    d.ellipse([x + w * .44, y + h * .10, x + w * .54, y + h * .20],
              fill=(120, 120, 120))
    d.ellipse([x + w * .50, y + h * .02, x + w * .60, y + h * .12],
              fill=(140, 140, 140))
    d.ellipse([x + w * .56, y + h * .10, x + w * .64, y + h * .18],
              fill=(160, 160, 160))


def scene_court(d, x, y, w, h):
    """Courthouse pediment, columns, gavel."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 228, 216))
    d.polygon([(x + w * .08, y + h * .34), (x + w * .50, y + h * .10),
               (x + w * .92, y + h * .34)], fill=(200, 192, 172))
    for cx in (0.20, 0.38, 0.56, 0.74):
        d.rectangle([x + w * cx, y + h * .36, x + w * (cx + .07),
                     y + h * .82], fill=(245, 242, 232),
                    outline=(160, 155, 140))
    d.rectangle([x + w * .06, y + h * .82, x + w * .94, y + h * .90],
                fill=(180, 172, 152))
    d.rectangle([x + w * .80, y + h * .55, x + w * .94, y + h * .62],
                fill=(120, 80, 40))
    d.line([(x + w * .86, y + h * .55), (x + w * .86, y + h * .42)],
           fill=(120, 80, 40), width=3)


def scene_scales(d, x, y, w, h, label="3 CASES"):
    """Scales of justice on a dark panel."""
    d.rectangle([x, y, x + w, y + h], fill=(24, 32, 54))
    cx = x + w * .50
    d.line([(cx, y + h * .16), (cx, y + h * .82)], fill=GOLD, width=3)
    d.line([(x + w * .22, y + h * .26), (x + w * .78, y + h * .26)],
           fill=GOLD, width=3)
    for sx in (0.22, 0.78):
        px = x + w * sx
        d.line([(px, y + h * .26), (px, y + h * .44)], fill=GOLD, width=2)
        d.pieslice([px - 14, y + h * .44, px + 14, y + h * .62], 0, 180,
                   fill=GOLD)
    d.ellipse([cx - 6, y + h * .10, cx + 6, y + h * .22], fill=GOLD)
    d.text((x + w * .06, y + h * .70), label, font=F(SANS_B, 12),
           fill=(255, 255, 255))


def scene_tanker(d, x, y, w, h, label="30+"):
    """Tanker truck on a road, flames above, smoke."""
    d.rectangle([x, y, x + w, y + h], fill=(250, 220, 170))
    d.rectangle([x, y + h * .72, x + w, y + h], fill=(90, 88, 86))
    d.line([(x, y + h * .72), (x + w, y + h * .72)], fill=(255, 255, 255),
           width=2)
    d.rounded_rectangle([x + w * .10, y + h * .42, x + w * .58, y + h * .70],
                        radius=10, fill=(220, 220, 215),
                        outline=(120, 120, 115))
    d.rectangle([x + w * .60, y + h * .48, x + w * .76, y + h * .70],
                fill=(180, 60, 40))
    d.rectangle([x + w * .63, y + h * .52, x + w * .72, y + h * .60],
                fill=(170, 210, 230))
    for wx in (0.20, 0.40, 0.68):
        d.ellipse([x + w * wx, y + h * .68, x + w * (wx + .09),
                   y + h * .82], fill=(30, 30, 30))
    d.polygon([(x + w * .42, y + h * .42), (x + w * .52, y + h * .16),
               (x + w * .58, y + h * .42)], fill=(240, 120, 30))
    d.polygon([(x + w * .50, y + h * .42), (x + w * .56, y + h * .26),
               (x + w * .62, y + h * .42)], fill=GOLD)
    d.ellipse([x + w * .66, y + h * .06, x + w * .74, y + h * .14],
              fill=(110, 110, 110))
    d.ellipse([x + w * .72, y + h * .12, x + w * .80, y + h * .20],
              fill=(130, 130, 130))
    d.text((x + w * .80, y + h * .04), label, font=F(SANS_B, 15), fill=RED)


SCENES = {
    "ship": scene_ship, "chart": scene_chart, "station": scene_station,
    "power": scene_power, "port": scene_port, "house": scene_house,
    "flags": scene_flags, "sewing": scene_sewing, "mine": scene_mine,
    "city": scene_city, "court": scene_court, "scales": scene_scales,
    "tanker": scene_tanker,
}

# ------------------------------------------------------------- the stories
# Every item happened or was first reported on Thursday 26 November
# 2026, checked against the wires (Reuters, AP, AFP, Yonhap, Xinhua,
# Al Jazeera, Haaretz, France24) and the primary sources (UKMTO, Rugby Australia).
# Tags: OFFICIAL = an authority's own word; CONFIRMED = two or more
# major outlets; REPORTED = one outlet's reporting; CLAIM = one side's
# word, not independently verified.

FEATURES = [
    dict(n=1, scene="power", place="NEW YORK \u00b7 WEATHER",
         tag="CONFIRMED",
         head="Thanksgiving storm floods East Coast; Macy's parade moves",
         body="80m+ under alerts, 70 mph winds; New Jersey declares emergency. Macy's 100th parade shifts to Sat 08:30 ET.",
         why="WHY IT MATTERS: Thanksgiving travel hit hard.",
         opts=dict(label="70 MPH")),
    dict(n=2, scene="chart", place="TOKYO \u00b7 MARKETS",
         tag="CONFIRMED",
         head="Asian shares rebound after AI sell-off",
         body="Nikkei +1.6%, Kospi +1.9% as the AI sell-off eases; Asian shares recover across the board.",
         why="WHY IT MATTERS: the AI boom's wobble steadies.",
         opts=dict(rising=True, lines=("NIKKEI  +1.6%", "KOSPI  +1.9%", "ASIA  REBOUNDS"), gold="+1.6%")),
    dict(n=3, scene="city", place="GAZA CITY \u00b7 WAR",
         tag="REPORTED",
         head="Israel kills Hamas minister Khaled Abu Nada in Gaza strike",
         body="Economy and education minister killed overnight in Deir al-Balah; his wife also killed. Five dead overnight in Gaza.",
         why="WHY IT MATTERS: a minister killed as truce frays."),
]

CARDS = [
    dict(n=4, scene="court", place="BRUSSELS \u00b7 EUROPE",
         tag="CONFIRMED",
         head="EU leaders meet on \u20ac45bn Ukraine loan, budget",
         body="Two-day summit opens in Brussels."),
    dict(n=5, scene="ship", place="SINGAPORE \u00b7 TRADE",
         tag="REPORTED",
         head="Nvidia halts chip-server shipments to SE Asia",
         body="Four countries hit by the halt.",
         opts=dict(badge_top="HALTED", badge_val="4 CTYS", labels=((0, "MY"), (1, "SG"), (3, "TH"), (5, "ID")))),
    dict(n=6, scene="mine", place="BOGOR \u00b7 DISASTER",
         tag="CONFIRMED",
         head="13 dead, 13 trapped in flooded gold mine",
         body="Illegal W. Java pit; search resumes.",
         opts=dict(depth="100 m")),
    dict(n=7, scene="house", place="SEOUL \u00b7 ECONOMY",
         tag="OFFICIAL",
         head="Bank of Korea hikes rate to 3.25%",
         body="2027 growth forecast lifted to 4.1%.",
         opts=dict(pct="3.25%", bill="BOK RATE")),
    dict(n=8, scene="flags", place="HANOI \u00b7 TRADE",
         tag="CONFIRMED",
         head="CPTPP, ASEAN, EU trade chiefs meet in Vietnam",
         body="Trade chiefs meet after tariff salvo."),
    dict(n=9, scene="port", place="DUBAI \u00b7 GULF",
         tag="REPORTED",
         head="Tanker hit by projectile off Dubai",
         body="50nm west of Dubai; no injuries.",
         opts=dict(label="TANKER HIT")),
    dict(n=10, scene="scales", place="SEOUL \u00b7 JUSTICE",
         tag="CONFIRMED",
         head="Top court confirms Yoon's perjury acquittal",
         body="Ex-president cleared; ruling final.",
         opts=dict(label="ACQUITTED")),
    dict(n=11, scene="power", place="NEVINNOMYSSK \u00b7 WAR",
         tag="REPORTED",
         head="Ukrainian drones hit power plant, chemical works",
         body="Industrial zone struck overnight.",
         opts=dict(label="POWER HIT")),
    dict(n=12, scene="city", place="FLINDERS IS. \u00b7 FIRE",
         tag="CONFIRMED",
         head="Bushfire burns 10% of Flinders Island",
         body="~14,000 ha; at least six homes lost."),
    dict(n=13, scene="city", place="KHARKIV \u00b7 WAR",
         tag="REPORTED",
         head="Russian drones hit Kharkiv high-rises; 2 killed",
         body="Morning strikes; at least 3 injured."),
]

# (number, one-line story, tag) — C confirmed, R reported.
ALSO = [
    (14, "Kyiv region \u00b7 \u226515 killed as Russia steps up attacks", "C"),
    (15, "Warsaw \u00b7 Poland plans limited no-fly zone in east", "R"),
    (16, "Sanaa \u00b7 Blast rocks capital; 2 missiles at Riyadh downed", "R"),
    (17, "S. Syria \u00b7 Israeli blast rocks Tel Ahmar, troops leave", "R"),
    (18, "S. Lebanon \u00b7 3 blasts as artillery hits Marjayoun", "R"),
    (19, "Gaza City \u00b7 Israeli drone strike, casualties reported", "R"),
    (20, "Taiz \u00b7 Houthi shelling kills a woman, injures 7", "R"),
    (21, "Yemen \u00b7 Army clashes with Houthis in Marib, al-Jawf", "R"),
    (22, "Gaza \u00b7 Winter floods threaten 1,000 sites, 200,000 tents", "R"),
    (23, "Doha \u00b7 Kushner: Trump keeps 'all options' on Iran", "R"),
    (24, "Washington \u00b7 Senator blames Iran war for Thanksgiving costs", "R"),
    (25, "World \u00b7 EU, China condemn new US tariffs", "C"),
    (26, "Oil \u00b7 Brent $94.71 as Gulf tensions rise", "R"),
    (27, "US \u00b7 Thanksgiving NFL: Lions-Bears, Cowboys-Eagles", "C"),
    (28, "Europe \u00b7 Europa League: Milan at Olympiacos, Juve host Omonia", "C"),
    (29, "Lucknow \u00b7 Congress marches on Constitution Day", "C"),
    (30, "Delhi \u00b7 Police curb farmers' protest march", "R"),
    (31, "New Delhi \u00b7 India pitches 2036 Olympics bid to IOC", "C"),
    (32, "Sandton \u00b7 Ramaphosa opens MSME breakfast", "C"),
    (33, "Benghazi \u00b7 Libya's east vows revenge for warship strike", "R"),
    (34, "Singapore \u00b7 'Very disappointed' over new US tariffs", "C"),
    (35, "Bangkok \u00b7 18% US tariff ceiling 'in line' with hopes", "C"),
    (36, "Kyoto \u00b7 China, Japan, Korea, ASEAN open pay talks", "C"),
    (37, "Tokyo \u00b7 Chinese firms 'growing threat' to Japan Inc", "C"),
    (38, "Seoul \u00b7 Spy agency denies China anti-US ops report", "C"),
    (39, "Seoul \u00b7 Hyundai keeps car CEOs, reshuffles affiliates", "R"),
    (40, "Beijing \u00b7 Data given to AI firm MiniMax 'accessed'", "R"),
    (41, "Beijing \u00b7 China welcomes EU delisting Yusha", "C"),
    (42, "Pyongyang \u00b7 Kim seeks wider use of tactical nukes", "C"),
    (43, "Brasília · Brazil blasts 'unacceptable' US tariff plans", "C"),
    (44, "Kinshasa · DR Congo Ebola cases pass 12,000", "C"),
    (45, "New Delhi · Top court tightens food warning labels", "C"),
    (46, "US · Nvidia posts Nemotron image-model weights", "R"),
    (47, "Bogotá · Colombia drops bid to join BRICS bank", "C"),
    (48, "US \u00b7 42 states move to stop Character.AI log sale", "R"),
    (49, "Canberra \u00b7 Australia set to miss 2035 emissions target", "C"),
    (50, "London \u00b7 Beale back for Wallabies after five years", "C"),
]

REGION_BAR = [
    ("N. AMERICA", 5), ("EUROPE", 6), ("MIDDLE EAST", 10),
    ("N. AFRICA", 1), ("SUB-SAHARAN AFRICA", 2), ("SOUTH ASIA", 4),
    ("EAST & SE ASIA", 15), ("OCEANIA", 3), ("GLOBAL", 2),
    ("LATIN AMERICA", 2),
]

FIELDS_BAR = (
    "20 FIELDS \u2014 War 10 \u00b7 Security 3 \u00b7 Diplomacy 6 \u00b7 Trade 5 \u00b7 "
    "Politics 4 \u00b7 Sport 4 \u00b7 Cyber 1 \u00b7 Economy 2 \u00b7 Disaster 2 \u00b7 "
    "Justice 3 \u00b7 AI 1 \u00b7 9 more, 1 each: Markets, Energy, Aid, Protest, "
    "Business, Weather, Climate, Health, Finance"
)

TIMELINE = (
    "THE DAY IN UTC \u00b7 00:30 Beale back for Wallabies \u00b7 01:39 Kyiv toll \u226515 "
    "\u00b7 06:23 Kharkiv strikes kill 2 \u00b7 06:44 EU summit opens \u00b7 09:06 World "
    "condemns tariffs \u00b7 14:05 China hails EU delisting"
)

STATS = [
    ("80m+", "under storm alerts on Thanksgiving"),
    ("\u20ac45bn", "Ukraine loan on EU summit table"),
    ("+1.6%", "Nikkei rebound after AI sell-off"),
    ("3.25%", "Bank of Korea rate after hike"),
    ("13", "dead, 13 trapped in Java gold pit"),
    ("10%", "of Flinders Island burnt by bushfire"),
]

DATE_CHECK = (
    "DATE CHECK \u2014 Every story above happened or was first reported on "
    "Thursday 26 November 2026. Left out, not 26 November: US tariff proposal "
    "on 14 economies (Wed 25) \u00b7 Asian chip crash, Kospi \u22126.2% (Wed 25) \u00b7 "
    "Pakistan's first astronaut docks at Tiangong (Wed 25) \u00b7 Chen Jining "
    "probe (Tue 24) \u00b7 Huawei's Brooklyn conviction (Tue 24) \u00b7 Cairo tanker "
    "fire, 30 killed (Wed 25) \u00b7 Gukesh Game 2 played (Wed 25) \u00b7 UK Budget "
    "2026 (28 Oct)."
)

# Rough continent shapes, (lon, lat) rings, drawn from a blank atlas.
LAND = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-80, 73),
     (-75, 62), (-65, 60), (-55, 47), (-70, 42), (-75, 35), (-80, 26),
     (-85, 30), (-90, 21), (-97, 16), (-105, 20), (-115, 28), (-125, 40),
     (-125, 49), (-140, 60), (-155, 58), (-165, 60)],
    [(-80, 10), (-75, 5), (-60, 5), (-50, 0), (-35, -8), (-40, -20),
     (-48, -28), (-58, -35), (-65, -45), (-70, -55), (-73, -40),
     (-72, -20), (-78, -5), (-80, 2)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (32, 31), (35, 28),
     (43, 12), (48, 11), (51, 0), (40, -10), (35, -18), (28, -33),
     (18, -35), (12, -18), (8, 4), (-8, 5), (-17, 15)],
    [(-10, 36), (-9, 43), (-2, 48), (-5, 50), (0, 51), (5, 53), (8, 57),
     (10, 59), (18, 56), (21, 55), (24, 59), (28, 60), (30, 70), (40, 68),
     (45, 68), (50, 60), (40, 55), (35, 50), (30, 46), (28, 44), (23, 40),
     (19, 42), (12, 44), (8, 44), (3, 43), (-2, 37), (-9, 37)],
    [(40, 68), (50, 70), (60, 69), (70, 72), (80, 73), (100, 77),
     (120, 73), (140, 72), (160, 70), (178, 66), (170, 60), (162, 55),
     (158, 50), (142, 45), (140, 38), (130, 35), (127, 40), (120, 32),
     (110, 20), (105, 10), (100, 8), (95, 15), (90, 22), (85, 20),
     (80, 8), (77, 8), (72, 20), (66, 25), (60, 25), (55, 26), (50, 29),
     (48, 30), (44, 29), (40, 36), (38, 36), (35, 36)],
    [(114, -22), (114, -30), (120, -34), (130, -32), (140, -38),
     (150, -37), (153, -27), (146, -19), (142, -11), (136, -12),
     (130, -13), (126, -14), (122, -17), (114, -20)],
]
# (lon, lat, story number) pins for the 13 illustrated stories.
PINS = [
    (-74, 41, 1), (139, 36, 2), (34, 31, 3), (4, 51, 4), (104, 1, 5),
    (107, -6, 6), (127, 37, 7), (106, 21, 8), (55, 25, 9), (129, 36, 10),
    (42, 44, 11), (148, -40, 12), (36, 50, 13),
]

# ------------------------------------------------------------- layout

TAG_COLORS = {
    "OFFICIAL": (36, 112, 74),
    "CONFIRMED": (30, 80, 140),
    "REPORTED": (176, 104, 0),
    "CLAIM": (176, 30, 20),
}

CARD_REGION = {
    4: "EUROPE", 5: "EAST & SE ASIA", 6: "EAST & SE ASIA",
    7: "EAST & SE ASIA", 8: "EAST & SE ASIA", 9: "MIDDLE EAST",
    10: "EAST & SE ASIA", 11: "EUROPE", 12: "OCEANIA", 13: "EUROPE",
}

MARGIN = 22
CW = W - 2 * MARGIN  # 980


def draw_top_band(d):
    d.rectangle([0, 0, W, 26], fill=NAVY)
    d.text((MARGIN, 5), "THE WORLD IN ONE DAY", font=F(SANS_B, 13),
           fill=(255, 255, 255))
    right = ("50 STORIES \u00b7 10 REGIONS \u00b7 20 FIELDS \u00b7 ALL FIRST "
             "REPORTED THURSDAY 26 NOVEMBER 2026")
    fnt = F(SANS_B, 10)
    d.text((W - MARGIN - d.textlength(right, font=fnt), 7), right,
           font=fnt, fill=GOLD)


def draw_region_bar(d, y):
    size = 11
    while size >= 9:
        fnt = F(SANS_B, size)
        widths = [int(d.textlength(f"{name} {n}", font=fnt)) + 16
                  for name, n in REGION_BAR]
        if sum(widths) + 6 * (len(widths) - 1) <= CW:
            break
        size -= 1
    x = MARGIN
    for (name, n), w in zip(REGION_BAR, widths):
        d.rounded_rectangle([x, y, x + w, y + 20], radius=3,
                            fill=REGION_COLORS[name])
        label = f"{name} {n}"
        d.text((x + (w - d.textlength(label, font=fnt)) / 2, y + 4), label,
               font=fnt, fill=(255, 255, 255))
        x += w + 6


def draw_stats(d, y):
    cell = CW // 6
    for i, (num, label) in enumerate(STATS):
        x = MARGIN + i * cell
        if i:
            d.line([(x - 3, y + 2), (x - 3, y + 42)], fill=FAINT, width=1)
        d.text((x, y), num, font=F(SERIF_B, 22),
               fill=RED if i % 2 == 0 else NAVY)
        put_lines(d, x, y + 26, label, F(SANS, 10), cell - 8, fill=SOFT,
                  gap=1.1, limit=2)


def draw_feature(d, fx, fy, feat):
    fw = 320
    SCENES[feat["scene"]](d, fx, fy, fw, 100, **feat.get("opts", {}))
    num_badge(d, fx + 12, fy + 12, feat["n"], r=11)
    y = fy + 104
    fnt = F(SANS_B, 10)
    d.text((fx, y + 2), feat["place"], font=fnt, fill=NAVY)
    tagbox(d, fx + fw - 78, y, feat["tag"], TAG_COLORS[feat["tag"]])
    y += 18
    y = put_lines(d, fx, y, feat["head"], F(SERIF_B, 22), fw, gap=1.15,
                  limit=3)
    y += 2
    y = put_lines(d, fx, y, feat["body"], F(SANS, 11), fw, gap=1.25,
                  limit=3)
    y += 3
    put_lines(d, fx, y, feat["why"], F(SERIF_I, 11), fw, fill=RED,
              gap=1.15, limit=1)


def draw_card(d, cx, cy, card):
    cw, ch = 189, 92
    SCENES[card["scene"]](d, cx, cy, cw, 36, **card.get("opts", {}))
    num_badge(d, cx + 11, cy + 11, card["n"], r=10)
    y = cy + 38
    fnt = F(SANS_B, 9)
    d.text((cx, y + 1), card["place"], font=fnt,
           fill=REGION_COLORS[CARD_REGION[card["n"]]])
    tagbox(d, cx + cw - 58, y, card["tag"], TAG_COLORS[card["tag"]], size=8)
    y += 14
    y = put_lines(d, cx, y, card["head"], F(SANS_B, 12), cw, gap=1.15,
                  limit=2)
    put_lines(d, cx, y + 1, card["body"], F(SANS, 9), cw, gap=1.2,
              limit=1)


def draw_map(d, mx, my, mw, mh):
    """World map with numbered pins for the 13 illustrated stories."""
    d.rectangle([mx, my, mx + mw, my + mh], fill=(226, 234, 238))
    s = min((mw - 8) / 360.0, (mh - 8) / 135.0)
    ox = mx + (mw - 360 * s) / 2
    oy = my + (mh - 135 * s) / 2 + 8 * s

    def xy(lon, lat):
        return ox + (lon + 180) * s, oy + (80 - lat) * s

    for ring in LAND:
        pts = [xy(lon, lat) for lon, lat in ring]
        d.polygon(pts, fill=(198, 192, 178), outline=(150, 144, 132))
    for lon, lat, n in PINS:
        px, py = xy(lon, lat)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                  outline=(255, 255, 255), width=1)
        fnt = F(SANS_B, 9)
        t = str(n)
        d.text((px - d.textlength(t, font=fnt) / 2, py - 5), t, font=fnt,
               fill=(255, 255, 255))


def draw_list(d, lx, ly, lw):
    d.text((lx, ly), "ALSO ON THURSDAY 26 NOVEMBER \u2014 37 MORE STORIES",
           font=F(SANS_B, 12), fill=INK)
    fnt = F(SANS, 9)
    right = "C CONFIRMED \u00b7 R REPORTED"
    d.text((lx + lw - d.textlength(right, font=fnt), ly + 2), right,
           font=fnt, fill=SOFT)
    col_w = (lw - 10) // 2
    fnt = F(SANS, 9)
    fnt_b = F(SANS_B, 9)
    half = 19
    for col in range(2):
        items = ALSO[col * half:(col + 1) * half]
        x = lx + col * (col_w + 10)
        y = ly + 16
        for n, text, tag in items:
            num = f"{n} "
            d.text((x, y), num, font=fnt_b, fill=RED)
            nx = x + d.textlength(num, font=fnt_b)
            line = f"{text} [{tag}]"
            one_line(d, nx, y, line, fnt, x + col_w - nx, fill=INK)
            y += 11.5


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    draw_top_band(d)
    # masthead
    one_line(d, MARGIN, 30, "Thursday 26 November 2026",
             F(SERIF_B, 58), CW, fill=NAVY)
    # red italic sub-headline
    one_line(d, MARGIN, 98,
             "Thanksgiving storm floods East Coast \u00b7 Asian shares rebound "
             "\u00b7 Hamas minister killed in Gaza",
             F(SERIF_I, 19), CW, fill=RED)
    draw_region_bar(d, 124)
    # fields line
    one_line(d, MARGIN, 149, FIELDS_BAR, F(SANS, 10), CW, fill=SOFT)
    # UTC timeline
    d.rectangle([MARGIN, 168, MARGIN + CW, 186], fill=NAVY)
    fnt = fit_text(d, TIMELINE, SANS_B, 11, CW - 16)
    d.text(((W - d.textlength(TIMELINE, font=fnt)) / 2, 171), TIMELINE,
           font=fnt, fill=(255, 255, 255))
    # stat strip
    draw_stats(d, 190)
    d.line([(MARGIN, 240), (MARGIN + CW, 240)], fill=INK, width=2)

    # three features
    for i, feat in enumerate(FEATURES):
        draw_feature(d, MARGIN + i * 330, 246, feat)
    d.line([(MARGIN, 508), (MARGIN + CW, 508)], fill=FAINT, width=1)

    # ten cards, two rows of five
    for row in range(2):
        for col in range(5):
            card = CARDS[row * 5 + col]
            draw_card(d, MARGIN + col * 197, 514 + row * 98, card)
    d.line([(MARGIN, 704), (MARGIN + CW, 704)], fill=FAINT, width=1)

    # bottom: map + numbered list
    d.text((MARGIN, 710), "THE WORLD \u2014 13 BIG STORIES PINNED",
           font=F(SANS_B, 12), fill=INK)
    draw_map(d, MARGIN, 728, 300, 168)
    d.text((MARGIN, 902), "Every pin is a story drawn above.",
           font=F(SANS, 9), fill=SOFT)
    draw_list(d, MARGIN + 320, 710, CW - 320)

    # date check + footer
    y = put_lines(d, MARGIN, 952, DATE_CHECK, F(SANS, 10), CW, fill=SOFT,
                  gap=1.3, limit=3)
    foot = ("Sources: Reuters, AP, AFP, Yonhap, Xinhua, Al Jazeera, Haaretz, "
            "France24, MercoPress, Moneycontrol, Rugby Australia, UKMTO. Original drawings; no photographs.")
    d.text((MARGIN, y + 4), foot, font=F(SANS, 10), fill=SOFT)
    d.line([(MARGIN, 1012), (MARGIN + CW, 1012)], fill=NAVY, width=3)

    img.save(HERE / "entry.png", format="PNG", optimize=True)


if __name__ == "__main__":
    main()
