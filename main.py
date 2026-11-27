#!/usr/bin/env python3
"""news-image-20261127 — Sum up Friday 27 November 2026's world news in one image.

Pure Python 3.13 standard library, no network, no fonts on disk.
Draws a 1024x1024 PNG newspaper poster with a hand-built 5x7 bitmap font
(all text upper-case) and writes it to /output/entry.png.
Deterministic: identical bytes on every run (fixed data, zlib level 9).
"""
import os
import struct
import zlib

W, H = 1024, 1024
OUT = os.environ.get("OUTPUT", "/output/entry.png")

# ---------------------------------------------------------------- palette
PAPER   = (247, 243, 234)
INK     = (26, 26, 26)
NAVY    = (18, 35, 63)
NAVY2   = (30, 58, 95)
RED     = (179, 39, 30)
TEAL    = (14, 107, 107)
AMBER   = (199, 125, 10)
GREEN   = (46, 125, 50)
PURPLE  = (107, 79, 161)
SLATE   = (84, 110, 122)
GREY    = (90, 90, 84)
LIGHT   = (255, 255, 255)
CREAM   = (232, 226, 210)
GOLD    = (212, 175, 55)
CONFIRM = (46, 125, 50)   # green chip = confirmed by 2+ sources / official
CLAIMC  = (199, 125, 10)  # amber chip = single source / a claim

REGION_COLORS = {
    "MIDDLE EAST": RED,
    "EUROPE":      (29, 78, 158),
    "ASIA-PACIFIC": TEAL,
    "AMERICAS":    AMBER,
    "AFRICA":      PURPLE,
    "SPORT":       GREEN,
    "TECH & BUSINESS": SLATE,
}

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows, 5 bits each (bit 4 = leftmost pixel). All caps + digits.
def _g(*rows):
    return rows

FONT = {
    "A": _g(0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "B": _g(0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110),
    "C": _g(0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110),
    "D": _g(0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110),
    "E": _g(0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111),
    "F": _g(0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000),
    "G": _g(0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111),
    "H": _g(0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "I": _g(0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "J": _g(0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100),
    "K": _g(0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001),
    "L": _g(0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111),
    "M": _g(0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001),
    "N": _g(0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001),
    "O": _g(0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "P": _g(0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000),
    "Q": _g(0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101),
    "R": _g(0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001),
    "S": _g(0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110),
    "T": _g(0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    "U": _g(0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "V": _g(0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    "W": _g(0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b11011, 0b10001),
    "X": _g(0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001),
    "Y": _g(0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100),
    "Z": _g(0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111),
    "0": _g(0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110),
    "1": _g(0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "2": _g(0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111),
    "3": _g(0b11110, 0b00001, 0b00001, 0b01110, 0b00001, 0b00001, 0b11110),
    "4": _g(0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010),
    "5": _g(0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110),
    "6": _g(0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110),
    "7": _g(0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000),
    "8": _g(0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110),
    "9": _g(0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100),
    " ": _g(0, 0, 0, 0, 0, 0, 0),
    ".": _g(0, 0, 0, 0, 0, 0b01100, 0b01100),
    ",": _g(0, 0, 0, 0, 0b01100, 0b00100, 0b01000),
    ":": _g(0, 0b01100, 0b01100, 0, 0b01100, 0b01100, 0),
    ";": _g(0, 0b01100, 0b01100, 0, 0b01100, 0b00100, 0b01000),
    "!": _g(0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0, 0b00100),
    "?": _g(0b01110, 0b10001, 0b00001, 0b00110, 0b00100, 0, 0b00100),
    "'": _g(0b00100, 0b00100, 0b01000, 0, 0, 0, 0),
    '"': _g(0b01010, 0b01010, 0, 0, 0, 0, 0),
    "-": _g(0, 0, 0, 0b01110, 0, 0, 0),
    "–": _g(0, 0, 0, 0b01110, 0, 0, 0),
    "—": _g(0, 0, 0, 0b11111, 0, 0, 0),
    "(": _g(0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010),
    ")": _g(0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000),
    "/": _g(0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000),
    "&": _g(0b01100, 0b10010, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101),
    "%": _g(0b11001, 0b11010, 0b00010, 0b00100, 0b01000, 0b01011, 0b10011),
    "+": _g(0, 0b00100, 0b00100, 0b11111, 0b00100, 0b00100, 0),
    "=": _g(0, 0, 0b11111, 0, 0b11111, 0, 0),
    "*": _g(0, 0b10101, 0b01110, 0b11111, 0b01110, 0b10101, 0),
    "#": _g(0b01010, 0b01010, 0b11111, 0b01010, 0b11111, 0b01010, 0b01010),
    "$": _g(0b00100, 0b01111, 0b10100, 0b01110, 0b00101, 0b11110, 0b00100),
    "_": _g(0, 0, 0, 0, 0, 0, 0b11111),
    "[": _g(0b01110, 0b01000, 0b01000, 0b01000, 0b01000, 0b01000, 0b01110),
    "]": _g(0b01110, 0b00010, 0b00010, 0b00010, 0b00010, 0b00010, 0b01110),
    ">": _g(0b10000, 0b01000, 0b00100, 0b00010, 0b00100, 0b01000, 0b10000),
    "<": _g(0b00001, 0b00010, 0b00100, 0b01000, 0b00100, 0b00010, 0b00001),
    "•": _g(0, 0, 0b01100, 0b01100, 0b01100, 0, 0),
    "·": _g(0, 0, 0, 0b01100, 0, 0, 0),
    "£": _g(0b00110, 0b01000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111),
    "€": _g(0b00110, 0b01001, 0b10000, 0b11110, 0b10000, 0b01001, 0b00110),
}

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            if 0 <= yy < self.h:
                for xx in range(x, x + w):
                    if 0 <= xx < self.w:
                        i = (yy * self.w + xx) * 3
                        self.px[i], self.px[i + 1], self.px[i + 2] = c

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def circle(self, cx, cy, r, c, fill=False):
        # midpoint circle; fill via scanline when requested
        x, y, d = 0, r, 1 - r
        pts = set()
        while x <= y:
            for sx, sy in ((x, y), (y, x), (-x, y), (-y, x),
                           (x, -y), (y, -x), (-x, -y), (-y, -x)):
                pts.add((cx + sx, cy + sy))
            if d < 0:
                d += 2 * x + 3
            else:
                d += 2 * (x - y) + 5
                y -= 1
            x += 1
        if fill:
            rows = {}
            for px, py in pts:
                rows.setdefault(py, []).append(px)
            for py, xs in rows.items():
                for xx in range(min(xs), max(xs) + 1):
                    self.set(xx, py, c)
        else:
            for px, py in pts:
                self.set(px, py, c)

    def text(self, x, y, s, scale, color):
        """Draw upper-case text; unknown chars become blank."""
        cx = x
        for ch in s.upper():
            g = FONT.get(ch)
            if g is None:
                g = FONT[" "]
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(s) * 6 * scale

def wrap(text, max_chars):
    words = text.split()
    lines, cur = [], ""
    for wd in words:
        nxt = (cur + " " + wd).strip() if cur else wd
        if len(nxt) <= max_chars:
            cur = nxt
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines

# ---------------------------------------------------------------- the news
# Featured: (headline, deck incl. source, region, level)
# level: "CONFIRMED" = 2+ sources or official; "CLAIM" = one source / a claim.
FEATURED = [
    ("GAZA: HAMAS WEIGHS REPLY AFTER",
     "ISRAEL KILLS 10 - REUTERS", "MIDDLE EAST", "CONFIRMED"),
    ("UK NET MIGRATION LOWEST SINCE 1997",
     "EXCLUDING PANDEMIC YEARS - NYT", "EUROPE", "CONFIRMED"),
    ("DIESEL TANKER CAPSIZES OFF IBIZA,",
     "1 DEAD, 7,000 TONNES ABOARD - BBC", "EUROPE", "CONFIRMED"),
    ("DEPARDIEU TO STAND TRIAL OVER",
     "ALLEGED 2018 RAPE - BBC", "EUROPE", "CONFIRMED"),
    ("MUSK: EVERY US CHILD TO GET",
     "2 SPACEX SHARES - THE HINDU", "TECH & BUSINESS", "CLAIM"),
    ("CHESS: GUKESH, SINDAROV DRAW",
     "GAME 3, TITLE MATCH LEVEL", "SPORT", "CONFIRMED"),
    ("INDIA TOP COURT: PMLA BENCH",
     "NEEDS A JUDGE - TOI, 27 NOV", "ASIA-PACIFIC", "CONFIRMED"),
    ("INDIA TOP COURT QUASHES BIHAR",
     "EARLY RELEASE - TOI, 27 NOV", "ASIA-PACIFIC", "CONFIRMED"),
    ("NEW ZEALAND FINAL COUNT DUE TODAY",
     "COALITION 67 OF 131 - NEWSTALK ZB", "ASIA-PACIFIC", "CONFIRMED"),
    ("TRUMP SEEKS PROBE OF 'FAKE' GDP",
     "GROWTH REVISED TO 4.3% - MINT", "AMERICAS", "CLAIM"),
    ("TRUMP AND NATO CHIEF TELL RUSSIA:",
     "PULL BACK IN EUROPE - 27 NOV", "EUROPE", "CLAIM"),
    ("US PLANS NEW TARIFFS ON EU,",
     "CHINA AND OTHERS - 27 NOV", "AMERICAS", "CLAIM"),
    ("SCHOOLS IN GERMANY, DENMARK GET",
     "EMAIL BOMB THREATS - 27 NOV", "EUROPE", "CLAIM"),
    ("UN: 47,000 WOMEN KILLED BY KIN",
     "IN 2025, 5 AN HOUR - UN REPORT", "AFRICA", "CONFIRMED"),
    ("INDIA CABINET CLEARS RS 11,000 CR",
     "BUILDING MACHINE SCHEME - AIR", "ASIA-PACIFIC", "CONFIRMED"),
    ("BLACK FRIDAY: HALF OF 'DEALS'",
     "ARE NO CHEAPER - CONSUMER NZ", "ASIA-PACIFIC", "CONFIRMED"),
]

# Briefs: (one line, region, level). 34 items.
BRIEFS = [
    ("KUWAIT STRIKE KILLS 2 (26 NOV)", "MIDDLE EAST", "CONFIRMED"),
    ("US STORM: 900,000 LOSE POWER (26 NOV)", "AMERICAS", "CONFIRMED"),
    ("MACY'S PARADE MOVED TO SAT (25 NOV)", "AMERICAS", "CONFIRMED"),
    ("ZELENSKYY: UKRAINE HIT SHIP OFF LIBYA", "EUROPE", "CLAIM"),
    ("RUSSIA ACCUSES ESTONIA OF HOSTILE ACTS", "EUROPE", "CLAIM"),
    ("CHINA: DEATH SENTENCE FOR SPYING", "ASIA-PACIFIC", "CLAIM"),
    ("IRAN SINGER GETS 74 LASHES UNVEILED", "MIDDLE EAST", "CLAIM"),
    ("US ARMY BURNS TOXIC EXPLOSIVES IN IOWA", "AMERICAS", "CLAIM"),
    ("EBOLA IN CONGO TOPS 12,000 CASES", "AFRICA", "CLAIM"),
    ("NEPAL TO DECLARE 4,000 LANDSLIDE DEAD", "ASIA-PACIFIC", "CLAIM"),
    ("BELGIUM OPENS TOP SATELLITE FACTORY", "EUROPE", "CLAIM"),
    ("65 HELD IN MEDITERRANEAN BORDER SWEEP", "EUROPE", "CLAIM"),
    ("US FLIGHTS TO DCA GROUNDED BY WEATHER", "AMERICAS", "CLAIM"),
    ("CAIRO HIGHWAY TANKER FIRE ENGULFS CARS", "AFRICA", "CLAIM"),
    ("EU OFFERS LITTLE ON US DRUG PRICE PUSH", "EUROPE", "CLAIM"),
    ("SPACEX GETS 1M SATELLITES OK (26 NOV)", "TECH & BUSINESS", "CONFIRMED"),
    ("NVIDIA PAUSES SE ASIA SALES (26 NOV)", "TECH & BUSINESS", "CONFIRMED"),
    ("BABCOCK $11.4BN SUB DEAL (26 NOV)", "TECH & BUSINESS", "CONFIRMED"),
    ("BANK OF ENGLAND EASES RULES (26 NOV)", "EUROPE", "CONFIRMED"),
    ("ALTRIA EYES IMPERIAL DEAL (26 NOV)", "TECH & BUSINESS", "CONFIRMED"),
    ("FERRARI SETS HAMILTON, LECLERC TARGET", "SPORT", "CONFIRMED"),
    ("BARRETT TO CAPTAIN ALL BLACKS", "SPORT", "CONFIRMED"),
    ("NZ V INDIA: 2ND TEST IN CHRISTCHURCH", "SPORT", "CONFIRMED"),
    ("CLAUDE TURNS ARTIFACTS INTO APPS", "TECH & BUSINESS", "CLAIM"),
    ("HINT OF GIANT PLANET BEYOND NEPTUNE", "TECH & BUSINESS", "CLAIM"),
    ("INDIA: SPECIAL PARLIAMENT FROM 30 NOV", "ASIA-PACIFIC", "CONFIRMED"),
    ("INDIA: GST CANCELLATIONS FROM 1 DEC", "ASIA-PACIFIC", "CONFIRMED"),
    ("KENYA: SCHOOLS SHORT OF FACILITIES", "AFRICA", "CONFIRMED"),
    ("AUSTRALIA BRACES FOR BUSHFIRE SEASON", "ASIA-PACIFIC", "CLAIM"),
    ("SYDNEY BATTLES FIRE ANT OUTBREAK", "ASIA-PACIFIC", "CLAIM"),
    ("CIA WATERBOARDING REPORT NAMES MORE", "AMERICAS", "CLAIM"),
    ("FRANCE FACES VOTE DEBACLE, NO RIVAL", "EUROPE", "CLAIM"),
    ("INDIA MARKS CONSTITUTION DAY (26 NOV)", "ASIA-PACIFIC", "CONFIRMED"),
    ("SBI CLERK MAINS RESULT 2026 ANNOUNCED", "ASIA-PACIFIC", "CONFIRMED"),
]

REGION_ORDER = ["MIDDLE EAST", "EUROPE", "ASIA-PACIFIC", "AMERICAS",
                "AFRICA", "SPORT", "TECH & BUSINESS"]

STATS = [
    ("900,000", "WITHOUT POWER IN THE US", "THANKSGIVING STORM, 26 NOV"),
    ("400,000", "NZ SPECIAL VOTES COUNTED", "FINAL RESULT DUE 27 NOV"),
    ("7,000 T", "DIESEL ON CAPSIZED TANKER", "OFF IBIZA, 27 NOV"),
    ("47,000", "WOMEN KILLED BY KIN IN 2025", "UN REPORT, ABOUT 5 AN HOUR"),
]

DATE_CHECK = [
    "DATE CHECK - NOT 27 NOV: KUWAIT DRONE STRIKE 26 NOV - POPE DIARIES 24 NOV",
    "CARTAGENA SIEGE 24-25 NOV - MACY'S PARADE CALL 25 NOV - GAZA SCHOOL",
    "DEATHS ARE A MONTH TOTAL, NOT ONE DAY. DATED ITEMS ARE MARKED ABOVE.",
]

# ---------------------------------------------------------------- drawing
def draw_full(c):
    c.rect(0, 0, W, H, PAPER)
    c.rect(0, 0, W, 104, NAVY)
    c.rect(0, 104, W, 4, GOLD)
    gx, gy, gr = 52, 52, 30
    c.circle(gx, gy, gr, GOLD)
    c.vline(gx, gy - gr, 2 * gr, GOLD)
    c.hline(gx - gr, gy, 2 * gr, GOLD)
    c.circle(gx, gy, gr // 2, GOLD)
    c.text(96, 18, "27 NOVEMBER 2026", 5, LIGHT)
    c.text(96, 62, "FRIDAY - THE WORLD IN ONE IMAGE", 2, GOLD)
    c.rect(872, 16, 128, 72, NAVY2)
    c.hline(872, 16, 128, GOLD, 2)
    c.hline(872, 86, 128, GOLD, 2)
    c.text(892, 26, "50", 4, LIGHT)
    c.text(884, 62, "STORIES", 2, GOLD)

    y = 112
    c.text(24, y + 4, "HOW TO READ:", 2, RED)
    c.rect(188, y + 8, 12, 12, CONFIRM)
    c.text(208, y + 4, "= CONFIRMED: 2+ SOURCES", 2, INK)
    c.rect(516, y + 8, 12, 12, CLAIMC)
    c.text(536, y + 4, "= CLAIM: 1 SOURCE", 2, INK)
    c.text(760, y + 4, "27 NOV UNLESS MARKED", 2, GREY)

    y0 = 144
    c.text(24, y0, "TOP STORIES - 16", 2, NAVY)
    c.hline(24, y0 + 20, 976, NAVY, 2)
    row_h = 34
    for i, (head, deck, region, level) in enumerate(FEATURED):
        col, row = i % 2, i // 2
        x = 24 if col == 0 else 512
        yy = y0 + 26 + row * row_h
        chip = CONFIRM if level == "CONFIRMED" else CLAIMC
        c.rect(x, yy + 2, 10, 10, chip)
        c.text(x + 16, yy, head, 2, INK)
        c.text(x + 16, yy + 15, deck, 2, GREY)
    feat_bottom = y0 + 26 + 8 * row_h  # 442

    band_y = feat_bottom + 6  # 448
    c.hline(24, band_y, 976, NAVY, 2)
    c.text(24, band_y + 8, "WHERE THE NEWS CAME FROM", 2, NAVY)
    c.text(516, band_y + 8, "BY THE NUMBERS", 2, NAVY)
    counts = {r: 0 for r in REGION_ORDER}
    for _, _, region, _ in FEATURED:
        counts[region] += 1
    for _, region, _ in BRIEFS:
        counts[region] += 1
    maxc = max(counts.values())
    bx, by = 24, band_y + 32
    for j, r in enumerate(REGION_ORDER):
        yy = by + j * 13
        c.text(bx, yy, r, 1, INK)
        bar_x = bx + 17 * 6 + 6
        bar_w = int(170 * counts[r] / maxc)
        c.rect(bar_x, yy + 1, bar_w, 8, REGION_COLORS[r])
        c.text(bar_x + bar_w + 6, yy, str(counts[r]), 1, INK)
    sx, sy = 516, band_y + 32
    for k, (num, lab, sub) in enumerate(STATS):
        col, row = k % 2, k // 2
        x = sx + col * 244
        yy = sy + row * 46
        c.rect(x, yy, 236, 42, CREAM)
        c.text(x + 8, yy + 4, num, 3, RED)
        c.text(x + 8, yy + 25, lab, 1, INK)
        c.text(x + 8, yy + 34, sub, 1, GREY)
    band_bottom = by + len(REGION_ORDER) * 13  # 448+32+91 = 571

    brief_y = band_bottom + 8  # 579
    c.text(24, brief_y, "THE DAY IN BRIEF - 34 MORE", 2, NAVY)
    c.hline(24, brief_y + 20, 976, NAVY, 2)
    for i, (txt, region, level) in enumerate(BRIEFS):
        col, row = i % 2, i // 2
        x = 24 if col == 0 else 512
        yy = brief_y + 26 + row * 19
        chip = CONFIRM if level == "CONFIRMED" else CLAIMC
        c.rect(x, yy + 3, 9, 9, chip)
        c.text(x + 14, yy, txt, 2, INK)
    brief_bottom = brief_y + 26 + 17 * 19  # 579+26+323 = 928

    dc_y = brief_bottom + 6  # 934
    c.rect(24, dc_y, 976, 62, CREAM)
    c.rect(24, dc_y, 976, 62, RED)
    # inner fill again (border effect): redraw fill inset
    c.rect(26, dc_y + 2, 972, 58, CREAM)
    c.text(36, dc_y + 6, "DATE CHECK - NOT 27 NOV:", 2, RED)
    c.text(36, dc_y + 24, "KUWAIT STRIKE 26 NOV - POPE DIARIES 24 NOV - CARTAGENA 24-25 NOV", 2, INK)
    c.text(36, dc_y + 42, "MACY'S PARADE CALL 25 NOV - GAZA SCHOOL DEATHS ARE A MONTH TOTAL.", 2, INK)
    foot_y = dc_y + 62 + 4  # 1000
    c.text(24, foot_y, "SOURCES: REUTERS, BBC, NYT, AP, NEWSTALK ZB, THE HINDU, TOI, MINT, DOW JONES, AFP.", 1, GREY)
    c.text(24, foot_y + 10, "DRAWN FROM REPORTS OF FRIDAY 27 NOVEMBER 2026. GREEN = CONFIRMED, AMBER = CLAIM.", 1, GREY)

# ---------------------------------------------------------------- PNG encode
def png_bytes(c):
    raw = bytearray()
    for y in range(c.h):
        raw.append(0)  # filter: none
        raw += c.px[y * c.w * 3:(y + 1) * c.w * 3]

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", c.w, c.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))

def main():
    assert len(FEATURED) == 16, len(FEATURED)
    assert len(BRIEFS) == 34, len(BRIEFS)
    for h, d, _, _ in FEATURED:
        assert len(h) <= 38 and len(d) <= 38, (h, d)
    for t, _, _ in BRIEFS:
        assert len(t) <= 38, t
    assert len(FEATURED) + len(BRIEFS) == 50
    c = Canvas(W, H, PAPER)
    draw_full(c)
    data = png_bytes(c)
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    with open(OUT, "wb") as f:
        f.write(data)
    print("wrote %s %d bytes" % (OUT, len(data)))

if __name__ == "__main__":
    main()
