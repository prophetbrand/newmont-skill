#!/usr/bin/env python3
"""Route a deck request to one of the two Newmont templates by the kind of deck asked for.
Usage: python route_template.py "<request text>" [--unattended] [--json]
Order: explicit template named ("<name> template" / "<name> layout") > cues on one side only > ask one clarifying
question (both or neither matched); weak cues count only in the cases noted beside them;
unattended runs default to Executive Summary and say why. Edit the cue tuples below to tune routing."""
import argparse, json, re

DETAILED_CUES = ("business review", "QBR", "quarterly business review", "monthly business review", "MBR",
                 "operational performance", "operating performance", "financial performance", "financial results",
                 "quarterly results", "results deck", "scorecard", "score card", "KPI dashboard", "KPIs",
                 "performance against plan", "people update", "labour update", "labor update", "workforce update",
                 "headcount", "labour relations", "investor relations", "IR update", "earnings", "progress report",
                 "progress update", "progress pictures", "cost summary", "balance sheet", "dividend", "highlights",
                 "risks and mitigations", "performance", "safety performance", "safety results",
                 "operating results", "results review", "dashboard",
                 "operations review", "ops review")
DETAILED_WEAK = ("outlook",)  # counts only alongside a strong Detailed View cue
EXEC_CUES = ("strategy", "strategic", "proposal", "pitch", "business case", "project update", "project kickoff",
             "explainer", "training", "onboarding", "workshop", "narrative", "framework", "roadmap", "timeline",
             "recommendation", "lessons learned")
EXEC_WEAK = ("plan", "overview", "approach", "options", "comparison", "explain", "town hall", "all-hands", "story",
             "vision", "introduction")  # count only when no strong Detailed View cue matched
_DV, _ES = r"detailed[\s\-]+(?:view[\s\-]+)?", r"exec(?:utive)?[\s\-]+(?:summary[\s\-]+)?"
_NOUN, _OR = r"(?:template|layout)s?\b", r"[\s\-]+(?:or|and|vs\.?|/)[\s\-]+"
# the name must sit next to "template"/"layout"; "detailed view or executive summary template" names both
EXPLICIT = {"detailed_view": r"\b(?:%s%s|detailed[\s\-]+view(?=%s%s%s))" % (_DV, _NOUN, _OR, _ES, _NOUN),
            "executive_summary": r"\b(?:%s%s|exec(?:utive)?[\s\-]+summary(?=%s%s%s))" % (_ES, _NOUN, _OR, _DV, _NOUN)}
NAMES = {"detailed_view": "Detailed View", "executive_summary": "Executive Summary"}
QUESTION = ("Which template should this deck use: Detailed View, for business and performance reporting (scorecards, "
            "financial and people dashboards, progress and outlook), or Executive Summary, for general storytelling "
            "(columns, panels, comparisons, statements, process, timeline, charts, tables)?")


def simplify(text):
    """Lower-case, drop possessives and simple plural/-ing endings so 'strategies' meets 'strategy'."""
    text = re.sub(r"['’]s\b", "", text.lower())
    def stem(m):
        w = m.group(0)
        if len(w) > 4 and w.endswith("ies"):
            return w[:-3] + "y"
        if len(w) > 6 and w.endswith("ing"):
            return w[:-3]
        return w[:-1] if len(w) > 3 and w.endswith("s") and not w.endswith("ss") else w
    return re.sub(r"[a-z]+", stem, text)


def spans(text, cue):
    """(start, end, tight) of the first match; multi-word cues may skip one filler word ('project progress update')."""
    words = [re.escape(w) for w in cue.lower().split()]
    for sep, tight in ((r"[\s\-]+", True), (r"[\s\-]+(?:\w+[\s\-]+)?", False)):
        m = re.search(r"\b%s\b" % sep.join(words), text)
        if m:
            return m.start(), m.end(), tight
        if len(words) == 1:
            return None


def cues_in(text, cues):
    found = {c: s for c in cues for s in [spans(text, c)] if s}
    # drop a cue that sits inside a longer, tightly matched cue ('plan' inside 'performance against plan')
    return {c for c, (a, b, _) in found.items()
            if not any(o != c and t and a2 <= a and b <= b2 and (b2 - a2) > (b - a) for o, (a2, b2, t) in found.items())}


def matches(text):
    all_cues = DETAILED_CUES + DETAILED_WEAK + EXEC_CUES + EXEC_WEAK
    hit = cues_in(text.lower(), all_cues) | cues_in(simplify(text), all_cues)
    strong = [c for c in DETAILED_CUES if c in hit]
    detailed = strong + [c for c in DETAILED_WEAK if c in hit and strong]
    execs = [c for c in EXEC_CUES if c in hit] + [c for c in EXEC_WEAK if c in hit and not strong]
    return {"detailed_view": detailed, "executive_summary": execs}


def route(request, unattended=False):
    matched = matches(request or "")
    res = {"template": None, "reason": "", "matched": matched, "ask": False, "question": None,
           "defaulted": False, "explicit": False}
    named = [t for t, pat in EXPLICIT.items() if re.search(pat, (request or "").lower())]
    if len(named) == 1:
        return dict(res, template=named[0], explicit=True,
                    reason="The request names the %s template explicitly." % NAMES[named[0]])
    d, e = matched["detailed_view"], matched["executive_summary"]
    if bool(d) != bool(e):
        t = "detailed_view" if d else "executive_summary"
        return dict(res, template=t, reason="Matched %s cues: %s." % (NAMES[t], ", ".join(d or e)))
    why = ("both templates were named" if len(named) > 1 else
           "cues for both templates matched (Detailed View: %s; Executive Summary: %s)" % (", ".join(d), ", ".join(e))
           if d else "no template cue matched")
    if unattended:
        return dict(res, template="executive_summary", defaulted=True,
                    reason="Defaulted to Executive Summary because %s and the run is unattended." % why)
    return dict(res, ask=True, question=QUESTION, reason="Asking because %s." % why)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("request")
    ap.add_argument("--unattended", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    r = route(a.request, a.unattended)
    if a.json:
        print(json.dumps(r, indent=2))
        return
    print("template: %s%s" % (r["template"], " (defaulted)" if r["defaulted"] else ""))
    print("reason:   %s" % r["reason"])
    if r["ask"]:
        print("ask:      %s" % r["question"])


if __name__ == "__main__":
    main()
