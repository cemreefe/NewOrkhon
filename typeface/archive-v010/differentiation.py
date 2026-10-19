"""Compare the compiled 0.10 fonts with the frozen 0.9.1 baseline."""

import json
from hashlib import sha256
from html import escape
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

from glyph_report import save_fragment

ROOT = Path(__file__).resolve().parent
BASE = ROOT / "archive-v091"
OUT = ROOT / "analysis"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REDRAWS = [
    (0x10C48, "BASH", "Two stacked loops replace the post-and-diagonal weave.", 0x10C24, "AEN"),
    (0x10C1A, "AEK", "Close the head; EP stays open.", 0x10C2F, "EP"),
    (0x10C41, "ESH", "Raise the link; close the fork.", 0x10C20, "AEL"),
]


def text(draw, xy, value, size=24, color="#151515", bold=False):
    draw.text(xy, value, font=ImageFont.truetype(BOLD if bold else SANS, size), fill=color)


def font(path, size):
    return ImageFont.truetype(str(path), size, layout_engine=ImageFont.Layout.RAQM)


def sign(draw, path, code, center, baseline, size, color="#151515"):
    face = font(path, size)
    char = chr(code)
    left, _, right, _ = face.getbbox(char, anchor="ls", direction="rtl")
    draw.text((center - (left + right) / 2, baseline), char, font=face,
              anchor="ls", direction="rtl", fill=color)


def redraw_sheet():
    image = Image.new("RGB", (1500, 1630), "white")
    draw = ImageDraw.Draw(image)
    text(draw, (50, 24), "NEW ORKHON / DIFFERENTIATION", 34, bold=True)
    text(draw, (50, 76), "0.9.1 before / 0.10 after. Same em size, baseline and ink-centred placement.", 21)
    for i, (code, name, reason, neighbour, neighbour_name) in enumerate(REDRAWS):
        y = 130 + i * 490
        text(draw, (50, y), f"{name}   U+{code:05X}", 27, bold=True)
        text(draw, (50, y + 38), reason, 21, "#555555")
        for case in range(2):
            origin = 50 + case * 720
            filename = f"NewOrkhonText{'Lowercase' if case else ''}-Regular.ttf"
            text(draw, (origin, y + 85), "Lowercase" if case else "Capital", 20)
            for j, (path, label, color) in enumerate((
                (BASE / filename, "Before", "#777777"),
                (ROOT / filename, "After", "#151515"),
                (ROOT / filename, f"Compare: {neighbour_name}", "#151515"),
            )):
                x = origin + 100 + j * 225
                baseline = y + 290
                draw.line((x - 95, baseline, x + 95, baseline), fill="#dddddd")
                sign(draw, path, neighbour if j == 2 else code, x, baseline, 210, color)
                text(draw, (x - 75, y + 350), label, 18, color)
            for size, yy in ((20, 405), (32, 440)):
                text(draw, (origin, y + yy), f"{size}px", 15, "#555555")
                for j, path in enumerate((BASE / filename, ROOT / filename)):
                    string = (chr(code) + chr(neighbour) + " ") * 3
                    draw.text((origin + 80 + j * 300, y + yy), string,
                              font=font(path, size), fill="#151515", direction="rtl")
    text(draw, (50, 1600), "Authored design proposal. Geometric separation is not a reader-confusion test.", 18, "#555555")
    image.save(OUT / "differentiation-before-after.png")


def local_sheet(before, after):
    items = [
        ("upper", 0x10C28), ("lower", 0x10C28), ("upper", 0x10C31),
        ("lower", 0x10C0D), ("lower", 0x10C3A),
        ("upper", 0x10C38), ("lower", 0x10C38),
    ]
    image = Image.new("RGB", (1500, 1570), "white")
    draw = ImageDraw.Draw(image)
    text(draw, (50, 25), "NEW ORKHON / COUNTERS AND LOCAL WEIGHT", 32, bold=True)
    text(draw, (50, 75), "Before 0.9.1 / after 0.10. Full stroke model retained outside the local corrections.", 21)
    old = {r["id"]: r for r in before["density"]}
    new = {r["id"]: r for r in after["density"]}
    for i, (case, code) in enumerate(items):
        x, y = 50 + (i % 2) * 730, 145 + (i // 2) * 350
        a, b = old[f"{case}-{code:05X}"], new[f"{case}-{code:05X}"]
        text(draw, (x, y), f"{b['name']} / {case} / U+{code:05X}", 23, bold=True)
        filename = f"NewOrkhonText{'Lowercase' if case == 'lower' else ''}-Regular.ttf"
        for j, path in enumerate((BASE / filename, ROOT / filename)):
            cx = x + 140 + j * 310
            draw.line((cx - 120, y + 220, cx + 120, y + 220), fill="#dddddd")
            sign(draw, path, code, cx, y + 220, 230, "#777777" if j == 0 else "#151515")
            text(draw, (cx - 45, y + 240), "Before" if j == 0 else "After", 18)
        text(draw, (x, y + 282),
             f"Body ink {a['body_ink_pct']:.1f}% → {b['body_ink_pct']:.1f}%", 20)
        text(draw, (x, y + 310),
             f"Largest ink disk ≈ {a['max_ink_diameter']:.0f} → {b['max_ink_diameter']:.0f} units", 20)
    text(draw, (50, 1540), "OE and AQ unchanged. AG stays ж; OQ stays pole-right in lowercase. Measurements are geometric diagnostics.", 18)
    image.save(OUT / "local-weight-before-after.png")


def outline(form):
    return " ".join(
        "M" + " L".join(f"{x:g},{-y:g}" for x, y in ring) + " Z"
        for polygon in form["polygons"] for ring in polygon
    )


def revision_body(before, after, changed):
    old = {f["id"]: f for f in before["forms"]}
    old_density = {f["id"]: f for f in before["density"]}
    new_density = {f["id"]: f for f in after["density"]}
    options, panels, rows = [], [], []
    order = {0x10C48: 0, 0x10C1A: 1, 0x10C41: 2, 0x10C28: 3}
    forms = [f for f in after["forms"]
             if f"u{f['code']:05X}" + (".lc" if f["case"] == "lower" else "") in changed]
    forms.sort(key=lambda f: (order.get(f["code"], 4), f["code"], f["case"] == "lower"))
    for i, b in enumerate(forms):
        a, da, db = old[b["id"]], old_density[b["id"]], new_density[b["id"]]
        title = f"{b['name']} · {b['case']} · U+{b['code']:05X}"
        options.append(f'<option value="{i}">{escape(title)}</option>')
        paths = [outline(a), outline(b)]
        boxes = []
        for label, content in (
            ("Before · 0.9.1", f'<path d="{paths[0]}" class="ink"/>'),
            ("After · 0.10", f'<path d="{paths[1]}" class="ink"/>'),
            ("Overlay · before solid, after dashed",
             f'<path d="{paths[0]}" class="old"/><path d="{paths[1]}" class="new"/>'),
        ):
            boxes.append(f'<figure><figcaption>{label}</figcaption>'
                         f'<svg viewBox="-450 -760 900 1000" role="img" aria-label="{escape(title)} — {label}">'
                         '<path class="guide" d="M-450,0H450 M-450,-510H450 M-450,-700H450"/>'
                         f'{content}</svg></figure>')
        stats = f"Body ink: {da['body_ink_pct']:.1f}% → {db['body_ink_pct']:.1f}%. " \
                f"Largest ink disk: ≈{da['max_ink_diameter']:.0f} → {db['max_ink_diameter']:.0f} units."
        panels.append(f'<section class="change a-section"><h2 class="a-section__title">{escape(title)}</h2>'
                      f'<div class="glyphs">{"".join(boxes)}</div><p>{stats}</p></section>')
        rows.append(f'<tr><th scope="row">{escape(title)}</th>'
                    f'<td>{da["body_ink_pct"]:.1f}% → {db["body_ink_pct"]:.1f}%</td>'
                    f'<td>≈{da["max_ink_diameter"]:.0f} → {db["max_ink_diameter"]:.0f}</td></tr>')
    pair_rows = []
    outcomes = []
    for case in ("upper", "lower"):
        for x, y in ((0x10C1A, 0x10C2F), (0x10C20, 0x10C41),
                     (0x10C24, 0x10C48), (0x10C21, 0x10C48)):
            ids = {f"{case}-{code:05X}" for code in (x, y)}
            a, b = [next(p for p in d["pairs"] if {p["a"], p["b"]} == ids)
                    for d in (before, after)]
            assert b["raster_mean"] < a["raster_mean"], (case, x, y)
            title = f'{case} · {b["a_name"]}/{b["b_name"]}'
            pair_rows.append(f'<tr><th scope="row">{title}</th><td>{a["raster_mean"] * 100:.1f}%</td>'
                             f'<td>{b["raster_mean"] * 100:.1f}%</td></tr>')
            outcomes.append({"pair": title, "before": a["raster_mean"], "after": b["raster_mean"]})
    (OUT / "revision-outcomes.json").write_text(json.dumps(outcomes, indent=2) + "\n")
    css = """
<style>
.glyphs{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.glyphs figure{margin:0;min-width:0}.glyphs figcaption{font-size:12px;min-height:32px}
.glyphs svg{width:100%;height:230px}.ink{fill:currentColor;fill-rule:evenodd}
.old{fill:rgb(var(--text-blue) / .15);stroke:rgb(var(--text-blue));stroke-width:4;fill-rule:evenodd}
.new{fill:none;stroke:rgb(var(--text-orange));stroke-width:6;stroke-dasharray:14 9;fill-rule:evenodd}
.guide{stroke:rgb(var(--text-tertiary) / .5);stroke-width:2}
.change p{font-size:13px}#revision-controls{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:16px 0}
#revision-controls[hidden]{display:none}select{max-width:100%;font:inherit;background:rgb(var(--bg-page));color:rgb(var(--text-primary));padding:8px;border:1px solid rgb(var(--border-primary))}
@media(max-width:680px){.glyphs{grid-template-columns:1fr 1fr}.glyphs figure:last-child{display:none}.glyphs svg{height:165px}.glyphs figcaption{font-size:11px}.a-shell{padding:14px 16px}.a-header__title{font-size:22px}.change p{font-size:11px}}
@media print{#revision-controls{display:none!important}.change[hidden]{display:block!important}.change{break-inside:avoid}.glyphs{grid-template-columns:repeat(3,1fr)}.glyphs figure:last-child{display:block}.glyphs svg{height:170px}}
</style>"""
    script = """
<script>
(()=>{const panels=[...document.querySelectorAll('.change')],choose=document.querySelector('#change-select');
let index=0;function show(n){index=(n+panels.length)%panels.length;panels.forEach((p,i)=>p.hidden=i!==index);
choose.value=index;document.querySelector('#change-position').textContent=(index+1)+' / '+panels.length;}
choose.addEventListener('change',()=>show(+choose.value));
document.querySelector('#change-prev').addEventListener('click',()=>show(index-1));
document.querySelector('#change-next').addEventListener('click',()=>show(index+1));
document.addEventListener('keydown',e=>{if(['SELECT','INPUT','BUTTON'].includes(e.target.tagName))return;
if(e.key==='ArrowLeft'||e.key==='ArrowRight'){e.preventDefault();show(index+(e.key==='ArrowRight'?1:-1));}});
const disclosures=[...document.querySelectorAll('details')];let states=[];
addEventListener('beforeprint',()=>{states=disclosures.map(d=>d.open);disclosures.forEach(d=>d.open=true);});
addEventListener('afterprint',()=>disclosures.forEach((d,i)=>d.open=states[i]));
document.querySelector('#revision-controls').hidden=false;show(0);
})();
</script>"""
    result = css + """
<p>AEK closes its bowl; ESH closes its fork; BASH becomes two flowing loops.
ENC opens its counters. Crowded AG/AR/OQ/IC strokes taper locally.</p>
<nav id="revision-controls" aria-label="Glyph changes" hidden>
<button class="a-btn" id="change-prev" aria-label="Previous glyph">←</button>
<label>Glyph <select id="change-select">""" + "".join(options) + """</select></label>
<button class="a-btn" id="change-next" aria-label="Next glyph">→</button>
<output id="change-position" aria-live="polite"></output></nav>
<noscript><p>All changes are shown below. JavaScript adds pagination only.</p></noscript>
""" + "".join(panels)
    result += '<details><summary>Before/after measurements</summary><div class="a-table-scroll"><table class="a-table">'
    result += '<caption>Native raster Dice · mean of 20, 24, 32 and 48 px</caption>'
    result += '<thead><tr><th scope="col">Pair</th><th scope="col">0.9.1</th><th scope="col">0.10</th></tr></thead><tbody>'
    result += "".join(pair_rows) + '</tbody></table><table class="a-table">'
    result += '<caption>Density per advance/body height and approximate ink-disk diameter in font units</caption>'
    result += '<thead><tr><th scope="col">Glyph</th><th scope="col">Body ink</th><th scope="col">Ink disk</th></tr></thead><tbody>'
    result += "".join(rows) + '</tbody></table></div></details>'
    result += """<details><summary>Scope and limitations</summary>
<p>13 of 84 glyph records change. Every other outline and advance is byte-identical to 0.9.1.
OE retains its approved outline, baseline and 90/64 weight. AQ remains identical across cases.
N/n, capital AG's three separate pieces, AN, and the EZ/AD/AER placement fixes are unchanged.
Lowercase AG stays ж. OQ keeps its selected orientation in each case.</p>
<p>Capital OQ/AES overlap increases from 75.1% to 79.1% as its join loses ink.
Capital AEN/ELT remains 86.8%; OEK/OP remains 84.6%. These are remaining geometric review targets,
not observed reading errors. Equal-width ENC bowls were tried and rejected because they increased OP similarity.</p>
<p>All overlays keep the original em scale and baseline; only horizontal ink centring removes sidebearings.
Coverage uses advance × body height (700 capitals; 510 lowercase). Ink disks are approximate to about 1 unit,
not literal stem widths. Similarity does not prove confusion; lower scores do not prove better reading.
This is a speculative typeface, not a historical reconstruction or reader-validated alphabet.</p>
<p>Reproduce: build.py, validate.py, glyph_similarity.py, glyph_similarity.py density, differentiation.py.</p>
</details>"""
    result += '<details><summary>Font license</summary><pre>' + escape((ROOT / "OFL.txt").read_text()) + '</pre></details>'
    save_fragment(result + script, "REVISION", "New-Orkhon-0.10-Changes.html")


def main():
    redraw_sheet()
    before = TTFont(BASE / "NewOrkhonText-Regular.ttf")
    after = TTFont(ROOT / "NewOrkhonText-Regular.ttf")
    changed = [
        name for name in after.getGlyphOrder()
        if before["glyf"][name].compile(before["glyf"]) != after["glyf"][name].compile(after["glyf"])
        or before["hmtx"][name] != after["hmtx"][name]
    ]
    (OUT / "changed-glyphs.json").write_text(json.dumps(changed, indent=2) + "\n")
    baseline = json.loads((BASE / "glyph-analysis.json").read_text())
    current = json.loads((OUT / "glyph-analysis.json").read_text())
    for directory, data in ((BASE, baseline), (ROOT, current)):
        for filename, digest in data["font_hashes"].items():
            assert sha256((directory / filename).read_bytes()).hexdigest() == digest
    local_sheet(baseline, current)
    revision_body(baseline, current, changed)
    print("Changed records:", ", ".join(changed))


if __name__ == "__main__":
    main()
