"""Native RTL shaping, collision checks and text proofs for the current release."""

import json
from functools import lru_cache
from pathlib import Path

import uharfbuzz as hb
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont
from shapely import affinity
from shapely.geometry import box

from build import EM_I_LIGATURES, LETTERS, LOWER, ROOT, VERSION, al_kerning, fitted
from construction_revision import CHANGED
from glyph_similarity import outline

BASE = ROOT / "archive-v013"
OUT = ROOT / "analysis"
UPPER = ROOT / "NewOrkhonText-Regular.ttf"
SMALL = ROOT / "NewOrkhonTextLowercase-Regular.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


@lru_cache
def loaded(path):
    tt = TTFont(path)
    face = hb.Face(Path(path).read_bytes())
    font = hb.Font(face)
    font.scale = (1000, 1000)
    return tt, font


def shaped(path, text, features=None):
    tt, font = loaded(str(path))
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.direction = "rtl"
    buffer.script = "orkh"
    buffer.language = "otk"
    hb.shape(font, buffer, features or {})
    x = 0
    result = []
    for info, pos in zip(buffer.glyph_infos, buffer.glyph_positions, strict=True):
        result.append({
            "name": tt.getGlyphName(info.codepoint), "cluster": info.cluster,
            "x": x + pos.x_offset, "y": pos.y_offset, "advance": pos.x_advance,
        })
        x += pos.x_advance
    return result


def placed_outlines(path, text, features=None):
    tt, _ = loaded(str(path))
    return [
        affinity.translate(outline(tt, row["name"]), xoff=row["x"], yoff=row["y"])
        for row in shaped(path, text, features)
    ]


def checks():
    current, _ = loaded(str(UPPER))
    previous = TTFont(BASE / UPPER.name)
    assert current.getBestCmap() == previous.getBestCmap()
    assert current.getGlyphOrder() == previous.getGlyphOrder()
    changed = []
    for name in previous.getGlyphOrder():
        if (current["glyf"][name].compile(current["glyf"]) != previous["glyf"][name].compile(previous["glyf"])
                or current["hmtx"][name] != previous["hmtx"][name]):
            changed.append(name)
    assert set(changed) == CHANGED

    data = {}
    for file, mode, expected in (
        (UPPER, {}, EM_I_LIGATURES[0]), (UPPER, {"ss01": 1}, EM_I_LIGATURES[1]),
        (SMALL, {}, EM_I_LIGATURES[1]), (SMALL, {"ss02": 1}, EM_I_LIGATURES[0]),
    ):
        joined = shaped(file, "𐰢𐰃", mode)
        apart = shaped(file, "𐰢𐰃", {**mode, "liga": 0})
        assert len(joined) == 1 and joined[0]["name"] == expected and joined[0]["cluster"] == 0
        assert len(apart) == 2
        assert sum(r["advance"] for r in joined) < sum(r["advance"] for r in apart)
        tt, _ = loaded(str(file))
        glyph = outline(tt, expected)
        assert glyph.geom_type == "Polygon" and glyph.is_valid
        top = 510 if ".lc." in expected else 700
        head = glyph.intersection(box(-2000, top * .65, 3000, top))
        assert head.geom_type == "Polygon", expected
        assert len(shaped(file, "𐰢 𐰃", mode)) == 3
        assert len(shaped(file, "𐰃𐰢", mode)) == 2
    assert len(shaped(UPPER, "𐰢𐰃", {"ss01": [(0, 1, 1)]})) == 2
    assert len(shaped(UPPER, "𐰢𐰃", {"ss01": [(1, 2, 1)]})) == 2
    carets = current["GDEF"].table.LigCaretList
    assert carets.Coverage.glyphs == list(EM_I_LIGATURES)
    assert all(g.CaretCount == 1 and g.CaretValue[0].Coordinate > 0 for g in carets.LigGlyph)

    shapes, advances = {}, {}
    for suffix, group in (("", LETTERS), (".lc", LOWER)):
        for letter in group:
            name = f"u{letter.code:05X}{suffix}"
            shapes[name], advances[name] = fitted(letter)
    pairs = al_kerning(shapes, advances)
    minimum = 10000.
    records = []
    for name, amount in pairs.items():
        code = int(name[1:6], 16)
        file = SMALL if name.endswith(".lc") else UPPER
        features = {} if file == SMALL else {"ss01": [(0, 1, 1)]}
        text = "𐰞" + chr(code)
        yes = shaped(file, text, features)
        no = shaped(file, text, {**features, "kern": 0})
        assert [r["name"] for r in yes] == [name, "u10C1E.lc"]
        assert no[1]["x"] - yes[1]["x"] == amount
        assert no[0]["x"] == yes[0]["x"]
        assert sum(r["advance"] for r in no) - sum(r["advance"] for r in yes) == amount
        a, b = placed_outlines(file, text, features)
        clearance = a.distance(b)
        assert clearance >= 28, (name, clearance)
        minimum = min(minimum, clearance)
        neighbor = shapes[name]
        x0, _, x1, _ = neighbor.bounds
        assert not neighbor.intersects(box(x0 + .65 * (x1 - x0), -400, x1 + 10, -35))
        records.append({"visual_left": name, "reduction": amount, "clearance": clearance})
    for text in ("𐰞𐰢", "𐰞𐰺", "𐰞𐰞", "𐰖𐰞", "𐰞 𐰖"):
        assert shaped(SMALL, text) == shaped(SMALL, text, {"kern": 0}), text
    for text in ("𐰞𐰖𐰣", "𐰞𐰞𐰃", "𐰞𐰢𐰃", "𐰞𐰖𐰞𐰖"):
        glyphs = placed_outlines(SMALL, text)
        assert all(not a.intersects(b) for i, a in enumerate(glyphs) for b in glyphs[i + 1:]), text
    for size in (20, 24, 32, 48):
        face = ImageFont.truetype(str(SMALL), size, layout_engine=ImageFont.Layout.RAQM)
        for text in ("𐰞𐰖", "𐰞𐰃", "𐰢𐰃", "𐰃𐰾𐱅𐰢𐰃"):
            expected = sum(r["advance"] for r in shaped(SMALL, text)) * size / 1000
            assert abs(face.getlength(text, direction="rtl") - expected) < .1
        image = Image.new("L", (100, 100))
        ImageDraw.Draw(image).text((4, 65), "𐰢𐰃", font=face, direction="rtl", fill=255, anchor="ls")
        assert image.getbbox()
    data.update({
        "version": VERSION, "unchanged_encoded_forms": 68, "unchanged_utility_glyphs": 5,
        "ligature_glyphs": list(EM_I_LIGATURES), "kerning_pairs": records,
        "minimum_compiled_clearance": minimum,
        "copy_text": "𐰢𐰃", "codepoints": ["U+10C22", "U+10C03"],
        "same_case_ligatures": True, "mixed_case_heads_left_separate": True,
    })
    (OUT / "changed-glyphs.json").write_text(json.dumps({
        "base_version": "0.13", "version": VERSION,
        "modified_standalone_glyphs": [name for name in changed if name not in EM_I_LIGATURES],
        "modified_ligatures": [name for name in changed if name in EM_I_LIGATURES],
        "added_glyphs": [],
        "layout_features": ["kern", "liga", "ss01", "ss02", "GDEF carets"],
    }, indent=2) + "\n")
    (OUT / "shaping-checks.json").write_text(json.dumps(data, indent=2) + "\n")
    print(f"PASS: {len(pairs)} RTL kern pairs, ≥{minimum:.1f} units compiled clearance; "
          "both case ligatures, case switches, caret positions, feature-off and text-size checks.")
    return data


def text(draw, xy, value, size=23, color="#171717", bold=False):
    draw.text(xy, value, fill=color, font=ImageFont.truetype(BOLD if bold else SANS, size))


def run(draw, path, string, right, baseline, size=115, color="#171717", features=None):
    face = ImageFont.truetype(str(path), size, layout_engine=ImageFont.Layout.RAQM)
    draw.text((right, baseline), string, font=face, direction="rtl",
              features=features, anchor="rs", fill=color)


def kerning_proof():
    im = Image.new("RGB", (1400, 1200), "white")
    d = ImageDraw.Draw(im)
    text(d, (45, 25), "NEW ORKHON / SHAPE-AWARE AL SPACING", 31, bold=True)
    text(d, (45, 75), "A neighbor can sit over AL's hook only when its right descender zone is clear.", 23)
    text(d, (45, 120), "Kerning disabled", 24, color="#777")
    text(d, (745, 120), f"Kerning enabled / {VERSION}", 24)
    for i, (label, string) in enumerate((
        ("AL + AY / tucked", "𐰞𐰖"),
        ("Source word / AL + I tucked", "𐰆𐰍𐰞𐰃"),
        ("Source word / AL + AN tucked", "𐰴𐰃𐰞𐰣𐰢𐰾"),
        ("AL + EM / unchanged: EM's tail uses that space", "𐰞𐰢"),
    )):
        y = 180 + i * 240
        text(d, (45, y), label, 22)
        for j, path in enumerate((SMALL, SMALL)):
            right = 630 + j * 700
            d.line((45 + j * 700, y + 155, right, y + 155), fill="#ddd")
            run(d, path, string, right, y + 155, 110, "#777" if j == 0 else "#171717",
                ["-kern"] if j == 0 else None)
    text(d, (45, 1170), "Right-aligned runs; the AL stays fixed while the safe neighbor moves into its empty space. Logical RTL text.", 18)
    im.save(OUT / "spacing-before-after.png")


def ligature_proof():
    im = Image.new("RGB", (1400, 1270), "white")
    d = ImageDraw.Draw(im)
    text(d, (45, 25), "NEW ORKHON / EM–I TOP JOIN", 31, bold=True)
    text(d, (45, 75), "The same two characters: EM U+10C22 followed by I U+10C03. Joined by standard liga.", 22)
    text(d, (45, 120), "Ligature disabled", 24, color="#777")
    text(d, (745, 120), f"Ligature enabled / {VERSION}", 24)
    for i, (label, filename, string, size) in enumerate((
        ("Capitals", UPPER.name, "𐰢𐰃", 200),
        ("Lowercase", SMALL.name, "𐰢𐰃", 200),
        ("İstemi / same sequence in the source text", SMALL.name, "𐰃𐰾𐱅𐰢𐰃", 130),
    )):
        y = 175 + i * 265
        text(d, (45, y), label, 22)
        for j, directory in enumerate((ROOT, ROOT)):
            right = 630 + j * 700
            d.line((45 + j * 700, y + 185, right, y + 185), fill="#ddd")
            run(d, directory / filename, string, right, y + 185, size, "#777" if j == 0 else "#171717",
                ["-liga"] if j == 0 else None)
    text(d, (45, 1000), "Native pixels / lowercase", 24, bold=True)
    for i, size in enumerate((20, 24, 32, 48)):
        y = 1050 + i * 45
        text(d, (45, y), f"{size} px", 18)
        for j, directory in enumerate((ROOT, ROOT)):
            run(d, directory / SMALL.name, "𐰃𐰾𐱅𐰢𐰃", 630 + j * 700, y + 30, size,
                features=["-liga"] if j == 0 else None)
    text(d, (45, 1240), "Standalone outlines are unchanged. Space boundaries and mismatched case heights do not join. Text stays copyable.", 18)
    im.save(OUT / "em-i-top-join.png")


if __name__ == "__main__":
    checks()
    kerning_proof()
    ligature_proof()
