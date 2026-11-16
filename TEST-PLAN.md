# newmont-brand: repeatability test plan

Goal: measure how consistently the skill turns the same prompt into the same quality of output, find what varies, and verify that question gating removes the "assumed and built the wrong thing" failures.

## Why output varied before the first revision (read of SKILL.md, 2026-11-05; the kit named here was retired on 2026-11-16)

1. **No intake step.** The skill never says what to find out before building. Format, page types, deck name, date, photos, spelling, slide count and the actual content are all left to the model to guess.
2. **Photos are required but never gated.** Cover, closing and photo-backdrop pages need image paths. With none given, runs variously skip photos, draw placeholder rectangles, download stock images or crash the kit.
3. **Toolchain is assumed, not checked.** The kit needs python-pptx; the checklist needs `pdffonts`; Open Sans must be installed as static files. On this machine none of the three is present, so each run improvises differently (installs, substitutes, or skips verification).
4. **The 230-line kit lives inline.** Every run must transcribe it into `newmont_kit.py`, which invites transcription errors and partial rewrites.
5. **No content-to-page-type mapping.** The same brief becomes a different slide structure each run because nothing says which page type fits which kind of content.
6. **Verification is unreachable.** "Render and look at every page" has no concrete command, so some runs render and fix, others ship blind.

## Method

- Four prompts, each run **3 times** per skill version, by independent subagents that see only the skill and the prompt (Opus, the model most users run the skill on).
- Baseline = the snapshot of the skill as it was (`newmont-skill-workspace/skill-snapshot`, config `old_skill`). Candidate = the revised skill (config `with_skill`).
- Subagents run unattended. The brief tells them: *if the skill's process calls for asking the user something, write the questions to `questions.md` and stop.* That makes gating observable and lets us check two things: under-specified prompts produce questions, and fully specified prompts do not.
- Grading is programmatic where possible (`newmont-skill-workspace/tools/grade_pptx.py`, `grade_html.py`) so the same check runs identically on every output, plus an LLM grader for the judgment calls (did it invent figures, did it summarise its changes).
- Repeatability is read two ways: per-assertion pass rate across the 3 runs (a check that flips between runs is the inconsistency), and for the gating case, the overlap of question topics across runs.
- Results go in `newmont-skill-workspace/iteration-N/<case>/<config>/run-K/` and are aggregated with skill-creator's `aggregate_benchmark.py`, then opened in its review viewer.

## Cases (`evals/`)

| Case | What it probes | Fully specified? |
|---|---|---|
| `underspecified-deck-asks-first` | A one-line deck request with no figures, photos, name or date. Should stop and ask, not invent Q3 safety numbers. | No |
| `complete-brief-deck` | Every input given (deck name, date, spelling, six pages of verbatim content, two photos). Should build without asking and match the brief exactly. | Yes |
| `html-one-pager` | Format translation to HTML with given content and no photos. Should build; palette, Open Sans, flat design, logo SVG. | Yes |
| `fix-off-brand-deck` | An agency deck in Calibri with wrong colours, shadows and rounded corners. Should keep all text, restyle to the system, and list what changed. | Mostly |

## Pass criteria for the revision

- Under-specified case: 3/3 runs stop and ask; questions cover the same core topics each time (deck name and date, the actual figures or source, photos, length, format).
- Complete-brief case: 0/3 runs ask; the programmatic checks (fonts, palette, slide size, footer and logo on content pages, table structure, no effects) pass in all 3 runs.
- Any assertion that passes in some runs and fails in others under the new skill is a defect to fix before calling the skill consistent.

## Running it again later

From the skill directory, with Claude Code installed: `claude plugin eval . --allow-tools Write,Edit,Bash --scaffold` runs the same case folders. The skill-creator workflow (this session) is the equivalent inside the app.

## Round four (2026-11-16): template routing and source of truth

The skill was rebuilt around the Brand Identity Guidelines (October 2025) and the two Feb 2026 PowerPoint templates. Decks are now instances of a template's named layouts (`scripts/newmont_deck.py`), the sources are resolved from `brand-sources.json` (`scripts/brand_sources.py`), requests are routed by `scripts/route_template.py`, and every request is logged (`scripts/brand_log.py`). The old hand-measured kit and its geometry checks are gone.

- Unit tests (`python3 -P -m unittest discover -s tests -v`) cover source resolution and versions, the loud failure when a file is missing or duplicated, every routing rule, the log fields, the kit's role maps for all 97 layouts (snapshots in `tests/fixtures/`), placeholder clean-up, the run record, and the checker's exit code on an off-brand deck.
- Five acceptance cases were added under `evals/` for the three phases: `routing-qbr-detailed-view`, `routing-strategy-exec-summary`, `routing-ambiguous-asks`, `missing-source-stops`, `activation-word-memo`. The nine earlier cases were re-pointed at layout names, the router's reason and the run record. Results: `evals/RESULTS-2026-11-16.md` (one smoke run each; the three-run repeatability pass is still to do).
