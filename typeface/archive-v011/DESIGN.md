# New Orkhon / Yeni Orhun

**A proposed text hand, version 0.11.** Forty-two encoded Orkhon signs with
uppercase and lowercase forms, compiled into installable TrueType fonts. This is speculative
type design informed by script history, not a recovered historical stage or
an inevitable future for Orkhon.

## Revision 0.11: AR restored; asymmetric AT

- **AR / U+10C3A, lowercase:** remove the 0.10 local taper. Its compiled
  outline and advance now exactly match 0.9.1, including the corrected
  baseline-reaching body. This is not a rollback of the baseline correction.
- **AT / U+10C43:** both t signs in historical `tuta` (𐱃𐰆𐱃𐰀) are this
  character. Replace the symmetric roof, central suspension and eye with a
  left upright, one right-hand bowl and a horizontal top arm. The eye is
  reconstructed as the side bowl; the roof is levelled into the arm. This
  is an authored writing-route change, not smoothing the rune's contour.
- The lowercase bowl fills baseline to x-height; its stem reaches ascender
  height 700. The capital has a larger bowl. A slanted arm was also rendered
  as a study; the horizontal arm is selected to share the family's level bars.
  The arm projects past the stem on the left. A right-only arm was rejected
  because lowercase AT/AY overlapped 88.7%; the overhang reduces that to 75.8%
  at native 20/24/32/48 px while retaining the requested b-like body.
- **AET / U+10C45** (the other t letter) is not present in `tuta` and is
  unchanged. All other 0.10 decisions remain.

Exactly three glyph records change from `archive-v010`: capital/lowercase AT
and lowercase AR. The remaining 81 outlines and advances are byte-identical.
AT has one counter in each case and deliberately lacks bilateral symmetry.

Reproduce: `python3 build.py`, `python3 validate.py`,
`python3 at_revision.py`, `python3 glyph_similarity.py`,
`python3 glyph_similarity.py density`, `python3 glyph_report.py --update`,
and `python3 showcase.py --update`. `at_revision.py` renders both top-arm
directions, the exact AR restore, and the word at native text sizes.
Font-name and head revision are 0.911. Fixed font timestamps make clean
builds byte-reproducible. Reader performance remains untested.

## Revision 0.10: distinction and local color

- BASH: continuous figure-eight route, with both counters retained.
  Capital body coverage 52.9% → 40.3%; lowercase 51.5% → 43.1%.
- AEK: close the head into a reversed-P bowl; keep EP open. Mean native
  raster Dice falls 92.5% → 79.1% in capitals and 92.2% → 28.7% in lowercase.
- ESH: raise the link to close the fork; retain AEL's open Y. Overlap falls
  92.2% → 83.9% in capitals and 90.2% → 73.2% in lowercase.
- ENC: widen and differentiate the bowls rather than thinning all strokes.
  The upper counter is smaller than the lower. An equal-bowl trial was
  rejected because it increased lowercase OP similarity.
- AG/AR/OQ/IC: cosine-blended local tapers on incoming strokes; unaffected
  uprights and terminals retain the regular stroke model. AR's free return,
  not its post junction, was the main local blob. Lowercase OQ retains the
  pole-right skeleton (advance 580, one unit less than 0.9.1);
  capital OQ retains its upright skeleton.

Exactly 13 glyph records change from the frozen `archive-v091` baseline:
capital AEK/ENC/IC/OQ/ESH/BASH and lowercase AG/AEK/ENC/OQ/AR/ESH/BASH.
All other compiled outlines and advances are byte-identical. OE retains its
approved construction, baseline and 90/64 model; AQ remains exactly identical
across cases; AN and the corrected EZ/AD/AER placements are unchanged.

Remaining pairs: capital AEN/ELT (86.8%) and OEK/OP (84.6%).
Capital OQ/AES increases 75.1% → 79.1% as the heavy join loses ink; the report
records that tradeoff. OE remains the darkest lowercase.
No score is a confusion probability or proof of reading improvement.

Reproduce: `python3 build.py`, `python3 validate.py`,
`python3 glyph_similarity.py`, `python3 glyph_similarity.py density`,
`python3 glyph_report.py`, and `python3 differentiation.py`.
The report body fragments compile with the artifact kit; supplied standalone
HTMLs work offline. Once compiled, `python3 differentiation.py --update` and
`python3 glyph_report.py --update` refresh their bodies offline.
`python3 showcase.py --update` refreshes embedded fonts.
Numerical font-name version is 0.910 for release 0.10, following 0.901 for
0.9.1. Source geometry and metrics are tested, not reader performance.

The following sections record earlier revisions, not the current scope.

## Revision 0.9.1: selected pole-right OQ

The user selected the **pole-right** sideways form for lowercase
OQ / U+10C38. The upright 0.9 form is archived. The selected letter
turns its stroke skeleton 90°, adjusts the width to the lowercase
family and is re-stroked at upright 82/59 contrast (not a rotated
bitmap or rotated serif slabs). Its two curved returns fill 0..510;
the pole projects right rather than descending. The advance is 581,
the ink centre y=255.02. The capital, other 41 lowercase forms and
all other metrics stay identical to 0.9. The selected glyph matches
the pole-right study in compiled outline and metrics. Both candidate
alphabets pass distinct-raster checks at 20/24/32/48 px; reading
performance remains untested.

The revised proof compares the former upright OQ, unselected pole-left
A and released pole-right B in the same historical word at text sizes.
The offline HTML at that revision embedded 0.9.1. Archived 0.9 fonts and source
are retained in `archive-v09`.

## Revision 0.9: body alignment, AL spacing and unicasal AQ

- **AR / U+10C3A:** deepen the free return from an ink minimum of +55.55
  to +0.03. The post still spans 510 to -190.
- **OE / U+10C07:** deepen the upper return from +128.04 to +0.05.
  Preserve the 510/-190 posts, construction and 90/64 stroke model.
  This supersedes the earlier exact-translation constraint: lowering the
  whole glyph would also lower its top and push its descender out of line.
- **AL / U+10C1E:** left sidebearing 32 to 18, advance 447 to 433.
  The shape is unchanged, translated left by 14; right spacing is unchanged.
- **AQ / U+10C34:** lowercase deliberately reuses its capital at full
  700-unit height, with identical contours and metrics. Both cases share
  one source definition rather than duplicated paths.
- **AN / U+10C23:** no change. Bounds -10..520 match the other round
  lowercase forms; its ink centroid is 255.04 against a body centre of 255.
  At 105 px/em the 10-unit top overshoot is about one pixel above the
  510 guide. Neither the font nor the proof grid has a measured y offset.
- **OQ / U+10C38:** no change yet. Its wings currently join at -190 and
  their tops are at 185: much of the upper body is an isolated pole.
  Its low ink centroid (138.95) describes the bottom-heavy distribution,
  not proof of a reading-performance problem. Plan: move the junction to
  the baseline, raise and shape the wings with the shared return grammar,
  keep only the pole below baseline, then compare against Y/IC/AS and
  test 20/24/32/48 px before selecting a redesign.

### OQ sideways alternative (as studied in 0.9)

The user proposed turning OQ sideways instead. `oq_study.py` compares
the two orientations without changing the release font. The pen skeleton
is rotated ±90°, its horizontal span is condensed to family proportions,
and its vertical endpoints are refitted to the 0..510 body. Curves are
re-stroked with upright 82/59 contrast; rotated serif slabs are not retained.
This is a typographic rotation study, not a literal rotation of a bitmap.

Both have advance 581 and ink centres near y=255. The native-size word
proof shows 24/32/48 px; both candidate alphabets pass unique, nonempty
rasters at 20/24/32/48 px. This does not establish readability. The
designer initially preferred left-projecting-pole A because B is closer
to AEG's existing open-right construction. The user chose B. Its pole
projects past the bowl, unlike AEG's contained bar. OQ remained identical
to 0.8 in the 0.9 release, then changed in 0.9.1.

In 0.9, exactly four lowercase glyph records changed from 0.8; all capitals and
every other lowercase outline/advance remain byte-identical. Exact-scope,
body-extrema, AL-translation, AQ-equality and AN-alignment checks enforce
these claims. The 0.8 fonts and source are retained in `archive-v08`.
The showcase at that revision embedded 0.9.1.

### Rebuild the current revision

Install `requirements.txt`, then run `python3 build.py`, `python3 validate.py`,
`python3 feedback.py`, `python3 case_proofs.py`, `python3 specimen.py`,
`python3 oq_study.py` and `python3 report.py`.
`python3 showcase.py --update` refreshes the embedded fonts and body inside
the supplied standalone HTML while retaining its bundled artifact shell.
Experimental OQ fonts are generated only under `studies/`. The main build
selects pole-right B; A remains a study.

## Revision 0.8: corrected placements — EZ, AD and AER

The user corrected the sketch targets: **1 → EZ, 2 → AD, 3 → AER**.
These are lowercase revisions, not changes to the capital alphabet.

- **EZ / U+10C14:** closed tilted loop, short lower upright and falling leg.
  The loop-and-leg outline is moved intact from its mistaken 0.7 placement.
  EM retains its open bowl, so the two signs are not collapsed.
- **AD / U+10C11:** a shared upright/top arm feeds two open returns,
  replacing the paired serpentine strokes. This outline is also moved
  intact from its mistaken 0.7 placement.
- **AER / U+10C3C:** two full-body m-like shoulders, with the central pole
  continuing to -190. This selects the descending alternative originally
  discussed for AER, rather than the plain m chosen for the mistaken OT target.
- **ELT / U+10C21, AL / U+10C1E, OT / U+10C47:** restored exactly to 0.6,
  including their outlines and advances. AL is again a dotless j.

All capitals and every other lowercase outline and advance are unchanged
from 0.6. Automatic comparisons require exactly EZ/AD/AER to differ from
0.6, and exactly those three plus the restored ELT/AL/OT to differ from 0.7.
The new proof shows the correct targets against 0.6, with red-old/blue-new
overlays, plus a separate restoration row against the misplaced 0.7 forms.
These remain speculative authored constructions, not historical evidence.

## Revision 0.7: superseded, misplaced sketches

Development history only: the assignments below were mistaken and are
reversed in 0.8. They do not describe the current font.

- **ELT / U+10C21:** the first option, a closed tilted loop, short lower
  upright and falling leg. EM retains its open bowl, so the two signs
  are not collapsed.
- **AL / U+10C1E:** the right-hand option, a shared upright/top arm with
  two open returns. This supersedes the dotless-j lowercase from 0.6.
  It has no descender; ENC retains closed bowls on its taller ascender.
- **OT / U+10C47:** the plain m-like option, with two rounded shoulders
  and three baseline feet. No central descender. Its shoulders follow
  AEN's single n without duplicating that letter.

All three occupy 510 to 0. All capitals and every other lowercase outline
and advance are unchanged from 0.6, including EZ, AD and AER. Validation
compares compiled outlines and metrics against the archived 0.6 font
and requires exactly these three differences.

The dedicated proof shows before/after at one em size, common height
guides and red-old/blue-new outline overlays. The full alphabet now
encloses each glyph pair with its own label and code point, so a crop
cannot accidentally attach the next row's name.

## Revision 0.6: body before tail

Development history: AL's dotless-j form was temporarily superseded in 0.7,
then restored in 0.8. AER's narrow roofs become m-like shoulders in 0.8.
The other body corrections remain current.

The 0.5 lowercase had a structural mistake: several bodies were perched
near the x-height, above long legs, while other supposed tails still ended
at the baseline. Checking only the overall bounding box did not detect it.
The correction separates the main body from the tail before fitting either.

- **AEN:** a single N/n replaces the crowded double N and double shoulder.
  No other sign in the present inventory uses that construction.
- **Lowercase AG:** literally ж: a central upright and four curved arms,
  without a descender. The alpha ribbon and cursive-ж approximation are
  superseded. Uppercase AG retains its three separate pieces.
- **Lowercase I/EP/AEK:** curved f-like heads at 510; posts descend to -190.
  I and EP are mirrored partners; AEK keeps EP's head plus a crossbar.
- **Lowercase OE:** no shape change. The uppercase outline, including its
  stroke weight, is translated down exactly 190 units. Both tops meet the
  lowercase body line; the left post descends.
- **Lowercase AL:** a dotless Latin j, with a curved hook below the baseline.
- **Lowercase EM/AEB:** the bowl/eye fills the x-height-to-baseline band;
  only the exit leg or pair of legs descends.
- **Lowercase AS/IC:** one/two deep returns fill that same body band;
  only the straight right post continues below the baseline.
- **Lowercase ESH:** its Y body reaches the baseline; the short descender
  carries the crossbar. AEL follows the same Y-body construction.
- **Related descending forms:** AER's two roofs occupy the body band;
  AQ/AR/OQ posts no longer rise to the ascender line. All descending
  lowercase forms now share the 510 body top and -190 descender line.

The before/after sheets show the actual lowercase body band, rather than
only reporting a top and bottom. Regression checks measure the bodies
separately from the tails and verify that OE is a pure translation.
The diagnostic 20–88 px sheet includes the revised signs, not just words
that happen to omit most of them. These checks do not prove reader performance.

## Revision 0.5: redraws, thickness, then first lowercase

Development history: the double-N AEN, lowercase ribbon AG and lowercase
body proportions described here were replaced in 0.6.

- **AEN:** two literal full-height Ns share the middle pole. Its lowercase
  counterpart has two genuine small-n shoulders sharing one middle upright.
  The old staggered saw interpretation is no longer the current capital.
- **EZ:** a rounded upper cup joins the two upper-reaching strokes.
  It is no longer differentiated from AEN merely by rounding similar Ns.
- **AG:** uppercase returns to its three separate pieces. The lowercase is
  an alpha-like ribbon with a pole below; the cursive-ж alternative is
  retained in the comparison sheet, not selected as the default.
- **AEG:** a *mirrored* rounded Cyrillic э, opening right with a horizontal
  arm into the left bowl. The direct э study was the wrong orientation.
- **ENT:** a dotless u. Removing the three dots was explicitly requested.
  The resulting outline does not duplicate another current sign, but this
  is a deliberate simplification of the historical reference.
- **ENC:** two bowls on a common left spine, a B-like proposal replacing the
  uneven bent zigzag. It changes the old counter count and needs reader testing.
- **AS:** one rounded upper return and a pole, using the same construction
  as IC's two returns. It is no longer a pinched two-horn S.
- **OT:** two symmetric hat tips meet a straight-sided inverted-u roof.
- **EC:** the lambda's right side space decreases from 26 to 8 units,
  independently of the later shared weight change.
- **EM:** the R-like bowl and leg remain the default. A one-crossing hybrid
  and a closer three-stroke chevron were compared: both crowded their joins.
  The comparison is retained so the lost crossings are explicit, not hidden
  behind a claim of inevitable evolution.

### Thickness audit

FontForge explains optical differences between horizontal, vertical and
diagonal strokes [S10]. Equal measurements do not guarantee equal apparent
weight. Ahrens and Mugikura describe reduced contrast for small optical sizes
[S11]. Neither source supplies a universal numerical ratio.

The chosen text compromise keeps 90-unit upright strokes and raises the thin
envelope from 46 to 64. A's arm centers move with the new half-thickness so
the cap and baseline do not clip away the added ink. A also receives paired
bracketed serifs. The shared serif lip grows from 14 to 20 units, its bracket
depth from 48 to 58, and its overhang from 24 to 30 per side. Actual raster
proofs run from 20 to 130 px; this is one text master, not an optical-size family.

### Using lowercase

Old Turkic has no Unicode uppercase/lowercase pairs. These are **font forms**
of the same 42 encoded signs, not new characters, a case-mapping standard or
a proposal to repurpose Latin code points.

- `NewOrkhonText-Regular.ttf`: capitals by default; OpenType stylistic set
  `ss01` selects all lowercase counterparts.
- `NewOrkhonTextLowercase-Regular.ttf`: lowercase by default for apps without
  stylistic-set controls; `ss02` restores capitals in that font.
- On the web, select the main font and use `font-feature-settings: "ss01" 1`
  for a lowercase span. Unicode `toLowerCase()`/`toUpperCase()` cannot perform
  this proposed casing; mixed case requires formatting, not a different string.

The current lowercase body is 510 units, ascenders 700, and descenders to -190.
Stem/thin envelopes are 82/59, except OE's preserved 90/64 outline.
Forms are independently fitted at their actual
size, not raster images of scaled capitals. Some simple forms necessarily
remain related, while single-n AEN, u ENT, ascender bowls and descending forks
change construction. Both fonts contain the same 89 glyphs (84 signs plus
space, divider, comma, period and .notdef) with different default cmaps.
The OpenType and default-lowercase paths have identical outlines/metrics;
renderer autohinting can still make their raster antialiasing differ.

## Revision 0.4: AEN/EZ, the dotted u, and joined AG

This revision tests the user's alternative family assignment rather than
rounding both AEN and EZ into similar silhouettes:

- **AEN, U+10C24:** a double-sawed N. Three supplied centerlines make the
  inclined pole and its two opposed saws. The pole now leans about 17 degrees,
  rather than 12 degrees. Its side strokes still join at different levels,
  roughly 155 and 545 units, preserving the staggered construction.
- **EZ, U+10C14:** the soft three-stroke option moves here. A pole inclined
  about 12 degrees carries two rounded side returns, both meeting at the
  middle. Their curves leave the outer posts tangentially, rather than
  making angular knees. The junction positions and curvature distinguish it
  from the sawed AEN; that distinction still needs reader testing.
- **IC, U+10C31:** retain the linked three-tip head, but replace the sloping
  tail with a genuinely vertical pole. Its straight right edge now receives
  stem-class side spacing.
- **ENT, U+10C26:** use the ordinary u construction: two straight posts joined
  by a rounded bottom. The three dots remain separate. They are features of
  the encoded reference sign, not decorative texture; making the bowl simpler
  does not by itself justify removing them.
- **AG, U+10C0D:** the reference and 0.3 have two opposing horns plus a detached
  lower staff. Join two matching cupped strokes to one staff. The open cupped
  space distinguishes AG from the straight-branch Y. A tighter returning-hook
  alternative was rejected because its extra reversal pinched that space.
  Joining the pieces is an authored modernization, not an attested cursive
  development or a claim that the historical pieces were mistakenly separate.

That revision used the sawed AEN / soft EZ alternative. The softer AEN
alternative was compared during iteration; this is an optical design choice,
not an optimization result. The source centerline count excludes serif
envelopes and does not claim an experimentally verified stroke order.

`revision-04.png` compares all five signs with both Noto and the delivered
0.3 font. Repeated-sign and 20–100 px proofs test them with the rest of the
alphabet. Automated checks cover their intended junctions, AEN/EZ half-turn
balance, AG mirror balance, the straight IC pole and ENT's three distinct dots.
The 0.3 decisions below are retained as the development history; 0.4
supersedes its curved AEN and sloped IC.

## Revision 0.3: movement, space and weight

The critique behind this revision was substantive: the set was too thin,
A's flag-and-hook construction was unconvincing, ÆN's construction was wrong,
and EM's asymmetry had no writing rationale.

- **Weight:** the vertical/horizontal stroke envelope changes from 64/30 to
  90/46 units. Serifs grow with the stems. Letters are not stretched horizontally;
  their ink widths and advances are fitted again after expansion. Proofs compare
  the same strings at 100, 64, 44, 32, 24 and 20 pixels.
- **A, U+10C00:** level the opposed end returns and incline the long connecting
  stroke into a mirrored-Z construction. Opposed returns plus a diagonal
  distinguish it from I's single top return and upright. This is a proposed
  redrawing, not an attested cursive form.
- **Return family:** I, AL, AEK, EP and OEK share level arms and short terminal
  beaks rather than unrelated flags. Their top/bottom placement, arm count,
  stem direction and lower shoulder remain different.
- **ÆN, U+10C24:** the previous revision put the left post on the **upper** half;
  the reference has it on the **lower** half. Correct that error. Incline the
  central stroke about 12 degrees and place corresponding rounded shoulders
  in the opposed wedges. The drawing corresponds under a half-turn, including
  its open spaces. This is a chosen construction and optical hypothesis,
  not evidence of historical stroke order or proven readability.
- **EM, U+10C22:** test both corner relaxation and new stroke routes. The chosen
  proposal returns an upper bowl to the left and then exits diagonally down
  right, like R without its left upright. It deliberately opens the old
  diamond counter and drops crossed-tail construction. Its distinction now
  relies on the bowl-and-leg combination; it is not topology-preserving.
  Symmetry is not imposed at the expense of that motion.
- **AN / ENY, U+10C23 / U+10C2A:** AN's ends now turn inward around a full
  open bowl, like reversed C. ENY's small angular notch is reinterpreted as
  the waist between two bowls, like Western 3. This changes the distribution
  of white space, rather than pasting a notch onto a parenthesis.
- **AEL / EC, U+10C20 / U+10C32:** the plain upper fork becomes serifed Y.
  The lower fork becomes lambda: its curved head continues through the right
  descending stroke while the left leg rises into it. They are not simple
  rotations of a common outline. These comparisons describe **shape**, not
  Latin or Greek sound values.
- **IC, U+10C31:** the three upper tips connect through two rounded returns,
  carried by a sloping right-hand tail: a Latinized, left–right mirrored
  Arabic numeral ٣. It is neither Western 3 nor a 180-degree rotation of ٣;
  its upper-tip orientation remains consistent with the reference.
- **ESH, U+10C41:** the reference actually has **two** upper tips and a low
  crossbar. The prior extra middle prong was another construction error.
  Correct it to Y plus bar, rather than extending the new three-tip IC
  construction to a sign that does not have three tips.
- **Flat joins:** inclined strokes ending in baseline/cap serifs are trimmed
  to those alignment edges before vertical fitting. A diagonal no longer
  projects below its foot and leaves a raised, ragged-looking serif.

### The pen-motion experiment

`ductus.py` compares three **assumed**, explicitly supplied routes:

1. Three lifted strokes retaining the diamond and crossing.
2. A single retraced route covering that construction.
3. An authored one-stroke bowl-and-leg route.

It resamples each route at 96 equal time stations and minimizes
`sum(||q - p||²) + 1200 * sum(||Δ³q||²)`, holding endpoints fixed.
The first term keeps the result near its supplied path; the second discourages
rapid changes of acceleration. The reference parametrization traverses the
polyline at constant speed. Discrete jerk regularization is inspired by
Flash and Hogan [S9], **not** their exact constrained minimum-jerk model.
There is no calibrated muscle model, measured handwriting, learned stroke
order, grip, pressure model, or optimization across all possible routes.
The printed EM centerline actually uses the computed bowl-and-leg trajectory;
serif and stroke-envelope treatment are separate print decisions.

Smoothing the original three routes rounds the corner but retains the
diamond. Retracing avoids lifts but introduces extra travel. The bowl-and-leg
route is simpler **because its route was changed by the designer**, not because
the smoother independently discovered an R. Travel figures depend on the
supplied dimensions; they are not measured writing times or proof of a best
letter. Fourier filtering could also smooth a supplied path, but cannot
choose which stroke to omit or how to resegment the glyph.

### Extension across the alphabet

Use one pen construction consistently within a family, then fit its white space:

- Opposed/single returns: common arm, endpoint and return direction.
- Staggered posts: use shoulders that occupy their wedges, not decorative
  humps unrelated to the connecting stem.
- Bows: common curvature and stroke contrast; turn ENY's notch into a
  structural waist and keep EM's leg.
- Forks: Y/lambda for the simple fork pair, connected returns for the trident.
  Preserve prong count, orientation and the crossed fork's separate bar.

The family proofs distinguish redrawn returns, ÆN/EM, open bowls and forks
from constructions retained from 0.2 with heavier strokes. The further-family
sheet compares the reference, the delivered 0.3 font, and the current
drawing, including the Arabic numeral that prompted the trident change.
It does not claim that a motor simulation has redesigned all 42 signs.

## What history actually supports

There is no universal rule that old angles become modern curves. Latin
uncial rounded some capital forms; later Gothic writing introduced more
angular constructions. Renaissance humanists deliberately returned to
Caroline models. Early Greek minuscule developed from informal writing,
not by smoothing each majuscule outline. Cyrillic civil type was a deliberate
redesign involving new shapes and an alphabet reform.

Those are different mechanisms: a change of tool or writing practice,
standardization, selective revival, and explicit reform. Visual similarity
alone does not demonstrate a historical relationship between scripts.

The following names are **our design principles**, inferred from these
examples, not established historical laws.

## Seven tenets and their applications

### 1. Ductus over contour

**Evidence:** Latin uncial used round constructions particularly visible in
E, M and U; Greek minuscule grew from earlier informal/cursive practices.
[S1, S2]

**Inference:** Start from a plausible movement of the pen rather than preserve
every segment of an inscriptional outline.

**Application:** Back-b gets a returned neck and a bowl; back-d's two
zigzags become two serpentine strokes. A consistent contrast model and
bracketed stem terminals unify the font. These are new authored paths,
not skeletons extracted from Noto.

### 2. A shared vertical system

**Evidence:** Half-uncial developed ascenders and descenders. Caroline and
Greek minuscule use a four-line system rather than a uniform two-line
majuscule height. [S1, S2]

**Inference:** A text script can reorganize the vertical relationships of
letters, not merely change their edges.

**Application:** The first draft used a premature mixture of low bowls, tall
stems and descenders. It did not hold together. Revision 0.2 instead uses
a common 700-unit unicasal body on a zero baseline in a 1000-unit em,
with 10-unit optical overshoots on selected round edges. The plain fork
and trident are distinguished by their actual prongs, not arbitrary
different heights. Minuscule is a historical option, not a mandatory
destination for every modern script.

### 3. Reconstruction over tracing

**Evidence:** Greek majuscule and minuscule are substantially different
constructions; humanist Latin selectively revived Caroline writing rather
than preserving the immediately preceding Gothic forms. [S1, S2]

**Inference:** Letter identity need not mean one-to-one survival of corners,
strokes, or counters.

**Application:** The upper square of rounded-front-k opens into a cap arm;
its lower tier becomes an arch. This intentionally changes the old
enclosure. The square aš sign becomes an oval. Preserve a learnable
relationship, not an archaeological tracing.

### 4. Family grammar over isolated inventions

**Evidence:** Caroline was a clear, uniform book script assembled from
predecessor traditions. Cyrillic civil type deliberately regularized and
redesigned forms for printing. [S1, S3]

**Inference:** Repeated construction should be systematic across an alphabet.

**Application:** p and front-k share left-arm construction; l², č/i
and š share a fork vocabulary but differ in prongs and crossbar. The
n and ny bows share curvature but retain the ny notch. Family membership here
is a design proposal, not a claim that all paired signs were graphically
related historically.

### 5. Distinctness before economy

**Evidence:** Greek minuscule ligatures could share or omit strokes; scribes
also added extensions or spacing to avoid ambiguous readings. [S2]

**Inference:** Ease of production is constrained by the distinctions readers
need. Simplification is not always progress.

**Application:** Keep the second shoulder of r², the š crossbar and the ny
waist. ENT's three dots are deliberately removed in 0.5 after checking for
inventory collisions, rather than treating every mark as inviolable.
Do not merge the two b signs or the two
n signs merely to reduce the inventory. Front/back pairs still have
different identities.

### 6. Optical rhythm over equal boxes

**Evidence:** Modern type design uses overshoot for round and pointed
forms. Fernando Mello, drawing on Tracy, Smeijers and Kindersley, explains
why inner and outer white space must be balanced and why equal numerical
gaps do not produce equal perceived space. These are typographic engineering
precedents, not palaeographic laws. [S4, S6]

**Inference:** A coherent alphabet requires unequal measurements in some
places, not identical boxes.

**Application:** Selected round forms reach 710/-10 against a 700/0 body.
The oval and closed bowls establish related counter proportions. Side spaces
are assigned by the shape of each edge: stem, round, diagonal or open,
then examined in repeated and mixed strings. They are not identical margins
or monospaced boxes. The 90-unit vertical and 64-unit horizontal stroke
envelopes are continuous, united geometrically at joins, and fitted before
the font advances are calculated. Stem serifs are bracketed, not added to
every arbitrary endpoint. The double-roof stem ends at its valley.

This spacing system is a starting fit plus visual review, not an automatic
formula claiming to solve optical balance.

### 7. Separate typeface reform from alphabet reform

**Evidence:** Cyrillic civil reform changed both forms and inventory.
These are separable decisions, not one inseparable operation. [S3]

**Application:** Change outlines only. Keep the existing Orkhon Unicode
characters and right-to-left order. Do not silently invent distinct modern
Turkish vowel letters or signs for f/v/c/j/h. The font does not fix or
translate an orthography. Such changes require a separate proposal.

## Reading the specimens

Gray references are **Noto Sans Old Turkic**, a modern reference font, not
facsimiles of inscriptions. Black forms are New Orkhon. Both represent the
same encoded signs. Comparison sheets proceed left to right for convenience;
actual Orkhon words run right to left.

The text sheet uses illustrative modern Turkish transliterations with vowels
written out. It does not reproduce historical spelling. Words were chosen
to avoid the unsupported modern consonants; no claim of reversible
transliteration is made. The earlier converter is not an authority for the
historical orthography.

## What is not proved

- No reader study or handwriting-speed trial has established better
  readability, learnability or faster writing. Stroke counts describe only
  the explicitly assumed routes.
- This is not a production family: no hinting, kerning, italic, bold,
  contextual alternates, or separate optical sizes yet.
- The fonts cover 42 Unicode signs explicitly named ORKHON, not the full
  Old Turkic block or Yenisei variants. It also contains space, full stop,
  comma and the two-dot divider U+205A.
- Font loading, 42 forms in each case, valid integer contours, fitted advances,
  the non-protruding roof, separate uppercase AG parts, dotless ENT, distinct
  AEN/EZ construction, mirrored AEG, straight IC pole, OT symmetry and actual
  A-arm thickness are checked automatically. The 0.6 regressions additionally
  check body proportions, curved descending returns, dotless-j AL,
  single-n AEN, literal ж AG and OE's unchanged translated outline.
  Tests also cover the motion
  objective, both OpenType maps, equivalent glyph outlines between fonts,
  RTL ordering and distinct nonempty rasters per case at 20/24/32/48 px. Distinct rasters
  do not prove that readers can distinguish them easily.

## Sources

**S1 — University of Zurich, Ad fontes: history of Latin scripts.**
Sections: Uncial and Half-Uncial; Insular Scripts; Caroline Minuscule;
Humanist Minuscule and Cursives. Also documents the adoption of runic
wynn and thorn into manuscript writing: an actual rune-to-book-script
precedent, but not proof of an Orkhon genealogy.
https://www.adfontes.uzh.ch/en/tutorium/schriften-lesen/schriftgeschichte/humanistische-minuskel-und-kursive/

**S2 — Timothy Janz / Vatican Library: Introduction to Minuscule Bookhands.**
Quadrilinear organization, development from informal writing, ligatures
and deliberate disambiguation.
https://spotlight.vatlib.it/en/greek-paleography/feature/2-introduction-to-minuscule-bookhands

**S3 — Presidential Library: Peter the Great approved the new alphabet.**
1708 printing and 1710 final approval; simultaneous redesign of forms
and alphabet composition. Its claim of simpler/rounder forms describes
this particular reform, not all script evolution.
https://www.prlib.ru/en/history/619018

**S4 — Ralf Herrmann, Typography.Guru: Overshoot.**
https://typography.guru/term/overshoot-r82/

**S5 — Unicode Consortium: Old Turkic code chart.**
Encoding and reference glyph labels; this is not an orthographic handbook.
https://www.unicode.org/charts/PDF/U10C00.pdf

**S6 — Fernando Mello: How to space a typeface.**
Optical centre; counterspace versus inter-letter space; straight, round
and mixed controls. Directly informed the 0.2 spacing revision.
https://www.myfonts.com/a/font/content/how-to-space-a-typeface

**S7 — Society of Fonts: Spacing a Font, Part 1.**
Practical account of the Tracy method. Distinguishes basic fitting from
pair kerning; explains repeated upright/round control strings.
https://www.societyoffonts.com/2018/09/19/spacing-a-font-part-1/

**S8 — Anton Koovit: U8.**
A designer's account of turning inconsistent historical station lettering
into a text face and checking weight at the intended physical size.
This informed the proofing method, not a claim that U8 and Orkhon
are historically related.
https://www.antonkoovit.com/typefaces/u8

**S9 — Tamar Flash and Neville Hogan: The coordination of arm movements:
an experimentally confirmed mathematical model (1985).**
Minimization of integrated squared jerk for planar voluntary arm movements.
This supplies the smooth-motion idea, not a claim that our regularized
routes are experimentally validated handwriting or historical reconstructions.
https://www.jneurosci.org/content/5/7/1688

**Reference font and license:** Noto Sans Old Turkic (Google), SIL Open Font
License 1.1. New Orkhon's paths were authored independently by visual
reference; Noto's outlines are not used by the build. The license and both
copyright notices are included with the source package.
https://github.com/notofonts/old-turkic

**S10 — Design With FontForge: Trusting Your Eyes; FontForge tutorial:
consistent stems, serifs and heights.**
Horizontal, diagonal and height illusions; measure a small number of shared
stems, then judge the actual design rather than treating numbers as proof.
https://designwithfontforge.com/en-US/Trusting_Your_Eyes.html
https://fontforge.org/docs/tutorial/editexample3.html

**S11 — Tim Ahrens and Shoko Mugikura: Size-specific adjustments to type designs.**
The public overview describes reduced contrast, increased width/x-height and
other compensations for small sizes. We read the overview, not the entire book.
https://justanotherfoundry.com/size-specific-adjustments-to-type-designs

## Build and inspect

```sh
python3 -m pip install -r requirements.txt
python3 build.py
python3 specimen.py
python3 case_proofs.py
python3 validate.py
python3 report.py
```

Pillow must have libraqm support for correct RTL rendering. Strings are
stored in logical order, passed with `direction="rtl"`, and never reversed
by hand. The renderer tests that the initial t² in Türk lands at the
right edge.

Proof labels and PDF text use DejaVu Sans/Serif from
`/usr/share/fonts/truetype/dejavu/` (Debian/Ubuntu package `fonts-dejavu-core`).
On another platform, adjust those label-font paths in `specimen.py` and
`report.py`. Noto and the delivered 0.4 comparison font are bundled.
Installing and using the finished TTF does not require Python or these tools.

Development checks used Ruff 0.17.1 and mypy 1.18.2:

```sh
ruff check build.py ductus.py lowercase.py case_proofs.py specimen.py validate.py report.py
python3 -m mypy
```
