"""Current 0.11 capital/lowercase proofs and deliberately retained studies."""

import unicodedata

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw

from build import LETTERS, Letter, geometry
from ductus import em_print_path
from lowercase import LOWER
from specimen import EXAMPLES, GRAY, INK, NEW, NOTO, ROOT, RULE, font, glyph, label

SMALL = ROOT / "NewOrkhonTextLowercase-Regular.ttf"
OLD = ROOT / "archive-v04" / "NewOrkhonText-Regular.ttf"
PREVIOUS = ROOT / "archive-v05" / "NewOrkhonText-Regular.ttf"
PREVIOUS_SMALL = ROOT / "archive-v05" / "NewOrkhonTextLowercase-Regular.ttf"
BEFORE_SKETCH = ROOT / "archive-v06" / "NewOrkhonTextLowercase-Regular.ttf"
MISPLACED_SKETCH = ROOT / "archive-v07" / "NewOrkhonTextLowercase-Regular.ttf"
CORRECTED_SKETCH = ROOT / "archive-v08" / "NewOrkhonTextLowercase-Regular.ttf"


def vector(draw, letter, cx, baseline, scale):
    shape = geometry(letter)
    x0, _, x1, _ = shape.bounds
    polys = [shape] if shape.geom_type == "Polygon" else list(shape.geoms)
    for poly in polys:
        draw.polygon([(cx + (x - (x0 + x1) / 2) * scale, baseline - y * scale)
                      for x, y in poly.exterior.coords], fill=INK)
        for ring in poly.interiors:
            draw.polygon([(cx + (x - (x0 + x1) / 2) * scale, baseline - y * scale)
                          for x, y in ring.coords], fill="white")


def lowercase_alphabet():
    im = Image.new("RGB", (1680, 1680), "white")
    d = ImageDraw.Draw(im)
    label(d, (70, 35), "NEW ORKHON / UPPERCASE AND LOWERCASE", 38, bold=True)
    label(d, (70, 96), "Same em size. Gray: uppercase. Black: lowercase. Body 510 / ascenders 700 / descenders -190.", 22, GRAY)
    for i, lower in enumerate(LOWER):
        col, row = i % 7, i // 7
        x, y = 70 + col * 225, 170 + row * 238
        name = unicodedata.name(chr(lower.code)).split("ORKHON ")[1]
        label(d, (x, y), f"{name} / U+{lower.code:05X}", 15, bold=True)
        d.line((x, y + 165, x + 190, y + 165), fill=RULE)
        d.line((x, y + 111, x + 190, y + 111), fill="#b5b5b5")
        d.line((x, y + 185, x + 190, y + 185), fill="#dddddd")
        glyph(d, x + 5, y + 165, chr(lower.code), NEW, 105, "#aaaaaa")
        glyph(d, x + 98, y + 165, chr(lower.code), SMALL, 105)
        label(d, (x, y + 191), f"{lower.top} / {lower.bottom}", 16, GRAY)
        d.rectangle((x - 8, y - 10, x + 202, y + 219), outline=RULE)
    label(d, (70, 1640), "Lowercase uses the same Unicode through OpenType ss01 or the supplied lowercase-default font.", 20, GRAY)
    im.save(ROOT / "lowercase-alphabet.png")


def case_text():
    im = Image.new("RGB", (1680, 1570), "white")
    d = ImageDraw.Draw(im)
    label(d, (70, 40), "CASE IN WORDS / SAME EM SIZE", 39, bold=True)
    label(d, (70, 103), "Logical Unicode text, RTL layout. An initial capital changes the font, not the encoding.", 23, GRAY)
    for i, (latin, text) in enumerate(EXAMPLES):
        y = 185 + i * 270
        label(d, (70, y), latin, 23, bold=True)
        label(d, (70, y + 57), "UPPER", 17, GRAY)
        glyph(d, 1580, y + 105, text, NEW, 85, "#777777", "rs")
        label(d, (70, y + 139), "LOWER + INITIAL", 17)
        capital_width = font(NEW, 85).getlength(text[0], direction="rtl")
        glyph(d, 1580, y + 195, text[0], NEW, 85, INK, "rs")
        glyph(d, 1580 - capital_width, y + 195, text[1:], SMALL, 85, INK, "rs")
        d.line((70, y + 235, 1610, y + 235), fill=RULE)
    sample = EXAMPLES[1][1]
    label(d, (70, 1305), "LOWERCASE AT TEXT SIZES", 22, bold=True)
    for i, size in enumerate((40, 32, 24, 20)):
        y = 1360 + i * 45
        label(d, (70, y - 20), f"{size} px", 18, GRAY)
        glyph(d, 1580, y + 10, sample, SMALL, size, INK, "rs")
    label(d, (70, 1525), "Illustrative modern Turkish transliteration; not historical Old Turkic spelling.", 21, GRAY)
    im.save(ROOT / "case-text.png")


def ag_options():
    im = Image.new("RGB", (1680, 1010), "white")
    d = ImageDraw.Draw(im)
    label(d, (70, 40), "AG / UPPERCASE STAYS SEPARATE", 39, bold=True)
    label(d, (70, 105), "Lowercase is now literally ж, with a central upright, four curved arms and no descender.", 23, GRAY)
    for x, name in ((150, "UPPERCASE"), (700, "REJECTED 0.5 LOWER"), (1220, "CURRENT / Ж")):
        label(d, (x, 220), name, 21, GRAY, bold=True)
    glyph(d, 170, 690, chr(0x10C0D), NEW, 500)
    glyph(d, 700, 690, chr(0x10C0D), PREVIOUS_SMALL, 500, "#aaaaaa")
    glyph(d, 1220, 690, chr(0x10C0D), SMALL, 500)
    for x in (150, 700, 1220):
        d.line((x, 690, x + 320, 690), fill=RULE)
    label(d, (150, 850), "Two horns and a pole.", 23, GRAY)
    label(d, (700, 850), "Discarded alpha ribbon.", 23, GRAY)
    label(d, (1220, 850), "Upright and four arms.", 23)
    label(d, (70, 960), "These are authored proposals, not historical reconstructions or measured handwriting.", 22, GRAY)
    im.save(ROOT / "lowercase-ag-options.png")


def capitals():
    groups = [
        [(0x10C14, "EZ: upper reaches join in a rounded cup."),
         (0x10C24, "AEN: one N replaces the crowded double N; lowercase is one n."),
         (0x10C0D, "AG: restore the three separated pieces for uppercase.")],
        [(0x10C0F, "AEG: mirrored Cyrillic э, opening to the right."),
         (0x10C26, "ENT: remove the three dots; retain an ordinary u."),
         (0x10C28, "ENC: two bowls on a new common spine; a deliberate counter change.")],
        [(0x10C3D, "AS: one rounded upper return; IC retains two."),
         (0x10C47, "OT: symmetric hat above an upright-sided inverted u."),
         (0x10C32, "EC: tighten only the right side space, from 26 to 8 units.")],
    ]
    for page, rows in enumerate(groups, 1):
        im = Image.new("RGB", (1680, 1510), "white")
        d = ImageDraw.Draw(im)
        label(d, (70, 35), f"UPPERCASE REDRAWS / 0.11 · {page}/3", 39, bold=True)
        for x, title in ((350, "REFERENCE"), (780, "DELIVERED 0.5"), (1210, "CURRENT 0.11")):
            label(d, (x, 150), title, 21, GRAY, bold=True)
        for i, (code, caption) in enumerate(rows):
            y = 215 + i * 410
            name = unicodedata.name(chr(code)).split("ORKHON ")[1]
            label(d, (70, y + 45), name, 30, bold=True)
            label(d, (70, y + 92), f"U+{code:05X}", 18, GRAY)
            for x, fp in ((350, NOTO), (780, PREVIOUS), (1210, NEW)):
                d.line((x, y + 270, x + 300, y + 270), fill=RULE)
                glyph(d, x + 20, y + 270, chr(code), fp, 330, "#999999" if fp == NOTO else INK)
            label(d, (350, y + 312), caption, 22)
            d.line((70, y + 365, 1610, y + 365), fill=RULE)
        label(d, (70, 1470), "Same encoded signs. Reference forms are Noto, not tracings of inscriptions.", 21, GRAY)
        im.save(ROOT / f"uppercase-revisions-{page}.png")


def weight_audit():
    sample = "".join(chr(c) for c in (0x10C00, 0x10C03, 0x10C1A, 0x10C1E, 0x10C2F, 0x10C14, 0x10C24, 0x10C32))
    sizes = (130, 88, 56, 40, 32, 24, 20)
    im = Image.new("RGB", (1680, 1550), "white")
    d = ImageDraw.Draw(im)
    label(d, (70, 38), "THICKNESS CHECK / SHARED ARMS AND SERIFS", 37, bold=True)
    label(d, (70, 105), "Stems 90. Horizontal strokes 46 → 64. Serif lips 14 → 20. Gray: 0.4; black: current.", 22, GRAY)
    old_base = 235
    for i, size in enumerate(sizes):
        new_base = old_base + round(size * .72) + 30
        divider = new_base + 35
        label(d, (70, old_base - 55), f"{size} px", 20, GRAY)
        label(d, (180, old_base - 55), "old", 17, GRAY)
        label(d, (180, new_base - 50), "new", 17)
        glyph(d, 1570, old_base, sample, OLD, size, "#888888", "rs")
        glyph(d, 1570, new_base, sample, NEW, size, INK, "rs")
        d.line((165, divider, 1590, divider), fill=RULE)
        if i + 1 < len(sizes):
            old_base = divider + round(sizes[i + 1] * .72) + 40
    label(d, (70, 1510), "Actual raster at each size; no scaling of a large glyph image.", 20, GRAY)
    im.save(ROOT / "weight-audit.png")


def em_options():
    hybrid = Letter(0x10C22, [em_print_path(), "M 80 110 C 185 235 315 380 460 525"],
                    [(475, 0, 1)], ("open", "round"), "One restored crossing")
    close = Letter(0x10C22, [
        "M 250 700 C 365 585 545 460 545 350 C 545 240 365 115 250 0",
        "M 85 570 C 190 475 335 325 460 125",
        "M 85 130 C 190 225 335 375 460 575",
    ], [], ("diagonal", "round"), "Preserved three-stroke route")
    im = Image.new("RGB", (1680, 790), "white")
    d = ImageDraw.Draw(im)
    label(d, (70, 45), "EM / WHAT THE SIMPLIFICATION REMOVES", 36, bold=True)
    for x, title in ((120, "REFERENCE"), (515, "BOWL + LEG"), (905, "ONE CROSSING"), (1300, "THREE STROKES")):
        label(d, (x, 164), title, 19, GRAY, bold=True)
        d.line((x, 550, x + 270, 550), fill=RULE)
    glyph(d, 140, 550, chr(0x10C22), NOTO, 440, "#999999")
    glyph(d, 515, 550, chr(0x10C22), NEW, 440)
    vector(d, hybrid, 1040, 550, .49)
    vector(d, close, 1430, 550, .49)
    for x, text in ((120, "Crossings and a chevron."), (515, "Clearer; crossings lost."),
                    (905, "A knot at the join."), (1300, "Closer, but crowded.")):
        label(d, (x, 610), text, 19, GRAY)
    label(d, (120, 695), "The R-like form remains the default, not a claim of historical inevitability.", 22, GRAY)
    im.save(ROOT / "em-closer-options.png")


def lowercase_revisions():
    rows = [
        (0x10C24, "One N / n. Remove the crowded second diagonal and shoulder."),
        (0x10C0D, "Literal ж: central upright and four curved arms, all within the body."),
        (0x10C1E, "Dotless j restored: body-height post and a curved descending hook."),
        (0x10C03, "Curve the head; lower the post. No square cap left above the body."),
        (0x10C2F, "Same curved head, mirrored. The post descends below the baseline."),
        (0x10C1A, "Curved mirrored-f head; retain the distinguishing crossbar."),
        (0x10C07, "OE now deepens its upper return to baseline; post heights and descender are retained."),
        (0x10C22, "The whole bowl occupies the body; only the exit leg descends."),
        (0x10C0B, "The whole eye occupies the body; only its two legs descend."),
        (0x10C3D, "One deep return fills the body; only the right post descends."),
        (0x10C31, "Two deep returns fill the body; only the right post descends."),
        (0x10C41, "The Y fork fills the body; the crossbar sits on the short descender."),
    ]
    for page in range(4):
        im = Image.new("RGB", (1680, 1510), "white")
        d = ImageDraw.Draw(im)
        label(d, (70, 35), f"LOWERCASE CORRECTIONS / 0.11 · {page + 1}/4", 38, bold=True)
        label(d, (70, 100), "Shaded band: x-height to baseline. Same em size in all three columns.", 23, GRAY)
        for x, title in ((350, "CURRENT UPPER"), (780, "REJECTED 0.5 LOWER"), (1210, "CURRENT LOWER")):
            label(d, (x, 160), title, 20, GRAY, bold=True)
        for row, (code, caption) in enumerate(rows[page * 3:page * 3 + 3]):
            y = 215 + row * 410
            baseline = y + 270
            name = unicodedata.name(chr(code)).split("ORKHON ")[1]
            label(d, (70, y + 70), name, 30, bold=True)
            label(d, (70, y + 115), f"U+{code:05X}", 18, GRAY)
            for x, path in ((350, NEW), (780, PREVIOUS_SMALL), (1210, SMALL)):
                top = baseline - 330 * .510
                d.rectangle((x, top, x + 300, baseline), fill="#f5f5f5")
                d.line((x, top, x + 300, top), fill="#b5b5b5")
                d.line((x, baseline, x + 300, baseline), fill="#888888")
                d.line((x, baseline + 330 * .190, x + 300, baseline + 330 * .190), fill=RULE)
                glyph(d, x + 20, baseline, chr(code), path, 330,
                      "#999999" if path == PREVIOUS_SMALL else INK)
            for value, offset in (("510", -330 * .510), ("0", 0), ("-190", 330 * .190)):
                label(d, (270, baseline + offset - 11), value, 16, GRAY)
            label(d, (350, y + 345), caption, 22)
            d.line((70, y + 390, 1610, y + 390), fill=RULE)
        label(d, (70, 1470), "Body proportions are design decisions, not demonstrated historical developments.", 21, GRAY)
        im.save(ROOT / f"lowercase-revisions-{page + 1}.png")


def lowercase_sizes():
    groups = ((0x10C24, 0x10C26, 0x10C24, 0x10C07),
              (0x10C03, 0x10C2F, 0x10C1A),
              (0x10C22, 0x10C0B), (0x10C3D, 0x10C31),
              (0x10C20, 0x10C41), (0x10C0D, 0x10C13),
              (0x10C1E, 0x10C3C))
    sample = " ".join("".join(chr(code) for code in group) for group in groups)
    im = Image.new("RGB", (1680, 1550), "white")
    d = ImageDraw.Draw(im)
    label(d, (70, 35), "REVISED LOWERCASE / ACTUAL RASTER SIZES", 37, bold=True)
    label(d, (70, 100), "Diagnostic sign groups, not words. Gray: rejected 0.5. Black: current 0.11. Logical RTL.", 22, GRAY)
    for i, size in enumerate((88, 64, 48, 32, 24, 20)):
        y = 190 + i * 210
        label(d, (70, y + 15), f"{size} px", 20, GRAY)
        for offset, name, path, color in ((60, "old", PREVIOUS_SMALL, "#999999"),
                                          (150, "new", SMALL, INK)):
            baseline = y + offset
            label(d, (180, baseline - 25), name, 18, GRAY)
            glyph(d, 1580, baseline, sample, path, size, color, "rs")
        d.line((165, y + 185, 1610, y + 185), fill=RULE)
    label(d, (70, 1495), "Raster checks expose failures; they do not establish reader performance.", 22, GRAY)
    im.save(ROOT / "lowercase-size-proof.png")


def sketch_diffs():
    rows = [
        (0x10C14, "EZ", "1 → EZ: closed loop + short lower post + falling leg."),
        (0x10C11, "AD", "2 → AD: shared upright and top arm + two open returns."),
        (0x10C3C, "AER", "3 → AER: two rounded m-like shoulders; central post descends to −190."),
    ]
    im = Image.new("RGB", (1680, 1980), "white")
    d = ImageDraw.Draw(im)
    label(d, (65, 35), "EZ / AD / AER — CORRECTED PLACEMENTS", 38, bold=True)
    label(d, (65, 100), "0.6 → 0.8. The three sketches now apply to the correct lowercase signs. Capitals unchanged.", 22, GRAY)
    for x, name in ((480, "BEFORE / 0.6"), (920, "AFTER / 0.8"), (1370, "OUTLINE OVERLAY")):
        label(d, (x - 150, 170), name, 22, bold=True)
    before, after = TTFont(BEFORE_SKETCH), TTFont(CORRECTED_SKETCH)
    for i, (code, name, note) in enumerate(rows):
        y = 230 + i * 400
        baseline, size = y + 235, 360
        d.rectangle((40, y - 12, 1640, y + 375), outline=RULE)
        label(d, (65, y + 55), name, 34, bold=True)
        label(d, (65, y + 105), f"U+{code:05X}", 21, GRAY)
        label(d, (65, y + 145), "lowercase", 18, GRAY)
        for x in (480, 920, 1370):
            d.rectangle((x - 165, baseline - .510 * size, x + 165, baseline), fill="#f5f5f5")
            for height in (510, 0, -190):
                yy = baseline - height * size / 1000
                d.line((x - 165, yy, x + 165, yy), fill=RULE)
        glyph(d, 480, baseline, chr(code), BEFORE_SKETCH, size, "#999999", "ms")
        glyph(d, 920, baseline, chr(code), CORRECTED_SKETCH, size, INK, "ms")
        for source, color in ((before, "#b1392b"), (after, "#135da8")):
            glyph_name = source.getBestCmap()[code]
            coords, ends, _ = source["glyf"][glyph_name].getCoordinates(source["glyf"])
            advance = source["hmtx"][glyph_name][0]
            start = 0
            for end in ends:
                ring = [(1370 + (x - advance / 2) * size / 1000, baseline - yy * size / 1000)
                        for x, yy in coords[start:end + 1]]
                d.line(ring + ring[:1], fill=color, width=2)
                start = end + 1
        label(d, (315, y + 330), note, 22)
    label(d, (65, 1470), "Equal em size and baseline; shaded band = 510 to 0. Overlay: red old / blue new.", 22, GRAY)
    label(d, (65, 1530), "ELT / AL / OT RESTORED — each is exactly its 0.6 form again", 26, bold=True)
    for x, code, name in ((65, 0x10C21, "ELT"), (605, 0x10C1E, "AL"), (1145, 0x10C47, "OT")):
        d.rectangle((x - 15, 1580, x + 475, 1860), outline=RULE)
        label(d, (x, 1595), f"{name} / U+{code:05X}", 23, bold=True)
        label(d, (x + 20, 1640), "MISPLACED 0.7", 17, GRAY)
        label(d, (x + 250, 1640), "RESTORED 0.8", 17)
        for cx in (x + 110, x + 345):
            for height in (510, 0, -190):
                yy = 1780 - height * .17
                d.line((cx - 80, yy, cx + 80, yy), fill=RULE)
        glyph(d, x + 110, 1780, chr(code), MISPLACED_SKETCH, 170, "#999999", "ms")
        glyph(d, x + 345, 1780, chr(code), CORRECTED_SKETCH, 170, INK, "ms")
    label(d, (65, 1905), "Historical 0.8 placement corrections: these six letters only. Same Unicode signs and logical RTL.", 22, GRAY)
    im.save(ROOT / "sketch-diffs.png")


def main():
    assert {g.code for g in LOWER} == {g.code for g in LETTERS}
    lowercase_alphabet()
    case_text()
    ag_options()
    capitals()
    weight_audit()
    em_options()
    lowercase_revisions()
    lowercase_sizes()
    sketch_diffs()
    print("Rendered case alphabet/text, lowercase corrections, capital revisions and weight/EM studies.")


if __name__ == "__main__":
    main()
