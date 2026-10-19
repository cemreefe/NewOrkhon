"""Authored lowercase counterparts for all 42 Orkhon signs.

The same Unicode signs select these forms via ss01 or a lowercase-default font.
The new height system has x-height 510, ascenders 700 and descenders to -150.
"""

from dataclasses import dataclass


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


LOWER = [
    Lower(0x10C00, ["M 385 430 L 385 490 L 105 490 L 380 20 L 100 20 L 100 80"],
          [(100, 510, -1), (380, 0, 1)], ("diagonal", "diagonal"),
          "Shorter opposed returns form the small mirrored z."),
    Lower(0x10C03, ["M 105 0 L 105 700 L 345 700 L 345 640"],
          [(105, 0, 1)], ("stem", "open"), "The upright ascends above the lowercase body.", top=700),
    Lower(0x10C06, ["M 115 510 C 115 405 175 330 265 255 C 175 180 115 105 115 0"],
          [], ("round", "open"), "One short, flowing cusp."),
    Lower(0x10C07, ["M 105 0 L 105 700 C 205 700 250 355 380 320 L 380 510"],
          [(105, 0, 1), (380, 510, -1)], ("stem", "stem"),
          "A tall left stem and short right post share a shoulder.", top=700),
    Lower(0x10C09, ["M 180 510 C 65 430 135 350 245 290 C 365 190 320 0 185 0 "
                    "C 70 0 65 105 100 180"],
          [], ("round", "round"), "One bowl and its returned head.", round_bottom=True),
    Lower(0x10C0B, ["M 240 510 C 100 460 105 325 240 260 C 375 325 380 460 240 510",
                    "M 240 260 L 115 -150", "M 240 260 L 365 -150"],
          [(115, -150, 1), (365, -150, 1)], ("diagonal", "diagonal"),
          "A small eye holds two genuine descenders.", bottom=-150),
    Lower(0x10C0D, ["M 335 255 C 260 465 75 435 75 255 C 75 75 260 45 335 255 "
                    "C 380 350 405 460 455 510",
                    "M 335 255 L 365 -150"],
          [(365, -150, 1)], ("round", "diagonal"),
          "Alpha-like continuous ribbon above a descending pole; uppercase stays three pieces.",
          bottom=-150),
    Lower(0x10C0F, ["M 430 425 C 350 510 210 510 130 430 C 10 335 20 170 130 75 "
                    "C 210 0 350 0 430 85", "M 425 255 L 70 255"],
          [], ("round", "open"), "Open-right small bow and middle bar, like a mirrored э.",
          round_top=True, round_bottom=True),
    Lower(0x10C11, ["M 95 510 C 235 445 240 320 95 255 C 240 190 235 65 95 0",
                    "M 300 510 C 445 445 445 320 300 255 C 445 190 445 65 300 0"],
          [], ("open", "round"), "Two matched short serpentine strokes."),
    Lower(0x10C13, ["M 105 510 L 380 0", "M 380 510 L 105 0"],
          [(105, 0, 1), (380, 0, 1)], ("diagonal", "diagonal"),
          "Small opposing diagonals share a crossing."),
    Lower(0x10C14, ["M 170 510 L 370 0",
                    "M 170 510 C 205 390 275 335 340 335 C 435 335 475 410 485 510 "
                    "L 485 260 C 460 210 390 195 270 255",
                    "M 80 0 L 80 135 C 80 235 170 320 270 255"],
          [(80, 0, 1), (170, 510, -1), (370, 0, 1), (485, 510, -1)],
          ("stem", "stem"), "A small rounded upper cup and a shorter left return."),
    Lower(0x10C16, ["M 100 0 L 100 700 L 100 495 C 455 495 455 0 100 0"],
          [(100, 0, 1), (100, 700, -1)], ("stem", "round"),
          "A tall post with one lower bowl.", top=700),
    Lower(0x10C18, ["M 100 335 C 65 535 380 555 390 345 C 385 240 260 240 260 80 L 260 -150"],
          [(260, -150, 1)], ("round", "round"),
          "Small open head and attached descender.", bottom=-150, round_top=True),
    Lower(0x10C1A, ["M 350 0 L 350 700 L 105 700 L 105 640",
                    "M 350 315 L 105 315"],
          [(350, 0, 1)], ("open", "stem"), "One ascender, two left arms.", top=700),
    Lower(0x10C1C, ["M 105 0 L 105 700 L 360 700 L 360 640",
                    "M 105 300 C 230 350 335 325 335 200 L 335 0"],
          [(105, 0, 1), (335, 0, 1)], ("stem", "open"),
          "Ascender cap arm above a smaller returned lower tier.", top=700),
    Lower(0x10C1E, ["M 350 700 L 350 30 L 105 30 L 105 100"],
          [(350, 700, -1)], ("open", "stem"),
          "Tall upright with a reduced bottom return.", top=700),
    Lower(0x10C20, ["M 90 510 L 245 245 L 245 -150", "M 400 510 L 245 245"],
          [(90, 510, -1), (400, 510, -1), (245, -150, 1)],
          ("diagonal", "diagonal"), "The Y fork gains a real descending tail.", bottom=-150),
    Lower(0x10C21, ["M 105 0 L 105 510 C 190 510 215 300 260 300 "
                    "C 305 300 330 510 415 510 L 415 0"],
          [(105, 0, 1), (415, 0, 1)], ("stem", "stem"),
          "Two short posts share a single low valley."),
    Lower(0x10C22, ["M 95 490 C 350 525 445 445 400 345 C 365 265 255 270 120 255 "
                    "L 390 -150"],
          [(390, -150, 1)], ("open", "round"),
          "Small R-like bowl and one descending exit leg.", bottom=-150),
    Lower(0x10C23, ["M 90 435 C 125 495 185 510 245 510 C 500 510 500 0 245 0 "
                    "C 185 0 125 15 90 75"],
          [], ("open", "round"), "A genuine small reversed C with inward ends.",
          round_top=True, round_bottom=True),
    Lower(0x10C24, ["M 95 0 L 95 510",
                    "M 95 360 C 95 555 290 555 290 340 L 290 0",
                    "M 290 0 L 290 510",
                    "M 290 360 C 290 555 485 555 485 340 L 485 0"],
          [(95, 0, 1), (95, 510, -1), (290, 0, 1), (290, 510, -1),
           (485, 0, 1)], ("stem", "stem"),
          "Two true small n shoulders share the middle upright, rather than scaled capitals."),
    Lower(0x10C26, ["M 100 510 L 100 170 C 100 -16 395 -16 395 170",
                    "M 395 510 L 395 0"],
          [(100, 510, -1), (395, 510, -1), (395, 0, 1)], ("stem", "stem"),
          "Dotless small u has a continued right post and baseline foot."),
    Lower(0x10C28, ["M 105 0 L 105 700",
                    "M 105 510 C 305 510 340 385 240 300 C 205 275 150 265 105 255",
                    "M 105 255 C 335 240 340 75 240 15 C 195 -10 145 0 105 0"],
          [(105, 0, 1), (105, 700, -1)], ("stem", "round"),
          "Two small bowls hang on an ascender; not an ENY 3.", top=700),
    Lower(0x10C2A, ["M 85 425 C 120 500 185 510 245 510 C 455 510 455 255 205 255 "
                    "C 455 255 455 0 245 0 C 185 0 120 10 85 85"],
          [], ("open", "round"), "A small double bowl with a leftward waist.",
          round_top=True, round_bottom=True),
    Lower(0x10C2D, ["M 295 700 L 295 0", "M 295 265 C 205 285 165 350 100 365"],
          [(295, 0, 1), (295, 700, -1)], ("open", "stem"),
          "One mid-stem branch on an ascender.", top=700),
    Lower(0x10C2F, ["M 350 0 L 350 700 L 105 700 L 105 640"],
          [(350, 0, 1)], ("open", "stem"), "Single mirrored cap return with ascender.", top=700),
    Lower(0x10C30, ["M 105 700 L 105 0",
                    "M 105 480 C 210 500 315 500 350 395 L 350 310",
                    "M 105 210 C 210 235 315 235 350 125 L 350 0"],
          [(105, 0, 1), (105, 700, -1), (350, 0, 1)], ("stem", "stem"),
          "An ascender links two shorter right-hand tiers.", top=700),
    Lower(0x10C31, ["M 85 510 L 85 390 C 85 295 270 295 270 390 L 270 510 "
                    "L 270 390 C 270 295 455 295 455 390 L 455 510",
                    "M 455 510 L 455 -150"],
          [(85, 510, -1), (270, 510, -1), (455, 510, -1), (455, -150, 1)],
          ("open", "stem"), "Three smaller tips and two rounded returns lead to a descender.",
          bottom=-150),
    Lower(0x10C32, ["M 80 510 C 195 510 220 405 250 330 L 405 -150",
                    "M 250 330 L 65 -150"],
          [(65, -150, 1), (405, -150, 1)], ("diagonal", "lambda"),
          "An offset head starts the small lambda; both legs descend.", bottom=-150),
    Lower(0x10C34, ["M 340 700 L 340 -150",
                    "M 340 300 C 215 340 140 385 100 385 C 150 235 140 90 100 0"],
          [(340, 700, -1), (340, -150, 1)], ("open", "stem"),
          "A tall q-post and separately curling left free leg.", top=700, bottom=-150),
    Lower(0x10C36, ["M 350 510 C 240 510 140 355 90 255 C 140 155 240 0 350 0 "
                    "L 350 510"],
          [(350, 0, 1), (350, 510, -1)], ("diagonal", "stem"),
          "Small triangular open-left body with its pointed side."),
    Lower(0x10C38, ["M 255 700 L 255 -150",
                    "M 70 185 C 175 185 230 75 255 -150 C 280 75 335 185 440 185"],
          [(255, 700, -1), (255, -150, 1)], ("open", "open"),
          "Two low wings share a descending center pole.", top=700, bottom=-150),
    Lower(0x10C3A, ["M 345 700 L 345 -150",
                    "M 345 265 C 215 265 145 135 100 85 C 150 250 155 430 100 495"],
          [(345, 700, -1), (345, -150, 1)], ("open", "stem"),
          "The related r-post keeps its free leg rising.", top=700, bottom=-150),
    Lower(0x10C3C, ["M 260 -150 L 260 365",
                    "M 75 375 C 110 375 115 510 165 510 C 215 510 225 375 260 365 "
                    "C 295 375 305 510 355 510 C 405 510 410 375 445 375"],
          [(260, -150, 1)], ("open", "open"),
          "Two small equal roofs meet the descending pole at the valley.", bottom=-150),
    Lower(0x10C3D, ["M 95 510 L 95 385 C 95 280 385 280 385 385 L 385 510",
                    "M 385 510 L 385 -150"],
          [(95, 510, -1), (385, 510, -1), (385, -150, 1)],
          ("open", "stem"), "One small return and long leg; the next sign has two returns.",
          bottom=-150),
    Lower(0x10C3E, ["M 130 0 L 130 510"],
          [(130, 0, 1), (130, 510, -1)], ("stem", "stem"),
          "One full-height lowercase minim."),
    Lower(0x10C3F, ["M 230 510 C 25 510 25 0 230 0 C 435 0 435 510 230 510"],
          [], ("round", "round"), "A small oval establishes round counterspace.",
          round_top=True, round_bottom=True),
    Lower(0x10C41, ["M 90 510 L 240 245 L 240 -150", "M 390 510 L 240 245",
                    "M 90 100 L 390 100"],
          [(90, 510, -1), (390, 510, -1), (240, -150, 1)], ("diagonal", "diagonal"),
          "The crossed fork retains two tips and a crossbar across its descender.",
          bottom=-150),
    Lower(0x10C43, ["M 90 600 L 255 700 L 420 600",
                    "M 255 700 L 255 365",
                    "M 255 365 C 170 345 115 245 105 155 C 145 45 195 0 255 0 "
                    "C 315 0 365 45 405 155 C 395 245 340 345 255 365"],
          [], ("diagonal", "diagonal"), "Tall roof and smaller suspended eye.",
          top=700, round_bottom=True),
    Lower(0x10C45, ["M 110 0 L 110 700",
                    "M 110 290 C 225 300 285 430 365 430 C 320 300 325 125 390 0"],
          [(110, 0, 1), (110, 700, -1)], ("stem", "open"),
          "Tall left post with a shorter falling free leg.", top=700),
    Lower(0x10C47, ["M 95 0 L 95 230 C 95 380 150 450 265 450 "
                    "C 380 450 435 380 435 230 L 435 0",
                    "M 190 510 C 220 475 240 455 265 450 C 290 455 310 475 340 510"],
          [(95, 0, 1), (435, 0, 1)], ("stem", "stem"),
          "A small inverted u carries two symmetric hat tips."),
    Lower(0x10C48, ["M 100 0 L 100 510 C 225 440 325 75 450 0 L 450 510 "
                    "C 325 440 225 75 100 0"],
          [(100, 0, 1), (100, 510, -1), (450, 0, 1), (450, 510, -1)],
          ("stem", "stem"), "Small woven diagonals retain both counters."),
]


ZH_AG = [
    "M 95 510 C 265 485 120 310 315 255 C 430 330 325 450 480 510",
    "M 315 255 L 345 -150",
    "M 95 0 C 195 65 210 155 315 255 C 400 125 420 40 500 0",
]
