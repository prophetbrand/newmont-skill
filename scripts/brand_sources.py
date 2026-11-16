#!/usr/bin/env python3
"""Resolve the approved Newmont brand source files (guidelines PDF, two pptx templates) from ONE configured folder.
Usage: python brand_sources.py [--json] [--role detailed_view]
Config: brand-sources.json at the repo root ("sources_dir", "log_file", "files": role -> glob/kind/label).
Env overrides: NEWMONT_BRAND_SOURCES (folder), NEWMONT_BRAND_LOG (log file), NEWMONT_BRAND_CONFIG (json path),
NEWMONT_BRAND_VALUES (brand-values.json, the values digested from the guidelines PDF; config key "values_file").
Replacing a file in the folder changes what the skill uses; a missing file, or more than one file matching a role,
raises SourceError (exit 2), never a fallback. A guidelines edition other than the one brand-values.json was digested
from prints a loud warning (stale_warning)."""
import argparse, datetime, glob, hashlib, json, os, re, sys, zipfile

DEFAULT_CONFIG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "brand-sources.json")
MONTHS = ("January February March April May June July August September October November December "
          "Jan Feb Mar Apr Jun Jul Aug Sep Sept Oct Nov Dec").split()
EDITION = re.compile(r"(?<![A-Za-z])(%s)[\s_\-]*(\d{4})(?!\d)" % "|".join(MONTHS), re.I)
GENERIC_TITLES = {"", "powerpoint presentation"}
FALLBACK_MSG = "Replace or add the file there; the skill will not fall back to older brand values."


class SourceError(RuntimeError):
    pass


def load_config(path=None):
    path = os.path.abspath(os.path.expanduser(path or os.environ.get("NEWMONT_BRAND_CONFIG") or DEFAULT_CONFIG))
    try:
        with open(path, encoding="utf-8") as f:
            cfg = json.load(f)
    except (OSError, ValueError) as e:
        raise SourceError("Cannot read brand source config %s: %s" % (path, e))
    base = os.path.dirname(path)
    def pick(env, key, default):
        """Env overrides resolve against the working directory; config values against the config's folder."""
        if os.environ.get(env):
            return os.path.abspath(os.path.expanduser(os.environ[env]))
        return os.path.normpath(os.path.join(base, os.path.expanduser(cfg.get(key, default))))
    cfg["sources_dir"] = pick("NEWMONT_BRAND_SOURCES", "sources_dir", "brand-sources")
    cfg["log_file"] = pick("NEWMONT_BRAND_LOG", "log_file", "logs/requests.jsonl")
    cfg["values_file"] = pick("NEWMONT_BRAND_VALUES", "values_file", "brand-values.json")
    cfg["config_path"] = path
    return cfg


def load_values(cfg=None):
    """The brand values digested from the guidelines PDF (palette, chart series, fonts, chart rules)."""
    path = (cfg or load_config())["values_file"]
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        raise SourceError("Cannot read brand values %s: %s" % (path, e))


def stale_warning(values, guidelines):
    """Warning text when the resolved guidelines edition differs from the edition the values were digested from."""
    have, want = guidelines.get("edition"), values.get("guidelines_edition")
    if have == want:
        return None
    return ("brand-values.json was digested from %s; the guidelines file is %s: re-digest before trusting colours "
            "and chart rules" % (want, have))


def edition(text):
    m = EDITION.search(text or "")
    if not m:
        return None
    month = m.group(1).title()
    return "%s %s" % (month if month in MONTHS[:12] else month[:3], m.group(2))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def doc_info(path, kind):
    """Return (title, edition) read from inside the file; either may be None."""
    try:
        if kind == "pptx":
            with zipfile.ZipFile(path) as z:
                xml = z.read("docProps/core.xml").decode("utf-8", "replace")
            m = re.search(r"<dc:title>(.*?)</dc:title>", xml, re.S)
            return (m.group(1).strip() if m else None), None
        if kind == "pdf":
            import pymupdf
            with pymupdf.open(path) as d:
                return (d.metadata or {}).get("title") or None, edition(d[0].get_text() if d.page_count else "")
    except Exception as e:  # unreadable file is a loud error, not a silent fallback
        raise SourceError("Cannot open %s (%s): %s. %s" % (path, kind, e, FALLBACK_MSG))
    return None, None


def describe(role, spec, path):
    title, ed = doc_info(path, spec.get("kind"))
    ed = ed or edition(os.path.basename(path)) or "unknown edition"
    st, sha = os.stat(path), sha256(path)[:12]
    return {"role": role, "label": spec.get("label", role), "path": path, "file_name": os.path.basename(path),
            "title": title if (title or "").strip().lower() not in GENERIC_TITLES else None,
            "version": "%s (sha %s)" % (ed, sha), "edition": ed, "sha256_12": sha, "size": st.st_size,
            "modified": datetime.datetime.fromtimestamp(st.st_mtime, datetime.timezone.utc).isoformat(timespec="seconds")}


def resolve(roles=None, cfg=None):
    cfg = cfg or load_config()
    files, out = cfg.get("files", {}), {}
    for role in roles or list(files):
        if role not in files:
            raise SourceError("Unknown brand source role '%s' (configured: %s)." % (role, ", ".join(files)))
        spec, d = files[role], cfg["sources_dir"]
        hits = sorted(glob.glob(os.path.join(glob.escape(d), spec["glob"])))
        if not hits:
            raise SourceError("Missing brand source '%s' (%s): no file matching '%s' in %s. %s"
                              % (role, spec.get("label", role), spec["glob"], d, FALLBACK_MSG))
        if len(hits) > 1:
            raise SourceError("Ambiguous brand source '%s' (%s): %d files match '%s' in %s: %s. Keep exactly one."
                              % (role, spec.get("label", role), len(hits), spec["glob"], d,
                                 ", ".join(os.path.basename(h) for h in hits)))
        out[role] = describe(role, spec, hits[0])
    return out


def manifest(roles=None, cfg=None):
    cfg = cfg or load_config()
    return {"resolved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "sources_dir": cfg["sources_dir"], "sources": resolve(roles, cfg)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--role", action="append", help="limit to a role (repeatable)")
    a = ap.parse_args()
    try:
        m = manifest(a.role)
        guidelines = m["sources"].get("guidelines") or resolve(["guidelines"])["guidelines"]
        warning = stale_warning(load_values(), guidelines)
    except SourceError as e:
        print("ERROR: %s" % e, file=sys.stderr)
        sys.exit(2)
    if warning:
        print("WARNING: " + warning, file=sys.stderr)
    if a.json:
        print(json.dumps(m, indent=2))
        return
    print("Brand sources in %s (resolved %s)" % (m["sources_dir"], m["resolved_at"]))
    for role, s in m["sources"].items():
        print("  %-18s %-28s %s" % (role, s["version"], s["file_name"]))


if __name__ == "__main__":
    main()
