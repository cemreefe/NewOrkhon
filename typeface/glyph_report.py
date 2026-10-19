"""Build the standalone body and proof sheets for the glyph audit."""

import html
import json
import re
import sys

from PIL import Image, ImageDraw, ImageFont

from glyph_similarity import OUT, ROOT, SMALL, UPPER

DATA = json.loads((OUT / "glyph-analysis.json").read_text())
FORMS = {form["id"]: form for form in DATA["forms"]}
DENSITY = {row["id"]: row for row in DATA["density"]}
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def save_fragment(body, name, output_name):
    start, end = f"<!-- NEW-ORKHON-{name}:START -->", f"<!-- NEW-ORKHON-{name}:END -->"
    fragment = start + "\n" + body + "\n" + end
    (OUT / f"{name.lower()}-body.html").write_text(fragment, encoding="utf-8")
    if "--update" in sys.argv:
        output = OUT / output_name
        document, count = re.subn(
            re.escape(start) + ".*?" + re.escape(end), lambda _: fragment,
            output.read_text(encoding="utf-8"), flags=re.DOTALL,
        )
        if count != 1:
            raise ValueError("Compile this body into the artifact shell once before updating.")
        output.write_text(document, encoding="utf-8")


def esc(text):
    return html.escape(str(text))


def label(form):
    return f'{form["name"]} · U+{form["code"]:05X} · {form["case"]}'


def path_data(form):
    return " ".join(
        "M" + " L".join(f"{x:g},{-y:g}" for x, y in ring) + " Z"
        for polygon in form["polygons"] for ring in polygon
    )


def icon(form):
    return (
        f'<svg class="mini-glyph" viewBox="-500 -760 1000 1000" role="img" '
        f'aria-label="{esc(label(form))}"><path fill="currentColor" fill-rule="evenodd" '
        f'd="{path_data(form)}"/></svg>'
    )


def top_pairs(group, count=6):
    return sorted(
        [row for row in DATA["pairs"] if row["group"] == group],
        key=lambda row: row["raster_mean"], reverse=True,
    )[:count]


def pairs_table(group):
    rows = []
    for number, row in enumerate(top_pairs(group), 1):
        a, b = FORMS[row["a"]], FORMS[row["b"]]
        rows.append(
            f'<tr><td>{number}</td><th scope="row">{icon(a)}{a["name"]} / {b["name"]}'
            f'<small>U+{a["code"]:05X} / U+{b["code"]:05X}</small></th>'
            f'<td data-numeric>{row["raster_mean"] * 100:.1f}%</td>'
            f'<td data-numeric>{row["outline_dice"] * 100:.1f}%</td>'
            f'<td data-numeric>{row["blur_mean"] * 100:.1f}%</td></tr>'
        )
    return (
        '<div class="a-table-scroll"><table class="a-table"><caption>'
        + {"lower": "Lowercase", "upper": "Capitals", "mixed": "Different-case, different-letter pairs"}[group]
        + '</caption><thead><tr><th>#</th><th>Pair</th><th>Raster Dice</th>'
        '<th>Outline Dice</th><th>Blurred Dice</th></tr></thead><tbody>'
        + "".join(rows) + "</tbody></table></div>"
    )


def density_table(case):
    selected = sorted(
        [row for row in DATA["density"] if row["case"] == case],
        key=lambda row: row["body_ink_pct"], reverse=True,
    )[:8]
    rows = []
    for row in selected:
        form = FORMS[row["id"]]
        rows.append(
            f'<tr><th scope="row">{icon(form)}{form["name"]}'
            f'<small>U+{form["code"]:05X}</small></th>'
            f'<td data-numeric>{row["body_ink_pct"]:.1f}%</td>'
            f'<td data-numeric>{row["body_vs_case_median"]:.2f}×</td>'
            f'<td data-numeric>{row["max_ink_diameter"]:.0f} units</td>'
            f'<td data-numeric>{row["blurred_core_pct"]:.1f}%</td></tr>'
        )
    return (
        '<div class="a-table-scroll"><table class="a-table"><caption>'
        + ("Lowercase" if case == "lower" else "Capitals")
        + '</caption><thead><tr><th>Glyph</th><th>Body ink</th><th>Vs median</th>'
        '<th>Largest ink disk</th><th>Blur core</th></tr></thead><tbody>'
        + "".join(rows) + "</tbody></table></div>"
    )


CSS = """
<style>
.a-shell { --max-width: 1200px; }
.a-header { margin-bottom: 16px; }
.a-header__title { font-size: 30px; letter-spacing: -.025em; }
.lead { font-size: 14px; line-height: 1.55; max-width: 1000px; margin-bottom: 20px; }
.controls { display: grid; grid-template-columns: 1fr 1fr 1.6fr; gap: 14px; border-block: 1px solid rgb(var(--border-primary)); padding: 14px 0; }
.controls label, .pixel-controls { font-size: 12px; color: rgb(var(--text-secondary)); }
.controls label > span { display: block; margin-bottom: 5px; }
select { width: 100%; min-height: 36px; padding: 5px 8px; background: rgb(var(--bg-page)); color: rgb(var(--text-primary)); border: 1px solid rgb(var(--border-primary)); border-radius: 4px; font: inherit; }
.navigator { display: flex; gap: 12px; align-items: center; justify-content: center; margin: 14px 0; }
.navigator .a-btn { min-width: 48px; min-height: 38px; }
.navigator output { font: 12px var(--font-mono); min-width: 150px; text-align: center; }
.preview-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
.glyph-box { border: 1px solid rgb(var(--border-primary)); min-width: 0; }
.glyph-box h3 { font: 12px var(--font-mono); margin: 12px 14px 0; min-height: 30px; }
.glyph-box svg { display: block; width: 100%; height: 150px; }
.glyph-box svg .body-band { fill: rgb(var(--tint-tertiary)); }
.guide { stroke: rgb(var(--text-tertiary)); stroke-width: 3; }
.outline { fill: currentColor; fill-rule: evenodd; }
.mark-a { fill: rgb(var(--text-blue) / .15); stroke: rgb(var(--text-blue)); stroke-width: 5; fill-rule: evenodd; }
.mark-b { fill: none; stroke: rgb(var(--text-orange)); stroke-width: 7; stroke-dasharray: 15 10; fill-rule: evenodd; }
.disk { fill: none; stroke: rgb(var(--text-blue)); stroke-width: 9; stroke-dasharray: 18 10; }
.overlay-legend { font-size: 11px; margin: 0 14px 12px; color: rgb(var(--text-secondary)); }
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 16px 0; }
.stats dt { font-size: 11px; color: rgb(var(--text-secondary)); }
.stats dd { margin: 5px 0 0; font: 20px var(--font-mono); }
.review-note { font-size: 13px; line-height: 1.55; margin: 14px 0; }
.pixel-row { display: flex; gap: 16px; align-items: center; padding: 10px 0; border-block: 1px solid rgb(var(--border-primary)); }
.pixel-controls { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; max-width: 250px; }
.pixel-controls select { width: auto; min-height: 30px; }
.pixel-canvases { display: flex; gap: 16px; align-items: center; }
canvas { width: 96px; height: 72px; background: white; border: 1px solid rgb(var(--border-primary)); }
.view-caption { font-size: 11px; color: rgb(var(--text-secondary)); }
.summary-list { margin-top: 22px; }
details { margin: 18px 0; }
summary { font-size: 13px; cursor: pointer; }
.a-table { font-size: 12px; }
.a-table caption { text-align: left; font-weight: 600; padding: 16px 0 8px; }
.a-table small { display: block; color: rgb(var(--text-secondary)); font: 10px var(--font-mono); }
.mini-glyph { width: 35px; height: 35px; vertical-align: middle; margin-right: 8px; }
.methods p { font-size: 13px; line-height: 1.65; max-width: 1000px; }
.methods h3 { font-size: 14px; margin-top: 20px; }
.methods code, .methods pre { font-size: 10px; overflow-wrap: anywhere; white-space: pre-wrap; }
.a-footnote { font-size: 11px; }
@media(max-width:680px) {
 .a-shell { padding: 12px 16px; }
 .a-header { display: grid; grid-template-columns: 1fr auto; gap: 8px; align-items: start; margin-bottom: 10px; }
 .a-header__title { font-size: 20px; }
 .a-header__subtitle { font-size: 10px; line-height: 1.35; }
 .lead { display: none; }
 .controls { grid-template-columns: 1fr 1fr; gap: 4px 12px; padding: 8px 0; }
 .controls label:first-child { grid-column: span 2; }
 .controls label { font-size: 10px; }
 select { min-height: 32px; }
 .navigator { margin: 10px 0; }
 .preview-grid { grid-template-columns: 1fr 1fr; gap: 10px; }
 #overlay-box { display: none; }
 .glyph-box h3 { font-size: 10px; margin: 8px 9px 0; min-height: 28px; }
 .glyph-box svg { height: 96px; }
 .stats { grid-template-columns: 1fr 1fr; gap: 8px 14px; margin: 12px 0; }
 .stats dt { font-size: 10px; }
 .stats dd { font-size: 17px; margin-top: 2px; }
 .review-note { font-size: 11px; margin: 10px 0; line-height: 1.45; }
 .pixel-row { gap: 8px; flex-wrap: nowrap; }
 .pixel-controls { width: 115px; max-width: 115px; font-size: 9px; gap: 4px; }
 .pixel-canvases { gap: 0; }
 canvas { width: 96px; height: 72px; }
 .view-caption { display: none; }
 .summary-list, details { margin: 8px 0; }
 .a-footnote { margin-top: 10px; padding-top: 6px; font-size: 9px; line-height: 1.4; }
 .a-table { font-size: 10px; }
}
@media print {
 .controls, .navigator, .pixel-controls { display: none; }
 .preview-grid { grid-template-columns: 1fr 1fr 1fr; }
 #overlay-box { display: block; }
 .glyph-box svg { height: 140px; }
 .summary-list > details > div { display: block !important; }
 .summary-list > details { break-inside: auto; }
 .a-table th, .a-table td { padding: 6px; }
 .a-table tr { break-inside: avoid; }
 .methods { display: none; }
}
</style>
"""

SHELL = """
<p class="lead"><strong>0.12 adds safe AL kerning and EM–I ligatures. All 84 standalone forms remain unchanged.</strong>
These measurements screen for geometric similarity and uneven color—not reading-error probabilities.</p>
<div class="controls a-no-print">
  <label><span>Review</span><select id="mode"><option value="pairs">Similar glyphs</option><option value="density">Dense glyphs</option></select></label>
  <label><span>Case</span><select id="group"><option value="lower">Lowercase</option><option value="upper">Capitals</option><option value="mixed">Mixed case, different letters</option><option value="counterparts">Same letter across cases</option></select></label>
  <label><span>Rank by</span><select id="order"></select></label>
</div>
<div class="navigator a-no-print">
  <button class="a-btn" id="previous" aria-label="Previous result">←</button>
  <output id="position" aria-live="polite" aria-atomic="true"></output>
  <button class="a-btn" id="next" aria-label="Next result">→</button>
</div>
<section id="inspector" aria-label="Selected glyph comparison">
  <div class="preview-grid">
    <div class="glyph-box"><h3 id="title-a"></h3><div id="svg-a"></div></div>
    <div class="glyph-box"><h3 id="title-b"></h3><div id="svg-b"></div></div>
    <div class="glyph-box" id="overlay-box"><h3 id="overlay-title">Outline overlay</h3><div id="svg-overlay"></div><p class="overlay-legend" id="overlay-legend">A: solid blue · B: dashed orange</p></div>
  </div>
  <p class="view-caption" id="view-caption"></p>
  <dl class="stats" id="stats"></dl>
  <p class="review-note" id="review-note"></p>
  <div class="pixel-row">
    <div class="pixel-controls">
      <span>Actual pixels</span>
      <select id="pixel-size" aria-label="Raster text size"><option>20</option><option selected>24</option><option>32</option><option>48</option></select><span>px/em</span>
      <label><input type="checkbox" id="pixel-blur"> Blur</label>
    </div>
    <div class="pixel-canvases"><canvas id="pixel-a" width="96" height="72" aria-label="Raster glyph A"></canvas><canvas id="pixel-b" width="96" height="72" aria-label="Raster glyph B"></canvas></div>
  </div>
</section>
<noscript><p>The explorer needs JavaScript. The ranked tables and methods below remain readable.</p></noscript>
"""

SCRIPT = """
<script>
(() => {
 "use strict";
 const forms = Object.fromEntries(DATA.forms.map(f => [f.id, f]));
 const density = Object.fromEntries(DATA.density.map(d => [d.id, d]));
 const byId = id => document.getElementById(id);
 const mode = byId("mode"), group = byId("group"), order = byId("order");
 let items = [], index = 0, active = [];
 const pairOrders = {raster_mean:"Native raster Dice · mean 20–48 px",blur_mean:"Blurred raster Dice · mean 20–48 px",outline_dice:"Outline ink overlap (Dice)",normalized_dice:"Height-normalized outline Dice"};
 const densityOrders = {body_ink_pct:"Body ink per advance",peak_over_nominal:"Largest ink disk / nominal stem",blurred_core_pct:"Blurred dark-core coverage at 24 px"};
 const percent = n => (n * 100).toFixed(1) + "%";
 const ucode = code => "U+" + code.toString(16).toUpperCase();
 const title = f => f.name + " · " + ucode(f.code) + " · " + f.case;
 const median = values => {const a=[...values].sort((a,b)=>a-b); return (a[20]+a[21])/2;};
 function path(f, normalize=false) {
   const low=f.bounds[1], high=f.bounds[3], scale=normalize?700/(high-low):1;
   return f.polygons.flatMap(poly=>poly.map(ring=>
    "M"+ring.map(([x,y])=>(x*scale)+","+(-(normalize?y-low:y)*scale)).join(" L")+" Z")).join(" ");
 }
 function svg(f, normalize=false, disk=null) {
   const height=normalize?700:(f.case==="upper"?700:510);
   let body='<rect class="body-band" x="-500" y="'+(-height)+'" width="1000" height="'+height+'"/>';
   body+='<path class="guide" d="M-500,0H500 M-500,'+(-height)+'H500"/>';
   body+='<path class="outline" d="'+path(f,normalize)+'"/>';
   if(disk) body+='<circle class="disk" cx="'+disk.circle_x+'" cy="'+(-disk.circle_y)+'" r="'+(disk.max_ink_diameter/2)+'"/>';
   return '<svg viewBox="-500 -760 1000 1000" role="img" aria-label="'+title(f)+'">'+body+'</svg>';
 }
 function overlay(a,b,normalize) {
   return '<svg viewBox="-500 -760 1000 1000" role="img" aria-label="A solid; B dashed. Outline overlay"><path class="guide" d="M-500,0H500"/><path class="mark-a" d="'+path(a,normalize)+'"/><path class="mark-b" d="'+path(b,normalize)+'"/></svg>';
 }
 function setStats(stats) {
   byId("stats").innerHTML=stats.map(([label,value])=>"<div><dt>"+label+"</dt><dd>"+value+"</dd></div>").join("");
 }
 function pairNote(row) {
   if(row.same_character) return row.exact_outline?
    "Intentional: AQ uses the same capital and lowercase outline. Do not count this as two different letters.":
    "This is the same character across cases. Family resemblance is expected; it is separate from different-letter similarity.";
   const key=[row.a_name,row.b_name].sort().join("/");
   const notes={
    "AEK/EP":"In 0.10 AEK closes its two arms into a bowl; EP retains the open head. Inspect the counter at native text sizes.",
    "AEL/ESH":"In 0.10 ESH raises its link to close the fork; AEL remains an open Y. The shared stem and branches still contribute overlap.",
    "AEN/BASH":"In 0.10 BASH replaces its paired posts with two stacked loops. AEN remains the user-selected N/n.",
    "BASH/ELT":"BASH now has a figure-eight route; ELT retains its earlier valley construction.",
    "AEN/ENT":"Shared uprights dominate n/u-like forms. Inspect shoulders, terminals and openings; a high score alone does not demand redesign.",
    "AET/OP":"Both rely on a left ascender and right-hand returns. Separate the tiers, counter openings or terminal rhythm.",
    "AET/OEK":"The tall post and right-hand construction overlap. Inspect the tier openings before adding more ink."
   };
   return notes[key]||"Inspect the overlay’s differing branches, counters and terminals. This is a geometric shortlist, not proof that readers confuse the letters.";
 }
 function densityNote(row) {
   const notes={
    BASH:"The new continuous figure-eight route reduces body coverage and the crowded crossing. Both counters remain; this glyph is not forced to the case median.",
    ENC:"0.10 widens the bowls and makes the upper tier smaller than the lower. An equal-bowl trial was rejected because it increased lowercase OP similarity.",
    AG:"The ж construction is retained. Incoming arms taper locally at the centre; the upright and outside terminals keep their full weight.",
    AR:"The 0.10 taper is reverted. This is exactly the approved 0.9.1 outline, including its baseline-reaching body and original weight.",
    OE:"Unchanged from 0.9.1: the approved shape, baseline and heavier 90/64 model are protected. It remains the darkest lowercase glyph.",
    IC:"Capital IC's last return is tapered where it converges on the straight pole. Lowercase IC is unchanged."
   };
   if(row.name==="AG"&&row.case==="upper") return "Capital AG has three separated components. Check their balance and spacing; it does not have the lowercase ж junction.";
   if(row.name==="OE"&&row.case==="upper") return "Check the diagonal/return’s local weight against its upright posts; do not infer heaviness from a narrow ink bounding box alone.";
   if(row.name==="AR"&&row.case==="upper") return "Inspect the return/stem meeting and relieve local ink buildup without changing the overall topology.";
   if(row.name==="OQ") return row.case==="lower"?
    "Lowercase OQ keeps the chosen pole-right skeleton. Only the converging wings taper; it remains light overall.":
    "Capital OQ keeps the upright skeleton. Only the converging wings taper; its local blob shrinks, but similarity to the plain minim increases.";
   if(row.name==="AQ"&&row.case==="lower") return "This lowercase deliberately equals its capital. Its height/weight difference is intentional; do not revise it without revisiting that decision.";
   return notes[row.name]||(row.peak_over_nominal>1.5?
    "The largest ink disk suggests a thick local meeting. Inspect the marked region; local relief may be enough.":
    "Check counterspace, advance and sidebearings before changing stroke weight. Narrow letters can have high coverage without a clogged join.");
 }
 function paint(canvasId,formId) {
   const size=byId("pixel-size").value;
   const buffer=Uint8ClampedArray.from(forms[formId].raster[size].flatMap(([n,v])=>Array(n).fill(v)));
   const source=document.createElement("canvas");source.width=96;source.height=72;
   const context=source.getContext("2d"),image=context.createImageData(96,72);
   for(let i=0;i<buffer.length;i++){image.data[i*4]=image.data[i*4+1]=image.data[i*4+2]=255-buffer[i];image.data[i*4+3]=255;}
   context.putImageData(image,0,0);
   const destination=byId(canvasId).getContext("2d");
   destination.fillStyle="white";destination.fillRect(0,0,96,72);
   destination.filter=byId("pixel-blur").checked?"blur("+(Number(size)/24)+"px)":"none";
   destination.drawImage(source,0,0);destination.filter="none";
 }
 function renderPixels(){if(active.length===2){paint("pixel-a",active[0]);paint("pixel-b",active[1]);}}
 function render() {
   const row=items[index],dense=mode.value==="density";
   byId("previous").disabled=index===0;byId("next").disabled=index===items.length-1;
   byId("position").textContent=(index+1)+" / "+items.length;
   let a,b;
   if(dense) {
     a=forms[row.id];
     const groupData=DATA.density.filter(d=>d.case===a.case);
     const mid=median(groupData.map(d=>d.body_ink_pct));
     const peer=[...groupData].sort((x,y)=>Math.abs(x.body_ink_pct-mid)-Math.abs(y.body_ink_pct-mid))[0];
     b=forms[peer.id];
     byId("title-a").textContent=title(a);
     byId("title-b").textContent="Near-median color · "+b.name;
     byId("svg-a").innerHTML=svg(a,false,row);
     byId("svg-b").innerHTML=svg(b,false,peer);
     byId("overlay-title").textContent="Largest local ink region";
     byId("svg-overlay").innerHTML=svg(a,false,row);
     byId("overlay-legend").textContent="Dashed circle: largest disk contained in ink.";
     byId("view-caption").textContent="Same em scale and baseline. Reference is a median-color example, not an ideal shape.";
     setStats([["Body ink / advance",row.body_ink_pct.toFixed(1)+"%"],["Vs "+a.case+" median",row.body_vs_case_median.toFixed(2)+"×"],["Largest ink disk",row.max_ink_diameter.toFixed(0)+" units"],["Disk / nominal stem",row.peak_over_nominal.toFixed(2)+"×"]]);
     byId("review-note").textContent=densityNote(row);
   } else {
     a=forms[row.a];b=forms[row.b];const normalize=order.value==="normalized_dice";
     byId("title-a").textContent="A · "+title(a);byId("title-b").textContent="B · "+title(b);
     byId("svg-a").innerHTML=svg(a,normalize);byId("svg-b").innerHTML=svg(b,normalize);
     byId("overlay-title").textContent="Outline overlay";byId("svg-overlay").innerHTML=overlay(a,b,normalize);
     byId("overlay-legend").textContent="A: solid blue · B: dashed orange";
     byId("view-caption").textContent=normalize?
      "Outline height normalized uniformly; baseline/height differences removed. Pixel proofs remain original scale.":
      "Same em scale and baseline; ink centred horizontally. No mirroring, rotation or vertical alignment.";
     setStats([["Native raster Dice",percent(row.raster_mean)],["Outline Dice",percent(row.outline_dice)],["Blurred raster Dice",percent(row.blur_mean)],["Outline distance",row.outline_hausdorff_em.toFixed(3)+" em"]]);
     byId("review-note").textContent=pairNote(row);
   }
   active=[a.id,b.id];renderPixels();
 }
 function refreshOrders() {
   const options=mode.value==="pairs"?pairOrders:densityOrders;
   order.innerHTML=Object.entries(options).map(([value,label])=>'<option value="'+value+'">'+label+'</option>').join("");
   [...group.options].forEach(o=>{o.disabled=mode.value==="density"&&!["upper","lower"].includes(o.value);});
   if(mode.value==="density"&&!["upper","lower"].includes(group.value))group.value="lower";
 }
 function rebuild() {
   items=(mode.value==="pairs"?DATA.pairs.filter(r=>r.group===group.value):
     DATA.density.filter(r=>r.case===group.value)).slice().sort((a,b)=>b[order.value]-a[order.value]);
   index=0;render();
 }
 mode.addEventListener("change",()=>{refreshOrders();rebuild();});
 group.addEventListener("change",rebuild);order.addEventListener("change",rebuild);
 byId("previous").addEventListener("click",()=>{index=Math.max(0,index-1);render();});
 byId("next").addEventListener("click",()=>{index=Math.min(items.length-1,index+1);render();});
 byId("pixel-size").addEventListener("change",renderPixels);byId("pixel-blur").addEventListener("change",renderPixels);
 let printOpened=[];
 window.addEventListener("beforeprint",()=>{
   if(printOpened.length)return;
   printOpened=[...document.querySelectorAll(".summary-list details")].filter(d=>!d.open);
   printOpened.forEach(d=>{d.open=true;});
 });
 window.addEventListener("afterprint",()=>{printOpened.forEach(d=>{d.open=false;});printOpened=[];});
 refreshOrders();rebuild();
 document.documentElement.dataset.auditReady="true";
})();
</script>
"""


def body():
    methods = """
<details class="methods">
<summary>Methods, limitations and reproducibility</summary>
<h3>What was compared</h3>
<p>84 standalone compiled contours from New Orkhon Text 0.12: 42 capitals and 42 lowercase forms.
The two unencoded EM–I ligatures are contextual forms and are not part of these single-letter comparisons.
0.12 adds 72 measured kerning pairs to lowercase AL; source outlines and advances are identical to 0.11.
There are 3,486 unordered pairs, of which 3,444 pair different characters and 42 are the same
character across cases. AQ's exact case equality is intentional and excluded from the default
different-letter lists. All source contour points are on-curve; their polygon geometry is used
directly, including holes. No database or SQL is involved: the source dataset is the two local TTF files.</p>
<h3>Similarity</h3>
<p>Ink is horizontally centred to remove sidebearings, preserving orientation, em scale and baseline.
There is no translation in y, rotation, mirroring, nonuniform stretch or pair-specific best alignment.
Outline Dice = 2 × intersection area / combined ink area. Native raster Dice uses actual Pillow/RAQM
20/24/32/48 px masks and the soft formula 2Σ(ab)/(Σa²+Σb²), excluding white-background agreement.
The default raster score is the unweighted mean of the four sizes. Pixel-phase/hinting effects can
therefore change a rank; outline and raster values are both shown. Hausdorff distance is measured
between contour boundaries in em units (1 em = 1,000 font units); lower is closer.</p>
<p>The blurred score applies a Gaussian radius of size/24 pixels to those rasters before the same
Dice formula. This is a loss-of-detail diagnostic, not an eye or reader model. The preview's browser
blur is illustrative and can differ slightly from Pillow's Gaussian implementation used for scores.
The height-normalized mode scales each complete ink bounding box uniformly to 700 units tall,
preserving aspect ratio and orientation but discarding original size and baseline position.</p>
<h3>Density</h3>
<p>Body color = ink area inside 0..700 (capitals) or 0..510 (lowercase) divided by advance × body height.
This includes sidebearings and reflects repetitive text color; it is not bbox fill. Medians are computed
separately for the 42 capitals and 42 lowercase forms. Small/narrow glyphs can have high coverage
without unusually thick strokes. Ascender/descender ink outside the body is excluded from this
particular measure; total ink per advance/em is also present in the CSV.</p>
<p>The largest disk entirely inside the ink identifies local blobs; its diameter is not a literal stem
width. GEOS maximum-inscribed-circle tolerance is 0.5 units, so diameters are approximate to about
1 unit. Ratios use the source glyph's nominal stem: 90 for capitals, generally 82 for lowercase,
with OE and AQ at 90. The CSV also includes 2 × ink area / total contour perimeter as a stroke proxy,
hole counts, and the diameter of the largest disk in each counter (the smallest of these per glyph);
that counter measure is not a minimum aperture or throat width.</p>
<p>The 24 px blur-core test renders ten repeated glyphs at their actual advance, blurs at radius 1 px,
then measures the fraction of the central six cells' body band with darkness ≥0.5, with fractional
edge weighting. Blur preserves total ink: this measure intentionally tests the surviving dark core,
not blurred average darkness. Threshold/radius choices are diagnostics, not validated readability cutoffs.
Robust z-scores in the CSV use each case's median and MAD; no universal pass/fail threshold is claimed.</p>
<h3>Decisions</h3>
<p>Applied: closed AEK bowl, raised/closed ESH link, two-loop BASH, wider unequal ENC bowls,
and local incoming-stroke tapers in lowercase AG/OQ and capital IC/OQ. The AR taper is reverted.
0.11 reconstructs AT as a stem, one right-hand bowl and a horizontal top arm; AET is unchanged.
In 0.11, three records changed from 0.10: capital/lowercase AT and restored lowercase AR.
In 0.12, none of the 84 standalone records changes; only positioning, substitutions and two ligature glyphs are added.
Fourteen of 84 glyph records differ from 0.9.1. OE, AQ, AN, N/n, the detached capital AG,
the corrected EZ/AD/AER placements, and all other records are unchanged.
Remaining close pairs include capital AEN/ELT and OEK/OP. Local relief is not blanket thinning.
These are authored typographic experiments, not recovered historical forms or reader-validated fixes.</p>
<h3>Reproduce</h3>
<pre>python3 glyph_similarity.py
python3 glyph_similarity.py density
python3 glyph_report.py</pre>
<p>CSV and JSON records retain all pairs, individual raster-size scores, metrics, contours and native
rasters. The HTML is a compiled standalone artifact; its editable body is generated by glyph_report.py.
Source font SHA-256 hashes:</p>
<pre>__HASHES__</pre>
<details><summary>Font license</summary><pre>__LICENSE__</pre></details>
</details>
"""
    methods = methods.replace("__HASHES__", esc(json.dumps(DATA["font_hashes"], indent=2)))
    methods = methods.replace("__LICENSE__", esc((ROOT / "OFL.txt").read_text()))
    tables = '<div class="summary-list"><details><summary>Ranked shortlist tables · both cases</summary><div>'
    tables += "".join(pairs_table(case) for case in ("lower", "upper", "mixed"))
    tables += "".join(density_table(case) for case in ("lower", "upper"))
    tables += "</div></details></div>"
    payload = json.dumps(DATA, separators=(",", ":")).replace("</", "<\\/")
    return CSS + SHELL + tables + methods + "<script>const DATA=" + payload + ";</script>" + SCRIPT


def text(draw, xy, value, size=22, fill="#171717", bold=False):
    draw.text(xy, value, fill=fill, font=ImageFont.truetype(BOLD if bold else SANS, size))


def draw_glyph(draw, form, xy, size=190, fill="#171717"):
    path = UPPER if form["case"] == "upper" else SMALL
    font = ImageFont.truetype(str(path), size, layout_engine=ImageFont.Layout.RAQM)
    draw.text(xy, chr(form["code"]), fill=fill, font=font, direction="rtl", anchor="ms")


def pairs_sheet():
    image = Image.new("RGB", (1680, 1590), "white")
    draw = ImageDraw.Draw(image)
    text(draw, (60, 30), "NEW ORKHON / CLOSEST GLYPH PAIRS", 37, bold=True)
    text(draw, (60, 91), "Native raster Dice, mean 20/24/32/48 px. Same em, baseline and orientation. Not confusion probability.", 22)
    for column, group in enumerate(("lower", "upper")):
        x = 60 + column * 810
        text(draw, (x, 155), "LOWERCASE" if group == "lower" else "CAPITALS", 27, bold=True)
        for row, pair in enumerate(top_pairs(group, 4)):
            y = 220 + row * 325
            draw.rectangle((x, y, x + 750, y + 305), outline="#ccc")
            a, b = FORMS[pair["a"]], FORMS[pair["b"]]
            text(draw, (x + 20, y + 15), f'{a["name"]} / {b["name"]}', 25, bold=True)
            text(draw, (x + 20, y + 54), f'U+{a["code"]:05X} / U+{b["code"]:05X}', 16, "#666")
            baseline = y + 225
            for cx, form in ((x + 250, a), (x + 520, b)):
                draw.line((cx - 100, baseline, cx + 100, baseline), fill="#ccc")
                draw_glyph(draw, form, (cx, baseline), 200)
            text(draw, (x + 20, y + 265),
                 f'Raster {pair["raster_mean"]*100:.1f}% · outline {pair["outline_dice"]*100:.1f}% · blur {pair["blur_mean"]*100:.1f}%', 20)
    text(draw, (60, 1550), "AQ's identical capital/lowercase pair is intentional and omitted here. No glyphs have been changed.", 22, "#666")
    image.save(OUT / "similar-pairs.png")


def density_sheet():
    image = Image.new("RGB", (1680, 1870), "white")
    draw = ImageDraw.Draw(image)
    text(draw, (60, 30), "NEW ORKHON / DENSE FORMS AND THICK JOINS", 36, bold=True)
    text(draw, (60, 88), "Body ink uses the actual advance, not the ink bounding box. Each case is compared with its own median.", 22)
    selected = []
    for case in ("upper", "lower"):
        rows = sorted([d for d in DATA["density"] if d["case"] == case],
                      key=lambda d: d["body_ink_pct"], reverse=True)[:6]
        selected.extend(rows)
    selected += [DENSITY["upper-10C38"], DENSITY["lower-10C38"], DENSITY["lower-10C0D"]]
    for i, row in enumerate(selected):
        col, line = i % 3, i // 3
        x, y = 60 + col * 535, 155 + line * 330
        draw.rectangle((x, y, x + 505, y + 312), outline="#ccc")
        form = FORMS[row["id"]]
        heading = f'{row["name"]} · {row["case"]} · U+{row["code"]:05X}'
        text(draw, (x + 16, y + 12), heading, 21, bold=True)
        baseline = y + 180
        body_height = 700 if row["case"] == "upper" else 510
        draw.rectangle((x + 180, baseline - body_height * .19, x + 325, baseline), fill="#f4f4f4")
        draw.line((x + 180, baseline, x + 325, baseline), fill="#bbb")
        draw_glyph(draw, form, (x + 255, baseline), 190)
        text(draw, (x + 16, y + 222),
             f'Body {row["body_ink_pct"]:.1f}% · {row["body_vs_case_median"]:.2f}× median', 20)
        text(draw, (x + 16, y + 253),
             f'Local disk {row["max_ink_diameter"]:.0f} / stem {row["nominal_stem"]}', 19, "#555")
        if i >= 12:
            text(draw, (x + 16, y + 283), "Local-junction check, not overall darkness", 17, "#555")
    text(draw, (60, 1830), "Case medians are recomputed from 42 forms each. Local disk is a blob diagnostic, not a literal stem width.", 21, "#666")
    image.save(OUT / "dense-glyphs.png")


if __name__ == "__main__":
    assert "density" in DATA and len(DATA["pairs"]) == 3486
    save_fragment(body(), "GLYPH-REPORT", "New-Orkhon-Glyph-Audit.html")
    pairs_sheet()
    density_sheet()
    print("Wrote report body and two full-frame proof sheets.")
