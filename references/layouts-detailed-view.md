`Newmont_PPT Template_Detailed View_Feb_2026.pptx` · Feb 2026 · master 0 "Newmont PP Feb-26": 46 layouts (master 1 "Newmont Always Safe PP Feb-26", 4 layouts, not catalogued)

Source of truth at runtime: `python3 scripts/catalog_layouts.py <template>`. Sample slide numbers refer to `references/template-sample-slides.md`.
Almost every content layout also has idx 16 (6pt source line, bottom), plus DATE, FOOTER and SLIDE_NUMBER placeholders (idx varies per layout); these are omitted below. Placeholders typed TABLE can only take `insert_table()` in python-pptx; where the samples show a chart in a TABLE placeholder, add the chart at that placeholder's box and delete the placeholder.

## Covers
| Layout | For | Placeholders to fill | Content limits | Samples |
|---|---|---|---|---|
| `Cover slide Opt 1` | Opening slide, title top-right on navy with two built-in mine photos (haul trucks / pit) | 14: title (48pt); 1: subtitle + date (10pt bold, gold) | Title 2 lines (~35 chars); subtitle 2 short lines | 16 |
| `Cover slide Opt 1b` | Variant of Opt 1: same boxes, different built-in photos (lake / pit) | 14: title; 1: subtitle + date | as above | 17 |
| `1_Cover slide Opt 1b` | Variant of Opt 1: same boxes, photos of two workers + aerial pit | 14: title; 1: subtitle + date | as above | 1, 14 |
| `3_Cover slide Opt 1b` | Variant of Opt 1: same boxes, conveyor + drill-rig photos, one extra rule line | 14: title; 1: subtitle + date | as above | 15 |
| `Cover slide Opt 2` | Opening slide with title lower (y 222pt), logo bottom-left, photos top-right and mid-left | 14: title; 1: subtitle + date | as above | 18 |
| `Cover slide Opt 2b` | Variant of Opt 2: different built-in photos | 14: title; 1: subtitle + date | as above | 19 |

Cover photos are baked into the layouts (free shapes), so pick the variant for its photos; they cannot be swapped via placeholders.

## Dividers, agenda, purpose
| Layout | For | Placeholders to fill | Content limits | Samples |
|---|---|---|---|---|
| `Section divider - Dark` | Section break: blue/cyan/gold block graphic, no title placeholder | 13: divider text (48pt) | 1-2 lines, ~30 chars | 20 |
| `Sub-section divider` | Lighter-weight break: navy full-bleed, large left title | 0: title (48pt) | 1-2 lines, ~35 chars | 21 |
| `Agenda` | Agenda with purpose statement left, numbered items right | 0: title; 1: "PURPOSE" label (12pt bold); 13: purpose sentence (32pt); 14: agenda items (18pt, numbered) | Purpose ~60 chars; 4 items of ~110 chars (reduce to 16/14/12pt for more) | 24 |
| `Purpose` | One purpose statement on navy with gold edge | 0: small label (12pt, e.g. "Purpose of this document:"); 13: statement (36pt) | 1 sentence, ~100 chars | 25 |

## Content (text-led)
| Layout | For | Placeholders to fill | Content limits | Samples |
|---|---|---|---|---|
| `Overall Highlights` | Function update: highlights left, risks right, KPI table lower right | 0: title; 1: left header; 13: left bullets (12pt); 3: right header; 2: right bullets; 15: KPI header; 14: KPI table | Left 9 bullets (~1200 chars); right 4 bullets (~550); table 4-5 rows | 26, 27 |
| `Highlights, Risks & Mitigations` | Two region/side-by-side panels with photo banners baked in | 0: title; 1: subtitle (14pt bold); 3, 15: panel headers (18pt bold, e.g. region); 17, 20: small banner tags (7pt); 18, 19: panel bullets (10pt) | 6-12 short lines per panel (~200 chars) | 31-37 |
| `Quarterly Performance` | Three parallel columns with headers plus a takeaway bar | 0: title; 1, 3, 14: column headers (kit roles `head1..head3`, 14pt bold); 13, 2, 15: column bullets (`col1..col3`); 16: takeaway (kit role `takeaway`, 10.5pt bold) | 3 bullets (~100 chars each) per column; takeaway ~200 chars | 53 |
| `Work Underway` | Four columns: shaded lead column + three topic columns | 0: title; 1: subtitle (kit role `head1`); 20: lead column (kit role `col1`); 21, 22, 23: topic columns (`col2..col4`, 14pt) | Lead ~700 chars; 6 bullets (~400 chars) per column | 68 |
| `Ex Summary` | Executive summary: narrative left, six icon + text call-outs right | 0: title; 1: lead-in; 30: narrative (10pt); 31, 33, 35, 37, 39, 41: call-outs (8pt bold head); 32-42 even: icon pictures; 23: rotated side tab | Narrative ~700 chars; call-outs ~240 chars each | 64 |
| `Labour Relations Landscape` | World-map landscape with call-outs; the map is a free shape | 0: title; 1: subtitle | Map labels must be drawn as shapes | 42 |

## Charts
| Layout | For | Placeholders to fill | Content limits | Samples |
|---|---|---|---|---|
| `ScoreCard` | H&S-style scorecard: two KPI strips, four small charts, commentary | 0: title; 1, 3: table headers (10pt bold); 14, 18: KPI tables; 19, 21: chart-group headers; 22-25: charts; 20: commentary header; 13: commentary bullets | Tables 2-3 rows; 4 bullets | 28 |
| `People Dashboard` | Workforce dashboard: four stat tiles with donuts, diversity bar | 0: title; 1, 17, 19, 21: tile headers (9pt bold); 18, 20, 22: donut charts; 23: band header; 25: headcount block (14pt bold); 26, 27: % figures; 24: bar chart | Tile headers 1-2 words; figures ~10 chars | 40, 41 |
| `Performance Against Plan` | Main chart + table left, two small charts and a table right | 0: title; 17: chart header; 25: main chart; 24: data table; 23, 31: column headers; 26, 28: small chart headers; 27, 29: small charts; 32: table; 30: note (8pt) | Note ~2 lines | 59 |
| `Performance Against Plan 2` | One large chart + strip table left, side table and chart right | 0: title; 17: header; 25: chart; 24: strip table; 32: table; 26: header; 27: chart; 30: note (8pt) | Note ~4 lines | 60 |
| `Customers & Markets` | Sales mix: KPI strip, two bar charts, two donuts with mini tables | 0: title; 1: subtitle (kit role `head1`, not `lead`); 24: KPI strip table; 17, 35, 26: chart headers; 25, 36, 27, 34: charts; 32, 33: mini tables | KPI strip 5 cells | 61 |
| `Summary Financial Metrics` | Six chart tiles (2 x 3) each with header | 0: title; 1: lead-in (14pt bold); 17, 26, 28, 30, 32, 34: headers (9pt bold); 25, 27, 29, 31, 33, 35: charts | Header ~25 chars | 66 |
| `Balance Sheet & Dividend Review` | Two charts side by side with commentary below | 0: title; 1: lead-in; 17, 20: headers; 14, 21: chart areas (TABLE type); 19, 2: commentary (12pt) | Commentary 2 bullets each | 56 |

## Tables and scorecards
| Layout | For | Placeholders to fill | Content limits | Samples |
|---|---|---|---|---|
| `Financial Performance (full Portfolio)` | Full-width financial table with lead-in | 0: title; 1: lead-in (14pt bold); 14: table | ~2 tables of 6-8 rows, or one of ~14 rows | 54, 55 |
| `ScoreCard Tables` | Two tables side by side (left shorter) | 0: title; 14, 18: tables | ~15 rows each | 29 |
| `Key Metrics` | Seven KPI tiles (2 + 3 + 2) as table placeholders | 0: title; 1: lead-in (14pt); 17-23: KPI tables | One metric + 1-2 lines each | 65 |
| `Commercial Performance Summary ` (note trailing space) | KPI tile tables left, summary bullets and legend right | 0: title; 24, 25: KPI tables; 20: summary (12pt); 26: legend table | 5 bullets | 58 |
| `QBR: Investor Relations Update` | Three columns: two text tables and share-price chart/table | 0: title; 24, 25: column tables; 23: header; 26: small table; 17: header; 14: table/chart | ~8 bullets per column | 57 |
| `Outlook` | Guidance table left, two smaller tables right | 0: title; 1: lead-in (OBJECT); 17: main table; 18, 19: side tables | Main ~8 rows; side ~3 rows | 63 |
| `Cost Summary` | Key points left, cost table right | 0: title; 1: key points (OBJECT); 17: table | 4 bullets; ~20 rows | 67 |
| `Risks & Mitigation` | Table left with four picture slots right | 0: title; 1: subtitle; 14: table; 17-20: pictures | ~10 rows | 39, 52 |

## Pictures
| Layout | For | Placeholders to fill | Content limits | Samples |
|---|---|---|---|---|
| `Images & Messaging` | Text box plus three photos in a 2 x 2 grid | 0: title; 20: text (12pt); 17, 18, 19: pictures | Text ~3 short paras (~150 chars) | 46 |
| `1_Images & Messaging` | Variant: adds a full-width lead-in (21, 14pt) and shortens the grid | 0: title; 21: lead-in; 20: text; 17-19: pictures | Lead-in ~230 chars | 47 |
| `Progress Pictures` | One full-width photo with caption | 0: title; 17: picture; 23: caption (10pt bold) | Caption 1 line | 38, 48 |
| `Progress Pictures x2` | Two photos with captions | 0: title; 17, 24: pictures; 23, 25: captions | Caption 1 line each | 49 |
| `Progress Pictures x3` | Three photos with captions | 0: title; 17, 24, 26: pictures; 23, 25, 27: captions | as above | 50 |
| `Progress Pictures x4` | Four photos (2 x 2) with captions | 0: title; 17, 24, 26, 28: pictures; 23, 25, 27, 29: captions | as above | 51 |

## Closing and Q&A
| Layout | For | Placeholders to fill | Content limits | Samples |
|---|---|---|---|---|
| `Thank you Opt 1` | Close: "Thank you" on navy with built-in haul-truck / pit photos | 14: text (54pt) | 1-2 words | 70 |
| `Thank you Opt 2` | Variant: same box, lake / pit photos | 14 | as above | 71 |
| `Thank you Opt 3` | Variant: conveyor / drill-rig photos | 14 | as above | 73 |
| `Thank you Opt 4` | Variant: workers / aerial pit photos | 14 | as above | 72 |
| `Thank you Opt 5` | Variant with your own photos | 14: text; 15, 16: pictures | as above | 74 |
| `Q&A` | Q&A with photo bleeding left on light-blue | 0: title (48pt); 13: picture | "Q&A" + ~40 chars | 22 |
| `Q&A Option 2` | Variant: cyan background, photo inset | 0: title; 13: picture | as above | 23 |

## Utility
| Layout | For | Placeholders to fill | Content limits | Samples |
|---|---|---|---|---|
| `Title and Content` | Generic slide; samples use it for guidance pages, tables and dashboards drawn as free shapes | 0: title; 1: body/object | ~8 bullets or one table | 2-13, 43-45, 62, 69 |
| `Title Only` | Free-form canvas (process chevrons, frameworks) | 0: title | n/a | 30 |

Variants summary: the six covers share identical placeholders (Opt 1 family title at y105, Opt 2 family at y222) and differ only in baked photos; Thank you Opt 1-4 identical except photos; Opt 5 swaps baked photos for picture placeholders; Q&A vs Option 2 differ in background and photo bleed; 1_Images & Messaging adds a lead-in.

## Picking a layout
| Need | Use | Runner-up |
|---|---|---|
| Opening | `1_Cover slide Opt 1b` | `Cover slide Opt 2` |
| Agenda | `Agenda` | `Purpose` |
| Section break | `Section divider - Dark` | `Sub-section divider` |
| One statement | `Purpose` | `Sub-section divider` |
| 2 parallel points | `Highlights, Risks & Mitigations` | `Overall Highlights` |
| 3 parallel points | `Quarterly Performance` | `Work Underway` (lead + 3) |
| 4 parallel points | `Work Underway` | `Ex Summary` (six call-outs) |
| Comparison | `Highlights, Risks & Mitigations` | `Balance Sheet & Dividend Review` |
| Process / timeline | `Title Only` + drawn chevrons (sample 30) | `Title and Content` with a table |
| KPI scorecard | `ScoreCard` | `Key Metrics` |
| Risks and mitigations | `Highlights, Risks & Mitigations` | `Risks & Mitigation` |
| Financial table | `Financial Performance (full Portfolio)` | `Cost Summary` |
| Chart(s) with commentary | `Performance Against Plan 2` | `Summary Financial Metrics` (six charts) |
| Photos with captions | `Progress Pictures x2` / `x3` / `x4` | `Images & Messaging` |
| People / labour dashboard | `People Dashboard` | `Labour Relations Landscape` |
| Outlook | `Outlook` | `Work Underway` |
| Close | `Thank you Opt 1` | `Q&A` |
