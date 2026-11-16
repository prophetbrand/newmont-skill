`Newmont_PPT Template_Executive Summary_Feb_2026.pptx` · Feb 2026 · master 0 "Newmont Exec Summary PPT": 51 layouts (master 1 "Newmont Always Safe PP Feb-26", 4 layouts; master 2 "Newmont Everyday PP Feb-26", 46 layouts with the same names as the Detailed View master; neither catalogued here)

Source of truth at runtime: `python3 scripts/catalog_layouts.py <template>`. Sample slide numbers refer to `references/template-sample-slides.md`.
Most content layouts also have idx 16 (6pt source line) and, on some, DATE/FOOTER/SLIDE_NUMBER; omitted below. Titles are 24pt, "two lines max, do not exceed five-column width" (~120 chars). Lead-in idx 17 (14pt) fits 2 lines (~230 chars).
The Detailed View layouts (ScoreCard, People Dashboard, Outlook, Progress Pictures and so on) are reachable in this file through master 2 "Newmont Everyday PP Feb-26"; see `layouts-detailed-view.md`.

## Covers
| Layout | For | Placeholders to fill | Content limits | Samples |
|---|---|---|---|---|
| `Cover slide Opt 1` | Opening slide, title top-right on navy with built-in haul-truck / pit photos | 14: title (48pt); 1: subtitle + date (10pt bold) | Title 2 lines (~35 chars); subtitle 2 short lines | 7, 8 |
| `1_Cover slide Opt 1` | Variant of Opt 1: same boxes, conveyor + drill-rig photos | 14: title; 1: subtitle + date | as above | 1, 6 |
| `2_Cover slide Opt 1` | Variant of Opt 1: same boxes, workers + aerial pit photos | 14: title; 1: subtitle + date | as above | 5 |
| `Cover slide Opt 1b` | Variant of Opt 1: lake / pit photos | 14: title; 1: subtitle + date | as above | 9 |
| `Cover slide Opt 2` | Title lower (y 222pt), logo bottom-left | 14: title; 1: subtitle + date | as above | 10 |
| `Cover slide Opt 2b` | Variant of Opt 2: different photos | 14: title; 1: subtitle + date | as above | 11 |

Cover photos are baked into the layouts (free shapes); choose by photo.

## Dividers, agenda, statements
| Layout | For | Placeholders to fill | Content limits | Samples |
|---|---|---|---|---|
| `Section divider - Dark` | Section break, blue/cyan/gold block graphic | 13: divider text (48pt) | 1-2 lines, ~30 chars | 12 |
| `Sub-section divider` | Lighter break, navy full-bleed title | 0: title (48pt) | 1-2 lines, ~35 chars | 13, 17, 31, 41, 48, 50, 52, 54, 66 |
| `Agenda` | Purpose left, numbered agenda right | 0: title; 1: "PURPOSE" label (12pt bold); 13: purpose (32pt); 14: items (18pt) | Purpose ~100 chars; 4 items of ~110 chars | 15 |
| `Agenda Image` | Purpose + short agenda left, full-height photo right half | 0: title; 1: label; 13: purpose + items (28pt first para); 15: picture | Purpose ~100 chars + 3 short items | 14 |
| `Statement` | One statement in large type on dark blue | 17: statement (24pt) | ~300 chars, 2 paras | 32 |
| `Story / Summary` | Input / story on top, output / conclusion in a dark band below | 17: story (24pt); 19: conclusion (24pt) | Story ~130 chars; conclusion ~40-80 chars | 34 |
| `Big statement with image - Light Blue` | Statement left, photo right, cyan background | 10: statement (28pt); 11: picture | ~175 chars | 35, 38 |
| `Big statement with image - Light` | Variant: pale blue-grey background | 10; 11 | as above | 36, 39 |
| `Big statement with image - Dark Blue` | Variant: dark-blue background | 10; 11 | as above | 37, 40 |

`Statement` and `Story / Summary` carry a 12pt title placeholder (idx 0) positioned above the slide (top -35pt): it is invisible, so fill it only for accessibility/outline.

## Content (columns and panels)
| Layout | For | Placeholders to fill | Content limits | Samples |
|---|---|---|---|---|
| `Title Sub and Content` | Title, lead-in, one body/table | 0: title; 17: lead-in; 1: body/table | ~8 bullets or ~12-row table | 53, 68 |
| `Two Column` | Two text columns under a lead-in | 0: title; 17: lead-in (14pt bold); 1, 2: columns | ~5 paras (~680 chars) per column | 19 |
| `Three Column` | Three text columns | 0: title; 17: lead-in; 1, 2, 18: columns | 2 paras (~310 chars) each | 20 |
| `Four Column` | Four text columns | 0: title; 17: lead-in; 1, 2, 18, 19: columns | 2 paras (~175 chars) each | 21 |
| `Two Column Comparison` | Two headed columns to compare | 0: title; 17: lead-in; 1, 3: headers (14pt bold); 13, 2: bodies | Header 1 line; body ~320 chars | 22 |
| `Three Column Comparison` | Three headed columns | 0; 17; 1, 3, 18: headers; 13, 2, 19: bodies | as above, ~250 chars | 23 |
| `Four Column Comparison` | Four headed columns | 0; 17; 1, 3, 18, 20: headers (2 lines); 13, 2, 19, 21: bodies | ~175 chars | 24 |
| `Two Column Panels` | Two shaded panels (title + body inside each) | 0: title; 17: lead-in; 1, 2: panels | 3 paras (~340 chars) | 25 |
| `Three Column Panels` | Three shaded panels | 0; 17; 1, 2, 18 | ~250 chars | 26 |
| `Four Column Panels` | Four shaded panels | 0; 17; 1, 2, 18, 19 | ~175 chars | 27 |
| `Two Column Panels Icon` | Two panels each with an icon on top | 0; 17; 1, 2: panels (12pt); 32, 33: icons | ~420 chars | 28 |
| `Three Column Panels Icon` | Three icon panels | 0; 17; 1, 2, 34: panels; 32, 33, 35: icons | ~256 chars | 29 |
| `Four Column Panels Icon` | Four icon panels | 0; 17; 1, 2, 34, 36: panels; 32, 33, 35, 37: icons | ~256 chars | 30 |

## Charts
All chart headers are 9pt bold (one line); charts sit on a light grey panel baked into the layout.
| Layout | For | Placeholders to fill | Content limits | Samples |
|---|---|---|---|---|
| `Single chart` | One full-width chart | 0: title; 19: chart header; 18: chart | 1 chart, ~8 categories | 56 |
| `Single chart with lead-in text` | One chart under a lead-in | 0; 17: lead-in; 19; 18 | as above | 55 |
| `Single chart with supporting text` | Bullets left, chart right | 0; 1: bullets; 23: header; 22: chart | ~7 bullets (~820 chars) | 61 |
| `Two charts` | Two charts side by side | 0; 19, 23: headers; 18, 22: charts | | 57 |
| `Two charts with supporting text` | Bullets left, two stacked charts right | 0; 1; 23, 25; 22, 24 | ~6 bullets | 62 |
| `Three charts` | Two stacked left, one tall right | 0; 19, 21, 23; 18, 20, 22 | | 58 |
| `Three charts with supporting text` | Bullets left, wide chart + two small | 0; 1; 19, 21, 23; 18, 20, 22 | ~6 bullets | 63 |
| `Four charts` | 2 x 2 charts | 0; 19, 21, 23, 25; 18, 20, 22, 24 | | 59 |
| `Four charts with supporting text` | Bullets left, 2 x 2 charts | 0; 1; 19, 21, 23, 25; 18, 20, 22, 24 | ~6 bullets | 64 |
| `Five charts with supporting text` | Short text top-left plus five charts | 0; 1: text (short box); 19-27 odd: headers; 18-26 even: charts | ~300 chars | 65 |
| `Six charts` | 3 x 2 charts with lead-in | 0; 17: lead-in (14pt bold); 19-29 odd: headers; 18-28 even: charts | | 60 |

## Tables and scorecards
No dedicated table layout in master 0; the samples place tables in OBJECT placeholders.
| Layout | For | Placeholders to fill | Content limits | Samples |
|---|---|---|---|---|
| `Title and Content` | Single full-width table | 0: title; 1: table | ~20 rows | 67 |
| `Title and Two Content` | Two tables stacked, second with subtitle; also agenda-as-table | 0; 1: top; 17: subtitle (14pt bold); 18: bottom | ~6 rows each | 16, 69 |
| `Two Content` | Two tables side by side | 0; 1, 2 | ~15 rows each | 70 |
| `Two Content Sub` | Two tables side by side under a lead-in | 0; 17; 1, 2 | ~12 rows each | 71 |
| `Four Content Sub` | 2 x 2 small tables/tiles under a lead-in (sample 73 squeezes six) | 0; 17; 1, 2, 18, 19 | ~5 rows each | 72, 73 |

## Pictures
Picture slots live in `Agenda Image` (15), `Big statement with image` (11), the `Panels Icon` layouts (icons) and `Thank you Opt 5`. For captioned photo grids use the Everyday master's `Progress Pictures` layouts.

## Closing
| Layout | For | Placeholders to fill | Content limits | Samples |
|---|---|---|---|---|
| `Thank you Opt 1` | Close on navy with haul-truck / pit photos | 14: text (54pt) | 1-2 words | 74 |
| `Thank you Opt 2` | Variant: different baked photos (no sample) | 14 | as above | none |
| `Thank you Opt 3` | Variant: conveyor / drill-rig photos | 14 | as above | 76 |
| `Thank you Opt 4` | Variant: workers / aerial pit photos | 14 | as above | 75, 77 |
| `Thank you Opt 5` | Variant with your own photos (picture placeholders) | 14; 15, 16: pictures | as above | 78, 79 |
No Q&A layout in master 0 (use the Everyday master's `Q&A`).

## Utility
| Layout | For | Placeholders to fill | Content limits | Samples |
|---|---|---|---|---|
| `Title Only` | Free-form canvas: infographics, process chevrons, frameworks, data synthesis (all drawn as free shapes) | 0: title | n/a | 3, 4, 33, 42-47, 49, 51 |
| `Title and Content` | Generic one body | 0: title; 1: body | ~8 bullets | 2, 18, 67 |
| `Title abd Sub` (sic) | Title + one subtitle line, otherwise empty | 0: title; 1: subtitle (14pt bold) | n/a | none |

Always Safe master samples 80-82 (`AS_Title Slide`, `AS_Section Divider_Digital`, `AS_Title and Content`) are for safety content only.

## Picking a layout
| Need | Use | Runner-up |
|---|---|---|
| Opening | `1_Cover slide Opt 1` | `Cover slide Opt 2` |
| Agenda | `Agenda` | `Agenda Image` |
| Section break | `Section divider - Dark` | `Sub-section divider` |
| One statement | `Statement` | `Big statement with image - Dark Blue` |
| 2 parallel points | `Two Column Panels` | `Two Column` |
| 3 parallel points | `Three Column Panels Icon` | `Three Column Comparison` |
| 4 parallel points | `Four Column Panels` | `Four Column Comparison` |
| Comparison | `Two Column Comparison` | `Two Content Sub` |
| Process / timeline | `Title Sub and Content` with a timeline table (sample 53) | `Title Only` + chevrons (samples 45, 47) |
| KPI scorecard | `Four Content Sub` | Everyday master `ScoreCard` |
| Risks and mitigations | `Two Column Comparison` | Everyday master `Highlights, Risks & Mitigations` |
| Financial table | `Title Sub and Content` | `Title and Content` |
| Chart(s) with commentary | `Single chart with supporting text` | `Two charts with supporting text` |
| Photos with captions | `Big statement with image - Light` | Everyday master `Progress Pictures x3` |
| People / labour dashboard | Everyday master `People Dashboard` | `Four charts with supporting text` |
| Outlook | `Story / Summary` | `Two Column Comparison` |
| Close | `Thank you Opt 1` | `Thank you Opt 5` |
