"""New Orkhon Sans: a neutral, optically corrected companion to the serif."""

from dataclasses import replace

SANS_SIDES = {
    "stem": 42, "round": 28, "diagonal": 24, "open": 20, "lambda": 8,
}


def sans_forms(capitals, lowercase):
    upper = [
        replace(letter, serifs=[], stroke_stem=84, stroke_hair=76, ink_zone=True,
                decision="Sans construction: flat terminals, near-even optical weight and compact side spaces.")
        for letter in capitals
    ]
    small = [
        replace(letter, serifs=[], stroke_stem=76, stroke_hair=70, ink_zone=True,
                decision="Sans construction: flat terminals, near-even optical weight and open counters.")
        for letter in lowercase
    ]
    cap = {letter.code: letter for letter in upper}
    by_code = {letter.code: letter for letter in small}
    top, bottom = 700 - 76 / 2, 76 / 2
    for code, paths in {
        0x10C00: [f"M 470 {top - 72} L 470 {top} L 100 {top} "
                  f"L 470 {bottom} L 100 {bottom} L 100 {bottom + 72}"],
        0x10C03: [f"M 125 0 L 125 {top} L 440 {top} L 440 {top - 72}"],
        0x10C1C: [f"M 125 0 L 125 {top} L 420 {top} L 420 {top - 72}",
                  cap[0x10C1C].paths[1]],
        0x10C1E: [f"M 365 700 L 365 {bottom} L 95 {bottom} L 95 {bottom + 72}"],
    }.items():
        cap[code] = replace(cap[code], paths=paths)
    ag = cap[0x10C0D]
    cap[0x10C0D] = replace(
        ag, paths=[*ag.paths[:2], "M 310 340 L 310 0"],
    )
    by_code[0x10C00] = replace(
        by_code[0x10C00],
        paths=["M 385 415 L 385 475 L 105 475 L 380 35 L 100 35 L 100 95"],
    )
    for code, stem, hair in (
        (0x10C07, 76, 61),  # OE's near-vertical return otherwise darkens with a near-monoline stroke.
        (0x10C0D, 76, 65),  # Preserve the open junction of literal ж.
        (0x10C1A, 76, 68),  # Keep the closed AEK counter open in small text.
        (0x10C28, 76, 67),  # Two enclosed bowls darken more than one.
        (0x10C3A, 76, 61),  # AR's returned body should still stop on the baseline.
        (0x10C48, 72, 65),  # The figure-eight has two closed counters and a narrow waist.
    ):
        by_code[code] = replace(by_code[code], stroke_stem=stem, stroke_hair=hair)
    enc = cap[0x10C28]
    floor = enc.stroke_hair / 2
    head = 700 - floor
    cap[0x10C28] = replace(enc, paths=[
        enc.paths[0],
        f"M 110 {head} C 400 {head} 465 550 360 445 C 325 405 210 385 110 370",
        f"M 110 370 C 475 355 500 {160 + floor} 390 {65 + floor} "
        f"C 335 {floor} 210 {floor} 110 {floor}",
    ])
    enc = by_code[0x10C28]
    floor = enc.stroke_hair / 2
    head = 510 - floor
    by_code[0x10C28] = replace(enc, paths=[
        enc.paths[0],
        f"M 105 {head} C 315 {head} 345 415 250 340 C 215 315 150 300 105 290",
        f"M 105 290 C 465 275 465 {85 + floor} 335 {15 + floor} "
        f"C 285 {floor} 180 {floor} 105 {floor}",
    ])
    cap[0x10C48] = replace(cap[0x10C48], stroke_stem=80, stroke_hair=71)
    oe = by_code[0x10C07]
    by_code[0x10C07] = replace(
        oe, paths=[oe.paths[0].replace("280 44.5 405 29.5", "280 45.5 405 30.5")],
    )
    aek = by_code[0x10C1A]
    by_code[0x10C1A] = replace(
        aek, paths=[
            aek.paths[0],
            aek.paths[1].replace("5 30 190 29.5", "5 34 190 34").replace("265 29.5", "265 34"),
        ],
    )
    oek = by_code[0x10C1C]
    by_code[0x10C1C] = replace(
        oek, paths=[
            "M 105 0 L 105 520 C 105 640 160 700 240 700 "
            "C 285 700 285 685 360 654.5",
            oek.paths[1],
        ],
        decision="Curved upper terminal follows the same cut angle as the f-like lowercase heads.",
    )
    ic = cap[0x10C31]
    first, second = ic.paths[0].split("L 255 700 ", 1)
    cap[0x10C31] = replace(
        ic, paths=[first + "L 255 700", "M 255 700 " + second, ic.paths[1]],
        reliefs=tuple((1, *relief[1:]) for relief in ic.reliefs),
    )
    ic = by_code[0x10C31]
    by_code[0x10C31] = replace(ic, paths=[
        "M 85 510 L 85 180 C 85 -13.333333 300 -13.333333 300 180 L 300 510",
        "M 300 510 L 300 180 C 300 -13.333333 515 -13.333333 515 180 L 515 510",
        ic.paths[1],
    ])
    cap[0x10C07] = replace(cap[0x10C07], paths=[
        "M 130 0 L 130 662",
        "M 130 662 C 240 662 280 365 405 350",
        "M 405 350 L 405 700",
    ])
    by_code[0x10C07] = replace(by_code[0x10C07], paths=[
        "M 130 -190 L 130 479.5",
        "M 130 479.5 C 240 479.5 280 45.5 405 30.5",
        "M 405 30.5 L 405 510",
    ])
    by_code[0x10C16] = replace(by_code[0x10C16], paths=[
        "M 100 0 L 100 700",
        "M 100 475 C 455 475 455 35 100 35",
    ])
    # The approved AQ repeats its capital even in the lowercase-default font.
    aq, source = by_code[0x10C34], cap[0x10C34]
    by_code[0x10C34] = replace(
        aq, paths=source.paths, serifs=[], stroke_stem=source.stroke_stem,
        stroke_hair=source.stroke_hair, top=700, bottom=0,
        decision="Identical capital and lowercase outlines in the Sans family.",
    )
    return list(cap.values()), list(by_code.values())
