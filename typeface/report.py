"""Create a permanent PDF containing the principles, evidence and proofs."""

from html import escape

from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

from build import ROOT, VERSION

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("Body", FONT_DIR + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("Bold", FONT_DIR + "DejaVuSans-Bold.ttf"))
SIZE = (840, 830)
BODY = ParagraphStyle("body", fontName="Body", fontSize=13, leading=19,
                      textColor=HexColor("#202020"))
SMALL = ParagraphStyle("small", parent=BODY, fontSize=11, leading=16)
HEADING = ParagraphStyle("heading", fontName="Bold", fontSize=17, leading=23)


def paragraph(canvas, text, y, style=BODY):
    paragraph = Paragraph(text, style)
    _, height = paragraph.wrap(740, 750)
    paragraph.drawOn(canvas, 50, y - height)
    return y - height - 11


def title(canvas, heading, subheading):
    canvas.setFillColor(HexColor("#151515"))
    canvas.setFont("Bold", 33)
    canvas.drawString(50, 772, heading)
    return paragraph(canvas, subheading, 739)


def footer(canvas, number):
    canvas.setFillColor(HexColor("#626262"))
    canvas.setFont("Body", 10)
    canvas.drawString(50, 27, f"NEW ORKHON / YENİ ORHUN · {VERSION} · experimental")
    canvas.drawRightString(790, 27, str(number))


def build_report():
    output = ROOT / "New-Orkhon-Design-and-Specimens.pdf"
    canvas = Canvas(str(output), pagesize=SIZE)
    canvas.setTitle(f"New Orkhon / Yeni Orhun — principles and revision {VERSION}")
    y = title(canvas, "NEW ORKHON / YENİ ORHUN",
              "A proposed two-case text hand: 42 encoded signs, 84 forms, existing Unicode, right to left.")
    y = paragraph(canvas, "The names below are design inferences from historical examples, "
                  "not universal laws or a claim that Orkhon would inevitably evolve this way.", y)
    tenets = [
        ("1. Ductus over contour", ("Greek minuscule and Latin uncial suggest rebuilding writing motion, "
         "not rounding an old outline. Here: an explicit EM pen-route study, bowls and shoulders.")),
        ("2. A shared vertical system", ("Historical scripts reorganized their vertical zones. "
         "Here: capitals 700, lowercase body 510, baseline 0 and descenders -190.")),
        ("3. Reconstruction over tracing", ("Humanist revival and Greek minuscule show that construction can change. "
         "Here: k opens into an arm; EM is resegmented into an open bowl and leg.")),
        ("4. Family grammar over isolated inventions", ("Standardization works across a script. "
         "Here: shared shoulders, fork branches, bowls, stems, contrast and bracketed serifs.")),
        ("5. Distinctness before economy", ("Economy is constrained by ambiguity. "
         "Here: preserve the ny waist, both r roofs, trident prongs and crossbar. ENT's dots are deliberately removed.")),
        ("6. Optical rhythm over equal boxes", ("Counterspace and inter-letter space must balance. "
         "Here: related counters, different side spaces for straight/round/open edges, and small overshoots.")),
        ("7. Separate typeface and alphabet reform", ("Civil type changed both, but they are separate choices. "
         "Here: redesign forms without silently changing the inventory or Turkish spelling rules.")),
    ]
    for heading, text in tenets:
        y = paragraph(canvas, heading, y, HEADING)
        y = paragraph(canvas, text, y)
    assert y > 42, y
    footer(canvas, 1)
    canvas.showPage()

    y = title(canvas, "EVIDENCE & LIMITS", "History informs the proposal; proofing tests the drawings.")
    sources = [
        ("University of Zurich / Ad fontes",
         ("Uncial, half-uncial, Caroline and humanist scripts. Rounding is not a one-way law: Gothic "
          "became more angular; humanists deliberately revived earlier writing."),
         "https://www.adfontes.uzh.ch/en/tutorium/schriften-lesen/schriftgeschichte/humanistische-minuskel-und-kursive/"),
        ("Vatican Library / Timothy Janz",
         ("Greek minuscule: informal-writing origins, four-line organization, shared/omitted strokes "
          "in ligatures, and deliberate disambiguation."),
         "https://spotlight.vatlib.it/en/greek-paleography/feature/2-introduction-to-minuscule-bookhands"),
        ("Presidential Library / Cyrillic civil reform",
         "Deliberate type redesign alongside inventory reform, 1708–1710; an example of planned change.",
         "https://www.prlib.ru/en/history/619018"),
        ("Fernando Mello / How to space a typeface",
         ("Practical synthesis of Tracy, Smeijers and Kindersley: balance inner and outer white, "
          "use upright/round controls, judge the result optically."),
         "https://www.myfonts.com/a/font/content/how-to-space-a-typeface"),
        ("Anton Koovit / U8",
         ("Turning inconsistent historical lettering into a text face; testing stroke weight "
          "at the intended physical size."),
         "https://www.antonkoovit.com/typefaces/u8"),
        ("Flash & Hogan / The coordination of arm movements, 1985",
         ("Minimum squared jerk as a model of smooth arm motion. Our toy model regularizes supplied "
          "routes; it does not reproduce their experiment or infer script evolution."),
         "https://www.jneurosci.org/content/5/7/1688"),
    ]
    for heading, text, url in sources:
        linked = f'<a href="{escape(url, quote=True)}" color="#151515"><u>{escape(heading)}</u></a>'
        y = paragraph(canvas, linked, y, HEADING)
        y = paragraph(canvas, text, y, SMALL)
    y = paragraph(canvas, "Checks and limits", y, HEADING)
    y = paragraph(canvas, "Font loading, 42-sign coverage, shared bounds, contained advances, "
                  "non-protruding roof join, prongs, dots, counters and actual RTL raster order pass. "
                  "Gray reference forms are Noto Sans Old Turkic—not inscription facsimiles. "
                  "Turkish examples are illustrative transliterations, not historical spelling. "
                  "No reader study, production hinting or kerning is claimed.", y, SMALL)
    y = paragraph(canvas, "Further sources, all glyph decisions, license, reproducible source "
                  "and validation details are in the accompanying source package.", y, SMALL)
    assert y > 42, y
    footer(canvas, 2)
    canvas.showPage()

    y = title(canvas, "WEIGHT AND CASE", "One text master, paired forms, unchanged Unicode.")
    for heading, text in [
        ("Contrast is optical, not equality",
         "FontForge's Trusting Your Eyes explains why equal-width horizontals and verticals look unequal, "
         "and why diagonal thickness also needs correction. The new thin stroke is 64 against 90-unit stems, "
         "rather than 46. A's horizontal arms are repositioned so they retain that weight at the cap and baseline. "
         "Shared serif lips increase from 14 to 20 units; A gains paired bracketed serifs."),
        ("Fit the intended size",
         "Ahrens and Mugikura describe reduced contrast and other compensations for small optical sizes. "
         "The 20–130 px raster proof is a design check, not a reading study or a claim of separate optical masters. "
         "EC's projecting lambda foot now has 8 units of right side space rather than 26."),
        ("Lowercase without a new encoding",
         "Old Turkic has no encoded Unicode case pairs. The 42 authored lowercase forms use x-height 510, "
         "ascenders 700 and descenders to -190. The main font selects them with stylistic set ss01. "
         "The supplied lowercase-default font needs no feature controls; ss02 restores capitals there. "
         "Copy/paste preserves the same logical right-to-left Unicode string."),
        ("AG and the remaining uncertainty",
         "Uppercase AG retains three separated pieces. Its lowercase is now literally ж, replacing the rejected "
         "alpha ribbon. The R-like EM remains a strong simplification: the comparison explicitly shows its lost "
         "crossings and the crowded closer alternatives. Neither choice is a reconstruction of historical handwriting."),
    ]:
        y = paragraph(canvas, heading, y, HEADING)
        y = paragraph(canvas, text, y)
    y = paragraph(canvas, '<a href="https://designwithfontforge.com/en-US/Trusting_Your_Eyes.html">'
                  '<u>FontForge: Trusting Your Eyes</u></a> · '
                  '<a href="https://justanotherfoundry.com/size-specific-adjustments-to-type-designs">'
                  '<u>Ahrens / Mugikura: Size-specific adjustments</u></a>', y, SMALL)
    assert y > 42, y
    footer(canvas, 3)
    canvas.showPage()
    y = title(canvas, "0.12 / SPACING AND TOP JOINS", "Contextual fitting, without changing the text or standalone forms.")
    for heading, text in [
        ("Fit around the dotless-j AL",
         "A letter on AL's visual left may tuck over its hook if its right descender zone is empty. "
         "Seventy-two capital/lowercase pairs receive measured negative kerning. Right-side descenders "
         "are excluded, and every enabled pair keeps at least 38.5 font units of compiled-outline clearance. "
         "The standalone advances do not change."),
        ("A continuous EM–I top",
         "Matching-case EM followed by I uses a standard ligature with a shared top route. "
         "The contextual I terminal is reshaped rather than overlapped. Mixed case heights and spaces "
         "remain separate. GDEF provides a component caret; the two logical characters stay copyable."),
        ("Scope and controls",
         "All 84 standalone forms and five utility glyphs exactly match 0.11. Two unencoded ligature "
         "glyphs and the kern/liga layout tables are added. ss01 and ss02 also select the matching "
         "ligature case. The showcase's Spacing and joins control switches both features on or off."),
        ("Verification",
         "Native HarfBuzz positions, compiled contour clearance, reversed pairs, rejected tails, case "
         "switches and 20/24/32/48 px text lengths are checked. An OpenType shaping client is required "
         "for the features. Geometric checks are not evidence of reader performance."),
    ]:
        y = paragraph(canvas, heading, y, HEADING)
        y = paragraph(canvas, text, y)
    assert y > 42, y
    footer(canvas, "3a")
    canvas.showPage()
    y = title(canvas, "0.11 / ASYMMETRIC AT", "Development history: AR restored and the tuta letter reconstructed.")
    for heading, text in [
        ("Correct letter, no transliteration change",
         "Both t signs in historical tuta are AT, U+10C43. AET, U+10C45, is unchanged. "
         "All underlying Unicode strings remain logical RTL. This is an outline change, not an alphabet reform."),
        ("Reconstruct the writing route",
         "The centred roof and suspended eye still read as an inscriptional emblem. Move the eye to the right "
         "of an upright, open it into one broad bowl, and level the roof into an arm. The lowercase becomes "
         "b-like: body to x-height, stem to ascender height. The capital has a larger bowl. "
         "The horizontal arm is selected; the slanted-arm study remains visible in the proof. "
         "Its left overhang distinguishes AT from AY's b-like form: their mean raster overlap "
         "falls from 88.7% in the first trial to 75.8% in the selected outline."),
        ("AR rollback and exact scope",
         "Remove only AR's 0.10 taper, restoring its exact 0.9.1 outline and advance. Its baseline correction "
         "remains. Exactly three records change from 0.10: capital AT, lowercase AT and lowercase AR. "
         "Every other compiled outline and advance is byte-identical."),
        ("What the checks mean",
         "Structural, case-selection, RTL and native-size checks screen for errors. The geometric audit "
         "still does not establish historical authenticity or reader performance. The next pages record "
         "development history, followed by proofs of the current typeface."),
    ]:
        y = paragraph(canvas, heading, y, HEADING)
        y = paragraph(canvas, text, y)
    assert y > 42, y
    footer(canvas, "3b")
    canvas.showPage()
    y = title(canvas, "0.10 / DISTINCTNESS AND COLOR", "Development history: closed heads, counters and local stroke relief.")
    for heading, text in [
        ("Construction, not a heavier identifying bar",
         "AEK closes its upper arms into a bowl while EP stays open. ESH raises the link to close its fork "
         "while AEL stays an open Y. BASH becomes two continuous loops, retaining both counters. "
         "ENC gains wider, unequal bowls; an equal-bowl trial was rejected because it resembled OP."),
        ("Measured change",
         "Capital BASH coverage falls 52.9% to 40.3%; lowercase 51.5% to 43.1%. "
         "AEK/EP mean raster Dice falls 92.5% to 79.1% in capitals and 92.2% to 28.7% in lowercase. "
         "AEL/ESH falls 92.2% to 83.9% and 90.2% to 73.2%. Dice is not a confusion probability."),
        ("Local weight and protected decisions",
         "Incoming strokes taper around dense joins in lowercase AG/AR/OQ and capital IC/OQ. "
         "The ordinary 90/64 and 82/59 models are unchanged elsewhere. OE is untouched, AQ remains "
         "identical across cases, AN stays aligned, and the earlier placements are preserved. "
         "Exactly 13 records change from 0.9.1; the other 71 outlines and advances are byte-identical."),
        ("Still unresolved",
         "Capital AEN/ELT and OEK/OP remain close. Capital OQ/AES overlap rises 75.1% to 79.1% "
         "as its dense join loses ink. OE remains the darkest lowercase. No reader study has been conducted. "
         "The following pages record development history and current specimen proofs."),
    ]:
        y = paragraph(canvas, heading, y, HEADING)
        y = paragraph(canvas, text, y)
    assert y > 42, y
    footer(canvas, "3c")
    canvas.showPage()
    y = title(canvas, "0.9.1 / POLE-RIGHT OQ", "Development history: the user-selected sideways lowercase.")
    for heading, text in [
        ("A sideways letter, not a rotated font",
         "The user selected study B, whose pole projects right. The 0.9 skeleton was turned 90 degrees, "
         "its width adjusted to the family, its body refitted to 0..510 and its curves re-stroked "
         "at 82/59 units of upright contrast. Rotated serif slabs were not retained."),
        ("Fit and scope",
         "The new advance is 581 and the vertical ink centre is y=255.02. The previously low wings "
         "now occupy the full body; there is no descender. The capital and the other lowercase forms "
         "have exactly the same compiled outlines and metrics as in 0.9. Study B's glyph and metrics "
         "are identical to the released lowercase OQ."),
        ("Readability remains open",
         "The side-by-side proof compares both orientations and the original in the same historical "
         "word at 24/32/48 px. All 42 lowercase forms retain distinct rasters at 20/24/32/48 px. "
         "Distinct rasters do not demonstrate reading performance or historical validity."),
    ]:
        y = paragraph(canvas, heading, y, HEADING)
        y = paragraph(canvas, text, y)
    assert y > 42, y
    footer(canvas, 4)
    canvas.showPage()
    y = title(canvas, "0.9 / MEASURED CORRECTIONS", "Development history: body position, AL spacing and unicasal AQ.")
    for heading, text in [
        ("AR and OE: body to baseline",
         "AR's upper return stopped 55.55 units above baseline; OE's stopped 128.04 above. "
         "Their returns now reach baseline within 0.1 units before contour rounding. "
         "The posts and -190 descender bounds stay in place. OE retains its construction and 90/64 stroke model, "
         "but the deepened return supersedes the older exact-translation constraint."),
        ("AL and AQ",
         "AL's left sidebearing tightens from 32 to 18 units, with advance 447 to 433. "
         "The actual letter is unchanged, translated 14 units left; right spacing is retained. "
         "Lowercase AQ now uses exactly the uppercase outline and metrics at full 700-unit height."),
        ("AN: measured, not moved",
         "AN has bounds -10 to 520, the same round overshoot as ASH and ENY. "
         "Its vertical ink centroid is 255.04 against a body centre of 255. "
         "It therefore has no measured upward placement error in the font or the common-baseline proof."),
        ("OQ: diagnosis and plan, not a new form",
         "Its wings start at 185 and meet at -190, leaving the upper 325 body units as an isolated pole. "
         "This created a bottom-heavy anchor silhouette. The user's sideways proposal was studied in both "
         "orientations: rotate the skeleton, refit the 0..510 body and restore upright 82/59 contrast. "
         "Candidate A's left-projecting pole was the initial recommendation over B. "
         "Both passed distinct-raster checks at 20/24/32/48 px, not a reading study. "
         "OQ remained unchanged in 0.9; the user then selected B for 0.9.1."),
        ("Exact scope",
         "Only the lowercase AR/OE/AQ outlines and AL's left spacing change from 0.8. "
         "Every capital and all other lowercase records remain byte-identical. "
         "These checks do not establish reader performance or historical validity."),
    ]:
        y = paragraph(canvas, heading, y, HEADING)
        y = paragraph(canvas, text, y)
    assert y > 42, y
    footer(canvas, 5)
    canvas.showPage()
    y = title(canvas, "0.8 / EZ, AD AND AER", "Development history: corrected lowercase sketch placements.")
    for heading, text in [
        ("EZ / U+10C14: loop and leg",
         "The rounded cup and lower return become a closed tilted loop, a short lower upright and a falling leg. "
         "This uses the first sketch option, not the crossed alternative. Its closed eye distinguishes it "
         "from EM's open bowl. The whole form stays between x-height 510 and baseline 0."),
        ("AD / U+10C11: shared stem, two open returns",
         "The right-hand sketch option replaces two separate serpentine strokes: a left upright and top arm feed two "
         "rounded returns. They remain open to the stem below the top arm, unlike ENC's two enclosed "
         "bowls on an ascender. AD has no descender."),
        ("AER / U+10C3C: m-like shoulders and a central descender",
         "Two full-body rounded shoulders replace the narrow hanging roofs. The central pole still "
         "descends to -190; the outer legs stop at the baseline. The shoulder construction follows "
         "AEN's n, but AER has two shoulders and a descender."),
        ("Scope and proof",
         "Only these three lowercase outlines and their advances change from 0.6. Every capital and all other "
         "lowercase signs are unchanged. ELT, AL and OT are restored exactly to their 0.6 outlines and "
         "metrics, reversing the misplaced 0.7 changes. Automatic comparisons check both archived fonts. The before/after sheet "
         "uses equal em sizes and common guidelines, with a red-old/blue-new outline overlay. "
         "Alphabet cells now enclose their own labels and code points to avoid ambiguous crops."),
        ("Previous body corrections retained",
         "The 0.6 single N/n, literal lowercase ж, curved descending I/EP/AEK and full EM/AEB/AS/IC/ESH bodies "
         "remain. In 0.8, OE was the capital outline translated down exactly 190 units; "
         "0.9 supersedes that constraint by deepening its return. "
         "These are speculative type-design choices; structural checks are not a reader study."),
    ]:
        y = paragraph(canvas, heading, y, HEADING)
        y = paragraph(canvas, text, y)
    assert y > 42, y
    footer(canvas, 6)
    canvas.showPage()
    for name in ("analysis/sans-alphabet-capitals.png", "analysis/sans-alphabet-lowercase.png",
                 "analysis/rtl-oe-before-after.png", "analysis/curved-heads-before-after.png",
                 "analysis/ad-enc-study.png", "analysis/ec-before-after.png",
                 "analysis/spacing-before-after.png", "analysis/em-i-top-join.png",
                 "analysis/ar-at-before-after.png",
                 "analysis/differentiation-before-after.png", "analysis/local-weight-before-after.png",
                 "feedback-diffs.png", "alignment-analysis.png", "oq-sideways-study.png", "sketch-diffs.png",
                 "lowercase-revisions-1.png", "lowercase-revisions-2.png",
                 "lowercase-revisions-3.png", "lowercase-revisions-4.png", "lowercase-size-proof.png",
                 "uppercase-revisions-1.png", "uppercase-revisions-2.png", "uppercase-revisions-3.png",
                 "weight-audit.png", "lowercase-alphabet.png", "lowercase-ag-options.png", "case-text.png",
                 "em-closer-options.png", "design-decisions.png", "alphabet-comparison.png",
                 "text-specimen.png", "spacing-proof.png"):
        with Image.open(ROOT / name) as image:
            w, h = image.size
        scale = min(SIZE[0] / w, SIZE[1] / h)
        width, height = w * scale, h * scale
        canvas.drawImage(str(ROOT / name), (SIZE[0] - width) / 2,
                         (SIZE[1] - height) / 2, width=width, height=height)
        canvas.showPage()
    canvas.save()
    print(output)


if __name__ == "__main__":
    build_report()
