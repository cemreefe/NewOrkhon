"""Revision proofs and explicitly hypothetical EM pen-motion experiments."""

import unicodedata

import numpy as np
from PIL import Image, ImageDraw, ImageOps

from ductus import ROUTES, length, trajectories
from specimen import GRAY, INK, NEW, NOTO, ROOT, RULE, SANS, font, glyph, label

OLD = ROOT / "archive-v02" / "NewOrkhonText-Regular.ttf"
EARLIER = ROOT / "archive-v03" / "NewOrkhonText-Regular.ttf"


def revisions():
    im = Image.new("RGB", (1680, 1580), "white")
    d = ImageDraw.Draw(im)
    label(d, (70, 40), "NEW ORKHON / THREE REBUILT SIGNS", 40, bold=True)
    label(d, (70, 108), "0.4 · heavier strokes · writing structure before surface treatment", 25, GRAY)
    for x, title in ((350, "REFERENCE"), (790, "PREVIOUS / 0.2"), (1230, "PROPOSAL / 0.4")):
        label(d, (x, 190), title, 21, GRAY, bold=True)
    rows = [
        (0x10C00, "A",
         "Level the opposed returns; incline the connecting stroke. Mirrored Z.",
         "The common cap arm also appears in I, AL, AEK, EP and OEK."),
        (0x10C24, "ÆN",
         "Restore the lower-left post. Tilt the middle stroke; use two opposed saws.",
         "The opposed wedges remain open. The two halves correspond under a half-turn."),
        (0x10C22, "EM",
         "A rounded bowl returns left, then exits into a leg. No left upright.",
         "An authored change of stroke route—not a shape discovered by smoothing."),
    ]
    for i, (code, name, line1, line2) in enumerate(rows):
        y = 245 + i * 425
        label(d, (70, y + 35), name, 34, bold=True)
        label(d, (70, y + 90), f"U+{code:05X}", 18, GRAY)
        for x, path, size in ((350, NOTO, 310), (790, OLD, 345), (1230, NEW, 345)):
            d.line((x, y + 270, x + 290, y + 270), fill=RULE)
            d.line((x, y + 28, x + 290, y + 28), fill=RULE)
            glyph(d, x + 30, y + 270, chr(code), path, size)
        label(d, (350, y + 310), line1, 23)
        label(d, (350, y + 350), line2, 21, GRAY)
    label(d, (70, 1530), "Existing Unicode / RTL. These are speculative designs, not an attested historical stage.", 22, GRAY)
    im.save(ROOT / "glyph-revisions.png")


def trace(d, name, x, baseline, size=400, smoothing=True):
    paths = trajectories(name, smoothing)
    for raw, p in zip(trajectories(name, False), paths, strict=True):
        xy = [(x + px * size / 700, baseline - py * size / 700) for px, py in p]
        ghost = [(x + px * size / 700, baseline - py * size / 700) for px, py in raw]
        d.line(ghost, fill="#d5d5d5", width=3)
        d.line(xy, fill=INK, width=5, joint="curve")
        d.ellipse((xy[0][0] - 6, xy[0][1] - 6, xy[0][0] + 6, xy[0][1] + 6), fill=INK)
        for j in (28, 61):
            direction = np.asarray(xy[j + 1]) - xy[j]
            direction /= np.linalg.norm(direction)
            end = np.asarray(xy[j])
            back = end - direction * 15
            normal = np.array([-direction[1], direction[0]]) * 7
            d.polygon([tuple(end), tuple(back + normal), tuple(back - normal)], fill=INK)
    return paths


def motion():
    im = Image.new("RGB", (1680, 1510), "white")
    d = ImageDraw.Draw(im)
    label(d, (70, 45), "EM / WRITING MOTION BEFORE TYPE", 40, bold=True)
    label(d, (70, 110), "Dots: pen starts. Arrows: travel. Pale lines: unsmoothed routes.", 24, GRAY)
    panels = [
        ("lifted", False, "1 / ANGULAR, LIFTED", "Three strokes; preserve the diamond."),
        ("lifted", True, "2 / SAME ROUTE, SMOOTHED", "Round corners; keep the old construction."),
        ("retraced", True, "3 / ONE STROKE, RETRACED", "Fewer lifts, but extra travel and a knot."),
    ]
    for i, (name, smoothing, title, caption) in enumerate(panels):
        x = 70 + i * 530
        label(d, (x, 210), title, 21, bold=True)
        paths = trace(d, name, x + 20, 710, smoothing=smoothing)
        label(d, (x, 745), caption, 21)
        strokes = "stroke" if len(paths) == 1 else "strokes"
        label(d, (x, 786), f"{len(paths)} {strokes} · {length(paths):.0f} units of travel", 20, GRAY)
    d.line((70, 850, 1610, 850), fill=RULE)
    label(d, (70, 890), "4 / CHANGE THE ROUTE", 23, bold=True)
    trace(d, "bowl_leg", 90, 1370)
    label(d, (70, 1410), "One open bowl, then a leg.", 22)
    label(d, (600, 890), "5 / PRINTED CANDIDATE", 23, bold=True)
    glyph(d, 660, 1370, chr(0x10C22), NEW, 570)
    label(d, (600, 1410), "R-like, without the left upright.", 22)
    label(d, (1110, 950), "WHAT THE MODEL DOES", 22, bold=True)
    for j, line in enumerate([
        "Penalize rapid acceleration changes",
        "while staying near a supplied path.",
        "",
        "It does not choose a stroke order",
        "or decide which features may vanish.",
        "",
        "The open bowl is a design choice.",
        "Not a simulated historical result.",
    ]):
        label(d, (1110, 1000 + j * 40), line, 21, GRAY)
    label(d, (70, 1470), "Toy model: endpoint-fixed fidelity + squared discrete jerk. Hypothetical routes, no measured handwriting.", 21, GRAY)
    im.save(ROOT / "ductus-study.png")


def families():
    im = Image.new("RGB", (1680, 1590), "white")
    d = ImageDraw.Draw(im)
    label(d, (70, 45), "EXTEND THE MOVEMENT, NOT ONE SILHOUETTE", 35, bold=True)
    label(d, (70, 110), "Gray: reference. Black: 0.4. Related signs share a construction, not every detail.", 24, GRAY)
    groups = [
        ("OPPOSED / SINGLE RETURNS", [0x10C00, 0x10C03, 0x10C1E, 0x10C2F],
         "Level the returns into common arms. Keep the diagonal / upright and top / bottom contrasts."),
        ("SHOULDERS / STAGGERED POSTS", [0x10C07, 0x10C24, 0x10C21, 0x10C1C],
         "AEN keeps opposed saws on an inclined pole; use rounded shoulders in the post family."),
        ("BOWLS / RETURNS / LEGS", [0x10C22, 0x10C23, 0x10C2A, 0x10C16],
         "Use related bowls: AN becomes reversed C, ENY becomes 3; keep EM's exit leg."),
        ("BRANCHES / DIAGNOSTIC MARKS", [0x10C20, 0x10C31, 0x10C32, 0x10C41],
         "Y / lambda for plain forks; mirrored Arabic 3 for the trident. Crossed Y keeps two tips."),
    ]
    for i, (title, codes, caption) in enumerate(groups):
        y = 205 + i * 325
        label(d, (70, y), title, 24, bold=True)
        for j, code in enumerate(codes):
            x = 100 + j * 385
            glyph(d, x, y + 200, chr(code), NOTO, 175, "#999999")
            glyph(d, x + 160, y + 200, chr(code), NEW, 200)
            label(d, (x, y + 223), f"U+{code:05X}", 16, GRAY)
        label(d, (70, y + 268), caption, 22)
        d.line((70, y + 307, 1610, y + 307), fill=RULE)
    label(d, (70, 1535), "0.4 revises AG, EZ, AEN, ENT and IC; earlier return, bowl, EM and fork designs remain.", 21, GRAY)
    im.save(ROOT / "family-proposals.png")


def further_families():
    im = Image.new("RGB", (1680, 2030), "white")
    d = ImageDraw.Draw(im)
    label(d, (70, 40), "BOWLS, FORKS AND CONNECTED RETURNS", 38, bold=True)
    label(d, (70, 105), "One open bowl / two bowls. Plain forks / three linked tips. Same encoding, revised construction.", 23, GRAY)
    for x, title in ((350, "REFERENCE"), (760, "EARLIER / 0.3"), (1170, "NEW PROPOSAL")):
        label(d, (x, 175), title, 21, GRAY, bold=True)
    rows = [
        (0x10C23, "Return the ends into a full open bowl: reversed C, not a parenthesis."),
        (0x10C2A, "The notch becomes a waist between two lobes: Western 3."),
        (0x10C20, "Straight upper arms and flat serif ends: Y."),
        (0x10C32, "A curved head continues into the descending stroke: lambda."),
        (0x10C31, "Three upper tips become two connected returns, with a straight right-hand pole."),
        (0x10C41, "Two tips and the separate low crossbar: Y plus bar, not a trident."),
    ]
    for i, (code, caption) in enumerate(rows):
        y = 220 + i * 260
        name = unicodedata.name(chr(code)).removeprefix("OLD TURKIC LETTER ORKHON ")
        label(d, (70, y + 40), name, 29, bold=True)
        label(d, (70, y + 85), f"U+{code:05X}", 18, GRAY)
        for x, path in ((350, NOTO), (760, EARLIER), (1170, NEW)):
            d.line((x, y + 190, x + 280, y + 190), fill=RULE)
            glyph(d, x + 30, y + 190, chr(code), path, 230)
        label(d, (350, y + 215), caption, 21)
        d.line((70, y + 250, 1610, y + 250), fill=RULE)
    for x, title in ((350, "ARABIC NUMERAL 3"), (760, "MIRRORED REFERENCE"), (1170, "LATINIZED PROPOSAL")):
        label(d, (x, 1810), title, 18, GRAY, bold=True)
    glyph(d, 380, 1950, "٣", SANS, 110)
    ref = Image.new("RGB", (100, 120), "white")
    glyph(ImageDraw.Draw(ref), 20, 100, "٣", SANS, 110)
    im.paste(ImageOps.mirror(ref), (780, 1850))
    glyph(d, 1200, 1950, chr(0x10C31), NEW, 140)
    label(d, (70, 2000), "Mirrored = reflected left–right. These are shape proposals, not Latin sound values or historical claims.", 20, GRAY)
    im.save(ROOT / "further-families.png")


def focus():
    im = Image.new("RGB", (1680, 2210), "white")
    d = ImageDraw.Draw(im)
    label(d, (70, 40), "NEW ORKHON 0.4 / FIVE RELATED CHANGES", 38, bold=True)
    label(d, (70, 105), "Simpler construction, deliberate joins, shared white space. Same Unicode and reading order.", 23, GRAY)
    for x, title in ((350, "REFERENCE"), (780, "PREVIOUS / 0.3"), (1210, "PROPOSAL / 0.4")):
        label(d, (x, 175), title, 21, GRAY, bold=True)
    rows = [
        (0x10C0D, "Two cupped horns join on one staff. Straight Y retains a different opening."),
        (0x10C14, "EZ gets the softened three-stroke construction: two returns meet at the middle."),
        (0x10C24, "AEN keeps two opposed saws on a pole slanted 17 degrees. Three authored strokes."),
        (0x10C26, "An ordinary upright u, not an oval. Its three dots stay separate."),
        (0x10C31, "The linked tips now sit on a genuinely vertical right-hand pole."),
    ]
    for i, (code, caption) in enumerate(rows):
        y = 220 + i * 380
        name = unicodedata.name(chr(code)).removeprefix("OLD TURKIC LETTER ORKHON ")
        label(d, (70, y + 50), name, 32, bold=True)
        label(d, (70, y + 100), f"U+{code:05X}", 18, GRAY)
        for x, path in ((350, NOTO), (780, EARLIER), (1210, NEW)):
            for offset in (0, 231):
                d.line((x, y + 268 - offset, x + 300, y + 268 - offset), fill=RULE)
            glyph(d, x + 20, y + 268, chr(code), path, 330)
        label(d, (350, y + 305), caption, 22)
        d.line((70, y + 358, 1610, y + 358), fill=RULE)
    label(d, (70, 2150), "AEN/EZ stroke counts describe supplied centerlines, not measured handwriting or historical ductus.", 21, GRAY)
    im.save(ROOT / "revision-04.png")


def sizes():
    im = Image.new("RGB", (1680, 1380), "white")
    d = ImageDraw.Draw(im)
    label(d, (70, 45), "WEIGHT / SAME SIZE, SAME TEXT", 40, bold=True)
    label(d, (70, 110), "0.2: stems 64 / horizontals 30      0.4: stems 90 / horizontals 46", 25, GRAY)
    sample = "𐰍𐰤𐰔 𐰀𐰃𐰀 𐰣𐰢𐰪 𐰠𐰲𐰱𐱁 𐰿𐰦"
    for i, size in enumerate((100, 64, 44, 32, 24, 20)):
        y = 210 + i * 180
        label(d, (70, y), f"{size} px", 21, GRAY)
        label(d, (225, y), "0.2", 18, GRAY)
        label(d, (225, y + 95), "0.4", 18)
        glyph(d, 1580, y + 27, sample, OLD, size, "#777777", "rs")
        glyph(d, 1580, y + 120, sample, NEW, size, INK, "rs")
    label(d, (70, 1330), "Unscaled raster proofs. At 20 px the body is 14 pixels high; this is still an experimental, unhinted font.", 21, GRAY)
    im.save(ROOT / "weight-proof.png")


if __name__ == "__main__":
    assert set(ROUTES) == {"lifted", "retraced", "bowl_leg"}
    assert font(NEW, 40).getlength(chr(0x10C22)) > 0
    revisions()
    motion()
    families()
    further_families()
    focus()
    sizes()
    print("Rendered revision, pen-motion, family and weight proofs.")
