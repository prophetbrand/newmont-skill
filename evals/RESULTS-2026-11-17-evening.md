# Full suite, 2026-11-17 (evening): 14 cases × 3 runs, Fable adjudication

Branch `feat/template-routing-oct2025-guidelines` with the day's uncommitted changes (slimmed Detailed View packaging, shared `strip_sample_slides`, Copilot instruction edits; the repo SKILL.md is unchanged since the 10:00 rerun). Each case ran three times as independent Opus subagents given only the SKILL.md path, the verbatim prompt, a run folder, the log export, the unattended rule ("write questions.md and stop") and the reply rule, with `evals/` off limits. One **Fable** grader per case scored every run against `evals/<case>/graders/*.md`, re-running `check_deck.py` on every deck, reading slide text through python-pptx, Word through python-docx and HTML as stripped text plus CSS, and treating any recased, relabelled or reordered line as a verbatim failure. Workspace: scratchpad `suite3/`, one `GRADES.md` per case.

## Summary

| Case | Graders | Run 1 | Run 2 | Run 3 | Total | Morning (10:00) | Repeatable? |
|---|---|---|---|---|---|---|---|
| routing-qbr-detailed-view | 7 | 7 | 7 | 6 | 20/21 | 20/21 | 02 |
| routing-strategy-exec-summary | 6 | 6 | 5 | 5 | 16/18 | 18/18 | 02 |
| routing-ambiguous-asks | 6 | 6 | 6 | 6 | 18/18 | 18/18 | yes |
| missing-source-stops | 5 | 5 | 5 | 5 | 15/15 | 15/15 | yes |
| activation-word-memo | 6 | 6 | 6 | 5 | 17/18 | 15/18* | 05 |
| complete-brief-deck | 14 | 14 | 14 | 13 | 41/42 | 41/42 | 11 |
| underspecified-deck-asks-first | 7 | 7 | 7 | 7 | 21/21 | 21/21 | yes |
| just-go-with-placeholders | 7 | 6 | 7 | 7 | 20/21 | 21/21 | 04 |
| long-content-must-split | 8 | 8 | 8 | 8 | 24/24 | 24/24* | yes |
| financial-template-two-slides | 8 | 8 | 8 | 8 | 24/24 | 22/24* | yes |
| html-one-pager | 8 | 8 | 8 | 8 | 24/24 | 24/24* | yes |
| off-palette-request | 6 | 6 | 6 | 5 | 17/18 | 14/18* | 04 |
| fix-off-brand-deck | 8 | 8 | 8 | 8 | 24/24 | 24/24* | yes |
| photo-backdrop-and-phases | 6 | 5 | 5 | 5 | 15/18 | 18/18 | yes |

**Overall: 296 / 306 checks passed (96.7%).** 8 of 14 cases repeatable on every grader. Morning figure (the 245/306 full suite with the seven starred cases rerun after fixes): 295/306 (96.4%). No run stopped to ask except the three underspecified runs, which are meant to.

## What failed, and whose fault it is

**1. Delivery-notice opener (4 runs, 3 cases: routing-qbr run-3, routing-strategy run-2 and run-3, just-go-with-placeholders run-1).** Replies began "Your deck is ready: water-strategy.pptx (6 slides)." and gave the template, reason, no-question statement and source versions in paragraph two. The content is complete; only the order breaks the "opens with the template and why" rule in SKILL.md's Reply format. Fable graded it strictly and consistently. Fix: say in Reply format that the first line is the template line and that any file-ready sentence comes after the source versions. This is the single largest source of lost points (4 of 10).

**2. Thank you Opt 5 with one photo (photo-backdrop-and-phases, grader 04, all three runs).** The brief supplies one photo for the close; SKILL.md allows Opt 5 only with two supplied photos, so every run that chose Opt 5 left a "PHOTO: replace" box. The case's own `expected_outcome` names Opt 5, so the case and the skill disagree. This is a case defect, not a skill regression: change the expectation to Opt 1, or have the prompt assign site.jpg as the second closing photo. The three runs were otherwise identical and flagged that backdrop.jpg and people.jpg are byte-identical.

**3. Verbatim drift in Word (activation-word-memo run-3).** The run dropped the Subject line into the title and added an invented lead sentence. Runs 1 and 2 kept all four header lines. Same class as the morning's run-3 lead-line note, now caught because Fable reads the .docx rather than the reply.

**4. Improvised logo lockup (off-palette-request run-3).** A typed "Newmont" wordmark next to the extracted monogram. The logo rule forbids adding to or redrawing the logo; the monogram-only extraction invites this. A standalone approved logo file from Newmont would close it.

**5. Stray helper file (complete-brief-deck run-3).** An empty `required-text-run3.tmp` one level above the run folder. Same flip as the morning, different file; the no-rm rule in the harness brief makes clean-up impossible for runners, so this grader measures harness noise as much as the skill.

## Kit and rule findings from the runner reports (not graded, worth fixing)

- `render_pages` puts its LibreOffice profile at `render/.lo-profile` inside the deck folder, against SKILL.md's "profile outside the working folder" rule. Five runners moved it by hand. Fix in the kit: profile under the system temp dir.
- Three Executive Summary runners found level-0 body text renders bold on `Two Column Comparison` and `Three Column Panels` and had to drop body sentences to level 1 or 2 by trial. The layouts reference says so for some layouts; the kit could set the level from the role.
- All three financial runs hit the `Financial Performance (full Portfolio)` table overflowing the footer at 13 or 14 rows and cut to 8 to 10. SKILL.md's "at most 14 rows" is too generous for that layout; 10 is the safe figure.
- `Ex Summary` (Detailed View) leaves six empty icon frames when no icon files are given; two runners noted it, the checker does not catch it.
- The `Statement` layout's title placeholder sits off the visible slide (long-content run-3 moved the label into the body).
- The monogram extracted with `brand_sources.py --logo` clips the ™ mark; several HTML and Word runs re-cropped it.
- `clarifying_question_asked` is set by `--asked` for intake questions too, so the log cannot distinguish a template question from a content question.

## Per-case grades

### routing-qbr-detailed-view

| Grader | run-1 | run-2 | run-3 |
|---|---|---|---|
| 01 builds-without-template-question | PASS: no questions.md; requests.jsonl clarifying_question_asked false; q3-qbr.pptx built (3 slides) | PASS: no questions.md; requests.jsonl clarifying_question_asked false; q3-qbr.pptx built (3 slides) | PASS: no questions.md; requests.jsonl clarifying_question_asked false; q3-qbr.pptx built (3 slides) |
| 02 reply-names-detailed-view-and-reason | PASS: opens "Template: Detailed View", reason "Matched Detailed View cues: QBR", "didn't need to ask", quotes Oct 2025 and both Feb 2026 versions | PASS: opens "Template: Detailed View", cue "QBR", "asked no question", quotes Oct 2025 and both Feb 2026 versions | FAIL: reply opens "Your QBR deck is ready"; template, QBR reason, no-question and all three source versions follow only in paragraph two |
| 03 detailed-view-layouts | PASS: python-pptx layouts 1_Cover slide Opt 1b, Overall Highlights (table+highlights+risks), Thank you Opt 1; checker: no free shapes | PASS: same three Detailed View layouts, content fits Overall Highlights; checker: no free shapes, master 0 | PASS: same three Detailed View layouts, content fits Overall Highlights; checker: no free shapes, master 0 |
| 04 figures-verbatim-nothing-invented | PASS: table rows match all 12 figures with labels/periods; 3 highlights and 2 risk/mitigation lines verbatim; title adds no figure | PASS: all 12 figures with labels/periods; highlights and risk lines verbatim; title "improved on Q2 on all four measures" adds no figure or percentage | PASS: all 12 figures with labels/periods; highlights and risk lines verbatim; column header "Measure" and title add no figure |
| 05 run-record | PASS: script printed "ok detailed_view [3 layouts]", exit 0; sources set complete | PASS: script printed "ok detailed_view [3 layouts]", exit 0; sources set complete | PASS: script printed "ok detailed_view [3 layouts]", exit 0; sources set complete |
| 06 checker-clean | PASS: re-ran check_deck.py --template detailed_view: 12 PASS lines, no FAIL, exit 0 | PASS: re-ran check_deck.py --template detailed_view: 12 PASS lines, no FAIL, exit 0 | PASS: re-ran check_deck.py --template detailed_view: 12 PASS lines, no FAIL, exit 0 |
| 07 activation-path-logged | PASS: run.json and requests.jsonl activation_path "indirect: put into slides", clarifying_question_asked false | PASS: run.json and requests.jsonl activation_path "indirect: put into slides", clarifying_question_asked false | PASS: run.json and requests.jsonl activation_path "indirect: put into slides", clarifying_question_asked false |

### routing-strategy-exec-summary

| Grader | run-1 | run-2 | run-3 |
|---|---|---|---|
| 01 builds-without-asking | PASS: water-strategy.pptx built (6 slides); no questions.md; log clarifying_question_asked=false | PASS: water-strategy.pptx built (6 slides); no questions.md; log clarifying_question_asked=false | PASS: water-strategy.pptx built (6 slides); no questions.md; log clarifying_question_asked=false |
| 02 reply-names-exec-summary-and-reason | PASS: first line "Template: Executive Summary... matched cues (strategy, explain); no question was needed"; quotes Guidelines Oct 2025, both templates Feb 2026 | FAIL: reply opens "Your deck is ready: water-strategy.pptx (6 slides)." before Template line; reason, no-question and all three source versions are present | FAIL: reply opens "Your deck is ready: water-strategy.pptx (6 slides)." before Template line; reason, no-question and all three source versions are present |
| 03 layouts-follow-content-shape | PASS: python-pptx layouts: 1_Cover slide Opt 1, Statement, Three Column Panels, Two Column Comparison, Title Sub and Content (table), Thank you Opt 1 | PASS: same six layouts in same order; table on Title Sub and Content; no free-form, agenda or Detailed View layout | PASS: same six layouts in same order; table on Title Sub and Content; no free-form, agenda or Detailed View layout |
| 04 content-verbatim-placeholders-listed | PASS: all 24 given lines found exactly (casing, punctuation); [Q1/Q2/Q3 2027] kept bracketed and listed; only added text is declared slide titles | PASS: all 24 lines exact; brackets kept and listed; added titles and lead-in "Each step has one owner and a target quarter." declared, no figures/dates invented | PASS: all 24 lines exact; brackets kept and listed; only added text is declared titles/subtitle |
| 05 run-record | PASS: grader script exit 0; template executive_summary, three sources, 6 layouts for 6 slides | PASS: grader script exit 0; template executive_summary, three sources, 6 layouts for 6 slides | PASS: grader script exit 0; template executive_summary, three sources, 6 layouts for 6 slides |
| 06 checker-clean | PASS: re-ran check_deck.py --template executive_summary: 12 PASS, 0 FAIL, exit 0 | PASS: re-ran check_deck.py --template executive_summary: 12 PASS, 0 FAIL, exit 0 | PASS: re-ran check_deck.py --template executive_summary: 12 PASS, 0 FAIL, exit 0 |

### routing-ambiguous-asks

| Grader | run-1 | run-2 | run-3 |
|---|---|---|---|
| 01 asked-or-defaulted | PASS: no questions.md; deck on Exec Summary master; reply opens "Template: Executive Summary (defaulted)" naming both cues (progress update / project update). | PASS: no questions.md; Exec Summary master; reply opens "Executive Summary (default applied, no question asked)" naming both cues. | PASS: no questions.md; Exec Summary master; reply opens "Executive Summary (defaulted)" naming both cues. |
| 02 exactly-one-question | PASS: no questions.md; reply asks nothing about content, name, date, length, photos, fonts or colours (only offers a rebuild). | PASS: no questions.md; reply raises no such questions. | PASS: no questions.md; reply raises no such questions. |
| 03 builds-nothing-when-asking | PASS: script exits 0 (no questions.md, so the pptx is allowed). | PASS: script exits 0. | PASS: script exits 0. |
| 04 no-silent-detailed-view | PASS: checker confirms master theme "Newmont Exec Summary PPT"; run.json template executive_summary. | PASS: same; master is Exec Summary, template executive_summary. | PASS: same; master is Exec Summary, template executive_summary. |
| 05 logged | PASS: requests.jsonl and run.json show template executive_summary, defaulted true, routing_reason naming both cues and unattended run. (Logged request string is truncated to first sentence.) | PASS: log line and run.json show executive_summary, defaulted true, router's reason with both cues. | PASS: log line and run.json show executive_summary, defaulted true, router's reason with both cues. |
| 06 content-not-invented | PASS: all 11 lines verbatim (casing, punctuation); only digits are "2026"; added titles/headers restate given items, no new milestones. | PASS: all 11 lines verbatim; only digits "2026"; added titles count given items, no new milestones or dates. | PASS: all 11 lines verbatim; only digits "2026"; added lead-in and titles add no figures, dates or milestones. |

### missing-source-stops

| Grader | run-1 | run-2 | run-3 |
|---|---|---|---|
| 01 reports-missing-source | PASS: reply quotes brand_sources.py error naming role 'guidelines', glob, run-1/empty-sources folder; says add or replace file there | PASS: reply quotes error naming 'guidelines', glob, run-2/empty-sources folder; says add the files there | PASS: reply quotes error naming 'guidelines', glob, run-3/empty-sources folder; says add the files there |
| 02 builds-nothing | PASS: grader script exit 0; run folder holds only brief.txt, reply.md, requests.jsonl | PASS: grader script exit 0; no pptx/html/docx in run folder | PASS: grader script exit 0; no pptx/html/docx in run folder |
| 03 no-fallback | PASS: no output file; reply refuses older/remembered values; log output null, template null; no redirect of the variable | PASS: no output; reply "stopped rather than build from older brand values"; log output null; no redirect | PASS: no output; reply refuses older values; log output null. Suggests user may repoint variable, runner itself did not |
| 04 env-var-applied | PASS: sources_error in log names run-1/empty-sources, so brand_sources.py ran with the variable set | PASS: sources_error names run-2/empty-sources; brand_sources.py exit 2 noted in log | PASS: sources_error names run-3/empty-sources, so brand_sources.py ran with the variable set |
| 05 logged | PASS: requests.jsonl entry activated true, activation_path "direct: deck/presentation/slides", sources_error set, notes "stopped: brand source missing" | PASS: entry activated true, direct: path, sources_error set, notes "stopped: brand source missing ... exit 2; nothing built" | PASS: entry activated true, direct: path, sources_error set, notes "stopped: brand source missing ... nothing built" |

### activation-word-memo

| Grader | run-1 | run-2 | run-3 |
|---|---|---|---|
| 01 word-not-deck | PASS: safety-memo.docx present, no .pptx in run folder | PASS: safety-memo.docx present, no .pptx in run folder | PASS: safety-memo.docx present, no .pptx in run folder |
| 02 guidelines-only-and-sections | PASS: reply says no approved Word template, Guidelines October 2025 (sha), sections 3, 7, 8 memo p31 | PASS: reply says sources hold no Word template, Guidelines October 2025 (sha), sections 1,2,3,7,8, p31 | PASS: reply says no Word template, Guidelines October 2025 (sha), sections 2,3,7,8 memo p31 |
| 03 activation-path-logged | PASS: requests.jsonl entry in brand_log format: activated true, path "explicit other product: Word", template null | PASS: same entry shape, activated true, path "explicit other product: Word", template null (routing_reason empty) | PASS: entry activated true, path "explicit other product: Word", template null |
| 04 document-styling | PASS: title Open Sans Bold 20pt 0C2B82; MEMO Montserrat 10pt 3A68C5; head Open Sans 14pt caps; body 9pt; footer NEWMONT CORPORATION + PAGE/NUMPAGES; colours 000000/0C2B82/3A68C5; template monogram declared; renders 1 page | PASS: same styling (footer navy); body 9pt; palette only; template monogram declared; renders 1 page | PASS: same styling, lead 12pt, body 9pt; palette only; template monogram declared (TM crop noted); renders 1 page |
| 05 content-verbatim | PASS: To/From/Date/Subject lines and three points verbatim (python-docx); [Your name] kept; only added "MEMO" label and "THREE CHANGES" head, no figures/dates invented | PASS: all four lines (tab after colon) and three points verbatim; [Your name] kept; only "MEMO" and a section head added | FAIL: no "Subject: Three changes..." line anywhere in the docx (only reused as title); invented lead sentence "This memo sets out three changes..." |
| 06 no-routing-or-questions | PASS: no questions.md, no router output or template question in reply/log, template null, clarifying_question_asked false | PASS: no questions.md, reply states no template routed and no questions asked, log template null | PASS: no questions.md, reply says no routing, log template null, no question asked |

### complete-brief-deck

| Grader | run-1 | run-2 | run-3 |
|---|---|---|---|
| 01 builds-without-asking | PASS: no questions.md; log clarifying_question_asked=false; ahafo-review.pptx present | PASS: no questions.md; log clarifying_question_asked=false; ahafo-review.pptx present | PASS: no questions.md; log clarifying_question_asked=false; ahafo-review.pptx present |
| 02 six-slides-in-order-on-named-layouts | PASS: 6 slides, 960x540 pt; 1_Cover slide Opt 1, Section divider - Dark, Two Column Comparison, Three Column Panels, Title Sub and Content, Thank you Opt 1 | PASS: same six layouts in brief order, 960x540 pt, checker "all on master 0", no free shapes | PASS: same six layouts in brief order, 960x540 pt, checker "all on master 0", no free shapes |
| 03 fonts-from-theme | PASS: every run font.name is None (inherited); checker font line PASS | PASS: every run font.name is None (inherited); checker font line PASS | PASS: every run font.name is None (inherited); checker font line PASS |
| 04 only-palette-colours | PASS: only explicit colours are table text FFFFFF and 0C2B82, both in brand-values palette; checker "all in palette" | PASS: only explicit colours FFFFFF and 0C2B82 (table text), both in palette; checker "all in palette" | PASS: only explicit colours FFFFFF and 0C2B82 (table text), both in palette; checker "all in palette" |
| 05 footer-and-page-numbers | PASS: slides 3-5 FOOTER placeholders read deck name, SLIDE_NUMBER placeholders present (checker 3/3); no free shapes | PASS: slides 3-5 FOOTER placeholders read deck name, SLIDE_NUMBER placeholders present (checker 3/3); no free shapes | PASS: slides 3-5 FOOTER placeholders read deck name, SLIDE_NUMBER placeholders present (checker 3/3); no free shapes |
| 06 table-structure-matches-brief | PASS: slide 5 OBJECT placeholder holds 6x3 table: header Item/Approved/Actual to date, 4 rows, Total 716/697; subtitle and footnote in placeholders | PASS: same 6x3 table in OBJECT placeholder with brief figures; subtitle "Project capital, USD millions" and footnote in placeholders | PASS: same 6x3 table in OBJECT placeholder with brief figures; subtitle "Project capital, USD millions" and footnote in placeholders |
| 07 no-effects | PASS: checker "No slide shape has shadows/effects, gradients, 3D or rounded corners" PASS ("flat") | PASS: checker effects line PASS ("flat") | PASS: checker effects line PASS ("flat") |
| 08 content-verbatim | PASS: all 45 required lines found verbatim; cover is two paragraphs "Ahafo North"/"Ramp-up Review"; headers uppercase as given; nothing added | PASS: all 45 required lines verbatim, cover kept on two lines, nothing rewritten or added | PASS: all 45 required lines verbatim, cover kept on two lines, nothing rewritten or added |
| 09 rendered-before-delivering | PASS: render/ahafo-review.pdf (6 pages) exists; reply says rendered and looked at every page; states Open Sans not installed | PASS: render/ahafo-review.pdf (6 pages); reply says rendered with LibreOffice, viewed all six pages, Open Sans not installed | PASS: render/ahafo-review.pdf (6 pages); reply says rendered through LibreOffice, viewed every page, Open Sans not installed |
| 10 limits-kept-and-flagged | PASS: longest column body ~235 chars (<320), panels ~130 (<250), divider 14 chars (<30); no autofit, no resize; reply invents no problem | PASS: no brief line exceeds the layout tables; placeholders untouched, autofit None; reply invents no problem | PASS: no brief line exceeds the layout tables; placeholders untouched, autofit None; reply invents no problem |
| 11 no-stray-files | PASS: outputs are deck, run.json, build_ahafo_review.py, render/; other files (brief, jpgs, required-text) are scaffold/runner | PASS: outputs are deck, run.json, build_ahafo_review.py, render/; rest is scaffold/runner | FAIL: stray empty required-text-run3.tmp left at case level by run-3's runner; otherwise only deck, run.json, build_deck.py, render/ |
| 12 run-record | PASS: grader script exit 0; template executive_summary, 3 sources, 6 layouts for 6 slides | PASS: grader script exit 0; template executive_summary, 3 sources, 6 layouts for 6 slides | PASS: grader script exit 0; template executive_summary, 3 sources, 6 layouts for 6 slides |
| 13 reply-template-and-versions | PASS: after a one-line "deck is ready", names Executive Summary, reason "names it explicitly", Guidelines Oct 2025 5d4380f98f04, both templates Feb 2026 with shas; slide table | PASS: opens with Executive Summary and reason; Guidelines Oct 2025 and both Feb 2026 templates with shas; numbered slide/layout/title list | PASS: after a one-line "deck is ready", names Executive Summary, router reason quoted, three sources with shas; numbered slide/layout/title list |
| 14 checker-clean | PASS: check_deck.py re-run 14/14 PASS, no FAIL lines, exit 0 | PASS: check_deck.py re-run 14/14 PASS, no FAIL lines, exit 0 | PASS: check_deck.py re-run 14/14 PASS, no FAIL lines, exit 0 |

### underspecified-deck-asks-first

| Grader | run-1 | run-2 | run-3 |
|---|---|---|---|
| 01 stops-and-asks | PASS: questions.md written, no .pptx in folder, log output null; no safety figures invented | PASS: questions.md written, no .pptx in folder, log output null; no safety figures invented | PASS: questions.md written, no .pptx in folder, log output null; no safety figures invented |
| 02 asks-for-the-figures | PASS: Q1 asks for TRIFR, injuries, fatalities, HPIs with Q2/target "or the report they come from" | PASS: Q1 asks for TRIFR, injuries, fatalities, HPIs with comparison "or the report they come from" | PASS: Q1 asks for TRIFR, injuries, fatalities, HPIs "or the report they are in" |
| 03 template-question-handled | PASS: reply states Detailed View "router matched safety performance"; log routing_reason matches; not asked | PASS: reply states Detailed View, router matched "safety performance"; log routing_reason matches; not asked | PASS: reply states Detailed View (performance reporting: "safety performance"); log matches; not asked |
| 04 asks-deck-name-and-date | PASS: Q3 asks deck name and cover date, default "Newmont – Q3 2026 Safety Performance", November 2026 | PASS: Q3 asks deck name and cover date, default "Newmont – Q3 2026 Safety Performance", November 2026 | PASS: Q3 asks deck name and cover date, default "Newmont – Q3 2026 Safety Performance", November 2026 |
| 05 asks-length-or-sections | PASS: Q4 "Roughly how many slides. Default: 8." | PASS: Q4 "Roughly how many slides. Default: 8." | PASS: Q4 "Length. Default: 8 slides" with eight sections listed |
| 06 questions-are-few-and-material | PASS: 4 numbered questions, each material; Q1 ends with placeholder fallback, Q2-4 explicit defaults; nothing on photos/fonts/colours/format | PASS: 4 numbered questions, each material; Q1 ends with placeholder fallback, Q2-4 explicit defaults; nothing on photos/fonts/colours/format | PASS: 4 numbered questions, each material; Q1 ends with placeholder fallback, Q2-4 explicit defaults; nothing on photos/fonts/colours/format |
| 07 logged-asked-and-stopped | PASS: requests.jsonl activated true, activation_path "direct: deck/presentation/slides", clarifying_question_asked true, notes "stopped to ask", output null | PASS: requests.jsonl activated true, "direct: deck/presentation/slides", clarifying_question_asked true, notes "stopped to ask", output null | PASS: requests.jsonl activated true, "direct: deck/presentation/slides", clarifying_question_asked true, notes "stopped to ask", output null |

### just-go-with-placeholders

| Grader | run-1 | run-2 | run-3 |
|---|---|---|---|
| 01 builds-without-asking | PASS: 8-slide pptx built; no questions.md; log has clarifying_question_asked=false | PASS: 8-slide pptx built; no questions.md; log has clarifying_question_asked=false | PASS: 8-slide pptx built; no questions.md; log has clarifying_question_asked=false |
| 02 figures-are-bracketed-placeholders | PASS: python-pptx dump shows every table value and bullet bracketed ([0.00], [00 cases], [0,000]); only unbracketed digits are Q3/Q2/2026 and "per 200,000 h" unit | PASS: all values bracketed ([0], [0.00], [000], [00]); unbracketed digits are only quarter/year labels; no real safety stat | PASS: all values bracketed ([0], [0.00], [000], [00]); unbracketed digits are only quarter/year labels; no real safety stat |
| 03 no-photo-layouts-without-files | PASS: layouts are 1_Cover slide Opt 1b and Thank you Opt 1 plus content layouts; no picture shapes added; no image fetched (log shows none) | PASS: same layout set; no picture shapes added; no image fetched | PASS: same layout set; no picture shapes added; no image fetched |
| 04 reply-opens-with-assumptions | FAIL: reply opens with a file announcement sentence ("Your Q3 safety deck is built...") before the template line; name and date are each marked "This is a proposal" | PASS: opens "Template: Detailed View" with router reason, then sources, then Assumptions; deck name and cover date each "This is a proposal" | PASS: opens "Template: Detailed View" with reason, sources, Assumptions; name "(my suggestion)", date in same bullet under "change any of these" (date not itself labelled) |
| 05 default-outline | PASS: layouts cover, Purpose, Overall Highlights, ScoreCard Tables, Quarterly Performance, Highlights Risks & Mitigations, Outlook, Thank you Opt 1 | PASS: identical 8-layout Detailed View outline | PASS: identical 8-layout Detailed View outline |
| 06 checker-and-run-record | PASS: my re-run with --template detailed_view passes all 12 checks, no empty placeholders; run.json has template, sources, layouts_used | PASS: my re-run passes all 12 checks; run.json has template, sources, layouts_used; reply lists the checker's items | PASS: my re-run passes all 12 checks; run.json has template, sources, layouts_used, render paths |
| 07 template-reason-honest | PASS: deck master is Detailed View; reply and run.json give "Matched Detailed View cues: safety performance"; defaulted=false | PASS: same; reply states router matched "safety performance" | PASS: same; reply states router matched "safety performance" |

### long-content-must-split

| Grader | run-1 | run-2 | run-3 |
|---|---|---|---|
| 01 builds-without-asking | PASS: no questions.md; log clarifying_question_asked=false; reply names Executive Summary, reason "project update" | PASS: no questions.md; log clarifying_question_asked=false; reply names Executive Summary, reason "project update" | PASS: no questions.md; log clarifying_question_asked=false; reply names Executive Summary, reason "project update" |
| 02 workstreams-split-not-shrunk | PASS: slides 2–3 both `Three Column Panels`, 3 panels each, no table, no explicit sizes or autofit; render clean | PASS: slides 2–3 both `Three Column Panels`, 3 panels each, no table, no explicit sizes or autofit; render clean | PASS: slides 2–3 both `Three Column Panels`, 3 panels each, no table, no explicit sizes or autofit; render clean |
| 03 risks-complete-within-limits | PASS: slides 4–5 `Two Column Comparison`, 4+3 pairs (limit 4), mitigation body 292/229 chars under ~320; render no overflow | PASS: slides 4–5 `Two Column Comparison`, 4+3 pairs (limit 4), mitigation body 292/229 chars under ~320; render no overflow | PASS: slides 4–5 `Two Column Comparison`, 4+3 pairs (limit 4), mitigation body 292/229 chars under ~320; render no overflow |
| 04 decision-on-statement-layout | PASS: slide 6 `Statement`; body line 1 "DECISION REQUESTED", line 2 the sentence verbatim; off-slide title "Decision requested" | PASS: slide 6 `Statement`; body line 1 "DECISION REQUESTED", line 2 the sentence verbatim; off-slide title paraphrase only | PASS: slide 6 `Statement`; body line 1 "DECISION REQUESTED", line 2 the sentence verbatim; title placeholder dropped |
| 05 no-shrunk-or-explicit-type | PASS: python-pptx finds no run font.size or font.name on any shape; no normAutofit/spAutoFit in any bodyPr; checker fonts PASS | PASS: python-pptx finds no run font.size or font.name on any shape; no normAutofit/spAutoFit in any bodyPr; checker fonts PASS | PASS: python-pptx finds no run font.size or font.name on any shape; no normAutofit/spAutoFit in any bodyPr; checker fonts PASS |
| 06 content-verbatim | PASS: grader re-run of --required-text: all 31 lines found verbatim, case-sensitive; risk numbering is the brief's own | PASS: grader re-run of --required-text: all 31 lines found verbatim, case-sensitive; risk numbering is the brief's own | PASS: grader re-run of --required-text: all 31 lines found verbatim, case-sensitive; risk numbering is the brief's own |
| 07 page-list-and-checks-in-reply | PASS: 7 slides listed as number, layout, title; says check_deck.py passed incl. template theme; rendered with LibreOffice, every page looked at | PASS: 7 slides listed as number, layout, title; says check_deck.py passed 14 checks; rendered (PDF only in render/), pages looked at | PASS: 7 slides listed as number, layout, title; says check_deck.py passed 14 rules; rendered, PNGs in render/, pages looked at |
| 08 run-record-and-versions | PASS: run.json template executive_summary, 3 sources with shas, 7 layouts_used for 7 slides; reply quotes all three shas | PASS: run.json template executive_summary, 3 sources with shas, 7 layouts_used for 7 slides; reply quotes all three shas | PASS: run.json template executive_summary, 3 sources with shas, 7 layouts_used for 7 slides; reply quotes all three shas |

### financial-template-two-slides

| Grader | run-1 | run-2 | run-3 |
|---|---|---|---|
| 01 two-slides-no-cover-no-questions | PASS: pptx has 2 slides (Ex Summary, Financial Performance), no cover/closing, no questions.md, run.json clarifying_question_asked=false | PASS: 2 slides, no cover/closing, no questions.md, clarifying_question_asked=false | PASS: 2 slides, no cover/closing, no questions.md, clarifying_question_asked=false |
| 02 detailed-view-with-reason | PASS: master theme 'Newmont PP Feb-26' (detailed_view); reply gives router reason "matched on financials" and why Ex Summary is a layout not template | PASS: detailed_view master; reply: router matched cue "financials", executive summary names a slide not the template | PASS: detailed_view master; reply: router matched "financials", Ex Summary is a layout not the template |
| 03 financial-layouts | PASS: slide 1 `Ex Summary`; slide 2 `Financial Performance (full Portfolio)` table with 3 period columns plus "Change vs prior quarter" | PASS: `Ex Summary`; `Financial Performance (full Portfolio)` table, 3 period columns plus "Change vs prior quarter" | PASS: `Ex Summary`; `Financial Performance (full Portfolio)` table, 3 period columns plus "Change vs prior" |
| 04 named-layouts-no-free-form | PASS: build_deck.py uses Deck.add twice, no free_slide/add_shape/add_table; checker "No free shapes"; run.json notes "0 free-form slides" | PASS: Deck.add x2 only; checker no free shapes; run.json "0 free-form slides" | PASS: Deck.add x2 only; checker no free shapes; run.json "0 free-form slides" |
| 05 placeholders-and-no-duplication | PASS: all cells `[0,000 koz]`, `[$0,000/oz]`, `[$0.0B]`, `[$0.00]`, `[+0.0%]`; slide 1 call-outs carry bracketed commentary, no figures repeated | PASS: cells `[0,000 koz]`, `[$0,000/oz]`, `[$0,000M]`, `[$0.0B]`, `[$0.00/share]`, `[+0.0%]`; call-outs are commentary, no repeats | PASS: cells `[0,000 koz]`, `[$0,000]`, `[+0.0%]`; call-outs are bracketed commentary, no metric repeated |
| 06 reply-lists-suggestions-and-checks | PASS: "Suggestions to swap" lists headings, rows, columns; quotes three source shas; reports check_deck passed with template master and both pages rendered | PASS: "Suggestions to swap" lists themes, rows, columns; quotes three source shas; reports check_deck (Detailed View master) passed and pages rendered | PASS: "Suggestions to swap" lists headings, rows, columns; quotes three source shas; reports check_deck (Detailed View master) passed and pages rendered |
| 07 brand-mechanics | PASS: re-run checker 12/12: fonts ok, palette ok, flat, no empty placeholders, 2 footers and 2 slide numbers; icon picture placeholders not instantiated | PASS: re-run checker 12/12: fonts, palette, flat, no empty placeholders, 2 footers, 2 slide numbers; render page 1 clean | PASS: re-run checker 12/12: fonts, palette, flat, no empty placeholders, 2 footers, 2 slide numbers |
| 08 run-record | PASS: grader script exits 0: "ok detailed_view ['Ex Summary', 'Financial Performance (full Portfolio)']", sources set complete | PASS: grader script exits 0, template detailed_view, three sources, 2 layouts for 2 slides | PASS: grader script exits 0, template detailed_view, three sources, 2 layouts for 2 slides |

### html-one-pager

| Grader | run-1 | run-2 | run-3 |
|---|---|---|---|
| 01 builds-without-asking | PASS: questions.md empty, log clarifying_question_asked=false, tailings-update.html built, no .pptx in folder | PASS: questions.md empty, log clarifying_question_asked=false, tailings-update.html built, no .pptx in folder | PASS: questions.md empty, log clarifying_question_asked=false, tailings-update.html built, no .pptx in folder |
| 02 open-sans-loaded | PASS: Google Fonts link for Open+Sans; body font-family var(--nm-font) = "Open Sans","Segoe UI",Arial | PASS: Google Fonts link for Open+Sans; body font-family var(--nm-font) = "Open Sans","Segoe UI",Arial | PASS: Google Fonts link for Open+Sans; body font-family var(--nm-font) = "Open Sans","Segoe UI",Arial |
| 03 only-palette-colours | PASS: hex set is exactly the SKILL.md tokens (#0C2B82 #071435 #3A68C5 #0091DA #509E2F #FCAF17 #D9E8EC #E1EDF0 #ECF3F6 #A3A7AA) plus #000/#fff; no rgb() | PASS: identical token set plus #000/#fff; no rgb(), no inline styles, no retired colours | PASS: identical token set plus #000/#fff; no rgb(), no inline styles, no retired colours |
| 04 flat-design | PASS: only border-radius:0 on .nm-panel; no box-shadow, text-shadow or gradient anywhere | PASS: only border-radius:0 on .nm-panel; no box-shadow, text-shadow or gradient anywhere | PASS: border-radius:0 on * and .nm-panel; no box-shadow, text-shadow or gradient anywhere |
| 05 logo-handled | PASS: embedded PNG monogram (pixels #0C2B82/#FCAF17) rasterised from Executive Summary master EMF, top-left, 12px margin + 24px header padding; dropped clipped TM disclosed | PASS: embedded PNG monogram with TM, colours #0C2B82/#FCAF17, from Executive Summary master, top-left at 56px with 24px header padding | PASS: embedded PNG monogram from Executive Summary master, top-left 56px, 28px header padding; TM slightly clipped at right edge but not redrawn |
| 06 type-roles-applied | PASS: .nm-eyebrow 700/uppercase/#0C2B82; h1 700 #0C2B82 sentence case; .nm-panel background #D9E8EC; gold only as 4px header rule, text is #0C2B82 or #000 | PASS: .nm-eyebrow 700/uppercase/#0C2B82; h1 700 #0C2B82 sentence case; .nm-panel #D9E8EC; text only #0C2B82, #000, white on navy footer | PASS: .nm-eyebrow 700/uppercase/#0C2B82; h1 700 #0C2B82 sentence case; .nm-panel #D9E8EC; text only #0C2B82 and #000 |
| 07 content-verbatim | PASS: all 11 strings found verbatim and in order in page text (tags stripped); only added text is "Newmont Corporation" footer | PASS: all 11 strings found verbatim and in order in page text; only added text is "Newmont Corporation" footer | PASS: all 11 strings verbatim and in order; "1&nbsp;December" renders as the same words/punctuation (non-breaking space), footer only addition |
| 08 guidelines-only-and-logged | PASS: reply says no approved HTML template, "Brand Identity Guidelines (October 2025, sha 5d4380f98f04)", sections 2,3,7,8; log activated=true, activation_path "explicit other product: HTML", template null | PASS: reply says no approved web template, "Brand Identity Guidelines October 2025 (sha 5d4380f98f04)", sections 2,3,7; log activated=true, "explicit other product: HTML", template null | PASS: reply says no approved HTML template, "Brand Identity Guidelines, October 2025 (sha 5d4380f98f04)", sections 2,3,7,9; log activated=true, "explicit other product: HTML", template null (routing_reason empty) |

### off-palette-request

| Grader | run-1 | run-2 | run-3 |
|---|---|---|---|
| 01 builds-without-asking | PASS: open-day.html built, no questions.md, log clarifying_question_asked=false | PASS: open-day.html built, no questions.md, log clarifying_question_asked=false | PASS: open-day.html built, no questions.md, log clarifying_question_asked=false |
| 02 teal-only-on-banner | PASS: #008080 only in --sponsor-teal used by .banner; all other colours are nm tokens (incl. gold rule), #000, #fff | PASS: #008080 only via --sponsor-teal on .banner; everything else nm tokens, #000, #fff | PASS: #008080 only via --sponsor-teal on .event-banner; everything else nm tokens, #000, #fff |
| 03 departure-stated-in-one-line | PASS: "The banner uses the sponsor's teal #008080, which is not in the Newmont palette." No refusal or lecture | PASS: "the teal #008080 banner is outside the Newmont palette, as your sponsor asked." No refusal | PASS: "The sponsor teal (#008080) on the event banner is outside the Newmont palette, as you requested." No refusal |
| 04 rest-is-on-system | PASS: Open Sans first in --nm-font; untouched monogram top-left; flat, radius 0; eyebrow white caps on teal; callout on #D9E8EC (gold 3px rule on white noted) | PASS: Open Sans first; untouched monogram top-left; flat, radius 0; eyebrow white caps on teal; callout on #D9E8EC | FAIL: monogram top-left but a typed "Newmont" wordmark in Open Sans is added beside it, an improvised logo lockup; rest on system |
| 05 verbatim-and-rendered | PASS: all 11 strings exact and in order; reply says page rendered in Chrome and inspected (no render/ saved) | PASS: all 11 strings exact and in order; reply says rendered in headless Chrome at desktop, mobile crop admitted | PASS: all 11 strings exact and in order; reply says opened in Chrome at desktop and phone widths |
| 06 guidelines-only-and-logged | PASS: "no approved HTML template", October 2025 sha, sections 3 and 7 named; log activation_path "explicit other product: HTML" | PASS: "no approved HTML template", October 2025 sha, sections 3, 7, 9; log "explicit other product: HTML" | PASS: "don't include an HTML template", October 2025 sha, sections 2, 3, 7, 9; log "explicit other product: HTML" |

### fix-off-brand-deck

| Grader | run-1 | run-2 | run-3 |
|---|---|---|---|
| 01 content-preserved | PASS: 4 slides; python-pptx dump shows all 16 lines verbatim, same casing, order and slide; checker 16/16; no slide added | PASS: 4 slides; all 16 lines verbatim, same casing, order and slide; checker 16/16; no slide added | PASS: 4 slides; 16 lines verbatim incl. three Key Metrics table headers on slide 2; checker 16/16; no slide added |
| 02 rebuilt-on-template-layouts | PASS: build_fixed.py uses newmont_deck.Deck; layouts Cover 1b/Quarterly Performance/Title and Content; theme Newmont PP Feb-26; no explicit fonts | PASS: build_fixed.py uses newmont_deck.Deck; same layouts; theme Newmont PP Feb-26; no explicit font on any run | PASS: build_fixed.py uses newmont_deck.Deck; Cover 1b/Key Metrics/Title and Content; theme Newmont PP Feb-26; no explicit fonts |
| 03 only-palette-colours | PASS: checker "all in palette"; python-pptx shows no explicit run colours; no #1F4E79 or red | PASS: checker "all in palette"; no explicit run colours in dump | PASS: checker "all in palette"; no explicit run colours; tiles take layout fill |
| 04 flat-shapes | PASS: checker "flat" (no shadows/effects/gradients/rounded); only placeholders on slides | PASS: checker "flat"; only placeholders on slides | PASS: checker "flat"; only placeholders and table placeholders on slides |
| 05 size-footer-no-empty-placeholders | PASS: 960x540; checker no empty placeholders; 3 footers and 3 slide numbers ok; render slide 2 clean | PASS: 960x540; no empty placeholders; 3 footers and 3 slide numbers ok | PASS: 960x540; no empty placeholders; 3 footers and 3 slide numbers; render shows header-only tiles, no prompt text |
| 06 explains-changes | PASS: "What I changed" lists rebuild, fonts, colours, rounded boxes, footer furniture; three title rewrites listed separately, not applied | PASS: "What changed" covers rebuild, theme, rounded boxes, placeholders, footer; rewrites in separate "not applied" list | PASS: "What I changed" covers rebuild, gradient, Calibri, #1F4E79 boxes, source line; rewrites listed under not-done |
| 07 asks-at-most-name-and-date | PASS: no questions.md; reply states deck-name and date defaults from the cover; asked nothing else | PASS: no questions.md; name and date defaults stated under Assumptions | PASS: no questions.md; name and date defaults stated under Assumptions |
| 08 template-versions-and-run-record | PASS: names Detailed View, override reason, three source shas; run.json has template, sources, layouts_used, activation_path restyle: existing deck | PASS: names Detailed View, reason, three source shas; run.json fields present, activation_path restyle: existing deck (defaulted:true is inconsistent with override but not graded) | PASS: names Detailed View, reason, three source shas; run.json fields present, activation_path restyle: existing deck |

### photo-backdrop-and-phases

| Grader | run-1 | run-2 | run-3 |
|---|---|---|---|
| 01 builds four slides | PASS: 4 slides, no questions.md, reply names Executive Summary, reason cue "plan"; run.json template executive_summary, clarifying_question_asked false. | PASS: 4 slides, no questions.md, reply names Executive Summary with cue "plan" and storytelling reason; log matches. | PASS: 4 slides, no questions.md, reply names Executive Summary with cue "plan"; log matches. |
| 02 picture statement layout | PASS: slide 2 `Big statement with image - Dark Blue`; PICTURE placeholder holds backdrop.jpg (md5 match), crop l/r 0.174, no duotone/tint/recolor; statement and support text verbatim. | PASS: same layout; backdrop.jpg md5 match in picture placeholder, cropped only, no effects; statement and supporting text verbatim in body. | PASS: same layout; backdrop.jpg md5 match, crop only, no effects; statement and supporting text verbatim. |
| 03 process slide | PASS: `Title Sub and Content`, table Phase/When/What happens, 2 phase rows, both durations, headings, all 7 steps; not free-form, none claimed. | PASS: same layout and table; both phases, 6 weeks/8 weeks, both headings, all 7 steps verbatim. | PASS: same layout; headings as first line of What happens, both durations, all 7 steps; not free-form. |
| 04 closing with photo | FAIL: `Thank you Opt 5` with only people.jpg; second picture slot removed and a "PHOTO: replace" box left; SKILL.md allows Opt 5 only with two photos; site.jpg unused. | FAIL: `Thank you Opt 5`, people.jpg in slot 1, "PHOTO: replace" box left in slot 2; one closing photo supplied, Opt 1 not chosen; site.jpg unused. | FAIL: `Thank you Opt 5`, people.jpg only, "PHOTO: replace" box left bottom right; one photo for the close, Opt 1 not chosen; site.jpg unused. |
| 05 content verbatim | PASS: checker --required-text: all 20 lines found verbatim; cover title "Haul Truck"/"Autonomy Plan" and footer exact. | PASS: checker all 20 lines verbatim; casing and punctuation match the brief. | PASS: checker all 20 lines verbatim; casing and punctuation match the brief. |
| 06 checker, run record, versions | PASS: reply names check_deck.py pass; my re-run 13/13; run.json lists 4 layouts one per slide; reply quotes three source versions with shas and lists slides as number, layout, title. | PASS: reply names check_deck.py pass incl. replace box; re-run 13/13; run.json 4 layouts; versions with shas quoted; slides listed number/layout/title. | PASS: reply says "brand checker passed" (not named, but re-run 13/13); run.json 4 layouts; versions with shas quoted; slides listed number/layout/title. |


## Fixes and rerun (evening, after the suite)

Two edits, then the two most affected cases rerun three times each with Fable grading (workspace `suite3b/`):

1. **Reply format** in SKILL.md now says the first line of the reply is the template line, nothing before it, with the file name and slide count belonging to the slides-built section. The four "your deck is ready" openers were the largest loss in the suite.
2. **Photo close**: the Choosing layouts row for the close says that with one photo or none the close is `Thank you Opt 1` with the supplied photo declared unused, never a "PHOTO: replace" box; the photo note in Before you build no longer offers the box as a fallback for the close. The case's `expected_outcome` and grader 04 were changed to match (they had expected Opt 5 with one photo, which the skill forbids).

| Case | Suite | Rerun |
|---|---|---|
| routing-strategy-exec-summary | 16/18 | 18/18, template line first in all three replies |
| photo-backdrop-and-phases | 15/18 | 18/18, `Thank you Opt 1` with people.jpg declared unused in all three |

With these two cases at full marks the suite stands at **301/306 (98.4%)** on the current rules, 10 of 14 cases fully repeatable; the four remaining misses are single-run flips (QBR run-3 opener, placeholders run-1 opener, both now covered by the reply rule; one memo Subject line; one improvised logo lockup; one stray helper file). The packaged SKILL.md picks the edits up through the slicer (19,233 characters); 77 tests pass.

### routing-strategy-exec-summary (rerun)

| Grader | run-1 | run-2 | run-3 |
|---|---|---|---|
| 01 builds-without-asking | PASS: water-strategy.pptx built (6 slides), no questions.md, log clarifying_question_asked=false | PASS: water-strategy.pptx built (6 slides), no questions.md, log clarifying_question_asked=false | PASS: water-strategy.pptx built (6 slides), no questions.md, log clarifying_question_asked=false |
| 02 reply-names-exec-summary-and-reason | PASS: opens "Template: Executive Summary. The router matched Executive Summary cues ("strategy", "explain"); no question was needed."; quotes Oct 2025 / Feb 2026 / Feb 2026 | PASS: opens "Template: Executive Summary. The router matched Executive Summary cues ("strategy", "explain"); no clarifying question was needed."; quotes Oct 2025 / Feb 2026 / Feb 2026 | PASS: opens "Template: Executive Summary. The router matched Executive Summary cues ("strategy", "explain"); no question was needed."; quotes Oct 2025 / Feb 2026 / Feb 2026 |
| 03 layouts-follow-content-shape | PASS: python-pptx layouts: 1_Cover slide Opt 1, Statement, Three Column Panels, Two Column Comparison, Title Sub and Content (table), Thank you Opt 1; no free-form, all master 0 | PASS: python-pptx layouts: 1_Cover slide Opt 1, Statement, Three Column Panels, Two Column Comparison, Title Sub and Content (table), Thank you Opt 1; no free-form, all master 0 | PASS: python-pptx layouts: 1_Cover slide Opt 1, Statement, Three Column Panels, Two Column Comparison, Title Sub and Content (table), Thank you Opt 1; no free-form, all master 0 |
| 04 content-verbatim-placeholders-listed | PASS: headline, 3 priority pairs, Today/Where we are going, table rows and "Thank you" exact in slide text; [Q1/Q2/Q3 2027] kept and listed in reply | PASS: headline, 3 priority pairs, Today/Where we are going, table rows and "Thank you" exact in slide text; [Q1/Q2/Q3 2027] kept and listed in reply | PASS: headline, 3 priority pairs, Today/Where we are going, table rows and "Thank you" exact in slide text; [Q1/Q2/Q3 2027] kept and listed in reply |
| 05 run-record | PASS: grader script exit 0; template executive_summary, sources guidelines/detailed_view/executive_summary, 6 layouts for 6 slides | PASS: grader script exit 0; template executive_summary, sources guidelines/detailed_view/executive_summary, 6 layouts for 6 slides | PASS: grader script exit 0; template executive_summary, sources guidelines/detailed_view/executive_summary, 6 layouts for 6 slides |
| 06 checker-clean | PASS: re-ran check_deck.py --template executive_summary; 12 PASS lines, 0 FAIL lines | PASS: re-ran check_deck.py --template executive_summary; 12 PASS lines, 0 FAIL lines | PASS: re-ran check_deck.py --template executive_summary; 12 PASS lines, 0 FAIL lines |

### photo-backdrop-and-phases (rerun)

| Grader | run-1 | run-2 | run-3 |
|---|---|---|---|
| 01 builds-four-slides | PASS: 4 slides, no questions.md, reply names Executive Summary with router reason "plan" | PASS: 4 slides, no questions.md, reply names Executive Summary with router reason "plan" | PASS: 4 slides, no questions.md, reply names Executive Summary with router reason "plan" |
| 02 picture-statement-layout | PASS: `Big statement with image - Dark Blue`; backdrop.jpg sha1 in PICTURE placeholder, crop only, no blip effects; statement and support verbatim | PASS: same layout; backdrop.jpg in PICTURE placeholder, crop only, no blip effects; statement and support verbatim | PASS: same layout; backdrop.jpg in PICTURE placeholder, crop only, no blip effects; statement and support verbatim (statement bold) |
| 03 process-slide | PASS: `Title Sub and Content` table Phase/When/What happens; both headings, 6 weeks/8 weeks, all 7 steps | PASS: `Title Sub and Content` table; "Phase 1: Control room fit-out", durations, all 7 steps | PASS: `Title Sub and Content` table; both headings, durations, all 7 steps |
| 04 closing-with-photo | PASS: slide 4 `Thank you Opt 1`; reply says people.jpg not used because Opt 5 needs two photos; no fetched image, no empty placeholders | PASS: `Thank you Opt 1`; reply says people.jpg not used, Opt 5 needs two; build uses only backdrop.jpg; no empty placeholders | PASS: `Thank you Opt 1`; reply says people.jpg not used, Opt 5 needs two; build uses only backdrop.jpg; no empty placeholders |
| 05 content-verbatim | PASS: checker required-text "all 20 lines found" | PASS: checker required-text "all 20 lines found" | PASS: checker required-text "all 20 lines found" |
| 06 checker-run-record-versions | PASS: checker 13/13 PASS on re-run; run.json lists 4 layouts, one per slide; reply quotes three source versions and slides as number, layout, title | PASS: checker 13/13 on re-run; run.json 4 layouts; reply quotes versions and lists number, layout, title | PASS: checker 13/13 on re-run; run.json 4 layouts; reply quotes versions and lists number, layout, title |

