#!/usr/bin/env python3
"""Catalogue the layouts of master 0 in a Newmont .pptx template.

Usage: python3 catalog_layouts.py <template.pptx> [--json out.json]

Reads the template live (never a cache): theme name, fonts and colour scheme,
then every layout of the first slide master with its placeholders (idx, type,
name, position/size in pt) and, for text placeholders, the first-level default
font size and bold flag when the layout XML sets them. Other masters are
listed by name only.
"""
import argparse, json, sys

from lxml import etree
from pptx import Presentation
from pptx.opc.constants import RELATIONSHIP_TYPE as RT

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
EMU_PER_PT = 12700
TEXT_TYPES = {"TITLE", "CENTER_TITLE", "SUBTITLE", "BODY", "OBJECT", "DATE",
              "FOOTER", "SLIDE_NUMBER", "VERTICAL_BODY", "VERTICAL_TITLE"}


def pt(emu):  # EMU -> points, 1 decimal
    return None if emu is None else round(emu / EMU_PER_PT, 1)


def theme_info(master):
    part = master.part.part_related_by(RT.THEME)
    root = etree.fromstring(part.blob)
    scheme = root.find(".//a:clrScheme", NS)
    colours = {}
    for el in scheme:
        name = etree.QName(el).localname
        child = el[0]
        colours[name] = child.get("val") or child.get("lastClr")
    fonts = {k: root.find(f".//a:fontScheme/a:{k}Font/a:latin", NS).get("typeface")
             for k in ("major", "minor")}
    return {"theme": root.get("name"), "colour_scheme": scheme.get("name"),
            "fonts": fonts, "colours": colours}


def text_defaults(ph):
    """First-level size (pt) and bold set directly in the layout XML."""
    el = ph._element
    for path in (".//a:lstStyle/a:lvl1pPr/a:defRPr", ".//a:p/a:r/a:rPr",
                 ".//a:p/a:endParaRPr"):
        rpr = el.find(path, NS)
        if rpr is not None and (rpr.get("sz") or rpr.get("b")):
            sz = rpr.get("sz")
            return (int(sz) / 100 if sz else None,
                    {"1": True, "0": False}.get(rpr.get("b")))
    return None, None


def placeholder_info(ph):
    f = ph.placeholder_format
    ptype = f.type.name if f.type is not None else "BODY"
    info = {"idx": f.idx, "type": ptype, "name": ph.name,
            "left": pt(ph.left), "top": pt(ph.top),
            "width": pt(ph.width), "height": pt(ph.height)}
    if ptype in TEXT_TYPES:
        info["size"], info["bold"] = text_defaults(ph)
    return info


def catalog(path):
    prs = Presentation(path)
    masters = list(prs.slide_masters)
    m0 = masters[0]
    data = {"file": path.rsplit("/", 1)[-1],
            "slide_size_pt": [pt(prs.slide_width), pt(prs.slide_height)],
            "other_masters": [{"index": i, "name": theme_info(m)["theme"],
                               "layouts": len(m.slide_layouts)}
                              for i, m in enumerate(masters) if i > 0],
            **theme_info(m0), "layouts": []}
    for i, lay in enumerate(m0.slide_layouts):
        free = sum(1 for s in lay.shapes if not s.is_placeholder)
        data["layouts"].append({"index": i, "name": lay.name, "free_shapes": free,
                                "placeholders": [placeholder_info(p) for p in lay.placeholders]})
    return data


def fmt_ph(p):
    extra = ""
    if p.get("size") or p.get("bold") is not None:
        extra = f" font={p.get('size')}pt" + (" bold" if p.get("bold") else "")
    return (f"    idx {p['idx']:>3} {p['type']:<12} {p['name']!r} "
            f"@({p['left']},{p['top']}) {p['width']}x{p['height']}{extra}")


def print_catalog(d):
    print(f"{d['file']}  size {d['slide_size_pt']} pt")
    print(f"master 0 theme {d['theme']!r}  colours {d['colour_scheme']!r}  fonts {d['fonts']}")
    print("  " + " ".join(f"{k}={v}" for k, v in d["colours"].items()))
    for m in d["other_masters"]:
        print(f"  (skipped master {m['index']} {m['name']!r}: {m['layouts']} layouts)")
    for lay in d["layouts"]:
        print(f"[{lay['index']}] {lay['name']}  (free shapes: {lay['free_shapes']})")
        for p in lay["placeholders"]:
            print(fmt_ph(p))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("template")
    ap.add_argument("--json", dest="json_out")
    args = ap.parse_args(argv)
    data = catalog(args.template)
    print_catalog(data)
    if args.json_out:
        with open(args.json_out, "w") as fh:
            json.dump(data, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
