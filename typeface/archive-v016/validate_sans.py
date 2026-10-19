"""Independent coverage, shaping, spacing and outline checks for the Sans family."""

import json
import unicodedata

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw
from shapely.geometry import box

from build import (
    EM_I_LIGATURES,
    FONT_VERSION,
    LETTERS,
    ROOT,
    VERSION,
    al_kerning,
    constructed,
    fitted,
    ink_strokes,
)
from glyph_similarity import outline
from lowercase import LOWER
from sans import SANS_SIDES, sans_forms
from shaping_revision import placed_outlines, shaped
from specimen import font
from validate import feature_mapping

UPPER = ROOT / "NewOrkhonSans-Regular.ttf"
SMALL = ROOT / "NewOrkhonSansLowercase-Regular.ttf"


def uniqueness(path, codes):
    for size in (20, 24, 32, 48):
        face = font(path, size)
        signatures = set()
        for code in codes:
            image = Image.new("L", (104, 86))
            ImageDraw.Draw(image).text(
                (68, 62), chr(code), fill=255, font=face, direction="rtl", anchor="rs",
            )
            assert image.getbbox(), (hex(code), size)
            signature = image.tobytes()
            assert signature not in signatures, (hex(code), size, path.name)
            signatures.add(signature)


def checks():
    capital, lower = sans_forms(LETTERS, LOWER)
    assert all(not item.serifs for item in [*capital, *lower])
    assert all(item.ink_zone for item in [*capital, *lower])
    codes = {item.code for item in capital}
    assert codes == {item.code for item in lower}
    assert len(codes) == 42
    assert all("ORKHON" in unicodedata.name(chr(code)) for code in codes)
    a, b = TTFont(UPPER, checkChecksums=2), TTFont(SMALL, checkChecksums=2)
    assert a.getGlyphOrder() == b.getGlyphOrder() and len(a.getGlyphOrder()) == 91
    for tt in (a, b):
        assert set(tt.getBestCmap()) == {32, 44, 46, 0x205A, *codes}
        assert FONT_VERSION in tt["name"].getDebugName(5)
        assert all(tt["glyf"][name].numberOfContours > 0 for name in tt.getGlyphOrder()
                   if name != "space")
        assert all(outline(tt, name).is_valid for name in tt.getGlyphOrder() if name != "space")
    for name in a.getGlyphOrder():
        assert a["glyf"][name].compile(a["glyf"]) == b["glyf"][name].compile(b["glyf"])
        assert a["hmtx"][name] == b["hmtx"][name]
    assert feature_mapping(a, "ss01") == {
        **{f"u{code:05X}": f"u{code:05X}.lc" for code in codes},
        EM_I_LIGATURES[0]: EM_I_LIGATURES[1],
    }
    assert feature_mapping(b, "ss02") == {
        **{f"u{code:05X}.lc": f"u{code:05X}" for code in codes},
        EM_I_LIGATURES[1]: EM_I_LIGATURES[0],
    }
    assert (a["glyf"]["u10C34"].compile(a["glyf"]) ==
            a["glyf"]["u10C34.lc"].compile(a["glyf"]))
    assert a["hmtx"]["u10C34"] == a["hmtx"]["u10C34.lc"]
    ag_cap = next(item for item in capital if item.code == 0x10C0D)
    ag_lower = next(item for item in lower if item.code == 0x10C0D)
    for item, expected in ((ag_cap, 340), (ag_lower, 510)):
        shape, _ = fitted(item, SANS_SIDES)
        center = (shape.bounds[0] + shape.bounds[2]) / 2
        assert shape.intersection(box(center - 5, 0, center + 5, 700)).bounds[3] >= expected - .001
    for code, upper in ((0x10C31, 510), (0x10C28, 700)):
        shape, _ = fitted(next(item for item in lower if item.code == code), SANS_SIDES)
        assert abs(shape.bounds[3] - upper) < .001
        assert abs(shape.bounds[1] - (-190 if code == 0x10C31 else 0)) < .001
    for group, top in ((capital, 700), (lower, 510)):
        oe = next(item for item in group if item.code == 0x10C07)
        assert abs(ink_strokes(oe)[2].bounds[3] - top) < .001
        ic = next(item for item in group if item.code == 0x10C31)
        routes = ink_strokes(ic)
        assert abs(routes[0].bounds[3] - top) < .001
        middle = routes[0].intersection(box(253 if top == 700 else 298, top - 2,
                                           257 if top == 700 else 302, top + 2))
        assert abs(middle.bounds[3] - top) < .001
    for group, suffix, fontfile, case_feature in (
        (capital, "", UPPER, {}), (lower, ".lc", SMALL, {}),
    ):
        signatures = set()
        for item in group:
            name = f"u{item.code:05X}{suffix}"
            shape, advance = fitted(item, SANS_SIDES)
            compiled = outline(a, name)
            assert shape.is_valid and shape.area > 0 and compiled.is_valid
            bottom = getattr(item, "bottom", 0) - (10 if item.round_bottom else 0)
            top = getattr(item, "top", 700) + (10 if item.round_top else 0)
            for route in ink_strokes(item):
                assert route.bounds[1] >= bottom - .001, (name, route.bounds)
                assert route.bounds[3] <= top + .001, (name, route.bounds)
                # Every fitted stroke survives construction; there is no box crop.
                assert route.difference(constructed(item).buffer(.31)).area < .1, name
            assert a["hmtx"][name][0] == advance
            assert 0 <= compiled.bounds[0] < compiled.bounds[2] <= advance
            assert compiled.bounds[1] == item.bottom - (10 if item.round_bottom else 0) \
                if suffix else compiled.bounds[1] == -(10 if item.round_bottom else 0)
            assert compiled.bounds[3] == item.top + (10 if item.round_top else 0) \
                if suffix else compiled.bounds[3] == 700 + (10 if item.round_top else 0)
            signature = compiled.wkb
            assert signature not in signatures, name
            signatures.add(signature)
        uniqueness(fontfile, codes)
    for path, mode, name in (
        (UPPER, {}, EM_I_LIGATURES[0]), (UPPER, {"ss01": 1}, EM_I_LIGATURES[1]),
        (SMALL, {}, EM_I_LIGATURES[1]), (SMALL, {"ss02": 1}, EM_I_LIGATURES[0]),
    ):
        joined = shaped(path, "𐰢𐰃", mode)
        assert len(joined) == 1 and joined[0]["name"] == name
        assert len(shaped(path, "𐰢𐰃", {**mode, "liga": 0})) == 2
    assert [x["cluster"] for x in shaped(SMALL, "𐰀𐰃")] == [1, 0]
    shapes, advances = {}, {}
    for group, suffix in ((capital, ""), (lower, ".lc")):
        for item in group:
            name = f"u{item.code:05X}{suffix}"
            shapes[name], advances[name] = fitted(item, SANS_SIDES)
    pairs = al_kerning(shapes, advances, capital, lower, SANS_SIDES)
    assert 60 <= len(pairs) <= 84
    minimum = 1000.
    for name, amount in pairs.items():
        code = int(name[1:6], 16)
        path = SMALL if name.endswith(".lc") else UPPER
        case = {} if path == SMALL else {"ss01": [(0, 1, 1)]}
        text = "𐰞" + chr(code)
        yes, no = shaped(path, text, case), shaped(path, text, {**case, "kern": 0})
        assert [row["name"] for row in yes] == [name, "u10C1E.lc"]
        assert sum(row["advance"] for row in no) - sum(row["advance"] for row in yes) == amount
        left, right = placed_outlines(path, text, case)
        minimum = min(minimum, left.distance(right))
    assert minimum >= 28, minimum
    for text in ("𐰞𐰢", "𐰞𐰺", "𐰞𐰞", "𐰞 𐰖"):
        assert shaped(SMALL, text) == shaped(SMALL, text, {"kern": 0})
    assert len(shaped(SMALL, "𐰃𐰾𐱅𐰢𐰃")) == 4
    output = {
        "version": VERSION, "signs": 42, "forms": 84, "glyphs": 91,
        "kerning_pairs": len(pairs), "min_compiled_clearance": minimum,
        "ligatures": list(EM_I_LIGATURES), "fonts": [UPPER.name, SMALL.name],
    }
    (ROOT / "analysis" / "sans-checks.json").write_text(json.dumps(output, indent=2) + "\n")
    print("PASS Sans", output)
    return output


if __name__ == "__main__":
    checks()
