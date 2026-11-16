#!/usr/bin/env python3
"""Check a deck built from a Newmont template (newmont_deck.py) against the template and Oct 2025 brand rules.
Usage: python check_deck.py deck.pptx --template detailed_view|executive_summary --deck-name "Newmont - X"
         [--free-form-slides 3,7] [--expect-slides 6] [--required-text brief.txt] [--out results.json]
Rules: opens; 960x540; master-0 theme name equals the chosen template's; layouts from the chosen template's master 0
(Everyday-master layouts pass but are flagged); no free shapes (slide-level shapes that are not placeholders or
placeholder-linked frames) on any slide unless listed in --free-form-slides ("PHOTO/CHART/TABLE: replace" boxes are
reported, not failed); no empty placeholders; explicit fonts from brand-values.json (inherited theme fonts are fine);
explicit RGB colours on slide-level shapes, text and charts in the brand-values.json palette or its template-neutral
greys (colours inside the layouts are the template's and are not checked); flat shapes; footer = deck name;
slide-number field wherever the layout has a SLIDE_NUMBER placeholder; required text; slide count.
Prints PASS/FAIL per rule and exits 1 when any rule FAILs; fix every FAIL before delivering. Needs python-pptx."""
import argparse, json, os, re, sys, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brand_sources

VALUES = brand_sources.load_values()  # palette, fonts and neutral greys digested from the guidelines PDF
_P = VALUES["palette"]
PALETTE = {c["hex"].upper() for c in _P["primary"] + _P["secondary"] + _P["tints"]} | {
    c.upper() for c in VALUES["template_neutral_colours"]}
FONTS = {VALUES["fonts"]["deck"], VALUES["fonts"]["accent"]}
REPLACE_BOXES = {"PHOTO: replace", "CHART: replace", "TABLE: replace"}  # drawn by newmont_deck for missing content
BAD_GEOM = {"roundRect", "round1Rect", "round2SameRect", "round2DiagRect", "snipRoundRect"}


def norm(s):
    return re.sub(r"\s+", " ", (s or "").replace("–", "-").replace("—", "-").replace("’", "'").replace("‘", "'")).strip().lower()


def ev(items, n=5):
    return "; ".join(items[:n]) + (" (+%d more)" % (len(items) - n) if len(items) > n else "") if items else ""


def loc(sl, sh, extra=""):
    return "slide %d '%s'%s" % (sl["index"], sh["name"], extra)


def ph_kind(ph):
    t = ph.placeholder_format.type
    return t.name if t is not None else "OBJECT"


def template_info(template):
    """(master-0 layout names, Everyday-master layout names, master-0 theme name) of the chosen template, read live."""
    import catalog_layouts
    from pptx import Presentation
    masters = list(Presentation(brand_sources.resolve([template])[template]["path"]).slide_masters)
    every = [l.name for m in masters[1:] if "everyday" in catalog_layouts.theme_info(m)["theme"].lower()
             for l in m.slide_layouts]
    return {l.name for l in masters[0].slide_layouts}, set(every), catalog_layouts.theme_info(masters[0])["theme"]


def template_layouts(template):
    """Live master-0 layout names (and Everyday-master names) of the chosen template, via brand_sources."""
    return template_info(template)[:2]


def chart_xml_issues(path):
    """Fonts and RGB colours set inside chart parts (they live outside the slide XML)."""
    fonts, colours = [], []
    with zipfile.ZipFile(path) as z:
        for n in z.namelist():
            if re.match(r"ppt/charts/chart\d+\.xml$", n):
                x = z.read(n).decode("utf-8", "replace")
                fonts += ["%s font %s" % (n, f) for f in set(re.findall(r'<a:latin typeface="([^"]+)"', x)) - FONTS]
                colours += ["%s colour %s" % (n, c) for c in set(v.upper() for v in re.findall(r'<a:srgbClr val="([0-9A-Fa-f]{6})"', x)) - PALETTE]
    return fonts, colours


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--template", choices=["detailed_view", "executive_summary"], required=True)
    ap.add_argument("--out", default=None, help="optional JSON results file")
    ap.add_argument("--expect-slides", type=int)
    ap.add_argument("--deck-name", required=True)
    ap.add_argument("--required-text")
    ap.add_argument("--free-form-slides", default="")
    a = ap.parse_args()
    res = []

    def add(text, passed, evidence):
        res.append({"text": text, "passed": bool(passed), "evidence": evidence})

    def finish():
        if a.out:
            with open(a.out, "w") as f:
                json.dump(res, f, indent=1)
        for r in res:
            print(("PASS " if r["passed"] else "FAIL ") + r["text"] + "\n     " + r["evidence"][:400])
        if not all(r["passed"] for r in res):
            sys.exit(1)

    if not os.path.exists(a.file):
        add("The pptx file exists and opens", False, "file not found: " + a.file)
        finish(); return
    try:
        import inspect_pptx
        from pptx import Presentation
        d = inspect_pptx.inspect(a.file)
        prs = Presentation(a.file)
        add("The pptx file exists and opens", True, "%d slides found" % len(d["slides"]))
    except Exception as e:
        add("The pptx file exists and opens", False, "error: %r (check_deck.py needs inspect_pptx.py beside it)" % e)
        finish(); return
    slides, pslides = d["slides"], list(prs.slides)
    if a.expect_slides is not None:
        add("The deck has exactly %d slides" % a.expect_slides, len(slides) == a.expect_slides,
            "found %d slides" % len(slides))
    add("The slide size is 960 x 540 pt (13.333 x 7.5 in)",
        abs(d["slide_w_pt"] - 960) <= 1 and abs(d["slide_h_pt"] - 540) <= 1,
        "size is %s x %s pt" % (d["slide_w_pt"], d["slide_h_pt"]))

    master0 = prs.slide_masters[0]
    try:
        allowed, everyday, theme = template_info(a.template)
    except Exception as e:
        add("Every slide uses a layout of the %s template" % a.template, False, "cannot read template: %s" % e)
        allowed = everyday = theme = None
    if theme is not None:
        import catalog_layouts
        got = catalog_layouts.theme_info(master0)["theme"]
        add("The deck's master-0 theme is the %s template's (%r)" % (a.template, theme), got == theme,
            "deck master-0 theme is %r" % got)
    if allowed is not None:
        bad, flagged = [], []
        for i, s in enumerate(pslides, 1):
            lay = s.slide_layout
            if lay.slide_master.part is master0.part and lay.name in allowed:
                continue
            if lay.name in everyday and lay.slide_master.part is not master0.part:
                flagged.append("slide %d '%s' (Everyday master, cross-template)" % (i, lay.name))
            else:
                bad.append("slide %d layout '%s' is not a master-0 layout of the %s template" % (i, lay.name, a.template))
        add("Every slide uses a named layout of the %s template's master 0" % a.template, not bad,
            ev(bad) or ("all on master 0" + ("; flagged: " + ev(flagged) if flagged else "")))

    free_ok = {int(x) for x in re.findall(r"\d+", a.free_form_slides)}
    bad, boxes = [], []
    for i, s in enumerate(pslides, 1):  # is_placeholder is also true for frames linked to a placeholder (<p:ph>)
        free = [sh for sh in s.shapes if not sh.is_placeholder and i not in free_ok]
        boxes += ["slide %d '%s'" % (i, sh.name) for sh in free if sh.name in REPLACE_BOXES]
        names = [sh.name for sh in free if sh.name not in REPLACE_BOXES]
        if names:
            bad.append("slide %d on '%s': %s" % (i, s.slide_layout.name, ", ".join("'%s'" % n for n in names)))
    add("No free shapes on any slide except free-form slides %s" % (a.free_form_slides or "(none)"),
        not bad, ev(bad) or "none" + ("; replace boxes still to fill: " + ev(boxes) if boxes else ""))

    bad = ["slide %d '%s' (%s)" % (i, ph.name, ph_kind(ph)) for i, s in enumerate(pslides, 1) for ph in s.placeholders
           if ph._element.tag.endswith("}sp") and not ph.text_frame.text.strip()]
    add("No empty placeholders (no 'Click to add' prompts)", not bad, ev(bad) or "none left")

    cfonts, ccolours = chart_xml_issues(a.file)
    bad = [loc(sl, sh, " run %r uses %s" % (r["text"][:30], r["font"])) for sl in slides for sh in sl["shapes"]
           for r in sh.get("runs", []) if r["text"].strip() and r["font"] and r["font"] not in FONTS] + cfonts
    add("Every explicitly set font is Open Sans or Montserrat (theme fonts inherited)", not bad, ev(bad) or "ok")

    bad = []
    def chk(c, where):
        if c and re.fullmatch(r"[0-9A-F]{6}", c) and c not in PALETTE:
            bad.append("%s colour %s" % (where, c))
    for sl in slides:
        chk(sl["background"], "slide %d background" % sl["index"])
        for sh in sl["shapes"]:
            chk(sh["fill"], loc(sl, sh, " fill"))
            chk(sh["line"]["color"], loc(sl, sh, " line"))
            for r in sh.get("runs", []):
                if r["text"].strip():
                    chk(r["color"], loc(sl, sh, " text %r" % r["text"][:20]))
    bad += ccolours
    add("Every explicit RGB colour on slides and charts is in the Newmont palette", not bad, ev(bad) or "all in palette")

    bad = []
    for sl in slides:
        if sl["background_kind"] == "gradient":
            bad.append("slide %d background is a gradient" % sl["index"])
        for sh in sl["shapes"]:
            if sh["has_effects"]:
                bad.append(loc(sl, sh) + " has effectLst")
            if sh["has_p_style"]:
                bad.append(loc(sl, sh) + " has p:style (theme shadow/line refs)")
            if sh["fill"] == "gradient":
                bad.append(loc(sl, sh) + " has gradFill")
            if sh["geometry"] in BAD_GEOM:
                bad.append(loc(sl, sh) + " is %s" % sh["geometry"])
    add("No slide shape has shadows/effects, gradients, 3D or rounded corners", not bad, ev(bad) or "flat")

    bad, nf, nn = [], 0, 0
    for i, s in enumerate(pslides, 1):
        kinds = {ph_kind(p) for p in s.slide_layout.placeholders}
        mine = {ph_kind(p): p for p in s.placeholders}
        if "FOOTER" in kinds:
            nf += 1
            got = mine["FOOTER"].text_frame.text if "FOOTER" in mine else None
            if got is None:
                bad.append("slide %d: footer placeholder missing" % i)
            elif norm(got) != norm(a.deck_name):
                bad.append("slide %d: footer %r != deck name" % (i, got[:60]))
    add("Footer reads %r wherever the layout has a footer" % a.deck_name, not bad, ev(bad) or "%d footers ok" % nf)

    bad = []
    for i, s in enumerate(pslides, 1):
        if "SLIDE_NUMBER" in {ph_kind(p) for p in s.slide_layout.placeholders}:
            nn += 1
            if not s._element.xpath('.//a:fld[@type="slidenum"]'):
                bad.append("slide %d on '%s'" % (i, s.slide_layout.name))
    add("A slide-number field is on every slide whose layout has a SLIDE_NUMBER placeholder", not bad,
        ("no slidenum field: " + ev(bad)) if bad else "%d slide numbers ok" % nn)

    if a.required_text:
        alltext = norm(" ".join(r["text"] for sl in slides for sh in sl["shapes"] for r in sh.get("runs", [])))
        with open(a.required_text, encoding="utf-8") as f:
            lines = [norm(l) for l in f.read().splitlines() if l.strip()]
        miss = [l for l in lines if l not in alltext]
        add("Every required text line appears verbatim in the deck", not miss,
            ("missing %d of %d: " % (len(miss), len(lines)) + ev(miss)) if miss else "all %d lines found" % len(lines))
    finish()


if __name__ == "__main__":
    main()
