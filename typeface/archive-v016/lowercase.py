"""Authored lowercase counterparts for all 42 Orkhon signs.

The same Unicode signs select these forms via ss01 or a lowercase-default font.
The height system has x-height 510, ascenders 700 and descenders to -190.
AQ deliberately reuses its capital form at full cap height.
"""

from dataclasses import dataclass

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path

AQ_PATHS = [
    "M 380 0 L 380 700",
    "M 380 330 C 245 350 175 470 105 460 C 175 285 155 125 95 0",
]
AQ_SERIFS = [(380, 0, 1), (380, 700, -1)]

OQ_UPRIGHT_PATHS = [
    "M 255 510 L 255 -190",
    "M 70 185 C 175 185 230 75 255 -190 C 280 75 335 185 440 185",
]


def sideways_oq_paths(direction: str) -> list[str]:
    if direction not in ("left", "right"):
        raise ValueError(direction)
    height_scale = 510 / 370
    transform = ((0, height_scale, -.7, 0, 0, -70 * height_scale)
                 if direction == "left"
                 else (0, -height_scale, .7, 0, 0, 440 * height_scale))
    paths = []
    for path in OQ_UPRIGHT_PATHS:
        pen = SVGPathPen(None)
        parse_path(path, TransformPen(pen, transform))
        paths.append(pen.getCommands())
    return paths


@dataclass
class Lower:
    code: int
    paths: list[str]
    serifs: list[tuple[int, int, int]]
    sides: tuple[str, str]
    decision: str
    top: int = 510
    bottom: int = 0
    round_top: bool = False
    round_bottom: bool = False
    dots: tuple = ()
    stroke_stem: int = 82
    stroke_hair: int = 59
    reliefs: tuple[tuple[int, float, float, float, float], ...] = ()
    ink_zone: bool = False


LOWER = [
    Lower(0x10C00, ["M 385 430 L 385 490 L 105 490 L 380 20 L 100 20 L 100 80"],
          [(100, 510, -1), (380, 0, 1)], ("diagonal", "diagonal"),
          "Shorter opposed returns form the small mirrored z."),
    Lower(0x10C03, ["M 105 -190 L 105 340 C 105 475 200 525 350 465"],
          [(105, -190, 1)], ("stem", "round"),
          "A curved f-like head fills the body above a descending left post.", bottom=-190),
    Lower(0x10C06, ["M 115 510 C 115 405 175 330 265 255 C 175 180 115 105 115 0"],
          [], ("round", "open"), "One short, flowing cusp."),
    Lower(0x10C07, ["M 130 -190 L 130 510 C 240 510 280 44.5 405 29.5 L 405 510"],
          [(130, -190, 1), (405, 510, -1)], ("stem", "stem"),
          "Deepen the upper return to the baseline; retain both post heights and the descender, at lowercase 82/59 weight.",
          bottom=-190),
    Lower(0x10C09, ["M 180 510 C 65 430 135 350 245 290 C 365 190 320 0 185 0 "
                    "C 70 0 65 105 100 180"],
          [], ("round", "round"), "One bowl and its returned head.", round_bottom=True),
    Lower(0x10C0B, ["M 240 480 C 65 400 65 110 240 30 C 415 110 415 400 240 480",
                    "M 240 30 L 115 -190", "M 240 30 L 365 -190"],
          [(115, -190, 1), (365, -190, 1)], ("diagonal", "diagonal"),
          "The eye fills x-height to baseline; only its two legs descend.", bottom=-190),
    Lower(0x10C0D, ["M 70 510 C 190 510 135 320 300 255 C 135 190 190 0 70 0",
                    "M 530 510 C 410 510 465 320 300 255 C 465 190 410 0 530 0",
                    "M 300 0 L 300 510"],
          [(70, 510, -1), (530, 510, -1), (70, 0, 1), (530, 0, 1),
           (300, 0, 1), (300, 510, -1)], ("open", "open"),
          "Literal lowercase Cyrillic ж; taper the four incoming arms locally, keeping the central upright.",
          reliefs=((0, 300, 255, 170, .5), (1, 300, 255, 170, .5))),
    Lower(0x10C0F, ["M 430 425 C 350 510 210 510 130 430 C 10 335 20 170 130 75 "
                    "C 210 0 350 0 430 85", "M 425 255 L 70 255"],
          [], ("round", "open"), "Open-right small bow and middle bar, like a mirrored э.",
          round_top=True, round_bottom=True),
    Lower(0x10C11, ["M 95 0 L 95 510",
                    "M 95 480 L 330 480 C 475 480 475 315 285 265 "
                    "C 505 225 500 0 315 0 C 270 0 245 10 220 40"],
          [(95, 0, 1), (95, 510, -1)], ("stem", "round"),
          "The second sketch's right-hand option: one upright and top arm join two open returns."),
    Lower(0x10C13, ["M 105 510 L 380 0", "M 380 510 L 105 0"],
          [(105, 0, 1), (380, 0, 1)], ("diagonal", "diagonal"),
          "Small opposing diagonals share a crossing."),
    Lower(0x10C14, ["M 185 245 C 105 330 60 425 130 480 "
                    "C 220 550 345 505 395 410 C 445 315 315 235 185 245",
                    "M 110 0 L 110 245 L 185 245 C 245 180 300 50 400 0"],
          [(110, 0, 1)], ("open", "round"),
          "The first sketch's loop-and-leg: a closed tilted eye, short lower post and falling leg."),
    Lower(0x10C16, ["M 100 0 L 100 700 L 100 495 C 455 495 455 0 100 0"],
          [(100, 0, 1), (100, 700, -1)], ("stem", "round"),
          "A tall post with one lower bowl.", top=700),
    Lower(0x10C18, ["M 100 335 C 65 535 380 555 390 345 C 385 240 260 240 260 80 L 260 -190"],
          [(260, -190, 1)], ("round", "round"),
          "Small open head and attached descender.", bottom=-190, round_top=True),
    Lower(0x10C1A, ["M 400 -190 L 400 375",
                    "M 400 340 C 400 475 255 525 105 465 "
                    "C -5 405 5 30 190 29.5 C 265 29.5 350 75 400 155"],
          [(400, -190, 1)], ("round", "stem"),
          "A rounded lower return closes the curved head into its post above the baseline, avoiding a stretched flat-bottomed counter.",
          bottom=-190, reliefs=((1, 400, 155, 125, .65),)),
    Lower(0x10C1C, ["M 105 0 L 105 520 C 105 640 160 700 240 700 "
                    "C 285 700 330 684.5 360 654.5",
                    "M 105 300 C 230 350 335 325 335 200 L 335 0"],
          [(105, 0, 1), (335, 0, 1)], ("stem", "open"),
          "A curved f-like ascender head replaces the squared cap arm; the lower tier stays on its original path.", top=700),
    Lower(0x10C1E, ["M 350 510 L 350 -65 C 350 -190 185 -225 95 -125"],
          [(350, 510, -1)], ("open", "stem"),
          "Dotless j with unchanged outline; tighten only its left sidebearing from 32 to 18.", bottom=-190),
    Lower(0x10C20, ["M 90 510 L 245 35 L 245 -190", "M 400 510 L 245 35"],
          [(90, 510, -1), (400, 510, -1), (245, -190, 1)],
          ("diagonal", "diagonal"), "The Y body reaches the baseline before its tail descends.", bottom=-190),
    Lower(0x10C21, ["M 105 0 L 105 510 C 190 510 215 300 260 300 "
                    "C 305 300 330 510 415 510 L 415 0"],
          [(105, 0, 1), (415, 0, 1)], ("stem", "stem"),
          "Two short posts share a single low valley."),
    Lower(0x10C22, ["M 95 480 C 470 535 490 70 120 30 L 340 -190"],
          [(340, -190, 1)], ("open", "round"),
          "The open R-like bowl fills the body; its exit leg alone descends.", bottom=-190),
    Lower(0x10C23, ["M 90 435 C 125 495 185 510 245 510 C 500 510 500 0 245 0 "
                    "C 185 0 125 15 90 75"],
          [], ("open", "round"), "A genuine small reversed C with inward ends.",
          round_top=True, round_bottom=True),
    Lower(0x10C24, ["M 390 0 L 390 510",
                    "M 390 350 C 390 525 95 525 95 330 L 95 0"],
          [(390, 0, 1), (390, 510, -1), (95, 0, 1)], ("stem", "stem"),
          "A single RTL n: the entry serif and shoulder spring from the right stem."),
    Lower(0x10C26, ["M 100 510 L 100 170 C 100 -16 395 -16 395 170",
                    "M 395 510 L 395 0"],
          [(100, 510, -1), (395, 510, -1), (395, 0, 1)], ("stem", "stem"),
          "Dotless small u has a continued right post and baseline foot."),
    Lower(0x10C28, ["M 105 0 L 105 700",
                    "M 105 510 C 315 510 345 415 250 340 C 215 315 150 300 105 290",
                    "M 105 290 C 465 275 465 85 335 15 C 285 -10 180 0 105 0"],
          [(105, 0, 1), (105, 700, -1)], ("stem", "round"),
          "Two wider body-height bowls open both counters without thinning the ascender.", top=700),
    Lower(0x10C2A, ["M 85 425 C 120 500 185 510 245 510 C 455 510 455 255 205 255 "
                    "C 455 255 455 0 245 0 C 185 0 120 10 85 85"],
          [], ("open", "round"), "A small double bowl with a leftward waist.",
          round_top=True, round_bottom=True),
    Lower(0x10C2D, ["M 295 700 L 295 0", "M 295 265 C 205 285 165 350 100 365"],
          [(295, 0, 1), (295, 700, -1)], ("open", "stem"),
          "One mid-stem branch on an ascender.", top=700),
    Lower(0x10C2F, ["M 350 -190 L 350 340 C 350 475 255 525 105 465"],
          [(350, -190, 1)], ("round", "stem"),
          "A curved mirrored-f head above a descending post; AEK retains its crossbar.", bottom=-190),
    Lower(0x10C30, ["M 105 700 L 105 0",
                    "M 105 480 C 210 500 315 500 350 395 L 350 310",
                    "M 105 210 C 210 235 315 235 350 125 L 350 0"],
          [(105, 0, 1), (105, 700, -1), (350, 0, 1)], ("stem", "stem"),
          "An ascender links two shorter right-hand tiers.", top=700),
    Lower(0x10C31, ["M 85 510 L 85 180 C 85 -20 300 -20 300 180 L 300 510 "
                    "L 300 180 C 300 -20 515 -20 515 180 L 515 510",
                    "M 515 510 L 515 -190"],
          [(85, 510, -1), (300, 510, -1), (515, 510, -1), (515, -190, 1)],
          ("open", "stem"), "Two full-body rounded returns; only the straight right pole descends.",
          bottom=-190),
    Lower(0x10C32, ["M 80 700 C 195 700 220 595 250 520 L 405 0",
                    "M 250 520 L 65 0"],
          [(65, 0, 1), (405, 0, 1)], ("diagonal", "lambda"),
          "Preserve the curved lambda outline and shift it up 190 units; both feet meet the baseline.", top=700),
    Lower(0x10C34, AQ_PATHS, AQ_SERIFS, ("open", "stem"),
          "Reuse the capital AQ at full size, with identical outline and spacing.",
          top=700, stroke_stem=90, stroke_hair=64),
    Lower(0x10C36, ["M 350 510 C 240 510 140 355 90 255 C 140 155 240 0 350 0 "
                    "L 350 510"],
          [(350, 0, 1), (350, 510, -1)], ("diagonal", "stem"),
          "Small triangular open-left body with its pointed side."),
    Lower(0x10C38, sideways_oq_paths("right"), [], ("round", "open"),
          "Keep the pole-right skeleton and 82/59 model; locally taper the wings at the horizontal pole.",
          reliefs=((1, 0, 255, 155, .5),)),
    Lower(0x10C3A, ["M 345 510 L 345 -190",
                    "M 345 265 C 215 265 145 80 100 29.5 C 150 220 155 430 100 495"],
          [(345, 510, -1), (345, -190, 1)], ("open", "stem"),
          "The free return reaches the baseline; keep the approved untapered outline.",
          bottom=-190),
    Lower(0x10C3C, ["M 585 0 L 585 510",
                    "M 585 350 C 585 525 340 525 340 330 L 340 -190",
                    "M 340 350 C 340 525 95 525 95 330 L 95 0"],
          [(585, 0, 1), (585, 510, -1), (340, -190, 1), (95, 0, 1)], ("stem", "stem"),
          "The descending m drawn RTL: entry serif on the right stem, two shoulders and a central descender.",
          bottom=-190),
    Lower(0x10C3D, ["M 95 510 L 95 180 C 95 -20 385 -20 385 180 L 385 510",
                    "M 385 510 L 385 -190"],
          [(95, 510, -1), (385, 510, -1), (385, -190, 1)],
          ("open", "stem"), "One full-body rounded return and a short descending pole; IC has two.",
          bottom=-190),
    Lower(0x10C3E, ["M 130 0 L 130 510"],
          [(130, 0, 1), (130, 510, -1)], ("stem", "stem"),
          "One full-height lowercase minim."),
    Lower(0x10C3F, ["M 230 510 C 25 510 25 0 230 0 C 435 0 435 510 230 510"],
          [], ("round", "round"), "A small oval establishes round counterspace.",
          round_top=True, round_bottom=True),
    Lower(0x10C41, ["M 250 -190 L 250 30 "
                    "C 200 90 125 295 80 480 C 175 520 325 520 420 480 "
                    "C 375 295 300 90 250 30"],
          [(250, -190, 1)], ("diagonal", "diagonal"),
          "The fork and raised link form a closed full-body head; only the central stem descends.",
          bottom=-190),
    Lower(0x10C43, ["M 110 0 L 110 700",
                    "M -15 670.5 L 405 670.5",
                    "M 110 480 C 470 510 470 0 110 30"],
          [(110, 0, 1)], ("stem", "round"),
          "A b-like full-body bowl shares its stem with an ascender; the top arm overhangs left to distinguish it from AY.",
          top=700),
    Lower(0x10C45, ["M 110 0 L 110 700",
                    "M 110 290 C 225 300 285 430 365 430 C 320 300 325 125 390 0"],
          [(110, 0, 1), (110, 700, -1)], ("stem", "open"),
          "Tall left post with a shorter falling free leg.", top=700),
    Lower(0x10C47, ["M 95 0 L 95 230 C 95 380 150 450 265 450 "
                    "C 380 450 435 380 435 230 L 435 0",
                    "M 190 510 C 220 475 240 455 265 450 C 290 455 310 475 340 510"],
          [(95, 0, 1), (435, 0, 1)], ("stem", "stem"),
          "A small inverted u carries two symmetric hat tips."),
    Lower(0x10C48, ["M 300 255 C -4 345 60 480 300 480 "
                    "C 540 480 604 345 300 255 C 28 175 -12 30 300 30 "
                    "C 612 30 572 175 300 255"],
          [], ("round", "round"),
          "A continuous figure-eight route places the two counters above and below a narrow crossing."),
]
