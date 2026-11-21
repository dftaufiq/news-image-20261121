#!/usr/bin/env python3
"""Build-time generator for entry.png: a one-page newspaper front page
summing up the world's news of Saturday 21 November 2026.

Drawn from scratch with Pillow (build-time only). The entry program,
main.py, is standard-library only and just copies the finished entry.png
into the grader's output directory, so both runs write identical bytes.

35 stories, each verified against reporting dated 21 November 2026 (market
figures are Friday's close, the latest available, and are labelled as such).
Stories from earlier days that other pages show as Saturday's news are
deliberately excluded and named in the DATE CHECK box. See README.md.

Run:  python3 generate_image.py   (writes entry.png next to this file)
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = Path(__file__).with_name("entry.png")
MARGIN = 22
CW = W - 2 * MARGIN  # content width: 980

# --- palette ------------------------------------------------------------------
PAPER = (251, 247, 239)
INK = (24, 24, 24)
NAVY = (22, 42, 74)
NAVY_DK = (13, 27, 51)
RED = (178, 32, 32)
GREY = (98, 96, 90)
RULE = (200, 192, 174)
SEA = (208, 224, 238)
LAND_DOT = (74, 96, 118)
WHITE = (255, 255, 255)

BEATS = {  # beat tag colours
    "CLIMATE": (26, 110, 60),
    "WAR": (158, 24, 24),
    "SECURITY": (70, 70, 78),
    "MARKETS": (140, 24, 24),
    "SPORT": (26, 110, 60),
    "ENERGY": (160, 90, 10),
    "WEATHER": (14, 110, 130),
    "RELIGION": (118, 58, 148),
    "DIPLOMACY": (30, 70, 130),
    "HEALTH": (158, 24, 24),
}

REGIONS = [  # (name, stories, colour) — sums to 35
    ("GLOBAL", 8, (108, 108, 108)),
    ("EUROPE", 7, (36, 84, 160)),
    ("MIDDLE EAST", 5, (190, 124, 18)),
    ("ASIA-PACIFIC", 5, (18, 138, 148)),
    ("UKRAINE WAR", 4, (158, 24, 24)),
    ("AMERICAS", 3, (118, 58, 148)),
    ("AFRICA", 3, (30, 128, 78)),
]

NUMBERS = [  # (big figure, label) for the day-in-numbers strip
    ("0", "climate deal agreed at COP31 as talks run on"),
    ("3", "Houthi missiles downed over Riyadh on Saturday"),
    ("\u22125.28%", "Nasdaq at Friday's close (22,617.73)"),
    ("$92.57", "Brent crude, Friday's settle (+0.64%)"),
    ("35.89", "VIX at Friday's close, highest in 19 months"),
    ("372,000", "people evacuated in Odisha before Akvan (Fri)"),
]

DECK = ("COP31 in overtime with no deal \u00b7 Three missiles downed over "
        "Riyadh \u00b7 Rutte flies to Warsaw \u00b7 Wall Street's worst week "
        "since 2020")

# --- the day's news (verified against 21 Nov 2026 reporting) ------------------
# leads: (number, place, beat, headline, deck, art key)
LEADS = [
    (1, "ANTALYA, T\u00dcRKIYE", "CLIMATE",
     "COP31 slips into overtime \u2014 still no deal",
     "Third draft due Saturday morning; fossil fuels and the $120bn "
     "target are out. Kurum: \u201cclose to the finish line but not "
     "there yet.\u201d (AP, AFP)",
     "cop31"),
    (2, "RIYADH, SAUDI ARABIA", "WAR",
     "Three Houthi missiles downed over Riyadh",
     "Coalition intercepts three ballistic missiles fired towards the "
     "capital on Saturday; Houthis threaten Saudi ports and warn "
     "airlines away. (Reuters)",
     "riyadh"),
    (3, "WARSAW, POLAND", "SECURITY",
     "Rutte flies to Warsaw after airspace breach",
     "NATO chief due on Saturday after Friday's incursion: a Kh-101 "
     "cruise missile and a drone crossed into Poland. Tusk: likely "
     "deliberate. (Reuters)",
     "warsaw"),
]

# features: (number, place, beat, headline, deck, art key)
FEATURES = [
    (4, "NEW YORK", "MARKETS",
     "Wall Street ends its worst week since 2020",
     "Nasdaq \u22125.28%; S&P in correction.",
     "wallst"),
    (5, "KYIV", "WAR",
     "Zelenskyy warns of \u2018double-tap\u2019 strikes",
     "\u201cTo kill as many as possible.\u201d",
     "zelenskyy"),
    (6, "TURIN", "SPORT",
     "ATP semis: the top four seeds in Turin",
     "Alcaraz\u2013Shelton, Zverev\u2013Medvedev.",
     "atp"),
    (7, "ENERGY", "ENERGY",
     "Brent settles at $92.57 a barrel",
     "+0.6% Friday; \u22123.4% on the week.",
     "brent"),
    (8, "MARKETS", "MARKETS",
     "Gold falls 3% to $3,517 at the close",
     "Down 3.02% at Friday's US close.",
     "gold"),
    (9, "ODISHA, INDIA", "WEATHER",
     "Akvan weakens; Odisha counts no deaths",
     "372,000 evacuated on Friday.",
     "akvan"),
    (10, "COOK ISLANDS", "WEATHER",
     "Xavier weakens; gale warnings hold",
     "Gales hold for three Cook Islands.",
     "xavier"),
    (11, "VATICAN", "RELIGION",
     "Vatican tree goes up at St Peter's",
     "Christmas comes to the Vatican.",
     "vatican"),
    (12, "BRUSSELS", "DIPLOMACY",
     "EU approves \u20ac1bn arms aid for Kyiv",
     "Plus \u20ac8bn disbursed to Kyiv.",
     "euaid"),
    (13, "EASTERN CONGO", "HEALTH",
     "Ebola in eastern Congo hits schools",
     "~100 schools affected, UN says.",
     "ebola"),
]

# briefs 14-35 (one line each at 11px condensed in a 307px column)
BRIEFS = [
    "BUDAPEST Hungary lifts block on EU talks with Ukraine",
    "PRAGUE Czechia accelerates air defence",
    "ROME Workers and students protest Meloni",
    "GAZA 22,000 children dead, health ministry says",
    "JAZAN Coalition downs 2 Houthi projectiles",
    "HODEIDAH UN: attacks threaten aid lifeline",
    "WEST BANK Settler guard shoots Palestinian dead",
    "UKRAINE Hits 3 Russian missile launchers",
    "LVIV Strike on Sknyliv station kills 2",
    "MOSCOW Putin rejects energy ceasefire",
    "PARIS Macron: four-way talks must happen",
    "PYONGYANG N. Korea, Laos agree closer ties",
    "BEIJING Urges Tokyo to clarify Taiwan stance",
    "SEOUL Firm offers $150m to Trump-linked robot maker",
    "SAN SALVADOR Bukele formalises third-term bid",
    "BRAS\u00cdLIA Indigenous land bill advances",
    "GEORGETOWN US floated giving part of Guyana away",
    "RABAT Morocco plans \u20ac366m defence sector",
    "DAKAR President passes budget by decree",
    "STABLECOINS Growth threatens stability, watchdog warns",
    "CHILDREN 1 in 4 live in a conflict area",
    "GENEVA UN killer-robot talks run past deadline",
]

DATE_CHECK = (
    "DATE CHECK \u2014 checked against the source and left out because they are "
    "NOT Saturday's news: the Denmark \u2018assassination plot\u2019 and Gupta's "
    "sentencing (Fri) \u00b7 the US clearing 900,000 AI chips for China and "
    "Mongolia's president resigning (Thu) \u00b7 India's H5N1 vaccine, the "
    "measles ruling, the SCO forum opening and the Kryvyi Rih strike (Fri) "
    "\u00b7 Cairncross fired and the HIMARS strike (Thu) \u00b7 Voyager 1's "
    "light-day (Wed) \u00b7 the ANC's 31% (4 Nov vote) \u00b7 Mackenzie's 200 "
    "years (6 Nov) \u00b7 the Kyiv barrage and Akvan's landfall (Fri)."
)

FOOTER = ("Every story happened, or was first reported, on Saturday 21 November "
          "2026. Market figures are Friday's close, the latest available. "
          "Sources named beside each story \u00b7 Original drawings")


# --- fonts ----------------------------------------------------------------------
FONT_DIR = Path("/usr/share/fonts/truetype")
_font_cache: dict = {}


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(str(FONT_DIR / path), size)
    return _font_cache[key]


SERIF_BOLD = "liberation/LiberationSerif-Bold.ttf"
SERIF_ITALIC = "dejavu/DejaVuSerif-Italic.ttf"
SANS = "dejavu/DejaVuSans.ttf"
SANS_BOLD = "dejavu/DejaVuSans-Bold.ttf"
SANS_COND = "dejavu/DejaVuSansCondensed.ttf"
SANS_COND_BOLD = "dejavu/DejaVuSansCondensed-Bold.ttf"


# --- text helpers ---------------------------------------------------------------
def wrap(draw: ImageDraw.ImageDraw, text: str,
          fnt: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    """Greedy word wrap to a pixel width."""
    out: list[str] = []
    line = ""
    for word in text.split(" "):
        trial = word if not line else line + " " + word
        if draw.textlength(trial, font=fnt) <= max_w:
            line = trial
        else:
            if line:
                out.append(line)
            line = word
    if line:
        out.append(line)
    return out


def put_lines(draw: ImageDraw.ImageDraw, x: int, y: int, lines: list[str],
              fnt: ImageFont.FreeTypeFont, fill, leading: int) -> int:
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def put_wrapped(draw: ImageDraw.ImageDraw, x: int, y: int, text: str,
                fnt: ImageFont.FreeTypeFont, max_w: int, fill,
                leading: int) -> int:
    return put_lines(draw, x, y, wrap(draw, text, fnt, max_w), fnt, fill,
                     leading)


def number_badge(draw: ImageDraw.ImageDraw, x: int, y: int, n: int,
                 size: int, colour) -> None:
    """Filled square with a white number inside."""
    draw.rectangle([x, y, x + size, y + size], fill=colour)
    f = font(SANS_BOLD, size - 6 if n < 10 else size - 7)
    t = str(n)
    tw = draw.textlength(t, font=f)
    draw.text((x + (size - tw) / 2, y + (size - f.size) / 2 - 1), t,
              font=f, fill=WHITE)


def tag_chip(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, bg,
             size: int = 11) -> int:
    """Small filled label; returns its width."""
    f = font(SANS_BOLD, size)
    w = int(draw.textlength(text, font=f)) + 12
    h = size + 8
    draw.rectangle([x, y, x + w, y + h], fill=bg)
    draw.text((x + 6, y + 3), text, font=f, fill=WHITE)
    return w


def starburst(draw: ImageDraw.ImageDraw, cx: float, cy: float, r: float,
              colour, core=None) -> None:
    """Eight-point explosion star, optionally with a bright core."""
    pts = []
    for i in range(16):
        ang = math.pi * i / 8 - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    draw.polygon(pts, fill=colour)
    if core:
        draw.ellipse([cx - r * 0.32, cy - r * 0.32, cx + r * 0.32,
                      cy + r * 0.32], fill=core)


def dashed_line(draw: ImageDraw.ImageDraw, pts, colour, width: int = 2,
                dash: int = 7, gap: int = 5) -> None:
    """Dashed polyline through pts."""
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        seg = math.hypot(x2 - x1, y2 - y1)
        if seg == 0:
            continue
        ux, uy = (x2 - x1) / seg, (y2 - y1) / seg
        s = 0.0
        while s < seg:
            e = min(s + dash, seg)
            draw.line([x1 + ux * s, y1 + uy * s, x1 + ux * e, y1 + uy * e],
                      fill=colour, width=width)
            s = e + gap


# --- illustration panels (all drawn from primitives) ----------------------------
def art_cop31(d, x, y, w, h):
    """Climate talks run out of time: globe, thermometer, clock at overtime."""
    d.rectangle([x, y, x + w, y + h], fill=(18, 60, 52))
    # globe, left
    gx, gy, gr = x + w * 0.22, y + h * 0.52, h * 0.36
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(64, 140, 190),
              outline=(220, 230, 220), width=2)
    d.ellipse([gx - gr * 0.55, gy - gr, gx + gr * 0.55, gy + gr],
              outline=(220, 230, 220), width=1)
    d.line([gx - gr, gy, gx + gr, gy], fill=(220, 230, 220), width=1)
    d.polygon([(gx - gr * 0.5, gy - gr * 0.3), (gx - gr * 0.1, gy - gr * 0.55),
               (gx + gr * 0.3, gy - gr * 0.2), (gx + gr * 0.1, gy + gr * 0.25),
               (gx - gr * 0.35, gy + gr * 0.3)], fill=(96, 170, 110))
    # thermometer, middle
    tx = x + w * 0.50
    d.rectangle([tx - 5, y + h * 0.16, tx + 5, y + h * 0.72],
                fill=(240, 240, 230))
    d.rectangle([tx - 5, y + h * 0.42, tx + 5, y + h * 0.72],
                fill=(230, 70, 50))
    d.ellipse([tx - 10, y + h * 0.68, tx + 10, y + h * 0.88],
              fill=(230, 70, 50))
    d.text((tx + 12, y + h * 0.18), "+1.5\u00b0C", font=font(SANS_BOLD, 11),
           fill=(255, 200, 120))
    # clock, right: hands past midnight, "OVERTIME"
    cx, cy, cr = x + w * 0.80, y + h * 0.50, h * 0.34
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(250, 246, 238),
              outline=(200, 170, 60), width=3)
    d.line([cx, cy, cx, cy - cr * 0.62], fill=INK, width=3)
    d.line([cx, cy, cx + cr * 0.55, cy + cr * 0.30], fill=INK, width=3)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=RED)
    tag_chip(d, x + 8, y + h - 26, "OVERTIME \u00b7 NO DEAL", RED)


def art_riyadh(d, x, y, w, h):
    """Night Riyadh: skyline with the tall tower, three missiles intercepted."""
    d.rectangle([x, y, x + w, y + h], fill=(14, 24, 46))
    for sx, sy in [(0.06, 0.12), (0.18, 0.07), (0.34, 0.14), (0.52, 0.06),
                   (0.70, 0.12), (0.86, 0.07), (0.94, 0.18), (0.44, 0.20)]:
        d.ellipse([x + w * sx - 1, y + h * sy - 1, x + w * sx + 1,
                   y + h * sy + 1], fill=(215, 215, 195))
    # skyline, tallest tower centre-left
    towers = [(0.00, 0.55, 0.10, 0.45), (0.11, 0.62, 0.08, 0.38),
              (0.20, 0.48, 0.09, 0.52), (0.30, 0.30, 0.08, 0.70),
              (0.39, 0.58, 0.09, 0.42), (0.50, 0.50, 0.08, 0.50),
              (0.60, 0.64, 0.09, 0.36), (0.70, 0.56, 0.08, 0.44),
              (0.80, 0.66, 0.09, 0.34), (0.90, 0.60, 0.10, 0.40)]
    for fx, fy, fw, fh in towers:
        d.rectangle([x + w * fx, y + h * fy, x + w * (fx + fw),
                     y + h * (fy + fh)], fill=(7, 12, 24))
        for wy in range(4):
            for wx in range(2):
                if (int(fx * 100) + wy * 2 + wx) % 3 == 0:
                    d.rectangle([x + w * fx + 4 + wx * 10,
                                 y + h * fy + 6 + wy * 11,
                                 x + w * fx + 8 + wx * 10,
                                 y + h * fy + 10 + wy * 11],
                                fill=(240, 200, 90))
    # tower crown light
    d.ellipse([x + w * 0.34 - 3, y + h * 0.30 - 5, x + w * 0.34 + 3,
               y + h * 0.30 + 1], fill=(255, 90, 70))
    # three incoming arcs, intercepted mid-sky with bursts
    for ax, ay, bx, by in [(0.95, 0.03, 0.74, 0.34), (0.82, 0.02, 0.58, 0.40),
                           (0.62, 0.02, 0.40, 0.36)]:
        dashed_line(d, [(x + w * ax, y + h * ay), (x + w * (ax + bx) / 2,
                     y + h * (ay + by) / 2 - 6), (x + w * bx, y + h * by)],
                    (255, 190, 90), width=2)
        starburst(d, x + w * bx, y + h * by, 11, (255, 150, 40),
                  (255, 230, 120))
    # shield over the city
    shx, shy = x + w * 0.55, y + h * 0.60
    d.polygon([(shx, shy - 12), (shx + 12, shy - 6), (shx + 12, shy + 4),
               (shx, shy + 14), (shx - 12, shy + 4), (shx - 12, shy - 6)],
              outline=(120, 220, 140), width=2)
    d.line([shx - 6, shy, shx - 1, shy + 5, shx + 7, shy - 5],
           fill=(120, 220, 140), width=2)
    tag_chip(d, x + 8, y + h - 26, "3 INTERCEPTED", RED)


def art_warsaw(d, x, y, w, h):
    """Poland on the map: red intrusion arrow from the east, NATO plane in."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 236, 242))
    # rough Poland outline
    poly = [(0.18, 0.22), (0.34, 0.12), (0.52, 0.16), (0.66, 0.10),
            (0.78, 0.22), (0.84, 0.38), (0.76, 0.52), (0.80, 0.66),
            (0.66, 0.78), (0.52, 0.86), (0.38, 0.80), (0.24, 0.82),
            (0.14, 0.64), (0.10, 0.44)]
    d.polygon([(x + w * a, y + h * b) for a, b in poly],
              fill=(255, 255, 255), outline=(36, 84, 160), width=2)
    # Warsaw dot
    wx, wy = x + w * 0.55, y + h * 0.38
    d.ellipse([wx - 5, wy - 5, wx + 5, wy + 5], fill=RED)
    d.text((wx + 8, wy - 6), "WARSAW", font=font(SANS_BOLD, 10), fill=NAVY)
    # intrusion arrows from the east (red)
    for ay in (0.30, 0.52):
        ex = x + w * 0.99
        d.line([ex, y + h * ay, x + w * 0.84, y + h * ay], fill=RED, width=3)
        d.polygon([(x + w * 0.84, y + h * ay - 6), (x + w * 0.84,
                   y + h * ay + 6), (x + w * 0.76, y + h * ay)], fill=RED)
    d.text((x + w * 0.88, y + h * 0.40), "EAST", font=font(SANS_BOLD, 9),
           fill=RED)
    # NATO plane flying in from the west
    px, py = x + w * 0.16, y + h * 0.30
    d.polygon([(px - 14, py), (px + 12, py - 3), (px + 16, py),
               (px + 12, py + 3), (px - 14, py + 2)], fill=NAVY)
    d.polygon([(px - 2, py - 8), (px + 4, py - 2), (px - 4, py - 1)],
              fill=NAVY)
    dashed_line(d, [(x + 4, y + h * 0.22), (px - 14, py)], NAVY, width=1)
    # NATO star (four-point) top left
    sx, sy = x + w * 0.10, y + h * 0.78
    d.polygon([(sx, sy - 10), (sx + 3, sy - 3), (sx + 10, sy), (sx + 3, sy + 3),
               (sx, sy + 10), (sx - 3, sy + 3), (sx - 10, sy), (sx - 3, sy - 3)],
              fill=(36, 84, 160))
    tag_chip(d, x + w - 96, y + h - 26, "NATO CHIEF IN", NAVY)


def art_wallst(d, x, y, w, h):
    """Falling market chart on a dark board."""
    d.rectangle([x, y, x + w, y + h], fill=(18, 20, 26))
    for gy in range(1, 3):
        d.line([x + 6, y + h * gy / 4, x + w - 6, y + h * gy / 4],
               fill=(48, 52, 62), width=1)
    pts = [(0.05, 0.10), (0.20, 0.20), (0.32, 0.16), (0.46, 0.34),
           (0.58, 0.32), (0.72, 0.48), (0.84, 0.46), (0.95, 0.62)]
    px = [(x + w * a, y + h * b) for a, b in pts]
    d.line(px, fill=(230, 60, 60), width=3, joint="curve")
    ex, ey = px[-1]
    d.polygon([(ex + 1, ey + 8), (ex - 7, ey - 2), (ex + 6, ey - 5)],
              fill=(230, 60, 60))
    tick = [("S&P", "\u22123.7%"), ("NASDAQ", "\u22125.3%"),
            ("DOW", "\u22121.9%")]
    tx = x + 8
    for name, val in tick:
        f1, f2 = font(SANS_BOLD, 9), font(SANS_BOLD, 10)
        d.text((tx, y + h - 26), name, font=f1, fill=(180, 180, 180))
        d.text((tx, y + h - 15), val, font=f2, fill=(255, 110, 110))
        tx += max(d.textlength(name, font=f1),
                  d.textlength(val, font=f2)) + 14


def art_zelenskyy(d, x, y, w, h):
    """Ukraine colours, warning triangle, two blasts: the double tap."""
    d.rectangle([x, y, x + w, y + h * 0.5], fill=(36, 100, 190))
    d.rectangle([x, y + h * 0.5, x + w, y + h], fill=(245, 200, 40))
    # warning triangle
    cx, cy = x + w * 0.5, y + h * 0.42
    d.polygon([(cx, cy - 16), (cx + 18, cy + 12), (cx - 18, cy + 12)],
              fill=(255, 255, 255), outline=INK, width=2)
    d.text((cx - 3, cy - 6), "!", font=font(SANS_BOLD, 16), fill=RED)
    # two bursts
    starburst(d, x + w * 0.16, y + h * 0.72, 9, (255, 150, 40),
              (255, 230, 120))
    starburst(d, x + w * 0.84, y + h * 0.72, 9, (255, 150, 40),
              (255, 230, 120))
    d.text((x + w * 0.16 - 4, y + h * 0.72 + 10), "1", font=font(SANS_BOLD, 9),
           fill=INK)
    d.text((x + w * 0.84 - 4, y + h * 0.72 + 10), "2", font=font(SANS_BOLD, 9),
           fill=INK)


def art_atp(d, x, y, w, h):
    """Indoor hard court, top down: lines, net, two balls."""
    d.rectangle([x, y, x + w, y + h], fill=(44, 110, 160))
    d.rectangle([x + w * 0.08, y + h * 0.10, x + w * 0.92, y + h * 0.90],
                outline=(255, 255, 255), width=2)
    d.rectangle([x + w * 0.22, y + h * 0.10, x + w * 0.78, y + h * 0.90],
                outline=(255, 255, 255), width=1)
    d.line([x + w * 0.08, y + h * 0.5, x + w * 0.92, y + h * 0.5],
           fill=(255, 255, 255), width=2)
    d.line([x + w * 0.5, y + h * 0.10, x + w * 0.5, y + h * 0.90],
           fill=(255, 255, 255), width=1)
    for bx, by in [(0.35, 0.28), (0.68, 0.72)]:
        d.ellipse([x + w * bx - 5, y + h * by - 5, x + w * bx + 5,
                   y + h * by + 5], fill=(210, 230, 60),
                  outline=(255, 255, 255), width=1)
    tag_chip(d, x + 6, y + 5, "SF \u00b7 TURIN", NAVY, size=9)


def art_brent(d, x, y, w, h):
    """Oil barrel and pumpjack at dusk."""
    d.rectangle([x, y, x + w, y + h], fill=(58, 44, 30))
    d.ellipse([x + w * 0.72, y + h * 0.08, x + w * 0.94, y + h * 0.42],
              fill=(240, 180, 80))
    # pumpjack silhouette
    bx, by = x + w * 0.30, y + h * 0.78
    d.line([bx, by, bx + 4, y + h * 0.30], fill=INK, width=4)
    d.line([bx - 26, y + h * 0.34, bx + 34, y + h * 0.24], fill=INK, width=4)
    d.line([bx + 30, y + h * 0.25, bx + 30, y + h * 0.44], fill=INK, width=2)
    d.line([bx - 12, by, bx + 16, by], fill=INK, width=4)
    # barrel
    d.rectangle([x + w * 0.62, y + h * 0.52, x + w * 0.86, y + h * 0.90],
                fill=(150, 60, 30), outline=(220, 170, 90), width=2)
    d.line([x + w * 0.62, y + h * 0.62, x + w * 0.86, y + h * 0.62],
           fill=(220, 170, 90), width=2)
    d.line([x + w * 0.62, y + h * 0.80, x + w * 0.86, y + h * 0.80],
           fill=(220, 170, 90), width=2)
    d.text((x + w * 0.66, y + h * 0.66), "OIL", font=font(SANS_BOLD, 9),
           fill=(255, 230, 180))


def art_gold(d, x, y, w, h):
    """Stacked gold ingots with a falling price arrow."""
    d.rectangle([x, y, x + w, y + h], fill=(30, 30, 38))
    def ingot(ix, iy, iw):
        d.polygon([(ix, iy + 12), (ix + 4, iy), (ix + iw - 4, iy),
                   (ix + iw, iy + 12)], fill=(212, 175, 55),
                  outline=(255, 225, 130))
        d.polygon([(ix + 4, iy), (ix + iw - 4, iy), (ix + iw - 8, iy - 5),
                   (ix + 8, iy - 5)], fill=(240, 205, 100))
    ingot(x + w * 0.10, y + h * 0.62, 34)
    ingot(x + w * 0.38, y + h * 0.62, 34)
    ingot(x + w * 0.66, y + h * 0.62, 34)
    ingot(x + w * 0.24, y + h * 0.38, 34)
    ingot(x + w * 0.52, y + h * 0.38, 34)
    ingot(x + w * 0.38, y + h * 0.14, 34)
    # down arrow
    ax = x + w * 0.88
    d.line([ax, y + h * 0.10, ax, y + h * 0.42], fill=(230, 60, 60), width=3)
    d.polygon([(ax - 6, y + h * 0.36), (ax + 6, y + h * 0.36),
               (ax, y + h * 0.50)], fill=(230, 60, 60))


def art_akvan(d, x, y, w, h):
    """Cyclone spiral over the Bay of Bengal, Odisha coast on the left."""
    d.rectangle([x, y, x + w, y + h], fill=(52, 110, 158))
    d.polygon([(x, y), (x + w * 0.30, y), (x + w * 0.24, y + h * 0.35),
               (x + w * 0.30, y + h * 0.62), (x + w * 0.20, y + h),
               (x, y + h)], fill=(214, 196, 150))
    d.text((x + 5, y + 4), "ODISHA", font=font(SANS_BOLD, 9), fill=(90, 70, 40))
    cx, cy = x + w * 0.62, y + h * 0.52
    for k, rr in enumerate(range(34, 6, -7)):
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], 210 + k * 60,
              210 + k * 60 + 250, fill=WHITE, width=3)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=WHITE)
    gx, gy = x + w * 0.28, y + h * 0.48
    d.ellipse([gx - 4, gy - 4, gx + 4, gy + 4], fill=RED)
    d.ellipse([gx - 8, gy - 8, gx + 8, gy + 8], outline=RED, width=2)
    tag_chip(d, x + w - 78, y + 5, "WEAKENING", (14, 110, 130), size=9)


def art_xavier(d, x, y, w, h):
    """South Pacific storm: swirl over blue sea, gale flag on an island."""
    d.rectangle([x, y, x + w, y + h], fill=(38, 96, 150))
    # island dots
    for ix, iy in [(0.12, 0.70), (0.24, 0.82), (0.86, 0.24), (0.78, 0.78)]:
        d.ellipse([x + w * ix - 6, y + h * iy - 4, x + w * ix + 6,
                   y + h * iy + 4], fill=(214, 196, 150))
    cx, cy = x + w * 0.52, y + h * 0.48
    for k, rr in enumerate(range(30, 6, -6)):
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], 150 + k * 70,
              150 + k * 70 + 240, fill=WHITE, width=3)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=WHITE)
    # gale flag on the biggest island
    fx, fy = x + w * 0.12, y + h * 0.70
    d.line([fx, fy - 4, fx, fy - 22], fill=INK, width=2)
    d.polygon([(fx, fy - 22), (fx + 16, fy - 18), (fx, fy - 14)],
              fill=RED)
    tag_chip(d, x + w - 92, y + h - 22, "GALE WARNING", RED, size=9)


def art_vatican(d, x, y, w, h):
    """St Peter's dome silhouette beside a lit Christmas tree."""
    d.rectangle([x, y, x + w, y + h], fill=(24, 36, 60))
    for sx, sy in [(0.10, 0.14), (0.30, 0.08), (0.55, 0.12), (0.78, 0.08),
                   (0.92, 0.16)]:
        d.ellipse([x + w * sx - 1, y + h * sy - 1, x + w * sx + 1,
                   y + h * sy + 1], fill=(220, 220, 200))
    # dome silhouette
    dx, dy = x + w * 0.30, y + h * 0.86
    d.rectangle([dx - 34, dy - 26, dx + 34, dy], fill=(10, 16, 30))
    d.pieslice([dx - 26, dy - 62, dx + 26, dy - 10], 180, 360,
               fill=(10, 16, 30))
    d.rectangle([dx - 3, dy - 72, dx + 3, dy - 58], fill=(10, 16, 30))
    d.ellipse([dx - 2, dy - 78, dx + 2, dy - 70], fill=(240, 200, 90))
    # tree
    tx = x + w * 0.74
    for k, (tw, ty) in enumerate([(30, 0.30), (24, 0.44), (18, 0.58)]):
        d.polygon([(tx, y + h * ty - 14), (tx - tw, y + h * ty + 14),
                   (tx + tw, y + h * ty + 14)], fill=(30, 120, 60))
    d.rectangle([tx - 4, y + h * 0.72, tx + 4, y + h * 0.86],
                fill=(120, 80, 40))
    starburst(d, tx, y + h * 0.30 - 16, 6, (255, 220, 90))
    for lx, ly in [(0.68, 0.40), (0.80, 0.44), (0.70, 0.56), (0.79, 0.60),
                   (0.74, 0.50)]:
        d.ellipse([x + w * lx - 2, y + h * ly - 2, x + w * lx + 2,
                   y + h * ly + 2], fill=(255, 220, 90))


def art_euaid(d, x, y, w, h):
    """EU circle of stars over a euro aid crate."""
    d.rectangle([x, y, x + w, y + h], fill=(24, 54, 140))
    ccx, ccy = x + w * 0.5, y + h * 0.36
    for i in range(12):
        ang = math.pi * 2 * i / 12 - math.pi / 2
        sx, sy = ccx + 30 * math.cos(ang), ccy + 16 * math.sin(ang)
        starburst(d, sx, sy, 3.2, (255, 210, 60))
    # crate
    d.rectangle([x + w * 0.30, y + h * 0.58, x + w * 0.70, y + h * 0.92],
                fill=(180, 140, 80), outline=(120, 90, 40), width=2)
    d.line([x + w * 0.30, y + h * 0.58, x + w * 0.70, y + h * 0.92],
           fill=(120, 90, 40), width=2)
    d.line([x + w * 0.70, y + h * 0.58, x + w * 0.30, y + h * 0.92],
           fill=(120, 90, 40), width=2)
    d.text((x + w * 0.44, y + h * 0.66), "\u20ac", font=font(SANS_BOLD, 16),
           fill=WHITE)


def art_ebola(d, x, y, w, h):
    """Virus particle with spikes; a schoolhouse below."""
    d.rectangle([x, y, x + w, y + h], fill=(70, 20, 28))
    cx, cy, cr = x + w * 0.5, y + h * 0.38, 13
    for i in range(12):
        ang = math.pi * 2 * i / 12
        x1, y1 = cx + cr * math.cos(ang), cy + cr * math.sin(ang)
        x2, y2 = cx + (cr + 7) * math.cos(ang), cy + (cr + 7) * math.sin(ang)
        d.line([x1, y1, x2, y2], fill=(230, 120, 120), width=2)
        d.ellipse([x2 - 2, y2 - 2, x2 + 2, y2 + 2], fill=(230, 120, 120))
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(200, 60, 60))
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(140, 30, 40))
    # schoolhouse
    sx = x + w * 0.5
    d.rectangle([sx - 30, y + h * 0.72, sx + 30, y + h * 0.94],
                fill=(230, 220, 200))
    d.polygon([(sx - 36, y + h * 0.72), (sx, y + h * 0.58),
               (sx + 36, y + h * 0.72)], fill=(150, 40, 40))
    d.rectangle([sx - 5, y + h * 0.80, sx + 5, y + h * 0.94], fill=(90, 60, 40))
    tag_chip(d, x + 6, y + 5, "OUTBREAK", RED, size=9)


ART = {
    "cop31": art_cop31, "riyadh": art_riyadh, "warsaw": art_warsaw,
    "wallst": art_wallst, "zelenskyy": art_zelenskyy, "atp": art_atp,
    "brent": art_brent, "gold": art_gold, "akvan": art_akvan,
    "xavier": art_xavier, "vatican": art_vatican, "euaid": art_euaid,
    "ebola": art_ebola,
}


# --- dot-grid world map ---------------------------------------------------------
# Rough continent outlines in (longitude, latitude); dots fall on land.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 79), (-85, 76),
     (-80, 73), (-70, 62), (-65, 60), (-60, 52), (-55, 47), (-60, 45),
     (-65, 44), (-70, 42), (-74, 40), (-76, 35), (-80, 32), (-81, 25),
     (-84, 30), (-90, 29), (-97, 26), (-97, 16), (-94, 16), (-90, 14),
     (-86, 13), (-83, 9), (-80, 8), (-77, 7), (-79, 9), (-83, 10),
     (-87, 13), (-90, 14), (-92, 15), (-96, 16), (-105, 20), (-110, 23),
     (-114, 29), (-117, 33), (-122, 37), (-124, 42), (-124, 48), (-130, 55),
     (-135, 58), (-145, 60), (-155, 58), (-162, 58)],
    # South America
    [(-79, 9), (-75, 11), (-72, 12), (-64, 10), (-60, 8), (-52, 5),
     (-50, 0), (-44, -3), (-35, -8), (-38, -15), (-40, -22), (-48, -28),
     (-52, -33), (-57, -38), (-62, -41), (-65, -45), (-68, -50), (-69, -52),
     (-71, -54), (-73, -50), (-73, -44), (-73, -37), (-71, -30), (-70, -23),
     (-75, -15), (-77, -12), (-80, -6), (-81, -1), (-80, 1), (-79, 6)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (0, 50), (3, 51),
     (5, 53), (8, 55), (8, 57), (10, 58), (12, 54), (18, 56), (21, 55),
     (24, 58), (23, 60), (21, 65), (18, 69), (25, 71), (30, 70), (32, 66),
     (28, 62), (24, 58), (30, 60), (28, 56), (26, 52), (30, 51), (32, 47),
     (29, 45), (28, 44), (23, 40), (22, 37), (26, 38), (28, 41), (30, 42),
     (28, 45), (24, 46), (19, 45), (16, 42), (18, 40), (16, 38), (15, 40),
     (12, 42), (10, 44), (8, 44), (6, 43), (3, 42), (0, 38), (-2, 37),
     (-6, 36), (-9, 37)],
    # Africa
    [(-17, 15), (-17, 21), (-10, 31), (-5, 35), (0, 36), (10, 37),
     (11, 34), (15, 32), (20, 32), (25, 32), (30, 31), (32, 31), (34, 28),
     (35, 23), (37, 18), (39, 15), (43, 12), (48, 11), (51, 12), (46, 5),
     (42, -1), (40, -4), (39, -7), (36, -18), (35, -23), (33, -26),
     (31, -29), (28, -33), (25, -34), (20, -35), (18, -33), (16, -28),
     (14, -22), (12, -18), (12, -13), (13, -9), (9, -1), (9, 4), (6, 5),
     (-2, 5), (-7, 5), (-13, 8), (-17, 12)],
    # Asia (incl. Middle East and India)
    [(30, 36), (35, 36), (36, 42), (40, 41), (44, 40), (47, 39), (48, 30),
     (50, 29), (52, 26), (54, 26), (57, 27), (58, 25), (61, 25), (66, 25),
     (67, 24), (70, 21), (72, 20), (73, 16), (75, 12), (77, 8), (80, 7),
     (80, 10), (84, 19), (88, 22), (91, 22), (92, 16), (94, 17), (97, 16),
     (98, 10), (100, 8), (101, 7), (103, 1), (104, 2), (105, 9), (107, 11),
     (109, 13), (109, 18), (106, 20), (108, 22), (110, 21), (114, 22),
     (117, 23), (120, 25), (121, 28), (122, 31), (122, 37), (126, 40),
     (128, 40), (130, 42), (132, 43), (135, 44), (137, 46), (140, 48),
     (142, 50), (142, 54), (141, 59), (139, 60), (142, 62), (150, 60),
     (155, 59), (158, 52), (160, 55), (162, 58), (162, 60), (170, 60),
     (178, 65), (178, 68), (170, 67), (160, 69), (155, 71), (145, 72),
     (135, 72), (125, 73), (115, 74), (105, 77), (100, 76), (95, 75),
     (90, 75), (85, 73), (80, 73), (75, 72), (70, 72), (65, 69), (60, 69),
     (55, 68), (50, 68), (45, 68), (40, 67), (35, 66), (32, 64), (30, 62),
     (30, 60), (32, 56), (35, 55), (38, 55), (40, 53), (42, 52), (44, 51),
     (46, 50), (48, 48), (47, 46), (44, 45), (42, 44), (40, 44), (38, 42),
     (35, 41), (33, 40)],
    # Australia
    [(113, -22), (114, -28), (115, -33), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (147, -38),
     (150, -37), (153, -32), (153, -27), (151, -24), (146, -19), (142, -15),
     (142, -11), (141, -13), (136, -12), (132, -11), (130, -13), (126, -14),
     (122, -17), (118, -20)],
    # Britain
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (137, 35), (139, 35), (140, 36),
     (141, 39), (141, 42), (142, 44), (144, 44), (141, 42), (140, 38),
     (139, 35), (136, 34), (133, 34), (131, 32)],
    # New Zealand
    [(167, -45), (170, -43), (173, -39), (175, -37), (178, -38), (176, -40),
     (174, -41), (172, -43), (169, -46)],
    # Indonesia
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -10),
     (125, -9), (130, -8), (135, -7), (140, -8), (141, -3), (138, 0),
     (135, 1), (132, -1), (128, 0), (125, 2), (122, 0), (120, 3), (117, 5),
     (114, 4), (110, 1), (105, 2), (100, 4)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (49, -20), (47, -25), (45, -25),
     (43, -22), (44, -18)],
]

# (story number, longitude, latitude, label dx, label dy)
PINS = [
    (1, 30.7, 36.9, 4, -12),     # Antalya
    (2, 46.7, 24.7, 4, -12),     # Riyadh
    (3, 21.0, 52.2, 4, -12),     # Warsaw
    (4, -74.0, 40.7, 4, -12),    # New York
    (5, 30.5, 50.5, -16, -12),   # Kyiv (label left: Warsaw is close)
    (6, 7.7, 45.1, 4, -12),      # Turin
    (9, 84.9, 19.3, 4, -12),     # Odisha
    (10, -159.8, -21.2, 4, -12),  # Cook Islands
    (11, 12.5, 41.9, -2, 8),     # Rome (label below: Turin is close)
    (13, 29.0, 1.5, 4, -12),     # eastern Congo
    (17, 34.5, 31.5, 4, 6),      # Gaza (label below: Antalya is close)
    (28, -89.2, 13.7, 4, -12),   # San Salvador
]


def _inside(lon: float, lat: float, poly) -> bool:
    """Ray-casting point-in-polygon test."""
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > lat) != (yj > lat):
            x_at = xi + (lat - yi) * (xj - xi) / (yj - yi)
            if lon < x_at:
                inside = not inside
        j = i
    return inside


def draw_map(d: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    """Equirectangular dot-grid world map with numbered story pins."""
    d.rectangle([x, y, x + w, y + h], fill=SEA, outline=NAVY, width=1)
    lon0, lon1 = -180.0, 180.0
    lat0, lat1 = 84.0, -58.0  # top, bottom
    step = 6
    for gx in range(x + 3, x + w - 2, step):
        lon = lon0 + (gx - x) / w * (lon1 - lon0)
        for gy in range(y + 3, y + h - 2, step):
            lat = lat0 + (gy - y) / h * (lat1 - lat0)
            for poly in CONTINENTS:
                if _inside(lon, lat, poly):
                    d.ellipse([gx - 1, gy - 1, gx + 1, gy + 1], fill=LAND_DOT)
                    break
    pin_f = font(SANS_BOLD, 9)
    for num, lon, lat, dx, dy in PINS:
        px = x + (lon - lon0) / (lon1 - lon0) * w
        py = y + (lat0 - lat) / (lat0 - lat1) * h
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=RED,
                  outline=WHITE, width=1)
        label = str(num)
        lx, ly = px + dx, py + dy
        tw = d.textlength(label, font=pin_f)
        d.rectangle([lx - 1, ly - 1, lx + tw + 1, ly + 9], fill=WHITE)
        d.text((lx, ly), label, font=pin_f, fill=RED)


# --- page layout ------------------------------------------------------------------
def main() -> None:
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    d.rectangle([0, 0, W, 6], fill=NAVY)
    d.rectangle([0, H - 6, W, H], fill=NAVY)

    # --- eyebrow ------------------------------------------------------------------
    eye_f = font(SANS_BOLD, 13)
    d.text((MARGIN, 13), "THE WORLD IN ONE DAY", font=eye_f, fill=RED)
    right = "35 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED SATURDAY 21 NOVEMBER 2026"
    d.text((W - MARGIN - d.textlength(right, font=eye_f), 13), right,
           font=eye_f, fill=INK)
    d.line([MARGIN, 35, W - MARGIN, 35], fill=INK, width=2)

    # --- masthead -----------------------------------------------------------------
    title = "Saturday 21 November 2026"
    size = 62
    while d.textlength(title, font=font(SERIF_BOLD, size)) > CW and size > 30:
        size -= 2
    tf = font(SERIF_BOLD, size)
    d.text(((W - d.textlength(title, font=tf)) / 2, 41), title, font=tf,
           fill=NAVY)
    deck_size = 16
    while (d.textlength(DECK, font=font(SERIF_ITALIC, deck_size)) > CW
           and deck_size > 10):
        deck_size -= 1
    deck_f = font(SERIF_ITALIC, deck_size)
    d.text(((W - d.textlength(DECK, font=deck_f)) / 2, 106), DECK,
           font=deck_f, fill=INK)
    d.line([MARGIN, 132, W - MARGIN, 132], fill=INK, width=3)

    # --- day in numbers -----------------------------------------------------------
    ny, nh = 140, 50
    cell = CW / len(NUMBERS)
    big_f, lab_f = font(SANS_BOLD, 24), font(SANS, 11)
    for i, (big, label) in enumerate(NUMBERS):
        cx = MARGIN + i * cell
        if i:
            d.line([cx - 6, ny + 4, cx - 6, ny + nh - 4], fill=RULE, width=1)
        d.text((cx + 4, ny), big, font=big_f,
               fill=RED if big.startswith("\u2212") else NAVY)
        put_wrapped(d, cx + 4, ny + 28, label, lab_f, cell - 12, GREY, 13)

    # --- region bar ---------------------------------------------------------------
    ry, rh = 198, 20
    total = sum(c for _, c, _ in REGIONS)
    rx = MARGIN
    reg_f = font(SANS_BOLD, 10)
    for name, count, colour in REGIONS:
        rw = CW * count / total
        d.rectangle([rx, ry, rx + rw, ry + rh], fill=colour)
        label = f"{name} {count}"
        lw = d.textlength(label, font=reg_f)
        if lw <= rw - 6:
            d.text((rx + (rw - lw) / 2, ry + 4), label, font=reg_f, fill=WHITE)
        rx += rw

    # --- lead stories -------------------------------------------------------------
    lead_w = (CW - 2 * 11) // 3
    ly = 226
    panel_h = 84
    for i, (n, place, beat, head, deck, art) in enumerate(LEADS):
        lx = MARGIN + i * (lead_w + 11)
        ART[art](d, lx, ly, lead_w, panel_h)
        ty = ly + panel_h + 8
        number_badge(d, lx, ty, n, 17, NAVY)
        d.text((lx + 22, ty + 1), f"{place}  \u00b7  {beat}",
               font=font(SANS_BOLD, 12), fill=BEATS[beat])
        hl = wrap(d, head, font(SANS_BOLD, 21), lead_w)
        if len(hl) > 2:
            print(f"WARNING: lead {n} headline wraps to {len(hl)} lines")
        hy = put_lines(d, lx, ty + 22, hl, font(SANS_BOLD, 21), INK, 24)
        dl = wrap(d, deck, font(SANS, 12), lead_w)
        if len(dl) > 3:
            print(f"WARNING: lead {n} deck wraps to {len(dl)} lines")
        put_lines(d, lx, hy + 4, dl, font(SANS, 12), (50, 50, 50), 16)
    d.line([MARGIN, 448, W - MARGIN, 448], fill=INK, width=1)

    # --- feature stories: 2 rows x 5 ----------------------------------------------
    feat_w = (CW - 4 * 10) // 5
    feat_panel = 48
    for row in range(2):
        fy = 456 + row * 133
        for col in range(5):
            n, place, beat, head, deck, art = FEATURES[row * 5 + col]
            fx = MARGIN + col * (feat_w + 10)
            ART[art](d, fx, fy, feat_w, feat_panel)
            ty = fy + feat_panel + 5
            number_badge(d, fx, ty, n, 14, NAVY)
            d.text((fx + 18, ty), f"{place} \u00b7 {beat}",
                   font=font(SANS_BOLD, 10), fill=BEATS[beat])
            hl = wrap(d, head, font(SANS_BOLD, 14), feat_w)
            if len(hl) > 2:
                print(f"WARNING: feature {n} headline wraps to {len(hl)} lines")
            hy = put_lines(d, fx, ty + 17, hl, font(SANS_BOLD, 14), INK, 15)
            deck_f2 = font(SANS_COND, 11)
            if d.textlength(deck, font=deck_f2) > feat_w:
                print(f"WARNING: feature {n} deck too long: {deck}")
            d.text((fx, hy + 2), deck, font=deck_f2, fill=(60, 60, 60))
    d.line([MARGIN, 722, W - MARGIN, 722], fill=INK, width=1)

    # --- bottom: map + briefs -----------------------------------------------------
    by = 730
    head_f = font(SANS_BOLD, 12)
    d.text((MARGIN, by), "WHERE IT HAPPENED", font=head_f, fill=RED)
    map_w, map_h = 300, 128
    draw_map(d, MARGIN, by + 18, map_w, map_h)
    d.text((MARGIN, by + 150),
           "Pins mark the numbered stories; 7 and 8 are market prices.",
           font=font(SANS, 10), fill=GREY)

    bx = MARGIN + map_w + 14
    bw = W - MARGIN - bx
    d.text((bx, by), "ALSO ON SATURDAY 21 NOVEMBER \u2014 22 MORE STORIES",
           font=head_f, fill=RED)
    brief_f = font(SANS_COND, 11)
    col_w = (bw - 12) // 2
    cols = [BRIEFS[:11], BRIEFS[11:]]
    for ci, col in enumerate(cols):
        cx = bx + ci * (col_w + 12)
        cy = by + 18
        for j, text in enumerate(col):
            num = 14 + ci * 11 + j
            d.text((cx, cy), f"{num}", font=font(SANS_BOLD, 11), fill=RED)
            lines = wrap(d, text, brief_f, col_w - 20)
            if len(lines) > 1:
                print(f"WARNING: brief {num} wraps to {len(lines)} lines: {text}")
            put_lines(d, cx + 20, cy, lines, brief_f, INK, 12)
            cy += 12 * max(1, len(lines))

    # --- date check -----------------------------------------------------------------
    dy = 894
    box_h = 72
    d.rectangle([MARGIN, dy, W - MARGIN, dy + box_h], outline=RED, width=1)
    d.rectangle([MARGIN, dy, MARGIN + 6, dy + box_h], fill=RED)
    dc_lines = wrap(d, DATE_CHECK, font(SANS, 10), CW - 24)
    put_lines(d, MARGIN + 14, dy + 7, dc_lines, font(SANS, 10), INK, 13)

    # --- footer -----------------------------------------------------------------------
    foot_f = font(SANS, 10)
    d.text(((W - d.textlength(FOOTER, font=foot_f)) / 2, 978), FOOTER,
           font=foot_f, fill=GREY)

    img.save(OUT, optimize=True)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
