#!/usr/bin/env python3
"""Append one JSON line per deck request to the configured request log (brand-sources.json "log_file", env NEWMONT_BRAND_LOG).
Usage: python brand_log.py --request "..." --activated --activation-path "direct: deck" --template executive_summary \\
         --reason "..." [--asked] [--defaulted] [--output deck.pptx] [--layouts "Cover slide Opt 1,Three Column"] [--notes "..."]
       python brand_log.py --tail 5
Fields: ts, request (first 300 chars), activated, activation_path (e.g. "direct: deck/presentation/slides",
"indirect: put into slides", "explicit other product: Word", "not activated: non-PowerPoint request"), template,
routing_reason, clarifying_question_asked, defaulted, sources (role -> version) or sources_error, output, layouts_used, notes."""
import argparse, datetime, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brand_sources


def log_path():
    """The configured log file; an unreadable config raises SourceError (no silent default path)."""
    return brand_sources.load_config()["log_file"]


def log_request(request="", activated=False, activation_path="", template=None, routing_reason="",
                clarifying_question_asked=False, defaulted=False, output=None, layouts_used=None, notes="", **extra):
    entry = {"ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
             "request": (request or "")[:300], "activated": bool(activated), "activation_path": activation_path,
             "template": template, "routing_reason": routing_reason,
             "clarifying_question_asked": bool(clarifying_question_asked), "defaulted": bool(defaulted)}
    try:  # the log line must be written even when the sources cannot be resolved
        entry["sources"] = {r: s["version"] for r, s in brand_sources.manifest()["sources"].items()}
    except Exception as e:
        entry["sources_error"] = str(e)
    entry.update(output=output, layouts_used=list(layouts_used or []), notes=notes, **extra)
    path = log_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def tail(n):
    path = log_path()
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f.read().splitlines()[-n:] if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tail", type=int)
    ap.add_argument("--request", default="")
    ap.add_argument("--activated", action="store_true")
    ap.add_argument("--activation-path", default="")
    ap.add_argument("--template", choices=["detailed_view", "executive_summary"])
    ap.add_argument("--reason", default="")
    ap.add_argument("--asked", action="store_true")
    ap.add_argument("--defaulted", action="store_true")
    ap.add_argument("--output")
    ap.add_argument("--layouts", default="")
    ap.add_argument("--notes", default="")
    a = ap.parse_args()
    if a.tail:
        for e in tail(a.tail):
            print(json.dumps(e, ensure_ascii=False))
        return
    e = log_request(request=a.request, activated=a.activated, activation_path=a.activation_path, template=a.template,
                    routing_reason=a.reason, clarifying_question_asked=a.asked, defaulted=a.defaulted, output=a.output,
                    layouts_used=[s.strip() for s in a.layouts.split(",") if s.strip()], notes=a.notes)
    print("logged to %s" % log_path())
    if "sources_error" in e:
        print("WARNING: brand sources not resolved: %s" % e["sources_error"], file=sys.stderr)


if __name__ == "__main__":
    main()
