"""Render specimens with explicit RTL layout; no manual string reversal."""

import sys
import unicodedata
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, features

from build import LETTERS

ROOT = Path(__file__).resolve().parent
NOTO = ROOT / "NotoSansOldTurkic-Regular.ttf"
NEW = ROOT / "NewOrkhonText-Regular.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
INK, GRAY, RULE = "#151515", "#626262", "#d4d4d4"


def font(path, size):
    return ImageFont.truetype(str(path), size, layout_engine=ImageFont.Layout.RAQM)


def label(d, pos, text, size=23, color=INK, bold=False):
    d.text(pos, text, font=font(BOLD if bold else SANS, size), fill=color)


def glyph(d, x, y, text, path, size, color=INK, anchor="ls"):
    d.text((x, y), text, font=font(path, size), fill=color,
           direction="rtl", anchor=anchor, language="tr")


def comparison():
    w, h = 1680, 1660
    im = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(im)
    label(d, (70, 45), "NEW ORKHON / YENİ ORHUN", 43, bold=True)
    label(d, (70, 110), "Revision 0.14 · RTL shoulders, lighter OE, curved OEK head and joined tilted serifs.", 25, GRAY)
    label(d, (70, 153), "Gray: Noto Orkhon reference     Black: hand-drawn New Orkhon", 24, GRAY)
    for i, letter in enumerate(LETTERS):
        col, row = i % 7, i // 7
        x, y = 70 + col * 225, 235 + row * 224
        name = f"{letter.code:05X}  " + unicodedata.name(chr(letter.code)).split("ORKHON ")[1]
        label(d, (x, y), name, 20)
        d.line((x, y + 142, x + 190, y + 142), fill="#e1d6c9")
        d.line((x, y + 61, x + 190, y + 61), fill="#e1d6c9")
        glyph(d, x + 20, y + 142, chr(letter.code), NOTO, 100, "#999999")
        glyph(d, x + 115, y + 142, chr(letter.code), NEW, 115)
        label(d, (x, y + 169), f"{letter.sides[0]} / {letter.sides[1]}", 16, GRAY)
        d.line((x, y + 200, x + 190, y + 200), fill=RULE)
    label(d, (70, 1600), "42 capitals · baseline 0 / cap 700 · round overshoot ±10 · same Unicode / RTL · 0.14", 22, GRAY)
    im.save(ROOT / "alphabet-comparison.png")


EXAMPLES = [
    ("Türk dili", "𐱅𐰇𐰼𐰜 𐰓𐰃𐰠𐰃"),
    ("Güzel bir gün", "𐰏𐰇𐰔𐰀𐰠 𐰋𐰃𐰼 𐰏𐰇𐰤"),
    ("Altın", "𐰀𐰡𐰃𐰣"),
    ("Ben Türkçe bilirim", "𐰋𐰀𐰤 𐱅𐰇𐰼𐰚𐰲𐰀 𐰋𐰃𐰠𐰃𐰼𐰃𐰢"),
]


def text_page():
    im = Image.new("RGB", (1680, 1660), "white")
    d = ImageDraw.Draw(im)
    label(d, (90, 55), "NEW ORKHON TEXT", 43, bold=True)
    label(d, (90, 120), "Letterforms redesigned for running text. Read Orkhon from right to left.", 26, GRAY)
    y = 225
    for latin, text in EXAMPLES:
        label(d, (90, y), latin, 27)
        label(d, (90, y + 49), "REFERENCE", 17, GRAY)
        glyph(d, 1580, y + 105, text, NOTO, 72, "#888888", "rs")
        label(d, (90, y + 148), "NEW", 17)
        glyph(d, 1580, y + 207, text, NEW, 88, INK, "rs")
        d.line((90, y + 250, 1580, y + 250), fill=RULE)
        y += 280
    label(d, (90, 1392), "Same text, smaller sizes", 24, bold=True)
    sample = EXAMPLES[1][1]
    for j, size in enumerate((44, 32, 24)):
        label(d, (90, 1442 + j * 50), f"{size} px", 19, GRAY)
        glyph(d, 1580, 1470 + j * 50, sample, NEW, size, anchor="rs")
    label(d, (90, 1610), "Modern Turkish transliteration with explicit vowels; not a translation into Old Turkic.", 21, GRAY)
    im.save(ROOT / "text-specimen.png")


CASE_STUDIES = [
    (0x10C3C, "A CLEAN DOUBLE ROOF",
     "Two equal shoulders meet above the stem; its top ends at their valley.",
     "No pole through the roof, no stray pointed overlap."),
    (0x10C16, "ONE VERTICAL SYSTEM",
     "The bowl shares the same cap and baseline as the other signs.",
     "Its counter width is related to the oval, not sized independently."),
    (0x10C1C, "REPLACE A CONSTRUCTION",
     "The upper rectangle opens into a cap arm; the lower tier becomes an arch.",
     "Two tiers remain. Keeping every old corner is not the identity rule."),
    (0x10C31, "PRESERVE THE REAL DIFFERENCE",
     "The č/i sign keeps its middle prong: a trident, not a plain fork.",
     "No invented descender is needed to distinguish it from l²."),
    (0x10C26, "AN EXPLICIT SIMPLIFICATION",
     "ENT becomes an ordinary dotless u, as requested.",
     "No other sign has this outline; this is not the historical form."),
    (0x10C3F, "SPACE IS PART OF THE LETTER",
     "Round edges receive less side space than straight stems.",
     "Fit counters and inter-letter gaps together; do not use equal margins."),
]


def cases():
    im = Image.new("RGB", (1680, 1660), "white")
    d = ImageDraw.Draw(im)
    label(d, (70, 45), "SIX EXPLICIT DESIGN DECISIONS", 40, bold=True)
    label(d, (70, 110), "Reference → proposed text form. New drawings, not automated outline conversion.", 24, GRAY)
    for i, (code, title, line1, line2) in enumerate(CASE_STUDIES):
        y = 210 + i * 230
        glyph(d, 95, y + 117, chr(code), NOTO, 130, "#888888")
        label(d, (220, y + 60), "→", 32, GRAY)
        glyph(d, 300, y + 117, chr(code), NEW, 140)
        label(d, (490, y + 10), title, 23, bold=True)
        label(d, (490, y + 57), line1, 22)
        label(d, (490, y + 96), line2, 22, GRAY)
        label(d, (490, y + 135), f"U+{code:05X}", 18, GRAY)
        d.line((70, y + 190, 1610, y + 190), fill=RULE)
    im.save(ROOT / "design-decisions.png")


def spacing_page():
    im = Image.new("RGB", (1680, 1660), "white")
    d = ImageDraw.Draw(im)
    label(d, (70, 45), "SPACE & CONSTRUCTION / REVISION 0.8", 39, bold=True)
    label(d, (70, 110), "Repeated signs expose uneven rhythm that an isolated alphabet can hide.", 25, GRAY)
    rows = [
        ("AG / AEN / EZ", "𐰍𐰤𐰔" * 4),
        ("ENT / SINGLE & DOUBLE BOWLS", "𐰦𐰣𐰪" * 4),
        ("FORK / TRIDENT / CROSSBAR", "𐰠𐰱𐱁𐰠𐰱𐱁𐰠𐰱𐱁"),
        ("A / AEN / EM", "𐰀𐰤𐰢𐰀𐰤𐰢𐰀𐰤𐰢"),
        ("DOUBLE ROOFS / STEMS", "𐰼𐰾𐰼𐰾𐰼𐰾𐰼𐰾"),
    ]
    for i, (caption, text) in enumerate(rows):
        y = 210 + i * 205
        label(d, (70, y), caption, 22, bold=True)
        baseline = y + 140
        d.line((70, baseline, 1590, baseline), fill="#e1d6c9")
        d.line((70, baseline - 70, 1590, baseline - 70), fill="#e1d6c9")
        glyph(d, 1590, baseline, text, NEW, 100, anchor="rs")
    label(d, (70, 1285), "0.4 → 0.8 / SAME WORDS", 22, bold=True)
    text = EXAMPLES[1][1]
    old = ROOT / "archive-v04" / "NewOrkhonText-Regular.ttf"
    if old.exists():
        glyph(d, 1590, 1410, text, old, 100, "#999999", anchor="rs")
    glyph(d, 1590, 1540, text, NEW, 100, anchor="rs")
    label(d, (70, 1610), "Optical spacing is a design judgement, not a claim of equal measured gaps.", 22, GRAY)
    im.save(ROOT / "spacing-proof.png")


def direction_test():
    # Prove that the starting t², not the final k, is rightmost.
    f = font(NEW, 100)
    text = "𐱅𐰇𐰼𐰜"
    rendered = Image.new("L", (700, 170), 255)
    draw = ImageDraw.Draw(rendered)
    draw.text((20, 110), text, font=f, direction="rtl", anchor="ls", fill=0)
    start_advance = f.getlength("𐱅", direction="rtl")
    length = f.getlength(text, direction="rtl")
    actual = rendered.crop((round(20 + length - start_advance), 0,
                            round(20 + length), 170))
    expected = Image.new("L", actual.size, 255)
    ImageDraw.Draw(expected).text((0, 110), "𐱅", font=f, direction="rtl",
                                 anchor="ls", fill=0)
    import numpy as np
    # Rounding of advance placement permits a one-pixel shift.
    a = np.array(actual) < 128
    e = np.array(expected) < 128
    errors = [np.mean(a != np.roll(e, shift, axis=1)) for shift in (-1, 0, 1)]
    assert min(errors) < .012, errors
    print("RTL raster check passed: initial t² is at the right edge.")


if __name__ == "__main__":
    if not features.check("raqm"):
        sys.exit("Pillow with libraqm is required for correct RTL rendering.")
    direction_test()
    comparison()
    text_page()
    cases()
    spacing_page()
    print("Rendered four full-resolution specimen sheets.")
