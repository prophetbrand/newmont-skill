#!/usr/bin/env python3
"""Build Newmont decks from the approved template's NAMED layouts (free-form slides only when no layout fits).
Usage:  d = Deck("executive_summary", "Newmont - [Deck]", date="[Month Year]", request=text, routing=route_result,
                 activation_path="direct: deck/presentation/slides", asked=False)   # activation_path is required
        d.roles("Three Column Panels")   # role -> idx, resolved live from the layout's placeholders
        d.add("Three Column Panels", title="..", lead="..", col1=["point", ("sub-point", 1)], col2="..", col3="..")
        d.add("Single chart with supporting text", title="..", body="..", chart1={"type": "column",
              "categories": [..], "series": {"name": [..]}})   # tables: {"header": [..], "rows": [[..]]}
        # picN=None / chartN=None / tableN=None draw a "PHOTO|CHART|TABLE: replace" box; a missing picture file raises
        s = d.free_slide("..");  rect(s, x, y, w, h, "D9E8EC");  text(s, x, y, w, h, "..")   # pt units
        record = d.save("out/deck.pptx")   # logs via brand_log.log_request and writes out/deck.pptx.run.json
        record = d.save("out/deck.pptx", render=True)   # also out/render/deck-page-N.png (60 dpi), record["render"]
CLI:    python3 newmont_deck.py executive_summary --roles "Three Column Panels"
Roles: title subtitle lead body colN headN tagN picN chartN tableN source sourceN date footer, or a bare idx.
The template comes from brand_sources.resolve() (SourceError when missing: no fallback). Every sample slide is
deleted on open (sldId, section entries and the presentation rels); python-pptx writes only parts reachable through
relationships, so no orphaned sample media is saved. Layouts are looked up by name on master 0; the Executive
Summary file's Everyday-master layouts are exposed as "everyday:<name>" and logged as cross-template.
Palette, chart series, fonts and chart rules come from brand-values.json (brand_sources.load_values); when the
guidelines PDF is a different edition, Deck() warns on stderr and the log entry carries values_stale: true."""
import argparse, json, os, pathlib, re, shutil, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from copy import deepcopy

from lxml import etree
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Pt

import brand_log, brand_sources, catalog_layouts

VALUES = brand_sources.load_values()  # SourceError when unreadable: no built-in fallback values
SERIES = VALUES["chart_series"]
NAVY, PHOTO_FILL = VALUES["palette"]["primary"][0]["hex"], "D9E8EC"
FONT, ACCENT_FONT = VALUES["fonts"]["deck"], VALUES["fonts"]["accent"]
CHART_TYPES = {"bar": XL_CHART_TYPE.BAR_CLUSTERED, "column": XL_CHART_TYPE.COLUMN_CLUSTERED,
               "line": XL_CHART_TYPE.LINE, "pie": XL_CHART_TYPE.PIE}
AXIS_PT, AXIS_RULE_PT = VALUES["chart_axis_label_pt"], VALUES["chart_axis_rule_pt"]  # 6 pt print minimum is unreadable on screen
FURNITURE = {"DATE": "date", "FOOTER": "footer", "SLIDE_NUMBER": "number"}
EVERYDAY = "everyday:"
SLIDENUM = ('<a:p xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:fld type="slidenum" '
            'id="{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}"><a:rPr lang="en-US"/><a:t>&#8249;#&#8250;</a:t></a:fld></a:p>')


def _rgb(hexstr):
    return RGBColor.from_string(hexstr.upper())


def _drop(shape):
    shape._element.getparent().remove(shape._element)


def _reading_order(infos):
    """Group into rows (tops within 20 pt), each row left to right, rows top to bottom."""
    rows = []
    for i in sorted(infos, key=lambda i: i["top"]):
        if rows and i["top"] - rows[-1][0]["top"] <= 20:
            rows[-1].append(i)
        else:
            rows.append([i])
    return [i for r in rows for i in sorted(r, key=lambda i: i["left"])]


def layout_roles(layout):
    """Role -> placeholder idx, worked out from the layout's live placeholder list."""
    infos = [catalog_layouts.placeholder_info(ph) for ph in layout.placeholders]
    roles, rest = {}, []
    for i in infos:
        t = i["type"]
        if t in ("TITLE", "CENTER_TITLE") and "title" not in roles:
            roles["title"] = i["idx"]
        elif t == "SUBTITLE" and "subtitle" not in roles:
            roles["subtitle"] = i["idx"]
        elif t in ("DATE", "FOOTER"):
            roles[t.lower()] = i["idx"]
        elif t in ("BODY", "OBJECT", "PICTURE", "CHART", "TABLE"):
            rest.append(i)
    src = sorted([i for i in rest if i["type"] == "BODY" and i["name"].startswith("Source")], key=lambda i: -i["top"])
    for n, i in enumerate(src):
        roles["source" if n == 0 else "source%d" % (n + 1)] = i["idx"]
    rest = [i for i in rest if i not in src]
    if "title" not in roles:  # covers, dividers, thank-you: the big BODY text is the title
        big = [i for i in rest if i["type"] == "BODY" and (i.get("size") or 0) >= 24]
        if big:
            top = max(big, key=lambda i: i["size"])
            roles["title"] = top["idx"]
            rest.remove(top)
    lead = [i for i in rest if i["type"] == "BODY" and i.get("size") == 14 and 110 <= i["top"] <= 130
            and (i.get("width") or 0) >= 600]  # a 14 pt column header at the lead's height is not the lead
    if lead:
        roles["lead"] = lead[0]["idx"]
        rest.remove(lead[0])
    takeaway = [i for i in rest if i["type"] == "BODY" and i.get("bold") and 10 <= (i.get("size") or 0) < 12
                and (i.get("width") or 0) >= 600 and i["top"] >= 400]  # full-width bold bar near the bottom
    if takeaway:
        roles["takeaway"] = takeaway[0]["idx"]
        rest.remove(takeaway[0])
    groups = {g: [] for g in ("head", "tag", "col", "pic", "chart", "table")}
    for i in rest:  # bold BODY = header, < 9 pt BODY = tag, other BODY/OBJECT = content column
        body = i["type"] == "BODY"
        groups[{"PICTURE": "pic", "CHART": "chart", "TABLE": "table"}.get(i["type"]) or (
            "head" if body and i.get("bold") else "tag" if body and (i.get("size") or 99) < 9 else "col")].append(i)
    for g, items in groups.items():
        for n, i in enumerate(_reading_order(items), 1):
            roles["%s%d" % (g, n)] = i["idx"]
    if len(groups["col"]) == 1:
        roles["body"] = groups["col"][0]["idx"]
    if "title" not in roles:  # a replaced template that loses its title placeholder must fail loudly
        raise LookupError("Layout %r yields no title role (placeholders: %s)" % (
            layout.name, ", ".join("%s idx %s" % (i["type"], i["idx"]) for i in infos)))
    return roles


def strip_sample_slides(prs):
    """Drop every slide (sldId, its relationship and the stale section list) from an open Presentation. python-pptx
    writes only parts reachable through relationships, so the sample slides' media, charts and embedded workbooks
    are not saved either; masters, layouts and the theme are untouched."""
    pres = prs.part._element
    lst = pres.find(qn("p:sldIdLst"))
    for sld in list(lst) if lst is not None else []:  # a blank presentation has no sldIdLst at all
        rid = sld.get(qn("r:id"))
        lst.remove(sld)
        prs.part.drop_rel(rid)
    for sec in list(pres.iter("{http://schemas.microsoft.com/office/powerpoint/2010/main}sectionLst")):
        sec.getparent().getparent().remove(sec.getparent())  # the p:ext holding the stale section list


class Deck:
    def __init__(self, template, deck_name, date=None, request="", routing=None, *, activation_path=None, asked=False):
        if not (activation_path or "").strip():
            raise ValueError("Deck() needs activation_path, e.g. 'direct: deck/presentation/slides' or "
                             "'indirect: put into slides'")
        srcs = brand_sources.resolve([template, "guidelines"])  # SourceError propagates: never fall back
        src = srcs[template]
        self.template, self.deck_name, self.date = template, deck_name, date
        self.request, self.routing, self.source = request, routing or {}, src
        self.activation_path, self.asked = activation_path, bool(asked)
        warning = brand_sources.stale_warning(brand_sources.load_values(), srcs["guidelines"])
        self.values_stale = bool(warning)
        if warning:
            print("WARNING: " + warning, file=sys.stderr)
        self.prs = Presentation(src["path"])
        self._delete_samples()
        masters = list(self.prs.slide_masters)
        self.layouts = {l.name: l for l in masters[0].slide_layouts}
        for m in masters[1:]:
            if "everyday" in catalog_layouts.theme_info(m)["theme"].lower():
                self.layouts.update({EVERYDAY + l.name: l for l in m.slide_layouts})
        self.used, self.free = [], set()

    def _delete_samples(self):
        strip_sample_slides(self.prs)

    def _layout(self, name):
        if name not in self.layouts:
            raise ValueError("No layout named %r in the %s template (master 0%s)." % (
                name, self.template, " or everyday:" if any(k.startswith(EVERYDAY) for k in self.layouts) else ""))
        return self.layouts[name]

    def roles(self, layout_name):
        return layout_roles(self._layout(layout_name))

    def add(self, layout_name, fills=None, size=None, **kw):
        layout = self._layout(layout_name)
        roles, fills = layout_roles(layout), dict(fills or {}, **kw)
        lay_ph = {p.placeholder_format.idx: p for p in layout.placeholders}
        targets, keys = {}, {}
        for key, value in fills.items():
            idx = roles.get(key, int(key) if str(key).isdigit() else None)
            if idx is None or idx not in lay_ph:
                raise ValueError("Layout %r has no role %r; available roles: %s (or a placeholder idx: %s)" % (
                    layout_name, key, ", ".join(sorted(roles)), ", ".join(str(i) for i in sorted(lay_ph))))
            if idx in keys:
                raise ValueError("Layout %r: %r and %r both fill placeholder idx %d" % (layout_name, keys[idx], key, idx))
            targets[idx], keys[idx] = value, key
        slide = self.prs.slides.add_slide(layout)
        self._furniture(slide, layout, targets)
        for idx, value in targets.items():
            ph = next(p for p in slide.placeholders if p.placeholder_format.idx == idx)
            _fill(slide, ph, value, size)
        for ph in list(slide.placeholders):  # no "Click to add" prompts may remain
            el = ph._element
            if el.tag == qn("p:sp") and (ph.placeholder_format.type is not None and
                                         ph.placeholder_format.type.name in ("PICTURE", "CHART", "TABLE")
                                         or not ph.text_frame.text.strip()):
                _drop(ph)
        self.used.append(layout_name)
        return slide

    def _furniture(self, slide, layout, targets):
        """python-pptx does not clone DATE/FOOTER/SLIDE_NUMBER; copy them from the layout and fill them."""
        for ph in layout.placeholders:
            kind = FURNITURE.get(ph.placeholder_format.type.name if ph.placeholder_format.type else "")
            if not kind:
                continue
            el = deepcopy(ph._element)
            el.find(qn("p:nvSpPr")).find(qn("p:cNvPr")).set("id", str(slide.shapes._next_shape_id))
            sppr, body = el.find(qn("p:spPr")), el.find(qn("p:txBody"))
            for child in list(sppr) + body.findall(qn("a:p")):
                child.getparent().remove(child)
            body.append(etree.fromstring(SLIDENUM) if kind == "number" else etree.Element(qn("a:p")))
            slide.shapes._spTree.append(el)
            default = {"footer": self.deck_name, "date": self.date}.get(kind)
            if default and ph.placeholder_format.idx not in targets:
                targets[ph.placeholder_format.idx] = default

    def free_slide(self, title=None):
        slide = self.add("Title Only", **({"title": title} if title else {}))
        self.free.add(len(self.used))
        return slide

    def save(self, path, render=False):
        path = os.path.abspath(path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.prs.save(path)
        pngs = {"render": render_pages(path)} if render else {}
        used = [("free-form:" if n in self.free else "") + name for n, name in enumerate(self.used, 1)]
        cross = [u for u in used if u.startswith(EVERYDAY)]
        notes = ["%d free-form slide%s" % (len(self.free), "" if len(self.free) == 1 else "s")]
        if cross:
            notes.append("%d cross-template layout(s) from the Everyday master" % len(cross))
        r = self.routing
        if getattr(self, "_record", None):   # a second save of the same deck updates the run record, not the log
            self._record.update(output=path, layouts_used=used, slides=len(self.used), notes="; ".join(notes), **pngs)
            with open(path + ".run.json", "w", encoding="utf-8") as f:
                json.dump(self._record, f, indent=2, ensure_ascii=False)
            return self._record
        self._record = record = brand_log.log_request(
            request=self.request, activated=True, activation_path=self.activation_path,
            template=self.template, routing_reason=r.get("reason") or r.get("routing_reason") or "",
            clarifying_question_asked=self.asked, values_stale=self.values_stale,
            defaulted=bool(r.get("defaulted", False)) and r.get("template") == self.template, output=path, layouts_used=used, notes="; ".join(notes),
            template_file=self.source["file_name"], template_version=self.source["version"],
            cross_template_layouts=cross, slides=len(self.used))
        record.update(pngs)
        with open(path + ".run.json", "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)
        return record


def render_pages(path, dpi=60):
    """Render a saved deck to <deck dir>/render/<stem>-page-N.png via soffice (profile in render/.lo-profile, so no
    profile folders land in the working directory) and pymupdf. Returns the PNG paths in page order."""
    soffice = shutil.which("soffice")
    if not soffice:
        raise RuntimeError("Cannot render %s: LibreOffice 'soffice' is not on PATH (install it or add it to PATH)." % path)
    out = os.path.join(os.path.dirname(path), "render")
    profile = os.path.join(out, ".lo-profile")
    os.makedirs(profile, exist_ok=True)
    stem = os.path.splitext(os.path.basename(path))[0]
    pdf, started = os.path.join(out, stem + ".pdf"), time.time()
    r = subprocess.run([soffice, "-env:UserInstallation=" + pathlib.Path(profile).as_uri(), "--headless",
                        "--convert-to", "pdf", "--outdir", out, path], cwd=out, capture_output=True, text=True)
    if r.returncode or not os.path.exists(pdf) or os.path.getmtime(pdf) < started - 2:  # no stale PDF reuse
        raise RuntimeError("soffice could not convert %s to PDF (exit %d): %s" % (path, r.returncode,
                                                                                   (r.stderr or r.stdout).strip()))
    import pymupdf
    pngs = []
    with pymupdf.open(pdf) as doc:
        for n, page in enumerate(doc, 1):
            pngs.append(os.path.join(out, "%s-page-%d.png" % (stem, n)))
            page.get_pixmap(dpi=dpi).save(pngs[-1])
    return pngs


def _fill(slide, ph, value, size):
    kind = ph.placeholder_format.type.name if ph.placeholder_format.type else "BODY"
    if kind == "PICTURE":
        if value is None:
            _replace_box(slide, ph, "PHOTO")
        elif not os.path.exists(str(value)):
            raise FileNotFoundError("Picture for placeholder idx %d not found: %s" % (ph.placeholder_format.idx, value))
        else:
            ph.insert_picture(str(value))
    elif value is None and kind in ("CHART", "TABLE"):
        _replace_box(slide, ph, kind)
    elif isinstance(value, dict) and "series" in value:
        _chart(slide, ph, value, kind)
    elif isinstance(value, dict) and "rows" in value:
        _table(slide, ph, value, kind)
    elif kind in ("CHART", "TABLE"):
        raise ValueError("Placeholder idx %d is %s: pass a chart or table dict" % (ph.placeholder_format.idx, kind))
    else:
        _set_text(ph.text_frame, value, size)


def _replace_box(slide, ph, label):
    """A D9E8EC box with a navy 10 pt '<LABEL>: replace' at the placeholder's box, in place of the placeholder."""
    s = rect(slide, *[v / 12700 for v in (ph.left, ph.top, ph.width, ph.height)], PHOTO_FILL)
    s.name = "%s: replace" % label
    _set_text(s.text_frame, s.name, 10, color=NAVY)
    _drop(ph)
    return s


def _set_text(tf, value, size=None, bold=False, color=None):
    items = value.split("\n") if isinstance(value, str) else list(value)
    tf.text = ""
    for n, item in enumerate(items):
        p = tf.paragraphs[0] if n == 0 else tf.add_paragraph()
        runs, p.level = item if isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], int) else (item, 0)
        runs = [(runs, bold, False)] if isinstance(runs, str) else runs
        for text_, b, i in runs:  # bold/italic only where the runs say so; layout fonts kept
            r = p.add_run()
            r.text, r.font.bold, r.font.italic = text_, b or None, i or None
            if size:
                r.font.size = Pt(size)
            if color:
                r.font.color.rgb = _rgb(color)


def _adopt(frame, ph, link=True):
    """Link a frame added at a placeholder's box to that placeholder (as PowerPoint does), then drop the placeholder.
    A chart in a TABLE placeholder or a table in a CHART placeholder is not linked (type mismatch); it stays a
    free frame at the box."""
    nvpr = frame._element.find(qn("p:nvGraphicFramePr")).find(qn("p:nvPr"))
    if link:
        nvpr.insert(0, deepcopy(ph._element.find(qn("p:nvSpPr")).find(qn("p:nvPr")).find(qn("p:ph"))))
    _drop(ph)
    return frame


def _chart(slide, ph, spec, kind):
    ctype = CHART_TYPES[spec["type"]]
    data = CategoryChartData(number_format=spec.get("number_format", "General"))
    data.categories = spec["categories"]
    for name, vals in spec["series"].items():
        data.add_series(name, vals)
    if kind == "CHART":
        chart = ph.insert_chart(ctype, data).chart
    else:  # Detailed View draws charts in TABLE placeholders: add at the box, drop the placeholder
        chart = _adopt(slide.shapes.add_chart(ctype, ph.left, ph.top, ph.width, ph.height, data), ph, link=kind != "TABLE").chart
    chart.font.size, chart.font.name = Pt(AXIS_PT), FONT
    chart.has_title = bool(spec.get("title"))
    if spec.get("title"):  # guideline p21: Montserrat Bold caps, 8 pt minimum
        chart.chart_title.text_frame.text = spec["title"].upper()
        f = chart.chart_title.text_frame.paragraphs[0].runs[0].font
        f.name, f.bold, f.size = ACCENT_FONT, True, Pt(9)
    chart.has_legend = len(spec["series"]) > 1 or spec["type"] == "pie"
    if chart.has_legend:
        chart.legend.position, chart.legend.include_in_layout = XL_LEGEND_POSITION.BOTTOM, False
    plot = chart.plots[0]
    if spec["type"] == "pie":
        plot.has_data_labels = True
        dl = plot.data_labels
        dl.show_value, dl.position = True, XL_LABEL_POSITION.OUTSIDE_END  # outside: readable on every slice colour
        dl.font.size, dl.font.color.rgb = Pt(AXIS_PT), _rgb(NAVY)
        for n, point in enumerate(plot.series[0].points):
            point.format.fill.solid()
            point.format.fill.fore_color.rgb = _rgb(SERIES[n % len(SERIES)])
            point.format.line.color.rgb, point.format.line.width = _rgb("FFFFFF"), Pt(1.5)  # slice gaps
        return
    for n, s in enumerate(plot.series):
        c = _rgb(SERIES[n % len(SERIES)])
        if spec["type"] == "line":
            s.format.line.color.rgb, s.format.line.width, s.smooth = c, Pt(2), False
        else:
            s.format.fill.solid()
            s.format.fill.fore_color.rgb = c
    chart.value_axis.has_major_gridlines = False
    for ax in (chart.category_axis, chart.value_axis):
        ax.format.line.color.rgb, ax.format.line.width = _rgb("000000"), Pt(AXIS_RULE_PT)  # p15: black rules
        ax.tick_labels.font.size, ax.tick_labels.font.name = Pt(AXIS_PT), FONT


def _is_number(s):
    return bool(re.fullmatch(r"[\s$€£(+\-–−]*\d[\d,]*(\.\d+)?\s*[%x)]?\s*", str(s)))


def _table(slide, ph, spec, kind):
    header, rows = spec["header"], spec["rows"]
    nr, nc = len(rows) + 1, len(header)
    if kind == "TABLE":
        table = ph.insert_table(nr, nc).table
    else:
        row_h = Pt(max(20, spec.get("size", 10) * 2.2))  # rows sized to text, not stretched to the box
        table = _adopt(slide.shapes.add_table(nr, nc, ph.left, ph.top, ph.width, min(ph.height, row_h * nr)), ph,
                       link=kind != "CHART").table
    table.first_row = table.horz_banding = False
    for n, w in enumerate(spec.get("col_widths") or []):
        table.columns[n].width = Pt(w)
    for r, row in enumerate([header] + rows):
        for c, val in enumerate(row):
            cell = table.cell(r, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = _rgb(NAVY if r == 0 else "FFFFFF")
            _set_text(cell.text_frame, str(val), spec.get("size", 10), bold=r == 0, color="FFFFFF" if r == 0 else NAVY)
            if r and _is_number(val):
                cell.text_frame.paragraphs[0].alignment = PP_ALIGN.RIGHT


def _flat(shape):
    for style in shape._element.findall(qn("p:style")):
        shape._element.remove(style)  # python-pptx's default style carries the theme shadow and line
    return shape


def text(slide, x, y, w, h, paragraphs, size=None, bold=False, color=None):
    tb = slide.shapes.add_textbox(Pt(x), Pt(y), Pt(w), Pt(h))
    tb.text_frame.word_wrap = True
    _set_text(tb.text_frame, paragraphs, size, bold=bold, color=color)
    return tb


def rect(slide, x, y, w, h, fill, edge=None):
    s = _flat(slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Pt(x), Pt(y), Pt(w), Pt(h)))
    s.fill.solid()
    s.fill.fore_color.rgb = _rgb(fill)
    if edge:
        s.line.color.rgb, s.line.width = _rgb(edge), Pt(0.75)
    else:
        s.line.fill.background()
    return s


def picture(slide, path, x, y, w, h):
    return _flat(slide.shapes.add_picture(path, Pt(x), Pt(y), Pt(w), Pt(h)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("template", choices=["detailed_view", "executive_summary"])
    ap.add_argument("--roles", action="append", help="layout name (repeatable); default: all layouts")
    a = ap.parse_args()
    d = Deck(a.template, "roles", activation_path="cli: roles")
    for name in a.roles or list(d.layouts):
        print("%-45s %s" % (name, json.dumps(d.roles(name))))


if __name__ == "__main__":
    main()
