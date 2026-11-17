# Newmont brand skill as an Agent Builder skill package

Prepared 17 November 2026. This is the optional cut-down skill experiment in `agent-config.md` section 5 (spike item H). Run it only after the plain build in `test-plan.md` has been tested.

## Build the zip

```bash
python3 -P scripts/package_for_copilot.py --out dist/newmont-brand-copilot-skill.zip   # --template executive_summary|detailed_view|both (default both)
python3 -P -m unittest discover -s tests -p "test_package_for_copilot.py" -v
```

The packager follows Agent Builder's limits (Microsoft Learn, 16 November 2026): SKILL.md under 20,000 characters, 25 MB per file, 50 MB per zip, at most 8 skills per agent. It refuses to build when a file or the zip would break a limit. It skips any approved source over 25 MB with a warning and writes a stop note into the generated SKILL.md. It also prints the manifest. `dist/` is not in `.gitignore`, so do not commit the zip.

## What the zip contains (build of 17 November 2026: 21.9 MB zipped)

| Path in the zip | Size | Notes |
|---|---|---|
| `SKILL.md` | 19,120 characters | Generated, see below |
| `references/skill-layouts-and-brand-rules.md` | 10.6 KB | "Choosing layouts" and "Brand rules the template does not enforce", verbatim |
| `references/layouts-executive-summary.md`, `layouts-detailed-view.md` | 10.3 KB, 11.5 KB | Layout digests |
| `brand-sources.json` | 0.6 KB | `sources_dir` rewritten to `brand-sources`; all three roles kept so a missing one fails loudly |
| `brand-values.json` | 3.1 KB | Values digested from the guidelines PDF |
| `brand-sources/Brand Guidelines October 2025.pdf` | 10.5 MB | |
| `brand-sources/Newmont_PPT Template_Executive Summary_Feb_2026.pptx` | 13.5 MB | |
| `scripts/` | 70 KB | `brand_sources.py`, `route_template.py`, `brand_log.py`, `catalog_layouts.py`, `inspect_pptx.py`, `newmont_deck.py`, `check_deck.py` |

The Detailed View template (73.5 MB) is **not** in the zip.

The generated SKILL.md is sliced from the repository SKILL.md by its `## ` headings, so later edits carry through. It contains the frontmatter (description 905 characters), a sandbox note, Phases 1 to 3, "Before you build" without the worked example, and a shortened "Building with the kit" (the API table and the example). It ends with "Checking before delivering" and "Reply format".

Two kept sections still sit in SKILL.md as headings, but their text is in `references/skill-layouts-and-brand-rules.md`, with a pointer telling the agent to read it before outlining. Without that move the kept text is 29,243 characters. Dropped entirely: "How a request flows", "Restyling", "Other formats" and the setup check (`pip install`, fonts, LibreOffice).

## Add it in Agent Builder

1. Open the agent's **Configure** tab and find **Skills**.
2. Choose **Add**, then upload `dist/newmont-brand-copilot-skill.zip`.
3. Leave code interpreter on. Save, then open **Preview** (web: **Try it**).

## What to test first, in this order

1. **Import check.** Ask: "Run `python3 -c "import pptx"` and `python3 -c "import pymupdf"` in your sandbox and tell me the output." If either fails, the skill should say the deck cannot be built here and offer the outline and layout list. It must not draw slides by hand. Record the result: this answers whether python-pptx is preinstalled.
2. **One Executive Summary build.** Run only if step 1 passed. Use suggested prompt 2 ("Build a short deck explaining our water stewardship strategy to site leaders.") with the full brief from `evals/routing-strategy-exec-summary/prompt.md`. Expect Executive Summary, the source versions in the reply, and the .pptx in OneDrive under `Documents/Copilot/Created/` (the reply's download link is minted under the agent's identity and may open as 'no access'; the OneDrive copy is the one to use). Run `check_deck.py` on the synced copy locally (see `test-plan.md`).
3. **Detailed View stop.** Run suggested prompt 1 ("put this into slides for the QBR"). Expect the reply to say the Detailed View template is not available in this package, with nothing built.

## What will not work

- **Detailed View decks.** These need the template under 25 MB, or hosted somewhere the sandbox can read, and the sandbox has no network. Until then, Detailed View requests stop.
- **The request log.** `logs/requests.jsonl` is written inside the sandbox and is deleted when the session ends. The reply carries the template, reason and source versions instead.
- **The guidelines PDF without pymupdf.** `newmont_deck.Deck` resolves the guidelines as well as the template, and the PDF is opened with pymupdf. Without it, every build stops with a SourceError.
- **Rendering.** LibreOffice is not expected in the sandbox, so decks are checked but not rendered, and Open Sans is probably not installed for previews.
- **Restyling, Word, Excel, email and HTML.** These are not in the package. The skill says it covers PowerPoint decks only, and a restyle is a rebuild on the routed template.
