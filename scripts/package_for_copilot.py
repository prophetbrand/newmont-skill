#!/usr/bin/env python3
"""Package the Newmont brand skill as a Microsoft 365 Copilot Agent Builder "Skill" zip.
Usage: python3 -P scripts/package_for_copilot.py --out dist/newmont-brand-copilot-skill.zip [--template both]
Limits: SKILL.md < 20,000 characters, 25 MB per file, 50 MB per zip. SKILL.md is sliced from the repo SKILL.md by its
`## ` headings so edits flow through; an approved source over 25 MB (resolved via brand-sources.json or
NEWMONT_BRAND_CONFIG) is skipped with a warning and a stop note in the generated SKILL.md."""
import argparse, json, os, re, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import brand_sources

MAX_FILE, MAX_ZIP, MAX_CHARS, MAX_DESC = 25_000_000, 50_000_000, 20_000, 1_000
SCRIPTS = ["brand_sources.py", "route_template.py", "brand_log.py", "catalog_layouts.py", "inspect_pptx.py",
           "newmont_deck.py", "check_deck.py"]
REFERENCES = ["layouts-executive-summary.md", "layouts-detailed-view.md", "brand-guidelines-2025-10.md", "template-sample-slides.md"]
KEEP = ["Phase 1", "Phase 2", "Phase 3", "Before you build", "Choosing layouts", "Brand rules the template does not "
        "enforce", "Building with the kit", "Checking before delivering", "Reply format"]
# Kept sections moved verbatim to MOVED_FILE (with a pointer left in SKILL.md): the kept set is ~29,000 characters.
MOVED, MOVED_FILE = KEEP[4:6], "references/skill-layouts-and-brand-rules.md"
KIT_DROP = ("**Setup check**", "```bash", "If Open Sans")  # setup paragraphs that pip-install or need fonts/soffice
ZIP_SYS_PATH = "import sys; sys.path.insert(0, 'scripts')  # this skill's scripts/ (its full path if run elsewhere)"


def mb(n):
    return "%.1f MB" % (n / 1e6) if n >= 100_000 else "%.1f KB" % (n / 1e3)


def sandbox_note(included, missing):
    roles = " ".join("--role " + r for r in ("guidelines", "executive_summary", "detailed_view") if r not in missing)
    lines = ["# Newmont brand agent (Microsoft 365 Copilot skill package)", "",
             "**Sandbox check first.** Run `python3 -c \"import pptx\"` before anything else. If it fails, tell the "
             "person this sandbox lacks python-pptx and the deck cannot be built here, and give the outline (number, "
             "layout name, title) and the layout list instead. Never draw slides by hand or with another library, and "
             "never try to install packages (no network). Then run `python3 -c \"import pymupdf\"`: without it the "
             "guidelines PDF cannot be read and `brand_sources.py` stops; handle that failure the same way.", "",
             "**Sources in this package** (`brand-sources/`): %s. Run commands from this skill's folder; check the "
             "sources with `python3 scripts/brand_sources.py %s` (with no arguments it also checks the absent "
             "template and exits 2)." % ("; ".join(included), roles), ""]
    for role, (label, why) in missing.items():
        lines += ["**%s is not available in this package** (%s). When the router or the person picks `%s`, stop: say "
                  "this template is not available in this package, build nothing, and log the request as stopped. "
                  "You may offer the other template; build on it only if the person agrees." % (label, why, role), ""]
    lines += ["**Not in this package:** restyling and other formats. Rebuild a deck to restyle it on the routed "
              "template, every sentence kept word for word. For Word, Excel, email or HTML, say this package covers "
              "PowerPoint decks only.", "",
              "**Files do not persist.** The request log (`logs/requests.jsonl`) and the deck last only for this "
              "session: put the source versions, template and reason in the reply, and tell the person to download "
              "the deck now.", ""]
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
        if key in MOVED:
            moved.append(sec)
            sec = "%s\nRead this section in `%s` before outlining: it is required, and was moved there only to fit " \
                  "the 20,000-character limit.\n" % (sec.splitlines()[0], MOVED_FILE)
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


def plan(template):
    """Return (in-memory members [(arcname, bytes)], file members [(arcname, path)], missing roles, SKILL.md chars)."""
    cfg = brand_sources.load_config()
    with open(cfg["config_path"], encoding="utf-8") as f:
        raw = json.load(f)
    wanted = {"both": ("executive_summary", "detailed_view")}.get(template, (template,))
    files, missing, included = [], {}, []
    for role, info in brand_sources.resolve(cfg=cfg).items():
        label = raw["files"][role].get("label", role)
        if role in ("executive_summary", "detailed_view") and role not in wanted:
            missing[role] = (label, "not selected with --template %s" % template)
        elif info["size"] >= MAX_FILE:
            missing[role] = (label, "%s is %s, over the 25 MB per-file limit" % (info["file_name"], mb(info["size"])))
            print("WARNING: skipping %s: %s" % (role, missing[role][1]), file=sys.stderr)
        else:
            files.append(("brand-sources/" + info["file_name"], info["path"]))
            included.append("%s, %s" % (info["file_name"], info["version"]))
    if "guidelines" in missing or len(missing) == 2:
        raise SystemExit("ERROR: the package needs the guidelines PDF and at least one template; missing: "
                         + ", ".join(missing))
    raw["sources_dir"] = "brand-sources"
    files += [("brand-values.json", cfg["values_file"])] + [("scripts/" + s, os.path.join(ROOT, "scripts", s))
              for s in SCRIPTS] + [("references/" + r, os.path.join(ROOT, "references", r)) for r in REFERENCES]
    skill, moved = build_skill_md(open(os.path.join(ROOT, "SKILL.md"), encoding="utf-8").read(),
                           sandbox_note(included, missing))
    data = [("SKILL.md", skill.encode("utf-8")), (MOVED_FILE, moved.encode("utf-8")),
            ("brand-sources.json", (json.dumps(raw, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))]
    return data, files, missing, len(skill)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True, help="zip path, e.g. dist/newmont-brand-copilot-skill.zip")
    ap.add_argument("--template", choices=["executive_summary", "detailed_view", "both"], default="both")
    a = ap.parse_args()
    try:
        data, files, missing, chars = plan(a.template)
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


if __name__ == "__main__":
    main()
