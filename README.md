# newmont-skill

`newmont-brand` is a Claude skill that acts as Newmont's brand agent for PowerPoint: it activates on any deck request, routes it to the right approved template, builds every slide from that template's named layouts, applies the Brand Identity Guidelines (October 2025), and logs the activation path, template choice and source versions for every request.

## Layout

- `SKILL.md` – the skill: activation, source of truth, template routing, intake, layout choice, brand rules the template does not enforce, kit usage, checker, reply and log format, other Office formats.
- `brand-sources.json` – the one configured location for the approved files (folder, globs, log path). `brand-sources/README.md` says what goes there; the files themselves are not versioned.
- `references/` – digests of the sources: `brand-guidelines-2025-10.md`, `layouts-executive-summary.md`, `layouts-detailed-view.md`, `template-sample-slides.md`. The live files always win over the digests.
- `scripts/brand_sources.py` – resolves the three sources, derives their versions, fails loudly when one is missing.
- `scripts/route_template.py` – routes a request to Detailed View or Executive Summary, or asks one question; unattended runs default to Executive Summary.
- `scripts/newmont_deck.py` – python-pptx kit that opens the routed template, drops its sample slides, adds slides by layout name and fills placeholders by role; writes a run record and the request log on save.
- `scripts/check_deck.py`, `scripts/inspect_pptx.py` – brand checker for template decks.
- `scripts/catalog_layouts.py` – prints a template's layouts and placeholders live; `scripts/brand_log.py` – the request log; `scripts/demo_build.py` – builds a demo deck from each template.
- `tests/` – unit tests (`python3 -P -m unittest discover -s tests -v`).
- `evals/` – repeatability and acceptance test cases in the `claude plugin eval` layout, plus dated results.
- `TEST-PLAN.md` – how the skill is tested.
- `out/` – demo renders from the Feb 2026 templates.

## Setting up

1. Copy or symlink this folder to `~/.claude/skills/newmont-brand/`.
2. Put the three approved files in `brand-sources/` (or point `NEWMONT_BRAND_SOURCES` at the folder that holds them): the Brand Identity Guidelines PDF, the Detailed View template and the Executive Summary template. See `brand-sources/README.md`.
3. `pip install python-pptx`; LibreOffice for rendered previews; Open Sans installed for faithful previews.
4. Check: `python3 scripts/brand_sources.py` prints three resolved files with their versions.

Replacing a file in `brand-sources/` changes the layouts, theme and logged versions with no code change.

## Running the evals

```bash
claude plugin eval . --allow-tools Write,Edit,Bash --scaffold
```

The workspace pattern (three runs per prompt, programmatic plus LLM grading) is described in `TEST-PLAN.md` and the dated results under `evals/`. Results dated before 2026-11-16 measured the retired hand-drawn kit and are kept only as history.
