"""Structural and shaping checks, not a reader study or historical validation."""

import io
import unicodedata

import numpy as np
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon

from build import (
    FONT_VERSION,
    HAIRLINE,
    HEIGHT,
    LETTERS,
    OVERSHOOT,
    ROOT,
    SIDES,
    Letter,
    fitted,
    geometry,
    stroke,
)
from ductus import ROUTES, STIFFNESS, resample, trajectories
from lowercase import LOWER, Lower, sideways_oq_paths
from specimen import EXAMPLES, NEW, direction_test
from specimen import font as raster_font

LOWER_FONT = ROOT / "NewOrkhonTextLowercase-Regular.ttf"


def check_outline(font, name, shape, advance, low, high):
    glyph = font["glyf"][name]
    glyph.recalcBounds(font["glyf"])
    x0, y0, x1, y1 = shape.bounds
    assert shape.is_valid and not shape.is_empty, name
    assert abs(y0 - low) < .001 and abs(y1 - high) < .001, (name, shape.bounds)
    assert 0 <= glyph.xMin < glyph.xMax <= advance, name
    assert abs(glyph.yMin - low) <= 1 and abs(glyph.yMax - high) <= 1, name
    coords, ends, _ = glyph.getCoordinates(font["glyf"])
    start = 0
    for end in ends:
        ring = Polygon(coords[start:end + 1])
        assert ring.is_valid and ring.area > 0, (name, start)
        start = end + 1
    return bytes(glyph.compile(font["glyf"]))


def raster_checks(path, codes):
    for size in (20, 24, 32, 48):
        seen = set()
        for code in codes:
            image = Image.new("L", (128, 128), 255)
            ImageDraw.Draw(image).text((8, 80), chr(code), font=raster_font(path, size),
                                      direction="rtl", anchor="ls", fill=0)
            ink = image.point(lambda value: 255 if value < 128 else 0)
            bounds = ink.getbbox()
            assert bounds is not None, (path.name, size, hex(code), "empty")
            crop = ink.crop(bounds)
            signature = (crop.size, crop.tobytes())
            assert signature not in seen, (path.name, size, hex(code), "duplicate")
            seen.add(signature)


def feature_mapping(font, tag):
    features = font["GSUB"].table.FeatureList.FeatureRecord
    item = next(record.Feature for record in features if record.FeatureTag == tag)
    result = {}
    for index in item.LookupListIndex:
        lookup = font["GSUB"].table.LookupList.Lookup[index]
        assert lookup.LookupType == 1
        for subtable in lookup.SubTable:
            result.update(subtable.mapping)
    return result


def validate():
    upper = TTFont(NEW, checkChecksums=2)
    lower_font = TTFont(LOWER_FONT, checkChecksums=2)
    expected = {code for code in range(0x10C00, 0x10C50)
                if "ORKHON" in unicodedata.name(chr(code), "")}
    codes = {letter.code for letter in LETTERS}
    forms: list[Letter | Lower] = [*LETTERS, *LOWER]
    for form in forms:
        for index, x, y, radius, minimum in form.reliefs:
            assert 0 <= index < len(form.paths) and radius > 0 and 0 < minimum <= 1
            stem, hair = getattr(form, "stroke_stem", 90), getattr(form, "stroke_hair", 64)
            profile_path = form.paths[index]
            regular = stroke(profile_path, stem, hair)
            tapered = stroke(profile_path, stem, hair, [(x, y, radius, minimum)])
            assert tapered.is_valid and tapered.difference(regular).area < 1e-6
    assert codes == expected == {letter.code for letter in LOWER}
    assert len(codes) == len(LOWER) == len(LETTERS) == 42
    for font in (upper, lower_font):
        assert len(font.getGlyphOrder()) == 89
        assert codes <= font.getBestCmap().keys()
        assert FONT_VERSION in font["name"].getDebugName(5)
        assert abs(font["head"].fontRevision - float(FONT_VERSION)) < .00002
    signatures = set()
    for letter in LETTERS:
        shape, advance = fitted(letter)
        low = -OVERSHOOT if letter.round_bottom else 0
        high = HEIGHT + (OVERSHOOT if letter.round_top else 0)
        name = f"u{letter.code:05X}"
        signature = check_outline(upper, name, shape, advance, low, high)
        assert signature not in signatures, name
        signatures.add(signature)
        assert upper.getBestCmap()[letter.code] == name
        assert abs(shape.bounds[0] - SIDES[letter.sides[0]]) < .001
        assert abs(advance - shape.bounds[2] - SIDES[letter.sides[1]]) <= 1
    lower_signatures = set()
    for small in LOWER:
        shape, advance = fitted(small)
        low = small.bottom - (OVERSHOOT if small.round_bottom else 0)
        high = small.top + (OVERSHOOT if small.round_top else 0)
        name = f"u{small.code:05X}.lc"
        signature = check_outline(upper, name, shape, advance, low, high)
        assert signature not in lower_signatures, name
        lower_signatures.add(signature)
        assert lower_font.getBestCmap()[small.code] == name
    for name in upper.getGlyphOrder():
        assert upper["glyf"][name].compile(upper["glyf"]) == lower_font["glyf"][name].compile(lower_font["glyf"]), name
        assert upper["hmtx"][name] == lower_font["hmtx"][name], name

    shapes = {letter.code: geometry(letter) for letter in LETTERS}
    roof = shapes[0x10C3C]
    assert not roof.intersects(LineString([(280, 650), (280, 730)]))
    assert shapes[0x10C31].contains(Point(250, 650))
    assert not shapes[0x10C20].contains(Point(250, 650))
    assert len(shapes[0x10C41].interiors) == 1
    assert not shapes[0x10C41].contains(Point(270, 550))
    assert len(shapes[0x10C1A].interiors) == 1
    a = shapes[0x10C00]
    assert abs(a.intersection(LineString([(220, 620), (220, 710)])).length - HAIRLINE) < 1
    assert abs(a.intersection(LineString([(350, -10), (350, 80)])).length - HAIRLINE) < 1
    assert a.contains(Point(285, 350))
    aen = shapes[0x10C24]
    assert len(next(letter for letter in LETTERS if letter.code == 0x10C24).paths) == 3
    assert all(aen.contains(Point(x, y)) for x in (80, 450) for y in (50, 650))
    assert len(aen.intersection(LineString([(0, 350), (600, 350)])).geoms) == 3
    ez = shapes[0x10C14]
    assert ez.geom_type == "Polygon" and len(ez.interiors) == 1
    ag = shapes[0x10C0D]
    assert ag.geom_type == "MultiPolygon" and len(ag.geoms) == 3
    ent_letter = next(letter for letter in LETTERS if letter.code == 0x10C26)
    assert not ent_letter.dots and shapes[0x10C26].geom_type == "Polygon"
    assert all(shapes[0x10C26].contains(Point(x, 550)) for x in (110, 490))
    assert not shapes[0x10C26].contains(Point(300, 550))
    assert shapes[0x10C31].contains(Point(475, 100))
    assert not shapes[0x10C31].contains(Point(355, 100))
    assert all(shapes[0x10C31].contains(Point(x, 650)) for x in (90, 255, 475))
    assert not shapes[0x10C31].contains(Point(250, 200))
    assert all(shapes[0x10C3D].contains(Point(x, 650)) for x in (120, 475))
    assert not shapes[0x10C3D].contains(Point(300, 650))
    aeg = shapes[0x10C0F]
    assert aeg.contains(Point(485, 350)) and not aeg.contains(Point(530, 350))
    assert shapes[0x10C22].geom_type == "Polygon" and not shapes[0x10C22].interiors
    ot = shapes[0x10C47]
    reflected = affinity.scale(ot, xfact=-1, yfact=1, origin=(300, 350))
    assert ot.symmetric_difference(reflected).area / ot.area < .001
    lambda_shape, lambda_advance = fitted(next(letter for letter in LETTERS if letter.code == 0x10C32))
    assert 7 <= lambda_advance - lambda_shape.bounds[2] <= 9
    for code, holes in ((0x10C0B, 1), (0x10C16, 1), (0x10C28, 2), (0x10C36, 1),
                        (0x10C3F, 1), (0x10C43, 1), (0x10C48, 2)):
        shape = shapes[code]
        polys = [shape] if shape.geom_type == "Polygon" else list(shape.geoms)
        assert sum(len(poly.interiors) for poly in polys) == holes, hex(code)
    lower_shapes = {small.code: geometry(small) for small in LOWER}
    small_by_code = {small.code: small for small in LOWER}
    lower_ag = lower_shapes[0x10C0D]
    assert not lower_ag.interiors and lower_ag.bounds[1] == 0
    assert len(small_by_code[0x10C0D].paths) == 3
    assert lower_ag.contains(Point(300, 100)) and lower_ag.contains(Point(300, 400))
    reflected = affinity.scale(lower_ag, xfact=-1, yfact=1, origin=(300, 255))
    assert lower_ag.symmetric_difference(reflected).area / lower_ag.area < .001
    assert lower_shapes[0x10C0F].geom_type == "Polygon"
    assert not lower_shapes[0x10C31].interiors
    assert not lower_shapes[0x10C26].interiors
    assert len(small_by_code[0x10C24].paths) == 2
    assert len(lower_shapes[0x10C24].intersection(LineString([(0, 250), (600, 250)])).geoms) == 2
    oe = small_by_code[0x10C07]
    oe_body = stroke(oe.paths[0].replace("M 130 -190 L 130 510", "M 130 510"),
                     oe.stroke_stem, oe.stroke_hair)
    ar = small_by_code[0x10C3A]
    ar_body = stroke(ar.paths[1], ar.stroke_stem, ar.stroke_hair)
    for body in (oe_body, ar_body):
        assert 0 <= body.bounds[1] < .1, body.bounds
    aq = small_by_code[0x10C34]
    assert aq.top == 700 and aq.bottom == 0
    assert lower_shapes[0x10C34].equals(shapes[0x10C34])
    assert upper["glyf"]["u10C34"].compile(upper["glyf"]) == \
        upper["glyf"]["u10C34.lc"].compile(upper["glyf"])
    assert upper["hmtx"]["u10C34"] == upper["hmtx"]["u10C34.lc"]
    an = lower_shapes[0x10C23]
    assert an.bounds[1] == -10 and an.bounds[3] == 520
    assert abs(an.centroid.y - 255) < .1
    oq_letter = small_by_code[0x10C38]
    oq_shape, oq_advance = fitted(oq_letter)
    assert oq_letter.paths == sideways_oq_paths("right")
    assert oq_letter.serifs == [] and oq_letter.top == 510 and oq_letter.bottom == 0
    assert oq_letter.sides == ("round", "open")
    assert oq_shape.bounds[0:2] == (32, 0) and oq_shape.bounds[3] == 510
    assert abs(oq_shape.bounds[2] - 563) < 2 and abs(oq_advance - 581) <= 1
    assert abs(oq_shape.centroid.y - 255) < .1
    for code in (0x10C03, 0x10C2F, 0x10C1A):
        small = small_by_code[code]
        assert small.top == 510 and small.bottom == -190
        assert " C " in small.paths[0], hex(code)
    mirrored_i = affinity.scale(lower_shapes[0x10C03], xfact=-1, yfact=1, origin=(227.5, 0))
    assert mirrored_i.hausdorff_distance(lower_shapes[0x10C2F]) < .31
    assert len(lower_shapes[0x10C1A].interiors) == 1
    assert len(lower_shapes[0x10C41].interiors) == 1
    assert not lower_shapes[0x10C2F].contains(Point(180, 160))
    for code in (0x10C14, 0x10C11):
        small = small_by_code[code]
        assert small.top == 510 and small.bottom == 0
        assert not small.dots
    assert len(lower_shapes[0x10C14].interiors) == 1
    assert not lower_shapes[0x10C22].interiors
    assert not lower_shapes[0x10C11].interiors
    assert lower_shapes[0x10C11].contains(Point(95, 250))
    assert not lower_shapes[0x10C11].contains(Point(180, 250))
    aer = lower_shapes[0x10C3C]
    assert not aer.interiors
    assert len(aer.intersection(LineString([(0, 250), (700, 250)])).geoms) == 3
    assert aer.contains(Point(340, -100))
    assert not aer.contains(Point(95, -100)) and not aer.contains(Point(585, -100))
    assert aer.bounds[1] == -190
    lower_al = small_by_code[0x10C1E]
    assert lower_al.top == 510 and lower_al.bottom == -190 and not lower_al.dots
    assert lower_shapes[0x10C1E].contains(Point(200, -160))
    assert not lower_shapes[0x10C1E].contains(Point(200, 0))
    bodies = {
        0x10C0B: small_by_code[0x10C0B].paths[0],
        0x10C22: small_by_code[0x10C22].paths[0].rsplit(" L ", 1)[0],
        0x10C31: small_by_code[0x10C31].paths[0],
        0x10C3D: small_by_code[0x10C3D].paths[0],
        0x10C41: small_by_code[0x10C41].paths[0].replace("M 250 -190 L 250 30", "M 250 30"),
        0x10C20: small_by_code[0x10C20].paths[1],
        0x10C3C: small_by_code[0x10C3C].paths[2],
    }
    for code, body_path in bodies.items():
        small = small_by_code[code]
        body = stroke(body_path, small.stroke_stem, small.stroke_hair)
        _, y0, _, y1 = body.bounds
        assert -45 <= y0 <= 50 and 470 <= y1 <= 555, (hex(code), body.bounds)
        assert y1 - y0 >= 450, (hex(code), "perched body")
        assert small.top == 510 and small.bottom == -190
    assert all(small.bottom == -190 for small in LOWER if small.bottom < 0)
    assert all(small.top == 510 for small in LOWER if small.bottom < 0)
    targets = {"u10C07.lc", "u10C3A.lc", "u10C1E.lc", "u10C34.lc", "u10C38.lc"}
    current_changes = {
        "u10C1A", "u10C28", "u10C31", "u10C38", "u10C41", "u10C48",
        "u10C0D.lc", "u10C1A.lc", "u10C28.lc", "u10C38.lc", "u10C3A.lc",
        "u10C41.lc", "u10C48.lc",
    }
    for revision, expected_changes in (
        ("08", targets | current_changes), ("09", current_changes),
        ("091", current_changes),
    ):
        previous = TTFont(ROOT / f"archive-v{revision}" / "NewOrkhonText-Regular.ttf")
        changed = set()
        assert previous.getBestCmap() == upper.getBestCmap()
        assert previous.getGlyphOrder() == upper.getGlyphOrder()
        for name in upper.getGlyphOrder():
            before_outline = previous["glyf"][name].compile(previous["glyf"])
            current_outline = upper["glyf"][name].compile(upper["glyf"])
            if before_outline != current_outline or previous["hmtx"][name] != upper["hmtx"][name]:
                changed.add(name)
        assert changed == expected_changes, (revision, changed)
    previous = TTFont(ROOT / "archive-v08" / "NewOrkhonText-Regular.ttf")
    name = "u10C1E.lc"
    old_glyph, new_glyph = previous["glyf"][name], upper["glyf"][name]
    old_coords, old_ends, old_flags = old_glyph.getCoordinates(previous["glyf"])
    new_coords, new_ends, new_flags = new_glyph.getCoordinates(upper["glyf"])
    assert list(old_ends) == list(new_ends) and list(old_flags) == list(new_flags)
    assert all((x - 14, y) == new for (x, y), new in zip(old_coords, new_coords, strict=True))
    assert upper["hmtx"][name] == (previous["hmtx"][name][0] - 14, 18)
    misplaced = TTFont(ROOT / "archive-v07" / "NewOrkhonText-Regular.ttf")
    for code, old_code in ((0x10C14, 0x10C21), (0x10C11, 0x10C1E)):
        name, old_name = f"u{code:05X}.lc", f"u{old_code:05X}.lc"
        assert upper["glyf"][name].compile(upper["glyf"]) == misplaced["glyf"][old_name].compile(misplaced["glyf"])
        assert upper["hmtx"][name] == misplaced["hmtx"][old_name]

    expected_feature = {f"u{code:05X}": f"u{code:05X}.lc" for code in codes}
    assert feature_mapping(upper, "ss01") == expected_feature
    assert feature_mapping(lower_font, "ss02") == {v: k for k, v in expected_feature.items()}
    sample = "".join(chr(code) for code in sorted(codes))
    assert raster_font(NEW, 80).getlength(sample, direction="rtl", features=["ss01"]) == \
        raster_font(LOWER_FONT, 80).getlength(sample, direction="rtl")
    for _, text in EXAMPLES:
        assert set(map(ord, text)) <= upper.getBestCmap().keys()
    for name, routes in ROUTES.items():
        for route, cooked in zip(routes, trajectories(name), strict=True):
            raw = resample(route)
            np.testing.assert_allclose(cooked[[0, -1]], raw[[0, -1]], atol=1e-10)
            raw_jerk = np.square(np.diff(raw, n=3, axis=0)).sum()
            jerk = np.square(np.diff(cooked, n=3, axis=0)).sum()
            fidelity = np.square(cooked - raw).sum()
            assert fidelity + STIFFNESS * jerk <= STIFFNESS * raw_jerk + 1e-6
    for path in (NEW, LOWER_FONT):
        raster_checks(path, codes)
    for font in (upper, lower_font):
        stream = io.BytesIO()
        font.save(stream)
        stream.seek(0)
        reopened = TTFont(stream, checkChecksums=2)
        assert reopened.getBestCmap() == font.getBestCmap()
    direction_test()
    result = (
        "PASS: 42 encoded Orkhon signs, each with uppercase and lowercase; 89 glyphs per font.\n"
        "PASS: valid unique outlines, integer contours, vertical zones and contained advances.\n"
        "PASS: A arms measure 64 units; single-N AEN and merged-cap EZ remain distinct.\n"
        "PASS: three separate uppercase AG pieces; literal body-height ж in lowercase AG.\n"
        "PASS: single-n lowercase AEN; curved descending I/EP/AEK.\n"
        "PASS: EZ has a closed loop and leg; AD has two open returns; AER has m-like shoulders and a central descender.\n"
        "PASS: exactly 13 glyph records differ from 0.9.1; every other outline and advance is byte-identical.\n"
        "PASS: AN is byte-identical to 0.8, including its metrics.\n"
        "PASS: AR/OE body bottoms meet baseline within 0.1 units; stems and descender bounds retained.\n"
        "PASS: AQ lowercase equals its capital, including compiled outline and metrics.\n"
        "PASS: OQ keeps the pole-right skeleton, 0..510 body and symmetric placement; advance changes by at most one unit.\n"
        "PASS: AL outline is translated 14 units left; advance reduced by 14; right spacing unchanged.\n"
        "PASS: AN bounds -10..520 and ink centroid y=255.04 support leaving its placement unchanged.\n"
        "PASS: EM/AEB/AS/IC/ESH and related bodies fill the x-height-to-baseline band.\n"
        "PASS: descending lowercase forms stop at body height and share the -190 descender line.\n"
        "PASS: mirrored AEG bar, dotless ENT, two-bowl ENC and symmetric OT.\n"
        "PASS: one-return AS / two-return IC; straight IC pole; tight lambda spacing.\n"
        "PASS: AEK/ESH each have a closed head; BASH retains two counters in its continuous figure-eight route.\n"
        "PASS: OpenType ss01 selects all 42 lowercase forms; ss02 restores capitals.\n"
        "PASS: both fonts have identical glyph outlines/metrics; different default cmaps.\n"
        "PASS: 42 distinct nonempty raster glyphs per case at 20/24/32/48 px.\n"
        "PASS: toy motion endpoints/objective, font round-trip and logical RTL ordering.\n"
        "Not tested: reader performance, historical/linguistic validity, OTS sanitizer.\n"
    )
    (ROOT / "validation.txt").write_text(result)
    print(result)


if __name__ == "__main__":
    validate()
