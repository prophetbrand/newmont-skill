#!/usr/bin/env python3
"""Package the Newmont brand skill as a Microsoft 365 Copilot Agent Builder or Copilot Studio "Skill" zip.
Usage: python3 -P scripts/package_for_copilot.py --out dist/newmont-brand-copilot-skill.zip [--template both]
Limits: SKILL.md < 20,000 characters, 25 MB per file, 50 MB per zip. SKILL.md is sliced from the repo SKILL.md by its
`## ` headings so edits flow through. A template over 25 MB (resolved via brand-sources.json or NEWMONT_BRAND_CONFIG)
is packaged with its sample slides stripped (the kit deletes them on open anyway; the Detailed View's 61 MB of embedded
chart workbooks live in those slides); the generated SKILL.md says the copy is derived from the approved file. A source
still over the limit after that is skipped with a warning and a stop note."""
import argparse, json, os, re, sys, tempfile, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import brand_sources

MAX_FILE, MAX_ZIP, MAX_CHARS, MAX_DESC = 25_000_000, 50_000_000, 20_000, 1_000
SCRIPTS = ["brand_sources.py", "route_template.py", "brand_log.py", "catalog_layouts.py", "inspect_pptx.py",
           "newmont_deck.py", "check_deck.py"]
REFERENCES = ["layouts-executive-summary.md", "layouts-detailed-view.md", "brand-guidelines-2025-10.md", "template-sample-slides.md"]
KEEP = ["Phase 1", "Phase 2", "Phase 3", "Before you build", "Choosing layouts", "Brand rules the template does not "
        "enforce", "Building with the kit", "Checking before delivering", "Reply format", "Restyling an existing deck",
        "Other formats"]
# Kept sections moved verbatim to MOVED_FILE (with a pointer left in SKILL.md): the kept set is ~29,000 characters.
# Reply format moves too: the Agent Builder Instructions (STEP 7) already set the reply shape in Copilot.
MOVED, MOVED_FILE = KEEP[4:6] + KEEP[8:], "references/skill-layouts-and-brand-rules.md"
SCRATCH = "/tmp/newmont-work"  # outside the exported working directory (/mnt/data)
KIT_DROP = ("**Setup check**", "```bash", "If Open Sans")  # setup paragraphs that pip-install or need fonts/soffice
ZIP_SYS_PATH = "import sys; sys.path.insert(0, 'scripts')  # this skill's scripts/ (its full path if run elsewhere)"


def mb(n):
    return "%.1f MB" % (n / 1e6) if n >= 100_000 else "%.1f KB" % (n / 1e3)


def slim_template(src, dst):
    """Write src without its sample slides to dst (masters, layouts and theme intact); return dst's size."""
    from pptx import Presentation
    from newmont_deck import strip_sample_slides
    prs = Presentation(src)
    strip_sample_slides(prs)
    prs.save(dst)
    return os.path.getsize(dst)


def shrink_template_media(src, dst, max_px=1600, quality=85, min_bytes=300_000):
    """Copy src to dst with large opaque PNG photos re-encoded as JPEG (rels and content types rewritten)."""
    import io, zipfile as zf
    from PIL import Image
    z = zf.ZipFile(src); conv = {}
    for n in z.namelist():
        if n.startswith("ppt/media/") and n.lower().endswith(".png") and z.getinfo(n).file_size >= min_bytes:
            im = Image.open(io.BytesIO(z.read(n)))
            if im.mode in ("RGBA", "LA") and im.getextrema()[-1][0] < 255:
                continue  # keeps transparency
            im = im.convert("RGB"); im.thumbnail((max_px, max_px)); buf = io.BytesIO()
            im.save(buf, "JPEG", quality=quality, optimize=True); conv[n] = (n[:-4] + ".jpeg", buf.getvalue())
    with zf.ZipFile(dst, "w", zf.ZIP_DEFLATED) as out:
        for i in z.infolist():
            if i.filename in conv:
                out.writestr(conv[i.filename][0], conv[i.filename][1]); continue
            data = z.read(i.filename)
            if i.filename.endswith(".rels"):
                s = data.decode("utf-8")
                for o, (nn, _) in conv.items():
                    s = s.replace(os.path.basename(o), os.path.basename(nn))
                data = s.encode("utf-8")
            if i.filename == "[Content_Types].xml" and b'Extension="jpeg"' not in data:
                data = data.replace(b'<Default Extension="png"',
                                    b'<Default Extension="jpeg" ContentType="image/jpeg"/><Default Extension="png"')
            out.writestr(i.filename, data)
    return os.path.getsize(dst)


def strip_picture_originals(src, dst):
    """Copy src to dst without the JPEG XR originals (ppt/media/*.wdp) kept for re-editing picture corrections: drop
    their rels, the <a:extLst> blocks that reference them and the wdp content type; the flattened picture stays."""
    import zipfile as zf
    z = zf.ZipFile(src); names = z.namelist(); drop = {}
    wdp = {n for n in names if n.lower().endswith(".wdp")}
    for n in names:
        if n.endswith(".rels"):
            s = z.read(n).decode("utf-8")
            ids = set(re.findall(r'<Relationship [^>]*Id="([^"]+)"[^>]*Target="[^"]*\.wdp"', s)) | \
                set(re.findall(r'<Relationship [^>]*Target="[^"]*\.wdp"[^>]*Id="([^"]+)"', s))
            if ids:
                drop[n] = ids
    with zf.ZipFile(dst, "w", zf.ZIP_DEFLATED) as out:
        for i in z.infolist():
            n = i.filename
            if n in wdp:
                continue
            data = z.read(n)
            ids = drop.get(os.path.join(os.path.dirname(n), "_rels", os.path.basename(n) + ".rels"))
            if n in drop:
                data = re.sub(r'<Relationship [^>]*Target="[^"]*\.wdp"[^>]*/>', "",
                              data.decode("utf-8")).encode("utf-8")
            elif ids and n.endswith(".xml"):
                s = data.decode("utf-8")
                for rid in ids:  # non-greedy, never crosses </a:extLst>: only the extLst holding this rId goes
                    s = re.sub(r'<a:extLst>(?:(?!</a:extLst>).)*?r:embed="%s"(?:(?!</a:extLst>).)*?</a:extLst>'
                               % re.escape(rid), "", s, flags=re.S)
                data = s.encode("utf-8")
            if n == "[Content_Types].xml":
                data = re.sub(rb'<Default Extension="wdp"[^>]*/>', b"", data)
            out.writestr(n, data)
    return os.path.getsize(dst)


def shrink_pdf(src, dst, max_px=800, quality=60, min_bytes=40_000):
    """Copy src to dst with images downsampled to JPEG and fonts subset; text and layout are untouched."""
    import io, pymupdf
    from PIL import Image
    d = pymupdf.open(src); done = set()
    for page in d:
        for im in page.get_images(full=True):
            xref = im[0]
            if xref in done:
                continue
            done.add(xref)
            try:
                raw = d.extract_image(xref)["image"]
                if len(raw) < min_bytes:
                    continue
                img = Image.open(io.BytesIO(raw)).convert("RGB"); img.thumbnail((max_px, max_px))
                buf = io.BytesIO(); img.save(buf, "JPEG", quality=quality, optimize=True)
                if len(buf.getvalue()) < len(raw):
                    page.replace_image(xref, stream=buf.getvalue())
            except Exception:
                continue
    d.subset_fonts()
    d.save(dst, garbage=4, deflate=True, clean=True)
    return os.path.getsize(dst)


def sandbox_note(included, missing, derived=()):
    roles = " ".join("--role " + r for r in ("guidelines", "executive_summary", "detailed_view") if r not in missing)
    lines = ["# Newmont brand agent (Microsoft 365 Copilot skill package)", "",
             "**Sandbox check first.** Run `python3 -c \"import pptx\"` before anything else. If it fails, say this "
             "sandbox lacks python-pptx so the deck cannot be built here, and give the outline (layout and title) "
             "instead. Never draw slides by hand or with another library; never install packages (no "
             "network). pymupdf and LibreOffice are usually absent here: `brand_sources.py` then takes the guidelines "
             "edition from the file name, and you skip the render step and say so.", "",
             "**Sources in this package** (`brand-sources/`): %s. Run commands from this skill's folder. Decide what "
             "is available only by running `python3 scripts/brand_sources.py %s` now, never from memory or an "
             "earlier chat (no arguments also checks an absent template, exit 2)." % ("; ".join(included), roles), ""]
    for label, file_name, sha, size in derived:
        lines += ["**%s is a derived copy** of the approved `%s` (sha %s), trimmed as its version says to fit the "
                  "host's size limit (%s)." % (label, file_name, sha, mb(size)), ""]
    if derived:
        lines += ["Text, masters, layouts and theme of a derived copy are unchanged. `brand_sources.py` reports the "
                  "approved sha as each copy's version.", ""]
    for role, (label, why) in missing.items():
        lines += ["**%s is not in this package** (%s). If the router or the person picks `%s`, stop: say so, build "
                  "nothing and log the request as stopped; offer the other template and build on it only if they "
                  "agree." % (label, why, role), ""]
    lines += ["**Where the deck goes.** The workspace and `logs/requests.jsonl` last one turn. Return the deck with "
              "the host's file tool (the attachment or 'create' tool): in Microsoft 365 Copilot the file is also "
              "copied to the person's OneDrive under `Documents/Copilot/Created/`; in Copilot Studio it is the "
              "attachment on the reply. Name only the delivery you observed, never a folder you did not write to. "
              "If a link fails or the person asks for the file again, re-attach the same file; rebuild only for a "
              "change.", "",
              "**One save per deck.** Copilot exports every file written under the working directory (`/mnt/data`) "
              "after each code run, and a re-saved deck arrives as another copy (`<deck> 2.pptx`). Build, check, fix "
              "and render in `%s/` instead, and only when the checker passes copy the final `.pptx`, the build "
              "script and the run record into the working directory, once; then write nothing more there." % SCRATCH,
              ""]
    return "\n".join(lines)


def build_skill_md(text, note):
    """Return (SKILL.md, moved-sections file): frontmatter, the note, then the KEEP sections in order, MOVED ones
    replaced by a pointer. Raise SystemExit when over the limits."""
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    fm = dict(re.findall(r"(?m)^(name|description): (.*)$", m.group(1))) if m else {}
    if not fm.get("name") or not 0 < len(fm.get("description", "")) < MAX_DESC:
        raise SystemExit("ERROR: SKILL.md frontmatter needs a name and a description under %d characters (it is %d)"
                         % (MAX_DESC, len(fm.get("description", ""))))
    parts = re.split(r"(?m)^(?=## )", text[m.end():])[1:]
    out = ["---\nname: %s\ndescription: %s\n---\n" % (fm["name"], fm["description"]), note]
    moved = ["# Sections of the Newmont brand skill read before outlining and building\n"]
    for key in KEEP:
        hits = [p for p in parts if p[3:].startswith(key)]
        if len(hits) != 1:
            raise SystemExit("ERROR: expected one '## %s' section in SKILL.md, found %d" % (key, len(hits)))
        sec = hits[0].rstrip() + "\n"
        if key == "Before you build":
            sec = re.sub(r"\n\nExample\. .*", "\n", sec, flags=re.S)
        if key == "Building with the kit":
            sec = "\n\n".join(b for b in sec.split("\n\n") if not b.startswith(KIT_DROP))
            sec = sec.replace("import sys; sys.path.insert(0, 'scripts')", ZIP_SYS_PATH)
            sec = sec.replace("d.save('tailings-strategy.pptx')", "d.save('%s/tailings-strategy.pptx')  # scratch; "
                              "copy to the working directory once the checker passes" % SCRATCH)
        if key in MOVED:
            moved.append(sec)
            sec = "%s\nRequired: read this section in `%s` (moved there to fit the 20,000-character limit).\n" \
                  % (sec.splitlines()[0], MOVED_FILE)
        out.append(sec)
    md = "\n".join(out)
    if len(md) >= MAX_CHARS:
        raise SystemExit("ERROR: generated SKILL.md is %d characters (limit %d)" % (len(md), MAX_CHARS))
    return md, "\n".join(moved)


def check_limits(members):
    """members: [(arcname, size)]. Raise SystemExit when a file or the total breaks Agent Builder's limits."""
    big, total = ["%s (%s)" % (n, mb(s)) for n, s in members if s >= MAX_FILE], sum(s for _, s in members)
    if big or total >= MAX_ZIP:
        raise SystemExit("ERROR: over the 25 MB per-file limit: " + ", ".join(big) if big else
                         "ERROR: package would be %s (limit 50 MB)" % mb(total))


def plan(template, workdir, profile="agent-builder"):
    """Return (in-memory members [(arcname, bytes)], file members [(arcname, path)], missing roles, SKILL.md chars).
    workdir receives slimmed copies of templates over the per-file limit. profile "copilot-studio" keeps the
    package under Copilot Studio's 20,000,000-character definition cap, both templates included: sample slides and
    picture originals (.wdp) stripped, large photo PNGs re-encoded as JPEG, the guidelines PDF with downsampled
    images; every derived copy is noted."""
    studio = profile == "copilot-studio"
    cfg = brand_sources.load_config()
    with open(cfg["config_path"], encoding="utf-8") as f:
        raw = json.load(f)
    wanted = {"both": ("executive_summary", "detailed_view")}.get(template, (template,))
    files, missing, included, derived = [], {}, [], []
    for role, info in brand_sources.resolve(cfg=cfg).items():
        label = raw["files"][role].get("label", role)
        path, version = info["path"], info["version"]
        if role in ("executive_summary", "detailed_view") and role not in wanted:
            missing[role] = (label, "not selected with --template %s" % template)
            continue
        if studio and info["file_name"].lower().endswith(".pdf"):
            small = os.path.join(workdir, info["file_name"]); size = shrink_pdf(path, small)
            print("NOTE: %s is %s; packaging it with downsampled images (%s)" % (info["file_name"], mb(info["size"]),
                                                                                 mb(size)), file=sys.stderr)
            derived.append((label, info["file_name"], info["sha256_12"], size))
            raw["files"][role]["approved_sha256_12"] = info["sha256_12"]
            path, version = small, version + ", images downsampled"; info = dict(info, size=size)
        if (info["size"] >= MAX_FILE or studio) and info["file_name"].lower().endswith(".pptx"):
            slim = os.path.join(workdir, info["file_name"])
            size = slim_template(path, slim)
            if studio:
                bare = os.path.join(workdir, "bare-" + info["file_name"]); strip_picture_originals(slim, bare)
                small = os.path.join(workdir, "small-" + info["file_name"]); size = shrink_template_media(bare, small)
                slim = small
            if size < MAX_FILE:
                print("NOTE: %s is %s; packaging it without its sample slides (%s)" % (
                    info["file_name"], mb(info["size"]), mb(size)), file=sys.stderr)
                derived.append((label, info["file_name"], info["sha256_12"], size))
                raw["files"][role]["approved_sha256_12"] = info["sha256_12"]
                path, version = slim, version + (", sample slides removed, picture originals removed, photos "
                                                 "re-encoded" if studio else ", sample slides removed")
                info = dict(info, size=size)
        if info["size"] >= MAX_FILE:
            missing[role] = (label, "%s is %s, over the 25 MB per-file limit" % (info["file_name"], mb(info["size"])))
            print("WARNING: skipping %s: %s" % (role, missing[role][1]), file=sys.stderr)
        else:
            files.append(("brand-sources/" + info["file_name"], path))
            included.append("%s, %s" % (info["file_name"], version))
    if "guidelines" in missing or len(missing) == 2:
        raise SystemExit("ERROR: the package needs the guidelines PDF and at least one template; missing: "
                         + ", ".join(missing))
    raw["sources_dir"], raw["values_file"], raw["log_file"] = "brand-sources", "brand-values.json", "logs/requests.jsonl"
    files += [("brand-values.json", cfg["values_file"])] + [("scripts/" + s, os.path.join(ROOT, "scripts", s))
              for s in SCRIPTS] + [("references/" + r, os.path.join(ROOT, "references", r)) for r in REFERENCES]
    skill, moved = build_skill_md(open(os.path.join(ROOT, "SKILL.md"), encoding="utf-8").read(),
                           sandbox_note(included, missing, derived))
    data = [("SKILL.md", skill.encode("utf-8")), (MOVED_FILE, moved.encode("utf-8")),
            ("brand-sources.json", (json.dumps(raw, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))]
    return data, files, missing, len(skill)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True, help="zip path, e.g. dist/newmont-brand-copilot-skill.zip")
    ap.add_argument("--template", choices=["executive_summary", "detailed_view", "both"], default="both")
    ap.add_argument("--profile", choices=["agent-builder", "copilot-studio"], default="agent-builder",
                    help="copilot-studio: derived copies sized for the 20M-character definition cap (both "
                         "templates fit)")
    a = ap.parse_args()
    with tempfile.TemporaryDirectory() as workdir:
        try:
            data, files, missing, chars = plan(a.template, workdir, a.profile)
        except brand_sources.SourceError as e:
            raise SystemExit("ERROR: %s" % e)
        members = [(n, len(b)) for n, b in data] + [(n, os.path.getsize(p)) for n, p in files]
        check_limits(members)
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        with zipfile.ZipFile(a.out + ".partial", "w", zipfile.ZIP_DEFLATED) as z:
            for n, b in data:
                z.writestr(n, b)
            for n, p in files:
                z.write(p, n)
    if os.path.getsize(z.filename) >= MAX_ZIP:
        raise SystemExit("ERROR: zip is %s, over the 50 MB limit (left at %s)" % (mb(os.path.getsize(z.filename)),
                                                                                    z.filename))
    os.replace(z.filename, a.out)
    print("\n".join(["  %10s  %s" % (mb(s), n) for n, s in members] + ["SKILL.md: %d characters (limit %d)" % (
        chars, MAX_CHARS)] + ["not included: %s (%s)" % (r, why) for r, (_, why) in missing.items()]))
    print("zip: %s, %s (limit 50 MB)" % (a.out, mb(os.path.getsize(a.out))))
    members = sum(s for _, s in members)
    if a.profile == "copilot-studio":
        print("members: %s (safe budget 14.5 MB: the agent definition caps at 20,000,000 characters, about 1.34 per "
              "byte)%s" % (mb(members), "" if members < 14_500_000 else "  WARNING: over the budget, the definition "
              "may break the 20,000,000-character cap"))


if __name__ == "__main__":
    main()
