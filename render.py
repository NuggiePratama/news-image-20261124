#!/usr/bin/env python3
"""Render the 24 November 2026 world-news image.

One self-contained Pillow program. No network, no clock, no randomness:
the same run always produces the same PNG bytes. Reads nothing but the
story table below; writes entry.png (1024x1024) next to this file.

Layout (1024 x 1024): masthead -> DATE CHECK strip (2 lines) -> hero
band with two hand-drawn pictograms -> one-line UTC timeline ->
three-column story grid grouped into 7 regions -> "By the numbers"
band -> two-line ticker -> sources footer.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size, bold=False):
    return ImageFont.truetype(FONTB if bold else FONT, size)


# (region, confidence, headline, one-line brief)
# [H] confirmed by 2+ major sources or an official statement.
# [M] one source, or a figure agencies report differently.
# [R] reported and attributed, not independently confirmed.
STORIES = [
    # ---- Middle East ----
    ("MIDDLE EAST", "R", "Hormuz: IRGC says 4 tankers hit mines",
     "3 hit Mon, a 4th Tue; maritime centre: unconfirmed."),
    ("MIDDLE EAST", "R", "IRGC says it attacked a container ship",
     "Switched off navigation, in restricted area — IRGC."),
    ("MIDDLE EAST", "H", "Iran tightens Hormuz blockade, 7 terms",
     "Closed 'day by day' until US concedes, army chief says."),
    ("MIDDLE EAST", "H", "Trump: toppling Iran 'probably doable'",
     "Regime change not his goal; stopping nukes is the aim."),
    ("MIDDLE EAST", "H", "Saudi PIF tower in Riyadh hit, 11+ hurt",
     "Suspected Houthi drone; 2nd hit on the tower in a week."),
    ("MIDDLE EAST", "M", "Houthis 60 km from Aden, ready to attack",
     "Yemen army: defence line built north, west of the city."),
    ("MIDDLE EAST", "H", "Israel kills Hamas security chief in Gaza",
     "Naeem Abu Nahel killed; 6 more die in other strikes."),
    ("MIDDLE EAST", "H", "Gaza meningitis epidemic alert after surge",
     "272 cases in Oct, 8x normal rate; 15 dead in 2026."),
    # ---- Europe & Ukraine ----
    ("EUROPE & UKRAINE", "H", "Ukraine hits Russian ships in 2 seas",
     "Sparta II hit in Finland gulf; corvette hit off Libya."),
    ("EUROPE & UKRAINE", "M", "Kyiv: corvette Merkury sunk off Benghazi",
     "Libyan officials say severely damaged, not sunk. [M]"),
    ("EUROPE & UKRAINE", "H", "Zaporizhzhia strike: 2 dead, ~50 hurt",
     "Overnight attack; victims incl. an infant, 4 children."),
    ("EUROPE & UKRAINE", "M", "Poland: new Russian airspace violation",
     "NATO sends detection aircraft after the incident."),
    ("EUROPE & UKRAINE", "R", "NATO vows defence vs space threat",
     "Russia may launch a nuclear-armed satellite in 60 days."),
    ("EUROPE & UKRAINE", "H", "Zelensky urges 4-party talks soon",
     "Kyiv ready to meet Tue; repeats NATO membership call."),
    ("EUROPE & UKRAINE", "M", "EU proposes 22nd Russia sanctions",
     "~60 banks, crypto networks targeted; needs all 27."),
    ("EUROPE & UKRAINE", "H", "Hungary PM Magyar visits Ukraine",
     "First visit as PM; energy, transport, minority rights."),
    ("EUROPE & UKRAINE", "H", "Ukraine needs EUR 115bn for 2027",
     "EUR 90bn arranged; EUR 25bn gap remains, Zelensky says."),
    # ---- Americas ----
    ("AMERICAS", "H", "Huawei guilty on 10 of 12 counts in US trial",
     "Trade secrets + bank fraud; racketeering acquitted."),
    ("AMERICAS", "H", "Trump to meet El-Sayed on 'Trumpcare'",
     "Medicare-for-All rebrand called 'very smart' by Trump."),
    ("AMERICAS", "H", "Trump pardons turkeys, vows ATC rebuild",
     "Turkeys spared; ATC '57 years old', Trump says."),
    ("AMERICAS", "H", "Giuliani awarded Medal of Freedom",
     "Top US civilian honour, closed-press Oval Office rite."),
    ("AMERICAS", "H", "Pentagon rebukes Canada over F-35",
     "Only 41.9% of Canada's air fleet serviceable."),
    ("AMERICAS", "H", "Cartagena: 25 held hostage in supermarket",
     "5 older women freed; airport landings briefly halted."),
    ("AMERICAS", "H", "Car bomb in Villavicencio injures 23",
     "Blast at offices on eve of FARC peace-deal anniversary."),
    ("AMERICAS", "H", "El Chapo Isidro captured, US drone help",
     "Mexico will try him despite a US extradition request."),
    # ---- Asia-Pacific ----
    ("ASIA-PACIFIC", "H", "Turkish Air Force helicopter crash kills 5",
     "AS-532 down after Eskisehir take-off; cause not given."),
    ("ASIA-PACIFIC", "M", "China: official gets death for spying",
     "Recruited abroad; 35 secrets, over 1m yuan — state press."),
    ("ASIA-PACIFIC", "H", "Shenzhou-24 crew named; Pakistani to fly",
     "Zeeshan Ali, 40, first foreigner on Tiangong station."),
    ("ASIA-PACIFIC", "H", "5.6 quake strikes Nepal near China border",
     "Epicentre near the border; no casualty toll reported yet."),
    ("ASIA-PACIFIC", "H", "Hanoi hot-pot blast kills at least 6",
     "Gas leak suspected; 10+ hurt, buildings evacuated."),
    ("ASIA-PACIFIC", "H", "Hasina plans return to Bangladesh",
     "Ex-PM in exile; Dhaka says she should be extradited."),
    ("ASIA-PACIFIC", "H", "Malaysia to return thousands to Myanmar",
     "1,500 by ship, 5,303 by air; days after ICJ ruling."),
    ("ASIA-PACIFIC", "H", "Indonesia nominates 2 VP candidates",
     "Sulaiman, Sugiono to replace Gibran, resigned 12 Nov."),
    ("ASIA-PACIFIC", "H", "S. Korea alert as Russian jets approach",
     "Jets in air-defence zone near Ulleungdo; airspace intact."),
    # ---- Africa ----
    ("AFRICA", "H", "Senegal AFCON title restored by CAS",
     "Referee right to resume chaotic Jan final, court says."),
    ("AFRICA", "R", "DR Congo plane missing, rebels claim hit",
     "Cessna 208 lost Sun; 4 aboard said captured — unverified."),
    ("AFRICA", "H", "Libya's Haftar visits Turkey for first time",
     "Meets Erdogan in Ankara; Erdogan visits Libya in Dec."),
    ("AFRICA", "H", "Tripoli demands answers from Kyiv",
     "Libya: attack in its waters threatens Med security."),
    # ---- Markets & Tech ----
    ("MARKETS & TECH", "H", "Nvidia -5.9% as Huang rally reverses",
     "Nasdaq -1.5%, S&P -0.5%; Dow +0.9% above 50,000."),
    ("MARKETS & TECH", "H", "Anthropic -6.5%, below $83 IPO price",
     "First close under offer price, 4 sessions after listing."),
    ("MARKETS & TECH", "M", "US plans new Section 301 tariffs",
     "China, EU targeted to replace court-struck levies."),
    ("MARKETS & TECH", "H", "US blacklists Megaspeed + 6 firms",
     "Bars advanced US tech; firm at centre of Nvidia scandal."),
    ("MARKETS & TECH", "H", "Sanofi to buy drugmaker Insmed, $41bn",
     "Biggest pharma deal of the day; both shares move."),
    ("MARKETS & TECH", "H", "Brent $88.71 after Hormuz mine reports",
     "Jan futures -66c; flows at 74% of pre-war levels."),
    ("MARKETS & TECH", "H", "Huang: 'in therapy', apologises in town hall",
     "Nvidia CEO addresses staff a day after his reinstatement."),
    # ---- Science & Space ----
    ("SCIENCE & SPACE", "H", "Euclid finds most distant quasar yet",
     "Active 630m yrs after Big Bang; redshift 8.13."),
    ("SCIENCE & SPACE", "H", "Ariane 6 launches 36 Amazon Leo satellites",
     "Kourou lift-off after delay; all satellites separated."),
    ("SCIENCE & SPACE", "H", "Nobel Physics: Halzen wins for IceCube",
     "South Pole neutrino detector honoured; announced Tue."),
    ("SCIENCE & SPACE", "H", "Russia launches Progress 97 to the ISS",
     "Cargo ship from Baikonur; docking expected Thursday."),
    # ---- Global ----
    ("GLOBAL", "H", "Guterres: AI risk framework within a year",
     "UN chief calls for a multilateral pact to limit AI risks."),
    ("GLOBAL", "H", "14 nations back ICJ Rohingya ruling",
     "UK, Spain, Canada, Australia + 10 affirm the verdict."),
]

TIMELINE = [
    ("00:00", "tankers hit mines"),
    ("02:09", "El Chapo captured"),
    ("08:14", "Ukraine hits Russian ships"),
    ("11:40", "Hamas chief killed"),
    ("14:27", "PIF tower hit"),
    ("20:41", "Huawei guilty"),
]

NUMBERS = [
    ("50", "stories"),
    ("7", "regions"),
    ("4", "tankers"),
    ("10/12", "Huawei"),
    ("-5.9%", "Nvidia"),
    ("$88.71", "Brent"),
    ("630m yrs", "quasar age"),
    ("1-0", "Senegal"),
]

TICKER_LINES = [
    "Also: Iraq takes Kurdish oilfields  ·  Saudi strikes in Yemen, 25 dead or missing  ·  Bukele: 3 soldiers killed in Haiti",
    "Solomon Islands picks Australia  ·  N. Korea shuts Swiss office  ·  Quantinuum quantum record  ·  Perseverance safe mode",
    "Pennsylvania measles, 9th death  ·  FIFA: US, Mexico, Costa Rica, Jamaica host 2031 Women's World Cup",
]

INK = (18, 22, 34)
PAPER = (250, 247, 238)
NAVY = (16, 34, 64)
AMBER = (245, 196, 66)
TEAL = (14, 110, 110)
RED = (176, 32, 32)
GREY = (90, 92, 100)
CARD = (255, 255, 255)
LINE = (205, 200, 186)


def trunc(draw, text, fnt, max_w):
    if draw.textlength(text, font=fnt) <= max_w:
        return text
    ell = "…"
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if draw.textlength(text[:mid] + ell, font=fnt) <= max_w:
            lo = mid
        else:
            hi = mid - 1
    return text[:lo] + ell


def draw_tanker(d, x, y, s, col):
    # Simple tanker pictogram: hull, deck, funnel, waves.
    d.polygon([(x, y + 22 * s), (x + 64 * s, y + 22 * s), (x + 56 * s, y + 34 * s),
               (x + 8 * s, y + 34 * s)], fill=col)
    d.rectangle([x + 12 * s, y + 10 * s, x + 44 * s, y + 22 * s], fill=col)
    d.rectangle([x + 48 * s, y + 2 * s, x + 54 * s, y + 22 * s], fill=col)
    for wx in (0, 22, 44):
        d.arc([x + wx * s, y + 38 * s, x + (wx + 16) * s, y + 46 * s],
              180, 360, fill=col, width=2)


def draw_gavel(d, x, y, s, col):
    d.rectangle([x, y + 6 * s, x + 44 * s, y + 16 * s], fill=col)
    d.rectangle([x + 20 * s, y + 16 * s, x + 26 * s, y + 38 * s], fill=col)
    d.rectangle([x + 8 * s, y + 38 * s, x + 38 * s, y + 44 * s], fill=col)


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead ----
    d.rectangle([0, 0, W, 58], fill=NAVY)
    d.text((14, 8), "THE WORLD IN ONE IMAGE", font=font(26, True), fill=(255, 255, 255))
    d.text((14, 38), "50 date-checked stories  ·  7 regions  ·  one UTC timeline",
           font=font(12), fill=(190, 200, 220))
    date_txt = "TUESDAY 24 NOVEMBER 2026"
    dw = d.textlength(date_txt, font=font(20, True))
    d.text((W - 14 - dw, 12), date_txt, font=font(20, True), fill=AMBER)
    d.text((W - 14 - d.textlength("All times UTC", font=font(11)), 38),
           "All times UTC", font=font(11), fill=(190, 200, 220))

    # ---- DATE CHECK strip (2 lines) ----
    d.rectangle([0, 58, W, 96], fill=AMBER)
    d.text((14, 62), "DATE CHECK — Tue 24 Nov 2026  ·  Every story first reported or confirmed on 24 Nov (UTC)",
           font=font(11, True), fill=INK)
    d.text((14, 78), "[H] confirmed by 2+ sources or an official statement  ·  [M] one source / figures differ  ·  "
                     "[R] reported, attributed, not independently confirmed",
           font=font(11, True), fill=INK)

    # ---- Hero band ----
    d.rectangle([0, 96, W, 156], fill=(255, 255, 255))
    d.line([0, 156, W, 156], fill=LINE, width=1)
    draw_gavel(d, 16, 104, 0.7, NAVY)
    d.text((56, 102), "Huawei guilty on 10 of 12 counts; racketeering acquitted",
           font=font(14, True), fill=INK)
    d.text((56, 120), "US jury convicts on trade secrets + bank fraud; sentencing Sep 2027.",
           font=font(11), fill=GREY)
    draw_tanker(d, 545, 104, 0.7, TEAL)
    d.text((598, 102), "Hormuz: IRGC says 4 tankers hit mines",
           font=font(14, True), fill=INK)
    d.text((598, 120), "Claims unconfirmed; Iran tightens the blockade, sets 7 terms.",
           font=font(11), fill=GREY)
    d.text((14, 140), "Nvidia gives back the rally: -5.9% after Monday's +30%  ·  Nasdaq -1.5%, Dow +0.9% above 50,000",
           font=font(11, True), fill=RED)

    # ---- UTC timeline ----
    d.rectangle([0, 156, W, 178], fill=(232, 228, 216))
    tl = "  •  ".join(f"{t}  {s}" for t, s in TIMELINE)
    d.text((14, 161), trunc(d, "UTC — " + tl, font(10, True), W - 28),
           font=font(10, True), fill=INK)
    d.line([0, 178, W, 178], fill=LINE, width=1)

    # ---- Story grid: 3 columns ----
    regions = []
    for s in STORIES:
        if not regions or regions[-1][0] != s[0]:
            regions.append((s[0], [s]))
        else:
            regions[-1][1].append(s)
    cols = [[], [], []]
    col_heights = [0, 0, 0]
    for name, items in regions:
        h = 22 + 36 * len(items)
        ci = col_heights.index(min(col_heights))
        cols[ci].append((name, items))
        col_heights[ci] += h + 10
    grid_top, grid_bot = 186, 934
    col_x = [14, 356, 698]
    col_w = 312
    max_y = grid_top
    for ci, blocks in enumerate(cols):
        used = sum(22 + 36 * len(items) + 10 for _, items in blocks) - 10
        gap = (grid_bot - grid_top - used) // max(1, len(blocks))
        y = grid_top
        for name, items in blocks:
            d.rectangle([col_x[ci], y, col_x[ci] + col_w, y + 20], fill=NAVY)
            d.text((col_x[ci] + 8, y + 3), name, font=font(12, True), fill=(255, 255, 255))
            d.text((col_x[ci] + col_w - 8 - d.textlength(str(len(items)), font=font(11, True)),
                    y + 4), str(len(items)), font=font(11, True), fill=AMBER)
            y += 20
            for _, mark, head, body in items:
                d.rectangle([col_x[ci], y + 1, col_x[ci] + col_w, y + 35], fill=CARD,
                            outline=LINE)
                d.text((col_x[ci] + 5, y + 4), f"[{mark}]", font=font(11, True),
                       fill=TEAL if mark == "H" else (RED if mark == "R" else (150, 110, 0)))
                d.text((col_x[ci] + 34, y + 4),
                       trunc(d, head, font(11, True), col_w - 40),
                       font=font(11, True), fill=INK)
                d.text((col_x[ci] + 5, y + 20),
                       trunc(d, body, font(10), col_w - 10),
                       font=font(10), fill=GREY)
                y += 36
            y += gap + 10
        max_y = max(max_y, y)
    assert max_y <= grid_bot + 12, f"grid overflow: {max_y}"

    # ---- By the numbers ----
    d.rectangle([0, 934, W, 972], fill=NAVY)
    d.text((14, 940), "BY THE NUMBERS", font=font(12, True), fill=AMBER)
    nx = 168
    for val, lab in NUMBERS:
        d.text((nx, 938), val, font=font(15, True), fill=(255, 255, 255))
        d.text((nx, 956), lab, font=font(10), fill=(190, 200, 220))
        nx += (d.textlength(val, font=font(15, True))
               + d.textlength(lab, font=font(10)) + 30)
    assert nx <= W - 10, f"numbers band overflow: {nx}"

    # ---- Ticker (3 lines) + footer ----
    ty = 976
    for line in TICKER_LINES:
        d.text((14, ty), trunc(d, line, font(10), W - 28), font=font(10), fill=INK)
        ty += 13
    d.text((14, 1014), "Sources: Reuters, AP, AFP, BBC, CNN, dailysummaryof.com, ESA, CAS, ICJ, company + official statements.",
           font=font(9), fill=GREY)

    img.save(OUT, optimize=True)
    return OUT


if __name__ == "__main__":
    path = render()
    print(f"wrote {path} {os.path.getsize(path)} bytes")
