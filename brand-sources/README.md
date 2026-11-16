# Approved brand sources

This folder is the ONE place the skill reads its approved Newmont source files from. The files themselves are
large binaries and are not committed (see `.gitignore`); only this README is.

## Expected files

| Role | Matches (glob) | Current file |
|---|---|---|
| `guidelines` | `Brand Guidelines*.pdf` | Brand Guidelines October 2025.pdf |
| `detailed_view` | `*Template_Detailed View*.pptx` | Newmont_PPT Template_Detailed View_Feb_2026.pptx |
| `executive_summary` | `*Template_Executive Summary*.pptx` | Newmont_PPT Template_Executive Summary_Feb_2026.pptx |

The globs, labels and folder are configured in `brand-sources.json` at the repo root.

## Replacing a file

1. Put the new file here with a name that still matches the glob, e.g. `Newmont_PPT Template_Detailed View_Aug_2026.pptx`.
2. Move the old file out of this folder. Exactly one file may match each glob: if two or more match, the skill
   stops with a SourceError that names every match (no newest-wins).
3. Run `python3 scripts/brand_sources.py` and check the version column (edition from the file name or PDF cover,
   plus a sha256 prefix that changes whenever the file content changes).

No code change is needed. If a file is missing or cannot be opened, the skill stops and says so; it never falls
back to older brand values.

## Brand values (`values_file`)

The guidelines PDF cannot be read by a script, so the values taken from it (palette with graphics-only flags, chart
series order, approved fonts, chart axis label size and rule weight, the template-neutral greys the checker accepts)
live in `brand-values.json` at the repo root, set by the `values_file` key in `brand-sources.json` (default
`brand-values.json`; `NEWMONT_BRAND_VALUES` overrides). Its `guidelines_edition` field records the PDF edition it was
digested from. When the PDF here is a different edition, `brand_sources.py` and the deck kit print a warning and the
log entry carries `"values_stale": true`: re-digest the new PDF into `brand-values.json` (never edit it from memory).

## Overrides

- `NEWMONT_BRAND_SOURCES` – use a different folder (absolute, or relative to the repo root).
- `NEWMONT_BRAND_LOG` – write the request log somewhere other than `logs/requests.jsonl`.
- `NEWMONT_BRAND_CONFIG` – use a different config json.
- `NEWMONT_BRAND_VALUES` – use a different brand values json.
