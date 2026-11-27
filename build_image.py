#!/usr/bin/env python3
"""Build the news-image-20261126 v3 front page (1024x1024 PNG).

Fresh rebuild for the 26 November 2026 edition: 38 verified stories,
10 regions, 3 large scene-illustrated features + 10 illustrated cards,
world map with pins, UTC timeline, stat strip and a DATE CHECK footer.
Everything is drawn with Pillow; no network, no clock, no randomness,
so two runs produce byte-identical output.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

CREAM = (247, 243, 232)
PAPER = (252, 250, 244)
NAVY = (26, 42, 74)
NAVY2 = (34, 56, 96)
RED = (178, 34, 34)
DARK = (28, 28, 28)
GREY = (96, 96, 96)
GOLD = (201, 162, 39)
LINE = (190, 182, 164)

FDIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size, subdir="dejavu"):
    return ImageFont.truetype(
        os.path.join("/usr/share/fonts/truetype", subdir, name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SERIF_I = lambda s: font("LiberationSerif-Italic.ttf", s, "liberation")
SANS = lambda s: font("DejaVuSans.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)


def wrap(draw, text, fnt, maxw):
    """Greedy word wrap; returns a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, xy, text, fnt, fill, maxw, lh=None, max_lines=None):
    x, y = xy
    lines = wrap(draw, text, fnt, maxw)
    if max_lines:
        lines = lines[:max_lines]
    if lh is None:
        lh = int(fnt.size * 1.22)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def chip(draw, xy, text, fnt, fg, bg):
    """Rounded tag chip; returns width used."""
    x, y = xy
    tw = draw.textlength(text, font=fnt)
    w = int(tw + 12)
    h = fnt.size + 8
    draw.rounded_rectangle([x, y, x + w, y + h], radius=4, fill=bg)
    draw.text((x + 6, y + 4), text, font=fnt, fill=fg)
    return w


# ---------------------------------------------------------------- stories
# fields: region, field, tag C=confirmed R=reported, dateline, headline,
# summary, why-it-matters (features only), lon/lat for the map pin.
FEATURES = [
    dict(key="storm", region="N. AMERICA", field="Weather", tag="C",
         date="NEW YORK", head="Thanksgiving storm floods East Coast; Macy's 100th parade moves",
         summ="80m+ under alerts, 70 mph winds; NJ declares emergency. Macy's 100th parade shifts to Sat.",
         why="Thanksgiving travel hit hard.",
         lon=-74.0, lat=40.7),
    dict(key="kuwait", region="MIDDLE EAST", field="War", tag="C",
         date="KUWAIT CITY", head="Iranian drones kill 2 Italians in Kuwait",
         summ="Drones hit a vital air-defence site; two Rheinmetall technicians dead, two hurt. Tehran denies it.",
         why="Gulf war widens to a NATO ally's staff.",
         lon=47.5, lat=29.3),
    dict(key="eu", region="EUROPE", field="Diplomacy", tag="C",
         date="BRUSSELS", head="EU leaders meet over \u20ac45bn Ukraine loan",
         summ="Two-day summit opens on the \u20ac45bn loan and the 2028-34 budget; Macron sets a December deadline.",
         why="Kyiv's funding hangs on the deal.",
         lon=4.35, lat=50.85),
]

CARDS = [
    dict(key="abunada", region="MIDDLE EAST", field="War", tag="C",
         date="GAZA CITY", head="Israel kills Hamas minister Khaled Abu Nada in Gaza",
         summ="Overnight strike in Deir al-Balah kills the minister and his wife; five dead.",
         lon=34.45, lat=31.5),
    dict(key="kyiv", region="EUROPE", field="War", tag="C",
         date="KYIV", head="\u226515 killed in Kyiv region as Russia intensifies attacks",
         summ="Overnight strikes hit the capital region; at least 15 dead.",
         lon=30.5, lat=50.45),
    dict(key="kharkiv", region="EUROPE", field="War", tag="C",
         date="KHARKIV", head="Russian drones hit Kharkiv high-rises; 2 killed",
         summ="Morning strike on residential towers injures at least three.",
         lon=36.25, lat=49.99),
    dict(key="bok", region="EAST & SE ASIA", field="Economy", tag="C",
         date="SEOUL", head="Bank of Korea hikes rate to 3.25%",
         summ="2027 growth forecast lifted to 4.1% as the won steadies.",
         lon=127.0, lat=37.5),
    dict(key="rebound", region="EAST & SE ASIA", field="Markets", tag="C",
         date="TOKYO", head="Asian shares rebound after AI sell-off",
         summ="Nikkei +1.6%, Kospi +1.9% as the AI sell-off eases.",
         lon=139.7, lat=35.7),
    dict(key="mumbai", region="SOUTH ASIA", field="Politics", tag="C",
         date="MUMBAI", head="India marks 18 years since 26/11",
         summ="Tributes for the 166 killed in 2008; leaders vow zero tolerance.",
         lon=72.8, lat=19.1),
    dict(key="javamime", region="EAST & SE ASIA", field="Disaster", tag="C",
         date="BOGOR", head="Java gold mine flood: 13 dead, 13 trapped",
         summ="Illegal 100m pit flooded after heavy rain; search resumes.",
         lon=106.8, lat=-6.6),
    dict(key="nvidia", region="EAST & SE ASIA", field="Tech", tag="R",
         date="SINGAPORE", head="Nvidia halts chip-server shipments to 4 SE Asian nations",
         summ="FT reports the pause; shares slip on supply fears.",
         lon=103.8, lat=1.35),
    dict(key="ebola", region="SUB-SAHARAN AFRICA", field="Health", tag="C",
         date="KINSHASA", head="DR Congo Ebola cases pass 12,000",
         summ="12,021 cases, 5,904 dead; second-largest outbreak on record.",
         lon=15.3, lat=-4.3),
    dict(key="flinders", region="OCEANIA", field="Fire", tag="C",
         date="FLINDERS IS.", head="Bushfire burns 10% of Flinders Island",
         summ="~14,000 ha scorched, at least six homes lost in Tasmania.",
         lon=148.0, lat=-40.0),
]

ALSO = [
    (14, "Nevinnomyssk drones hit plant", "EUROPE", "C"),
    (15, "Poland plans limited no-fly zone", "EUROPE", "R"),
    (16, "Top court upholds Yoon acquittal", "EAST & SE ASIA", "C"),
    (17, "CPTPP, ASEAN, EU chiefs meet", "EAST & SE ASIA", "C"),
    (18, "Tanker hit 50nm west of Dubai", "MIDDLE EAST", "C"),
    (19, "Sanaa blast; Saudis stop missiles", "MIDDLE EAST", "C"),
    (20, "Israel blows up Tel Ahmar site", "MIDDLE EAST", "C"),
    (21, "3 blasts in Marjayoun, Lebanon", "MIDDLE EAST", "C"),
    (22, "Israeli drone attack, W. Gaza City", "MIDDLE EAST", "R"),
    (23, "Houthi shelling in Taiz kills 1", "MIDDLE EAST", "R"),
    (24, "Gaza floods; 200,000 tents needed", "MIDDLE EAST", "C"),
    (25, "Brent crude $94.71 a barrel", "MIDDLE EAST", "C"),
    (26, "World condemns new US tariffs", "GLOBAL", "C"),
    (27, "Singapore 'very disappointed'", "EAST & SE ASIA", "C"),
    (28, "Thailand: 18% tariff in line", "EAST & SE ASIA", "C"),
    (29, "China, Japan, Korea in pay talks", "EAST & SE ASIA", "C"),
    (30, "JETRO: China threat to Japan firms", "EAST & SE ASIA", "C"),
    (31, "Seoul denies China anti-US report", "EAST & SE ASIA", "C"),
    (32, "MiniMax data accessed by outsiders", "EAST & SE ASIA", "R"),
    (33, "China hails EU delisting Yusha", "EAST & SE ASIA", "C"),
    (34, "Kim: wider tactical nuclear use", "EAST & SE ASIA", "C"),
    (35, "Brazil blasts 'unacceptable' tariffs", "LATIN AMERICA", "C"),
    (36, "Colombia drops BRICS bank bid", "LATIN AMERICA", "C"),
    (37, "India tightens food warning labels", "SOUTH ASIA", "C"),
    (38, "Libya army vows warship revenge", "N. AFRICA", "R"),
]

REGION_ORDER = ["N. AMERICA", "EUROPE", "MIDDLE EAST", "N. AFRICA",
                "SUB-SAHARAN AFRICA", "SOUTH ASIA", "EAST & SE ASIA",
                "OCEANIA", "GLOBAL", "LATIN AMERICA"]
REGION_COLORS = {
    "N. AMERICA": (31, 93, 140), "EUROPE": (122, 63, 120),
    "MIDDLE EAST": (178, 34, 34), "N. AFRICA": (196, 120, 20),
    "SUB-SAHARAN AFRICA": (52, 120, 62), "SOUTH ASIA": (190, 90, 30),
    "EAST & SE ASIA": (24, 110, 110), "OCEANIA": (90, 90, 160),
    "GLOBAL": (70, 70, 70), "LATIN AMERICA": (150, 110, 20),
}

STATS = [
    ("80m+", "under storm alerts on Thanksgiving"),
    ("\u20ac45bn", "Ukraine loan on the EU table"),
    ("12,021", "DR Congo Ebola cases"),
    ("3.25%", "Bank of Korea rate after hike"),
    ("+1.9%", "Kospi rebound after AI sell-off"),
    ("13", "dead in Java gold mine flood"),
]

TIMELINE = [
    ("01:39", "Kyiv toll \u226515"),
    ("04:47", "Brazil blasts tariffs"),
    ("06:23", "Kharkiv strikes kill 2"),
    ("06:44", "EU summit opens"),
    ("09:06", "World condemns tariffs"),
    ("11:00", "Kuwait kills 2"),
]

DATE_CHECK = ("DATE CHECK \u2014 Every story above happened or was first reported on "
              "Thursday 26 November 2026. Left out, not 26 November: US tariff proposal "
              "on 14 economies (Wed 25) \u00b7 Asian chip crash, Kospi \u22126.2% (Wed 25) \u00b7 "
              "Pakistan's first astronaut docks at Tiangong (Wed 25) \u00b7 Chen Jining probe "
              "(Tue 24) \u00b7 Huawei Brooklyn conviction (Tue 24) \u00b7 Cairo tanker fire, "
              "30 killed (Wed 25) \u00b7 Gukesh draws Game 2 (Wed 25).")

SOURCES = ("Sources: Reuters, AP, AFP, Yonhap, Xinhua, Al Jazeera, Haaretz, France24, "
           "MercoPress, Moneycontrol, The Hindu, CNN, Arab News, UKMTO. "
           "Original drawings; no photographs.")


# ---------------------------------------------------------------- scene art
# Each scene draws inside the box (x, y, w, h). All shapes are plain
# Pillow primitives; nothing is loaded from disk.

def _sky(draw, box, top, bot):
    x, y, w, h = box
    for i in range(h):
        t = i / max(h - 1, 1)
        c = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
        draw.line([(x, y + i), (x + w, y + i)], fill=c)


def _bolt(draw, cx, y0, s, color=(255, 214, 0)):
    pts = [(cx, y0), (cx - 6 * s, y0 + 14 * s), (cx - 1 * s, y0 + 14 * s),
           (cx - 7 * s, y0 + 30 * s), (cx + 5 * s, y0 + 12 * s),
           (cx, y0 + 12 * s)]
    draw.polygon(pts, fill=color)


def _flame(draw, cx, base, s, c1=(255, 140, 0), c2=(255, 60, 0)):
    draw.polygon([(cx - 9 * s, base), (cx - 4 * s, base - 22 * s),
                  (cx + 1 * s, base - 10 * s), (cx + 5 * s, base - 26 * s),
                  (cx + 10 * s, base)], fill=c1)
    draw.polygon([(cx - 5 * s, base), (cx - 2 * s, base - 12 * s),
                  (cx + 2 * s, base - 5 * s), (cx + 5 * s, base)], fill=c2)


def _smoke(draw, cx, y, s, n=4):
    for i in range(n):
        r = (7 + i * 2) * s
        draw.ellipse([cx - r + i * 5 * s, y - i * 9 * s,
                      cx + r + i * 5 * s, y + r - i * 9 * s],
                     fill=(120, 118, 112))


def scene_storm(draw, box):
    x, y, w, h = box
    _sky(draw, box, (38, 52, 84), (92, 110, 140))
    # rain
    for i in range(26):
        rx = x + 8 + (i * 37) % (w - 16)
        ry = y + 6 + (i * 23) % (h - 30)
        draw.line([(rx, ry), (rx - 4, ry + 10)], fill=(190, 205, 225), width=1)
    # pylon
    px = x + w * 0.16
    draw.line([(px, y + h - 8), (px - 14, y + 18)], fill=(24, 24, 28), width=3)
    draw.line([(px, y + h - 8), (px + 14, y + 18)], fill=(24, 24, 28), width=3)
    draw.line([(px - 20, y + 26), (px + 20, y + 26)], fill=(24, 24, 28), width=3)
    _bolt(draw, x + w * 0.42, y + 8, 1.0)
    # parade balloon
    bx, by = x + w * 0.74, y + h * 0.30
    draw.ellipse([bx - 26, by - 18, bx + 26, by + 18], fill=(214, 48, 48))
    draw.ellipse([bx - 26, by - 18, bx - 2, by + 18], fill=(232, 90, 90))
    draw.polygon([(bx - 8, by + 16), (bx + 8, by + 16), (bx, by + 30)], fill=(120, 80, 40))
    draw.rectangle([bx - 7, by + 30, bx + 7, by + 38], fill=(90, 60, 30))
    # ground
    draw.rectangle([x, y + h - 8, x + w, y + h], fill=(30, 34, 44))
    draw.text((x + w - 62, y + h - 24), "70 MPH", font=SANS_B(13), fill=(255, 255, 255))


def scene_kuwait(draw, box):
    x, y, w, h = box
    _sky(draw, box, (58, 48, 40), (214, 176, 120))
    # sun haze
    draw.ellipse([x + w - 52, y + 8, x + w - 16, y + 44], fill=(240, 210, 150))
    # ground
    draw.rectangle([x, y + h - 26, x + w, y + h], fill=(188, 148, 92))
    # radar dish on a mast
    mx = x + w * 0.30
    draw.rectangle([mx - 3, y + 44, mx + 3, y + h - 26], fill=(60, 60, 60))
    draw.pieslice([mx - 26, y + 14, mx + 26, y + 62], 180, 360, fill=(210, 210, 205))
    draw.ellipse([mx - 26, y + 14, mx + 26, y + 62], outline=(90, 90, 90), width=2)
    # drones
    for dx, dy in [(0.62, 0.22), (0.78, 0.12), (0.88, 0.30)]:
        cx, cy = x + w * dx, y + h * dy
        draw.ellipse([cx - 12, cy - 4, cx + 12, cy + 4], fill=(40, 40, 44))
        draw.ellipse([cx - 3, cy - 8, cx + 3, cy + 8], fill=(40, 40, 44))
    # explosion burst
    ex, ey = x + w * 0.66, y + h * 0.55
    for r, c in [(26, (255, 170, 0)), (18, (255, 110, 0)), (10, (255, 60, 0))]:
        draw.ellipse([ex - r, ey - r, ex + r, ey + r], fill=c)
    _smoke(draw, ex + 6, ey - 26, 0.8, 3)


def scene_eu(draw, box):
    x, y, w, h = box
    draw.rectangle([x, y, x + w, y + h], fill=(20, 42, 96))
    # circle of stars
    import math
    cx, cy, r = x + w * 0.30, y + h * 0.46, h * 0.34
    for i in range(12):
        a = -math.pi / 2 + i * math.pi / 6
        sx, sy = cx + r * math.cos(a), cy + r * math.sin(a)
        draw.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=(255, 213, 0))
    # summit building
    bx = x + w * 0.58
    draw.rectangle([bx, y + h - 52, bx + w * 0.36, y + h], fill=(214, 208, 192))
    for i in range(4):
        cx2 = bx + 10 + i * 22
        draw.rectangle([cx2, y + h - 44, cx2 + 10, y + h - 8], fill=(120, 112, 96))
    draw.polygon([(bx - 4, y + h - 52), (bx + w * 0.18, y + h - 66),
                  (bx + w * 0.36 + 4, y + h - 52)], fill=(178, 34, 34))


def scene_gaza(draw, box):
    x, y, w, h = box
    _sky(draw, box, (70, 60, 52), (206, 178, 140))
    # buildings
    pitch = max(9.0, h * 0.22)
    for bx, bw, bh in [(0.04, 0.20, 0.52), (0.28, 0.16, 0.68), (0.48, 0.22, 0.44),
                       (0.74, 0.18, 0.60)]:
        top = y + h - 8 - h * bh
        draw.rectangle([x + w * bx, top, x + w * (bx + bw), y + h - 8],
                       fill=(96, 84, 70))
        rows = max(1, int((h * bh - 6) / pitch))
        for wy in range(rows):
            wy0 = top + 4 + wy * pitch
            draw.rectangle([x + w * bx + 4, wy0,
                            x + w * bx + 12, wy0 + 8], fill=(255, 214, 90))
    _smoke(draw, x + w * 0.55, y + h * 0.30, 1.0, 4)
    _flame(draw, x + w * 0.60, y + h - 8, 1.0)
    # drone
    dx, dy = x + w * 0.82, y + 16
    draw.ellipse([dx - 10, dy - 3, dx + 10, dy + 3], fill=(40, 40, 44))
    draw.line([(dx - 14, dy - 6), (dx + 14, dy - 6)], fill=(40, 40, 44), width=2)


def scene_kyiv(draw, box):
    x, y, w, h = box
    _sky(draw, box, (24, 30, 52), (70, 78, 110))
    # apartment blocks
    pitch = max(9.0, h * 0.22)
    for bx, bw, bh in [(0.05, 0.26, 0.62), (0.35, 0.24, 0.78), (0.63, 0.28, 0.55)]:
        top = y + h - 8 - h * bh
        draw.rectangle([x + w * bx, top, x + w * (bx + bw), y + h - 8],
                       fill=(52, 52, 66))
        rows = max(1, int((h * bh - 6) / pitch))
        for r in range(rows):
            for c in range(3):
                ry0 = top + 4 + r * pitch
                draw.rectangle([x + w * bx + 5 + c * 14, ry0,
                                x + w * bx + 13 + c * 14, ry0 + 8],
                               fill=(255, 206, 80))
    _flame(draw, x + w * 0.47, y + h * 0.42, 1.3)
    _smoke(draw, x + w * 0.47, y + h * 0.22, 1.0, 4)
    draw.rectangle([x, y + h - 8, x + w, y + h], fill=(30, 30, 38))


def scene_kharkiv(draw, box):
    x, y, w, h = box
    _sky(draw, box, (44, 44, 60), (120, 118, 130))
    # high-rise, damaged
    bx, bw = x + w * 0.18, w * 0.30
    draw.rectangle([bx, y + 16, bx + bw, y + h - 8], fill=(110, 104, 92))
    rows = max(1, int((h - 32) / 12))
    for r in range(rows):
        for c in range(3):
            ry0 = y + 22 + r * 12
            draw.rectangle([bx + 6 + c * 16, ry0,
                            bx + 16 + c * 16, ry0 + 8], fill=(60, 56, 48))
    # broken top corner
    draw.polygon([(bx + bw, y + 16), (bx + bw, y + h - 8), (bx + bw - 22, y + 16)], fill=(44, 44, 60))
    _flame(draw, x + w * 0.62, y + h - 8, 1.2)
    _smoke(draw, x + w * 0.62, y + h * 0.34, 1.0, 4)
    # second block
    draw.rectangle([x + w * 0.66, y + h * 0.42, x + w * 0.92, y + h - 8], fill=(88, 84, 76))


def scene_bank(draw, box):
    x, y, w, h = box
    _sky(draw, box, (206, 222, 232), (240, 240, 234))
    # bank building
    bx, bw = x + w * 0.20, w * 0.60
    draw.rectangle([bx, y + h * 0.30, bx + bw, y + h - 8], fill=(70, 96, 130))
    for i in range(4):
        cx2 = bx + 12 + i * 26
        draw.rectangle([cx2, y + h * 0.42, cx2 + 10, y + h - 8], fill=(220, 224, 230))
    draw.polygon([(bx - 6, y + h * 0.30), (bx + bw / 2, y + h * 0.08),
                  (bx + bw + 6, y + h * 0.30)], fill=(40, 60, 92))
    # rising arrow
    draw.line([(x + w * 0.10, y + h * 0.42), (x + w * 0.42, y + h * 0.30),
               (x + w * 0.62, y + h * 0.34), (x + w * 0.90, y + h * 0.12)],
              fill=(24, 140, 60), width=4)
    draw.polygon([(x + w * 0.90, y + h * 0.12), (x + w * 0.82, y + h * 0.12),
                  (x + w * 0.90, y + h * 0.22)], fill=(24, 140, 60))


def scene_chart(draw, box):
    x, y, w, h = box
    draw.rectangle([x, y, x + w, y + h], fill=(18, 40, 34))
    # grid
    for gy in range(1, 4):
        yy = y + h * gy / 4
        draw.line([(x + 6, yy), (x + w - 6, yy)], fill=(40, 80, 66), width=1)
    pts = [(x + 8 + i * (w - 16) / 7, y + h - 10 - i * (h - 20) / 7)
           for i in range(8)]
    draw.line(pts, fill=(60, 220, 120), width=3)
    draw.ellipse([pts[-1][0] - 5, pts[-1][1] - 5, pts[-1][0] + 5, pts[-1][1] + 5],
                 fill=(255, 213, 0))
    draw.rectangle([x + 24, y + 2, x + 116, y + 36], fill=(18, 40, 34))
    draw.text((x + 28, y + 4), "NIKKEI +1.6%", font=SANS_B(10), fill=(255, 255, 255))
    draw.text((x + 28, y + 20), "KOSPI +1.9%", font=SANS_B(10), fill=(60, 220, 120))


def scene_candle(draw, box):
    x, y, w, h = box
    _sky(draw, box, (30, 28, 44), (80, 70, 90))
    # Gateway arch
    ax, ay = x + w * 0.30, y + h * 0.30
    draw.rectangle([ax, ay, ax + w * 0.40, y + h * 0.85], fill=(150, 130, 100))
    draw.pieslice([ax + w * 0.10, ay + 6, ax + w * 0.30, ay + h * 0.85], 180, 360,
                  fill=(30, 28, 44))
    draw.rectangle([ax + w * 0.10, ay + h * 0.55, ax + w * 0.30, y + h * 0.85],
                   fill=(30, 28, 44))
    # candle
    cx = x + w * 0.82
    draw.rectangle([cx - 5, y + h * 0.44, cx + 5, y + h * 0.85], fill=(240, 236, 220))
    _flame(draw, cx, y + h * 0.44, 0.9)
    draw.ellipse([cx - 14, y + h * 0.40, cx + 14, y + h * 0.40 + h * 0.55],
                 outline=(255, 200, 60), width=2)


def scene_mine(draw, box):
    x, y, w, h = box
    _sky(draw, box, (90, 80, 60), (200, 180, 130))
    # pit walls
    draw.polygon([(x, y + h * 0.30), (x + w, y + h * 0.30), (x + w * 0.86, y + h),
                  (x + w * 0.14, y + h)], fill=(120, 96, 66))
    # water at the bottom
    draw.polygon([(x + w * 0.20, y + h * 0.72), (x + w * 0.80, y + h * 0.72),
                  (x + w * 0.86, y + h), (x + w * 0.14, y + h)], fill=(40, 110, 150))
    draw.line([(x + w * 0.24, y + h * 0.80), (x + w * 0.76, y + h * 0.80)],
              fill=(140, 200, 230), width=2)
    # helmet
    hx, hy = x + w * 0.50, y + h * 0.52
    draw.pieslice([hx - 16, hy - 12, hx + 16, hy + 12], 180, 360, fill=(255, 200, 0))
    draw.rectangle([hx - 18, hy - 2, hx + 18, hy + 2], fill=(255, 200, 0))
    draw.text((x + 26, y + 4), "100m PIT", font=SANS_B(11), fill=(255, 255, 255))


def scene_chip(draw, box):
    x, y, w, h = box
    draw.rectangle([x, y, x + w, y + h], fill=(16, 26, 44))
    u = h / 56.0
    # chip
    cx, cy = x + w * 0.38, y + h * 0.52
    draw.rectangle([cx - 26 * u, cy - 26 * u, cx + 26 * u, cy + 26 * u], fill=(30, 120, 90))
    draw.rectangle([cx - 14 * u, cy - 14 * u, cx + 14 * u, cy + 14 * u], fill=(16, 26, 44))
    draw.text((cx - 9 * u, cy - 9 * u), "AI", font=SANS_B(14), fill=(120, 230, 180))
    for dx, dy in [(-34, -20), (-34, 0), (-34, 20), (34, -20), (34, 0), (34, 20),
                   (-20, -34), (0, -34), (20, -34), (-20, 34), (0, 34), (20, 34)]:
        draw.line([(cx + dx * 0.7 * u, cy + dy * 0.7 * u), (cx + dx * u, cy + dy * u)],
                  fill=(120, 200, 170), width=2)
    # stop sign
    sx, sy = x + w * 0.80, y + h * 0.30
    draw.regular_polygon((sx, sy, 16 * u), 8, fill=(200, 30, 30))
    draw.text((sx - 11, sy - 7), "STOP", font=SANS_B(9), fill=(255, 255, 255))


def scene_virus(draw, box):
    x, y, w, h = box
    draw.rectangle([x, y, x + w, y + h], fill=(232, 238, 240))
    # virus circles with spikes
    for cx, cy, r in [(0.30, 0.42, 20), (0.62, 0.30, 15), (0.72, 0.66, 17),
                      (0.42, 0.74, 12)]:
        px, py = x + w * cx, y + h * cy
        for a in range(0, 360, 45):
            import math
            dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
            draw.line([(px + dx * r, py + dy * r),
                       (px + dx * (r + 8), py + dy * (r + 8))],
                      fill=(120, 40, 60), width=2)
        draw.ellipse([px - r, py - r, px + r, py + r], fill=(150, 50, 70))
    # medical cross chip
    draw.rounded_rectangle([x + w - 34, y + 6, x + w - 6, y + 34], radius=4,
                           fill=(255, 255, 255))
    draw.rectangle([x + w - 24, y + 10, x + w - 16, y + 30], fill=(200, 30, 30))
    draw.rectangle([x + w - 30, y + 16, x + w - 10, y + 24], fill=(200, 30, 30))


def scene_fire(draw, box):
    x, y, w, h = box
    _sky(draw, box, (70, 40, 20), (230, 140, 60))
    # island ground
    draw.ellipse([x - 10, y + h * 0.55, x + w + 10, y + h * 1.15], fill=(90, 70, 44))
    # trees
    for tx in (0.20, 0.45, 0.70, 0.88):
        px = x + w * tx
        draw.rectangle([px - 2, y + h * 0.40, px + 2, y + h * 0.58], fill=(60, 40, 20))
        draw.ellipse([px - 12, y + h * 0.16, px + 12, y + h * 0.48], fill=(40, 110, 50))
    _flame(draw, x + w * 0.30, y + h * 0.55, 1.4)
    _flame(draw, x + w * 0.62, y + h * 0.55, 1.1)
    _smoke(draw, x + w * 0.45, y + h * 0.30, 1.0, 3)


SCENES = {
    "storm": scene_storm, "kuwait": scene_kuwait, "eu": scene_eu,
    "abunada": scene_gaza, "kyiv": scene_kyiv, "kharkiv": scene_kharkiv,
    "bok": scene_bank, "rebound": scene_chart, "mumbai": scene_candle,
    "javamime": scene_mine, "nvidia": scene_chip, "ebola": scene_virus,
    "flinders": scene_fire,
}


def paste_scene(img, key, box):
    """Render one scene into its own tile and paste it, so no shape can
    spill outside its box."""
    x, y, w, h = box
    tile = Image.new("RGB", (int(w), int(h)), CREAM)
    td = ImageDraw.Draw(tile)
    SCENES[key](td, (0, 0, w, h))
    img.paste(tile, (int(x), int(y)))
    d2 = ImageDraw.Draw(img)
    d2.rectangle([x, y, x + w, y + h], outline=(120, 112, 96), width=1)


# ---------------------------------------------------------------- world map
# A deliberately coarse world map: continent blobs positioned by rough
# longitude/latitude boxes inside the map frame.

MAP_LON = (-168.0, 192.0)
MAP_LAT = (-58.0, 84.0)

# (lon_min, lat_min, lon_max, lat_max) per land blob, hand-placed.
BLOBS = [
    (-168, 15, -55, 72),      # North America
    (-80, -56, -34, 12),      # South America
    (-11, 36, 40, 70),        # Europe
    (-18, -35, 52, 37),       # Africa
    (40, 5, 180, 78),         # Asia (big block)
    (95, -50, 155, -10),      # SE Asia / Oceania north
    (112, -44, 154, -10),     # Australia
    (166, -48, 180, -34),     # New Zealand
    (-170, 60, -140, 72),     # Alaska (overlap, fine)
    (60, 42, 135, 72),        # Russia / Siberia (overlap, fine)
]


def lonlat_to_xy(lon, lat, box):
    x0, y0, x1, y1 = box
    fx = (lon - MAP_LON[0]) / (MAP_LON[1] - MAP_LON[0])
    fy = 1.0 - (lat - MAP_LAT[0]) / (MAP_LAT[1] - MAP_LAT[0])
    return x0 + fx * (x1 - x0), y0 + fy * (y1 - y0)


def draw_map(draw, box, stories):
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=(214, 228, 236))
    draw.rectangle([x0, y0, x1, y1], outline=(150, 168, 184), width=1)
    for (lo0, la0, lo1, la1) in BLOBS:
        ax, ay = lonlat_to_xy(lo0, la1, box)
        bx, by = lonlat_to_xy(lo1, la0, box)
        draw.rounded_rectangle([ax, ay, bx, by], radius=10, fill=(198, 188, 160))
    # graticule
    for lon in range(-150, 181, 30):
        gx, _ = lonlat_to_xy(lon, 0, box)
        draw.line([(gx, y0), (gx, y1)], fill=(190, 206, 216), width=1)
    for lat in (-30, 0, 30, 60):
        _, gy = lonlat_to_xy(0, lat, box)
        draw.line([(x0, gy), (x1, gy)], fill=(190, 206, 216), width=1)
    # pins
    for i, s in enumerate(stories, start=1):
        px, py = lonlat_to_xy(s["lon"], s["lat"], box)
        draw.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                     outline=(255, 255, 255), width=2)
        draw.text((px - 3, py - 6), str(i), font=SANS_B(9), fill=(255, 255, 255))


# ---------------------------------------------------------------- page build
def region_counts():
    counts = {r: 0 for r in REGION_ORDER}
    for s in FEATURES + CARDS:
        counts[s["region"]] += 1
    for _, _, r, _ in ALSO:
        counts[r] += 1
    return counts


def field_counts():
    counts = {}
    for s in FEATURES + CARDS:
        counts[s["field"]] = counts.get(s["field"], 0) + 1
    # ALSO items carry no field in the tuple; assign by keyword below.
    return counts


ALSO_FIELDS = {
    14: "War", 15: "Security", 16: "Justice", 17: "Diplomacy", 18: "War",
    19: "War", 20: "War", 21: "War", 22: "War", 23: "War", 24: "Aid",
    25: "Energy", 26: "Trade", 27: "Trade", 28: "Trade", 29: "Diplomacy",
    30: "Business", 31: "Security", 32: "Cyber", 33: "Diplomacy",
    34: "Security", 35: "Trade", 36: "Finance", 37: "Justice",
    38: "Diplomacy",
}


def build():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    mx = 24                      # side margin
    cw = W - 2 * mx              # content width

    # ---- eyebrow band
    d.rectangle([0, 0, W, 30], fill=NAVY)
    d.text((mx, 8), "THE WORLD IN ONE DAY", font=SANS_B(14), fill=(255, 255, 255))
    right = "38 STORIES \u00b7 10 REGIONS \u00b7 18 FIELDS \u00b7 ALL FIRST REPORTED THURSDAY 26 NOVEMBER 2026"
    tw = d.textlength(right, font=SANS_B(12))
    d.text((W - mx - tw, 9), right, font=SANS_B(12), fill=(255, 213, 0))

    # ---- masthead
    y = 34
    d.text((mx, y), "Thursday ", font=SERIF_B(54), fill=NAVY)
    w1 = d.textlength("Thursday ", font=SERIF_B(54))
    d.text((mx + w1, y), "26 November 2026", font=SERIF_B(54), fill=RED)

    # ---- red italic sub-headline
    y = 94
    d.text((mx, y), "Storm floods East Coast \u00b7 Drones kill 2 Italians in Kuwait \u00b7 EU summit opens in Brussels",
           font=SERIF_I(18), fill=RED)

    # ---- stat strip
    y = 120
    cell = cw / 6.0
    for i, (num, lab) in enumerate(STATS):
        cx = mx + i * cell
        d.text((cx + 4, y), num, font=SANS_B(25),
               fill=RED if i % 2 == 0 else NAVY)
        draw_wrapped(d, (cx + 4, y + 31), lab, SANS(10), GREY, cell - 10,
                     lh=12, max_lines=2)
        if i:
            d.line([(cx, y + 2), (cx, y + 54)], fill=LINE, width=1)
    y = 180
    d.line([(mx, y), (W - mx, y)], fill=NAVY, width=2)

    # ---- region chips (short labels; shrink the font if they overflow)
    y = 186
    counts = region_counts()
    short = {"SUB-SAHARAN AFRICA": "S. AFRICA", "EAST & SE ASIA": "E. & SE ASIA",
             "LATIN AMERICA": "LATIN AMER."}
    cf = SANS_B(11)
    total = sum(d.textlength("%s %d" % (short.get(r, r), counts[r]), font=cf) + 17
                for r in REGION_ORDER if counts[r])
    if total > cw:
        cf = SANS_B(10)
    cx = mx
    for r in REGION_ORDER:
        n = counts[r]
        if not n:
            continue
        label = "%s %d" % (short.get(r, r), n)
        cx += chip(d, (cx, y), label, cf, (255, 255, 255),
                   REGION_COLORS[r]) + 5
    # ---- fields line: big fields with counts, the rest grouped
    y = 210
    fc = field_counts()
    for num, _, _, _ in ALSO:
        f = ALSO_FIELDS[num]
        fc[f] = fc.get(f, 0) + 1
    big = sorted([(k, v) for k, v in fc.items() if v > 1], key=lambda kv: -kv[1])
    small = sorted([k for k, v in fc.items() if v == 1])
    fline = ("18 FIELDS \u2014 " + " \u00b7 ".join("%s %d" % (k, v) for k, v in big)
             + " \u00b7 %d more, 1 each: %s" % (len(small), ", ".join(small)))
    d.text((mx, y), fline, font=SANS(10), fill=GREY)

    # ---- UTC timeline bar
    y = 228
    d.rectangle([mx, y, W - mx, y + 22], fill=NAVY)
    tx = mx + 8
    d.text((tx, y + 4), "THE DAY IN UTC", font=SANS_B(10), fill=(255, 213, 0))
    tx += d.textlength("THE DAY IN UTC", font=SANS_B(10)) + 12
    for t, what in TIMELINE:
        seg = "%s %s" % (t, what)
        d.text((tx, y + 4), seg, font=SANS(10), fill=(255, 255, 255))
        tx += d.textlength(seg, font=SANS(10)) + 14

    # ---- features: 3 across
    y = 258
    fcol = (cw - 2 * 14) / 3.0
    art_h = 92
    fbottom = y
    for i, s in enumerate(FEATURES):
        fx = mx + i * (fcol + 14)
        paste_scene(img, s["key"], (fx, y, fcol, art_h))
        # number badge
        d.ellipse([fx + 4, y + 4, fx + 26, y + 26], fill=RED)
        d.text((fx + 11, y + 8), str(i + 1), font=SANS_B(13), fill=(255, 255, 255))
        ty = y + art_h + 6
        d.text((fx, ty), "%s \u00b7 %s" % (s["date"], s["field"].upper()),
               font=SANS_B(11), fill=NAVY)
        tagw = d.textlength("%s \u00b7 %s" % (s["date"], s["field"].upper()), font=SANS_B(11))
        chip(d, (fx + tagw + 8, ty - 1),
             "CONFIRMED" if s["tag"] == "C" else "REPORTED", SANS_B(9),
             (255, 255, 255), NAVY if s["tag"] == "C" else (150, 90, 20))
        hy = ty + 17
        hy = draw_wrapped(d, (fx, hy), s["head"], SERIF_B(20), DARK, fcol,
                          lh=22, max_lines=3)
        sy = draw_wrapped(d, (fx, hy + 2), s["summ"], SANS(12), (60, 60, 60),
                          fcol, lh=14, max_lines=3)
        d.text((fx, sy + 2), "WHY IT MATTERS: " + s["why"], font=SERIF_I(11),
               fill=RED)
        fbottom = max(fbottom, sy + 17)
    y = fbottom + 8

    # ---- cards: 2 rows x 5
    ccol = (cw - 4 * 10) / 5.0
    cart_h = 46
    for row in range(2):
        for col in range(5):
            s = CARDS[row * 5 + col]
            n = 4 + row * 5 + col
            cx = mx + col * (ccol + 10)
            cy = y + row * 116
            paste_scene(img, s["key"], (cx, cy, ccol, cart_h))
            d.ellipse([cx + 3, cy + 3, cx + 21, cy + 21], fill=RED)
            d.text((cx + 8, cy + 6), str(n), font=SANS_B(11), fill=(255, 255, 255))
            ty = cy + cart_h + 4
            d.text((cx, ty), "%s \u00b7 %s" % (s["date"], s["field"].upper()),
                   font=SANS_B(9), fill=NAVY)
            tagw = d.textlength("%s \u00b7 %s" % (s["date"], s["field"].upper()),
                                font=SANS_B(9))
            chip(d, (cx + tagw + 5, ty - 1),
                 "C" if s["tag"] == "C" else "R", SANS_B(8),
                 (255, 255, 255), NAVY if s["tag"] == "C" else (150, 90, 20))
            hy = ty + 13
            hy = draw_wrapped(d, (cx, hy), s["head"], SERIF_B(13), DARK, ccol,
                              lh=14, max_lines=2)
            draw_wrapped(d, (cx, hy + 1), s["summ"], SANS(10), (60, 60, 60),
                         ccol, lh=12, max_lines=2)
    y = y + 2 * 116 + 4
    d.line([(mx, y), (W - mx, y)], fill=NAVY, width=2)

    # ---- map + ALSO list (3 columns)
    y += 10
    map_w = 330
    map_h = 160
    d.text((mx, y), "THE WORLD \u2014 13 BIG STORIES PINNED",
           font=SANS_B(12), fill=NAVY)
    draw_map(d, (mx, y + 20, mx + map_w, y + 20 + map_h),
             FEATURES + CARDS)
    d.text((mx, y + 20 + map_h + 6), "Every pin is a story drawn above.",
           font=SANS(10), fill=GREY)
    lx = mx + map_w + 16
    lw = W - mx - lx
    d.text((lx, y), "ALSO ON THURSDAY 26 NOVEMBER \u2014 25 MORE STORIES",
           font=SANS_B(12), fill=NAVY)
    d.text((lx + lw - 150, y), "C CONFIRMED \u00b7 R REPORTED",
           font=SANS(9), fill=GREY)
    ly = y + 20
    colw = (lw - 2 * 10) / 3.0
    for idx, (num, text, region, tag) in enumerate(ALSO):
        col = idx // 9
        row = idx % 9
        ax = lx + col * (colw + 10)
        ay = ly + row * 16
        d.text((ax, ay), "%d" % num, font=SANS_B(9), fill=RED)
        d.text((ax + 18, ay), text, font=SANS(9), fill=DARK)
        tw2 = d.textlength(text, font=SANS(9))
        d.text((ax + 18 + tw2 + 4, ay), "[%s]" % tag, font=SANS_B(8),
               fill=NAVY if tag == "C" else (150, 90, 20))

    # ---- footer
    fy = y + 20 + map_h + 26
    d.line([(mx, fy), (W - mx, fy)], fill=LINE, width=1)
    fy = draw_wrapped(d, (mx, fy + 6), DATE_CHECK, SANS(10), DARK, cw,
                      lh=13, max_lines=3)
    d.text((mx, fy + 4), SOURCES, font=SANS(9), fill=GREY)

    img.save(OUT, format="PNG")
    return OUT


if __name__ == "__main__":
    print(build())
    # sanity counts
    total = len(FEATURES) + len(CARDS) + len(ALSO)
    print("stories:", total, "| regions:", len([r for r, n in region_counts().items() if n]))
    fc = field_counts()
    for num, _, _, _ in ALSO:
        f = ALSO_FIELDS[num]
        fc[f] = fc.get(f, 0) + 1
    print("fields:", len(fc), "| total field assignments:", sum(fc.values()))
