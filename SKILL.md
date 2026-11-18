---
name: newmont-brand
description: Newmont's brand agent for decks. Use it whenever someone asks to create, build, draft, make, put together, update or redesign a PowerPoint, deck, presentation or slides, including indirect phrasing ("put this into slides for the QBR", "turn these notes into a few pages for the board", "a short presentation on X"). It picks the right approved Newmont template (Detailed View for business and performance reporting, Executive Summary for strategy and storytelling), builds every slide from that template's named layouts, applies the Brand Identity Guidelines (October 2025), and logs the activation, template choice and source versions. Also use it when a person explicitly asks for a Word document, Excel workbook, email or other Microsoft Office content "in the Newmont style" or "on-brand"; do not use it for Word, Excel or email requests that do not ask for Newmont branding, nor for non-Newmont work.
---

# Newmont brand agent

This skill reads three approved files from one configured location and nothing else: the **Brand Identity Guidelines (October 2025)**, the **PowerPoint Template – Detailed View (Feb 2026)** and the **PowerPoint Template – Executive Summary (Feb 2026)**. Their digests are in `references/` (read them for detail), but the templates themselves are the source of truth: every slide you build is an instance of one of their named layouts, with the theme's fonts and colours, and the version of each file is recorded with every deck.

Units are points (pt). Both templates are 960 × 540 pt (16:9).

## How a request flows

1. **Activate and name the path.** Decide whether this skill applies (next section) and which activation path it is. You will log it at the end.
2. **Resolve the sources.** Run `python3 scripts/brand_sources.py`. If it exits non-zero, stop and tell the person which file is missing and where it is expected; do not build from memory of older values.
3. **Intake.** Compare the request with "Before you build". Ask for missing must-haves in one message, then wait.
4. **Route to a template.** Run `python3 scripts/route_template.py "<the request>"`. Follow its decision; ask its clarifying question when it says to.
5. **Outline.** Write the slide list (number, layout name, title) using "Choosing layouts", and put it in your reply.
6. **Build** with `scripts/newmont_deck.py`. Named layouts only; a free-form slide only when no layout fits, and say so.
7. **Check and look.** Run `scripts/check_deck.py`, render, open every page, fix every FAIL.
8. **Deliver and log.** Reply in the format at the end. The kit writes the request log when you save; for requests that end without a deck (not activated, stopped to ask, source missing), write the log entry yourself with `scripts/brand_log.py`.

## Phase 1: activation

**Activate** for any request to create, build, draft, write, make, put together, update, restyle or redesign a PowerPoint, deck, presentation, slides, pages for a meeting, a pitch or a board pack, whatever the wording, and including indirect phrasing such as "put this into slides", "turn this into a few pages for the QBR", "can you deck this up". Every such request from a Newmont user is a Newmont deck; the person does not have to say "Newmont".

**Also activate** when the person explicitly asks for another Microsoft Office product in Newmont style: a Word document, Excel workbook, Outlook email or signature, "on-brand", "in the Newmont template", "to brand standards". Then apply "Other formats" below.

**Do not activate** for Word, Excel, email or other non-PowerPoint requests that do not ask for Newmont branding, for decks about another company that are not Newmont's, or for questions that only mention a deck in passing ("summarise this deck for me" is a reading task, not a build).

Name the path in your log and reply, with one of these labels:

| Label | Example |
|---|---|
| `direct: deck/presentation/slides` | "build a deck on Q3 safety" |
| `indirect: put into slides` | "put these notes into slides for the QBR" |
| `restyle: existing deck` | "fix this deck so it looks like Newmont" |
| `explicit other product: Word` (or Excel, email) | "a Word memo in the Newmont template" |
| `not activated: non-PowerPoint request` | "write me an email to the site manager" |

In a Claude session this skill only runs when it was loaded, so "not activated" entries can be written only by the host that decided not to load it; when you are loaded and decide the request is out of scope, log that yourself and say so in one line.

## Phase 2: source of truth

The configured location is `brand-sources.json` at the skill root: a `sources_dir` (default `brand-sources/` beside it, overridden by the environment variable `NEWMONT_BRAND_SOURCES`), one glob per role, and a `log_file`. `brand-sources/README.md` says what belongs there. Nothing in the scripts names a file by path; replacing a file in the folder changes the layouts, theme and versions the kit uses with no code change.

Before any build:

```bash
python3 scripts/brand_sources.py          # prints role, version and file for all three sources
```

- The version string is the edition read from the file ("October 2025" from page 1 of the PDF; "Feb 2026" from the template file name) plus a sha256 prefix, so two files with the same edition but different content are told apart. Put the versions in your reply and they go into the log automatically.
- **If a source is missing, will not open, or matches more than one file, the script exits 2 with the role, the glob and the folder.** Stop, show the person that message, and build nothing. Never fall back to the values in `references/` or in this file: they are digests, not the approved files. The one exception is an explicit Word, Excel or email request, which needs only the guidelines PDF; say which file was absent.
- The templates are read live, so a replaced template changes layouts, theme and versions at once. The guidelines PDF cannot be read by a script, so its values (palette with graphics-only flags, chart series order, fonts, chart axis sizes) are digested into `brand-values.json` (the contrast pairs stay in the reference and in this file) beside the config, stamped with the edition they came from. When the PDF in the folder is a different edition from that stamp, `brand_sources.py` and the kit print a warning and the log entry carries `values_stale: true`; tell the person, build on the template (which still governs the deck), and name the re-digest as the follow-up. Do not edit `brand-values.json` from memory.
- Where the guidelines and a template disagree (the October 2025 guidelines list the bright blue as `#0091DA` and allow Montserrat; the Feb 2026 templates use `#12A6E6` as a theme accent and Open Sans as the only theme font), **the template governs a deck** because the deck is an instance of it, and the guidelines govern everything the template does not set: charts, photography, contrast pairs, legal name, boilerplate, and all non-PowerPoint formats. Say so in one line if the person asks why a colour differs from the PDF.

## Phase 3: template routing

Run the router on the request text before outlining:

```bash
python3 scripts/route_template.py "put this into slides for the QBR"
python3 scripts/route_template.py "a deck on the tailings strategy" --unattended   # when no one can answer
```

Its rules, which you follow rather than re-derive:

- **Detailed View** for business reviews and QBRs, operational or financial performance and results, scorecards and KPI dashboards, people, labour or workforce updates, investor relations, progress reporting (progress updates, progress pictures), cost summaries, balance sheet and dividend reviews, highlights with risks and mitigations.
- **Executive Summary** for strategy, proposals and business cases, project updates and kick-offs, explainers and overviews, training and onboarding, narratives, frameworks, roadmaps, plans, recommendations, options and comparisons, town halls.
- A request that names a template ("use the detailed view template") gets that template.
- **Fits both, or neither:** ask the one clarifying question the router prints, and nothing else in that message beyond the intake questions you already owe. If no one can answer (an unattended run, or the person has said to proceed with defaults), it defaults to Executive Summary; your reply then opens with the template chosen and the reason the router gave.
- Detailed View layouts are also present inside the Executive Summary file (its "Everyday" master). Use one from there only when a single slide of a storytelling deck needs it (a scorecard in a strategy deck); the kit logs it as a cross-template layout.

The log entry records the template, the reason and whether the question was asked. Do not override the router silently: if you disagree with its choice, say why in the reply and log your choice as the reason. When it matched nothing, apply the two lists above yourself before accepting the default: a deck of figures, results, costs, headcount or a scorecard is Detailed View even when the words are misspelt or unusual ("the quartlery financials"). A request for "an executive summary slide" names a slide, not the Executive Summary template.

## Before you build: the inputs this skill cannot supply

The template reproduces whatever it is given, including guesses. Most bad outputs are correct styling applied to assumed content, invented figures or a made-up deck name on every footer. Notice what you do not know and ask for it once, before writing code.

**Must have.** If the request does not give these, stop and ask; do not build around them.

| Input | Why it blocks | If the person cannot supply it |
|---|---|---|
| **The content**: the actual points, figures, data, or a source document | A Newmont deck is read as fact. Never invent statistics, results, names or dates. | Offer to build the structure with bracketed placeholders and list every placeholder in the reply. A placeholder shows its format, `[0,000 koz]`, `[+0.0%]`, `[$0.0B]`, `[DD Month YYYY]`, never a bare `[0]`. Brackets the person wrote themselves ("From: [Your name]") are placeholders they intend; keep them as given and do not ask about them. |
| **The template**, when the router asks | The two templates have different layouts; a scorecard built on Executive Summary columns is the wrong deck. | Default to Executive Summary and say so. |
| **Deck name and date** | The deck name is the footer of every slide and the date sits under the cover title. | Propose one from the subject ("Newmont – Q3 2026 Safety Performance", the current month) and mark it a proposal. |

**Decide and state.** Use the default, name it at the top of the reply, do not ask.

- Length: what the content needs, one idea per slide. Say the slide count.
- Photos: the covers and closings carry their own photographs, so none are needed for a standard deck. Picture layouts (Progress Pictures, Images & Messaging, Big statement with image, Thank you Opt 5) need real files, one per picture placeholder; without enough of them, avoid the layout (the close always has a fallback: Opt 1), or, for a content slide the person asked for by name, build it with the kit's "PHOTO: replace" box and list it as a placeholder. Never fetch, generate or tint images.
- Spelling: match the person's writing; otherwise US (the guidelines are US).
- A colour, font or element the person asks for that is outside the system: build it as asked and state in one line that it departs from the Newmont system; do not ask whether they meant it. Only what the person asked for counts as a departure; your own choices follow the system, and a size or colour you picked is never reported as one. Text on a requested off-system band uses whichever of white or dark blue passes contrast on it.
- When you invent structure the brief did not give (metric rows, table columns, section names), list those items in the reply as suggestions to swap, separately from the placeholders.
- A date whose weekday does not match the calendar, or any other small inconsistency in the brief: use the brief as written and flag it in one line; do not ask.
- Each metric appears once in a deck: as a tile, a table row or a chart, with later slides adding periods or detail, never the same figure repeated.
- Audience and purpose: infer from the request.
- File name: from the subject, lowercase with hyphens.
- Everything the template decides: fonts, sizes, colours, logo, footer layout. Asking about these wastes the person's time.

**How to ask.** One message, numbered, at most six questions, content first, each ending with the default you will use if they say "just go". Add the router's template question as one of them when it applies. A complete brief gets zero questions. If the person says "just make it", build with placeholders and open the reply with the assumptions. In an unattended run: the template question alone is answered by the router's default (Executive Summary, stated in the reply); any other must-have that is missing means you write the questions down, log the request as asked-and-stopped, and stop rather than guess.

Example. "put together a newmont deck on our Q3 safety performance for the exec team" routes to Detailed View (performance). Ask:
1. The Q3 figures (TRIFR, recordable injuries, fatalities, high-potential incidents, with Q2 or the target for comparison), or the report they are in. Nothing is built without them.
2. The two or three messages the executives should leave with, and any decision needed.
3. Deck name and cover date. Default: "Newmont – Q3 2026 Safety Performance", November 2026.
4. Roughly how many slides. Default: 8.

## Choosing layouts

Pick the layout from the shape of the content, not from taste, so the same brief always becomes the same deck. Exact layout names matter: the kit looks them up by string. Full placeholder lists, limits and sample slides are in `references/layouts-executive-summary.md`, `references/layouts-detailed-view.md` and `references/template-sample-slides.md`; the live list for the installed file is `python3 scripts/catalog_layouts.py <template.pptx>`.

**Executive Summary (storytelling)**

| The content is… | Layout | Limits |
|---|---|---|
| The opening | `1_Cover slide Opt 1` (photos vary by cover variant; pick one and keep it) | title ≤ 2 lines (~35 characters); subtitle line and date |
| What the deck covers | `Agenda` (`Agenda Image` with a photo) | purpose ~100 characters; 4 items |
| A new chapter (decks of 8+ slides) | `Section divider - Dark`; lighter: `Sub-section divider` | ≤ 2 lines, ~30 characters |
| One claim that stands alone | `Statement` (its title placeholder sits off the slide, so a label goes in the body's first line); with a photo: `Big statement with image - Dark Blue` (`Light`, `Light Blue`) | ~300 characters; picture needs a file |
| A story and its conclusion | `Story / Summary` | story ~130, conclusion ~80 characters |
| Two, three or four parallel points | `Two/Three/Four Column Panels` (`… Panels Icon` only with icon files); plain text: `Two/Three/Four Column` | 2–3 short paragraphs per panel, ~250 characters at three |
| Headed comparison (before/after, option A/B, risks/mitigations) | `Two Column Comparison`; three or four options: `Three/Four Column Comparison` | header one line; body ~320 characters at two columns, ~250 at three, ~175 at four. Risks with mitigations always pair in `Two Column Comparison` (risk left, mitigation right), up to four pairs per slide, a fifth pair starts a second slide of the same layout |
| One chart | `Single chart with lead-in text`; with commentary: `Single chart with supporting text` | ≤ 8 categories; ≤ 7 bullets |
| Two to six charts | `Two charts`, `Three charts`, `Four charts`, `Six charts`, each also `… with supporting text` | one header line per chart |
| A table | `Title Sub and Content` (lead-in + table) or `Title and Content` | ≤ 12 rows; two tables: `Two Content` |
| Several small tables or KPI tiles | `Four Content Sub` | ≤ 5 rows each |
| A process, timeline or framework | `Title Sub and Content` with a timeline table whose columns are always Phase, When, What happens, Owner (drop Owner only when the brief has none); a drawn process is a free-form slide on `Title Only` (say so) | ≤ 8 rows |
| The close | `Thank you Opt 1` (its photograph is built in); `Thank you Opt 5` only when the person supplied two photo files for it. With one photo or none, use Opt 1 and say the supplied photo was not used and why; never leave a "PHOTO: replace" box on the close | one or two words |

**Detailed View (business and performance reporting)**

| The content is… | Layout | Limits |
|---|---|---|
| The opening | `1_Cover slide Opt 1b` | as above |
| Purpose or agenda | `Purpose`; `Agenda` | one sentence ~100 characters; 4 items |
| A new chapter | `Section divider - Dark`; `Sub-section divider` | ~30 characters |
| Overall highlights with risks and a KPI table | `Overall Highlights` | 9 and 4 bullets; table 4–5 rows |
| Highlights, risks and mitigations by region or function | `Highlights, Risks & Mitigations` | two panels, 6–12 short lines each |
| Three columns of performance points with a takeaway | `Quarterly Performance` | 3 bullets per column |
| Lead column plus three topics | `Work Underway` | 6 bullets per column |
| Executive summary narrative with call-outs | `Ex Summary` | narrative ~700 characters; 6 call-outs |
| Scorecard: KPI strips, small charts, commentary | `ScoreCard`; tables only: `ScoreCard Tables` | tables 2–3 rows; 4 bullets |
| KPI tiles | `Key Metrics` (7 tiles) | one metric and 1–2 lines each |
| Financial table | `Financial Performance (full Portfolio)`; costs: `Cost Summary` | ≤ 14 rows; columns are this period, prior period, same period last year, then a change column against the prior period, with the unit in the first header cell; rows grouped Operating, Financial, Balance sheet |
| Chart with table and commentary | `Performance Against Plan` / `… 2`; six charts: `Summary Financial Metrics` | |
| Balance sheet and dividend | `Balance Sheet & Dividend Review` | two charts, 2 bullets each |
| Investor relations | `QBR: Investor Relations Update` | ~8 bullets per column |
| Customers and markets | `Customers & Markets` | |
| People or workforce | `People Dashboard`; labour map: `Labour Relations Landscape` (map labels are free shapes) | |
| Risks with pictures | `Risks & Mitigation` | ≤ 10 rows, 4 pictures |
| Progress photos | `Progress Pictures`, `x2`, `x3`, `x4`; with text: `Images & Messaging` | one caption line each |
| Outlook and guidance | `Outlook` | main table ≤ 8 rows |
| The close | `Thank you Opt 1`; questions: `Q&A` | |

Rules:

- **Named layouts only.** A free-form slide (`free_slide`, on `Title Only`) is allowed only when no layout fits (a drawn process, a map); name it in the reply and it is logged as free-form. Never rebuild a layout by hand.
- One idea per slide. When text exceeds a limit, shorten or split it onto a second slide of the same layout; never shrink the type or move the placeholders.
- **The person's words are kept word for word**, including capitalisation, labels and order, on every slide and in every format, not only when restyling. Titles you write yourself follow the voice rules; titles and text they gave do not get recased or relabelled. The `--required-text` file you hand the checker is their text exactly as given, never an edited copy.
- Titles are one-sentence statements in sentence case, ≤ 2 lines. When the brief gives none, write each from that slide's own content and list them under the assumptions.
- Every deck: cover, content slides, closing; agenda when it has four or more sections; dividers only in decks of 8+ slides.
- Default outlines when only a topic is given (figures to come or placeholders agreed), fixed so two builds match. Executive Summary, 8 slides: cover; `Statement` with the headline; `Agenda`; `Three Column Panels` with the themes; `Two Column Comparison` (what is working / what needs attention); `Single chart with supporting text` (chart marked "CHART: replace" without data); `Title Sub and Content` with the plan as a table; `Thank you Opt 1`. Detailed View, 8 slides: cover; `Purpose`; `Overall Highlights`; `ScoreCard Tables` with the headline figures against prior period and target; `Quarterly Performance`; `Highlights, Risks & Mitigations`; `Outlook`; `Thank you Opt 1`. Drop a slide only when the person asks for a shorter deck, and say which.
- When the person's own text exceeds a limit, keep their words and the layout as they are, and name in the reply the line that needs shortening and by roughly how much.

## Brand rules the template does not enforce

From the Brand Identity Guidelines, October 2025 (`references/brand-guidelines-2025-10.md` has every value).

- **Colour.** Primary: dark blue `#0C2B82` (PMS 287), gold `#FCAF17` (PMS 130). Secondary: darkest navy `#071435`, mid blue `#3A68C5`, bright blue `#0091DA` (graphics only on white), green `#509E2F` (graphics only on white), pale blue-grey `#D9E8EC`; each with 80/50/20% tints. Light panels are `#D9E8EC` or a 20% tint, not a 10% screen. The templates' theme adds `#12A6E6` as an accent and `#A3A7AA` as a grey; use them where the template does.
- **Contrast pairs** (text on ground), from the guideline matrix: gold only on `#0C2B82` or `#071435`, never on white; white text on `#0C2B82`, `#071435`, `#3A68C5`; on white, `#0091DA` and `#509E2F` only bold or over 18 pt; `#D9E8EC` text only on the two dark blues. Copy is otherwise black, white or dark blue.
- **Type.** Open Sans is the template theme and the deck font; Montserrat is approved for chart titles, pull quotes and subtext but the templates do not use it, so keep Open Sans in decks and use Montserrat only in other formats where the guidelines name it. Approved weights: Regular, Italic, SemiBold, Bold, Extra Bold. Verdana or Tahoma only in HTML email and signatures. Never set a font name on slide text; the layout inherits the theme. Charts are the exception: python-pptx charts do not inherit the theme reliably, so the kit names Open Sans on chart text and Montserrat Bold caps on a chart title, as the guidelines specify.
- **Charts.** Flat: no bevels, shadows, gradients or 3D. Series colours in order `#0C2B82`, `#FCAF17`, `#071435`, `#3A68C5`, `#0091DA`, `#509E2F`, then the 80% tints. 0.5 pt black axis rules; 8 pt axis labels (the guidelines' 6 pt is a print minimum and unreadable on screen); no gridlines; legend at the bottom when there is more than one series; pie slices separated by white gaps with the value labelled outside each slice in navy (inside, labels vanish on the dark slices); the chart heading goes in the layout's header placeholder, not in the chart. The kit's chart builder does all of this; a chart with no data yet is passed as `None` and drawn as a box marked "CHART: replace".
- **Gradients and patterns.** Data graphics stay flat. The two approved background gradients (287→282, 2386→287) and the topographic line pattern are used only where a layout already carries them; do not add them to content slides.
- **Logo artwork for other formats.** None of the three sources ships a stand-alone logo file. For Word, HTML or email, use the logo image embedded in the template master (`scripts/brand_sources.py --logo out.png` extracts it) and say in the reply that it came from the template, not from an approved logo file; Corporate Communications can supply the artwork later. This is decide-and-state: never stop to ask for a logo.
- **Photography.** Real Newmont operations and people, documentary and unfiltered, hi-vis and white branded hard hats, natural light. Covers and closings have theirs baked in. Never stock-looking, generated, duotoned or tinted images; a white 90% overlay or an approved gradient overlay is the only treatment, and only where a layout provides it.
- **Logo.** It is in the layouts; never add a second one, redraw it, recolour the triangle or add effects. Clear space is half the height of the N. Monogram alone is fine internally.
- **Legal name and boilerplate.** "Newmont Corporation" in formal titles, legal copy and the footers of documents (deck footers carry the deck name; the layouts already print the company name); "Newmont" or "the Company" in sentences. The approved boilerplate paragraph is in the reference (section 1); use it verbatim when a deck needs company description.
- **Voice.** Titles are full-sentence assertions in sentence case. Body: a bold lead-in, then one or two plain sentences; lists for scope and steps. Tone confident, pragmatic, plain-spoken.

## Building with the kit

**Setup check** before writing code:

```bash
python3 -c "import pptx" 2>/dev/null || pip install python-pptx
python3 scripts/brand_sources.py
fc-list 2>/dev/null | grep -qi "open sans" && echo "Open Sans installed" || echo "Open Sans NOT installed"
which soffice || ls /Applications/LibreOffice.app/Contents/MacOS/soffice
```

If Open Sans is not installed, the file is still correct (the theme names it; PowerPoint uses it wherever it is installed), but tell the person your preview used a substitute so line breaks may differ. If LibreOffice is missing, say the deck was checked but not rendered.

`scripts/newmont_deck.py` opens the routed template from the configured location, removes its sample slides, and adds slides by layout name, filling placeholders by role. Import it from the `scripts` folder (add it to `sys.path`); do not copy or edit it.

| Call | Does |
|---|---|
| `Deck(template, deck_name, date=None, request='', routing=None, *, activation_path, asked=False)` | `template` is `"detailed_view"` or `"executive_summary"`; `activation_path` (keyword, required) is one of the Phase 1 labels; pass the router's dict as `routing` so the log records its reason, and `asked=True` when you asked the clarifying question (the router's own flag is reset once it is answered); raises `SourceError` if the file is missing |
| `d.roles(layout_name)` | returns the roles a layout accepts (`title`, `subtitle`, `lead`, `body`, `col1..colN`, `head1..headN`, `tag1..`, `pic1..`, `chart1..`, `table1..`, `source`) as a dict of role to placeholder idx, resolved from the live file; the CLI `python3 scripts/newmont_deck.py executive_summary --roles "<layout>"` prints it |
| `d.add(layout_name, **fills)` | adds one slide; text is a string (paragraphs on `\n`), a list of strings, `(text, level)` bullets or `[(text, bold, italic), …]` runs; `picN` takes a file path or `None` (a wrong path raises); `chartN` a dict `{"type", "categories", "series"}` or `None`; `tableN` or a content role a dict `{"header", "rows"}` or `None`; `None` draws a "PHOTO/CHART/TABLE: replace" box; unfilled placeholders are removed. Put a chart in a `chartN` role and a table in a `tableN` or content role; a chart forced into a table placeholder (or the reverse) becomes an unlinked frame that the checker counts as free-form |
| `d.free_slide(title)` | a `Title Only` slide for the rare case no layout fits; draw on it with the module functions `text`, `rect`, `picture` (`from newmont_deck import text, rect, picture`) |
| `d.save(path)` | writes the deck, the run record `<path>.run.json`, and the request log line |

```python
import sys; sys.path.insert(0, 'scripts')
from newmont_deck import Deck
from route_template import route
r = route('a deck explaining our tailings strategy to site leaders')
d = Deck('executive_summary', 'Newmont – Tailings Strategy', date='November 2026',
         request='a deck explaining our tailings strategy to site leaders', routing=r,
         activation_path='direct: deck/presentation/slides')
d.add('1_Cover slide Opt 1', title='Tailings strategy', subtitle='Site leadership briefing\nNovember 2026')
d.add('Statement', body='Every facility will meet the Global Industry Standard on Tailings Management by 2028.')
d.add('Three Column Panels', title='Three commitments shape the next two years', lead='The plan rests on three commitments.',
      col1=[('Close the gaps', 0), 'Independent reviews at every site by Q2.'],
      col2=[('Build the capability', 0), 'Accountable executives named per facility.'],
      col3=[('Report openly', 0), 'Annual public disclosure from 2027.'])
d.add('Single chart with supporting text', title='Reviews are ahead of plan',
      col1=['[Commentary line 1]', '[Commentary line 2]'], head1='Facilities reviewed by quarter',
      chart1={'type': 'column', 'categories': ['Q1', 'Q2', 'Q3'], 'series': {'Reviewed': [4, 7, 9]}})
d.add('Thank you Opt 1', title='Thank you')
d.save('tailings-strategy.pptx')
```

Run `d.roles('<layout>')` for any layout before filling it the first time; the role names depend on the placeholders the installed file has, and they are the thing that changes when a template is replaced.

## Checking before delivering

```bash
python3 scripts/check_deck.py deck.pptx --template executive_summary --deck-name "Newmont – Tailings Strategy" [--free-form-slides 5] [--required-text brief.txt] [--expect-slides 8]
soffice -env:UserInstallation=file:///tmp/lo-profile --headless --convert-to pdf --outdir render deck.pptx   # or d.save(path, render=True)
```

Both `--template` and `--deck-name` are required, and the checker exits 1 on any FAIL. It confirms that the deck's master is the chosen template's (theme name) and every slide uses one of its named layouts, that no slide carries free shapes except those listed as free-form, that no empty placeholder prompts remain, that any font or colour you set explicitly is approved, that nothing you added has a shadow, gradient, 3D or rounded corner, that the footer carries the deck name and the page number field is present, the slide size, and the required text. Fix every FAIL. Then open the rendered pages and check what the script cannot: no text overflows its placeholder, titles are ≤ 2 lines, charts are legible, nothing overlaps the baked-in photos.

## Reply format

Deliver only the deck, the build script and the run record. Renders go in a `render/` folder, the LibreOffice profile outside the working folder, and nothing else is left behind: no proxy decks, stray PDFs, copied kits or virtual environments.

The first line of the reply is the template line: the template chosen and why (the router's reason, and whether a question was asked or the default applied). Nothing comes before it, not a greeting and not a "your deck is ready" sentence; the file name and slide count belong with the slides built. Then every source `brand_sources.py` resolved, each with the version it reports (both templates when both are present); then assumptions and placeholders, if any. Then the slides built (number, layout name, title), any free-form slide and why, what was checked (checker run, rendered and looked at, or why not; whether Open Sans was installed for the preview), and any departure from the system in one line each. Do not describe the brand rules back to the person.

The kit writes the log line on `save()` (a rebuild of the same request to the same file replaces the earlier line). When no deck is saved, log by hand with the template as routed (or none), `--asked` when you stopped on a question, no output, and a note saying why you stopped, for example:

```bash
python3 scripts/brand_log.py --request "put this into slides for the QBR" --activated --activation-path "indirect: put into slides" --template detailed_view --reason "Matched Detailed View cues: QBR." --notes "stopped to ask for the figures"
python3 scripts/brand_log.py --tail 3
```

## Restyling an existing deck

Rebuild it on the routed template rather than patching fonts and colours in place: patched files keep foreign theme fonts and effects. Read every slide's text first; map each slide to a layout with the tables above (title and bullets become `Title and Content` or `Title Sub and Content`; three boxes become `Three Column Panels`); ask only for the deck name and date if they are not in the file, with a proposed default; build; check; reply with what changed and anything you could not carry over.

"Keep the content" means every sentence word for word, in its original order and on its original slide, titles, credits and footers included. Change case, size, position and colour; do not rewrite titles, reorder lines, drop credits, or add slides (no closing slide unless the original had one). Offer title rewrites as a separate list in the reply.

## Other formats (only when explicitly asked for in Newmont style)

Apply the guidelines PDF directly; there is no approved template for these in the sources, so say so and name the guideline sections used by the numbered headings of `references/brand-guidelines-2025-10.md` (for example "3 Colour, 7 Typography, 8 Standard document").

- **Word, PDF, Docs.** Standard document (guidelines p30): a dark navy header band with the reversed logo left; title Open Sans Bold 20/21 pt navy; intro Open Sans Light 15/21 pt; section heads Montserrat Regular 10/12 pt caps with 0.5 pt letter-spacing in `#0C2B82`; body Open Sans Regular 9/12 pt; footer "NEWMONT CORPORATION" in Montserrat caps left, page number right. Report or memo (p31): monogram top-left, a Montserrat 10 pt caps label in `#3A68C5`, title Open Sans Bold 20/27 pt, section heads Open Sans Regular 14 pt caps, lead 12/16 pt, body 9/12 pt, footer "NEWMONT CORPORATION | [DOCUMENT TITLE]" left and "DATE | PAGE x OF y" right above a rule. Tables: dark blue header row with white bold text, 0.5 pt grey rules. Call-outs on `#D9E8EC`.
- **Excel.** Open Sans throughout, header row `#0C2B82` with white bold text, no banding or borders other than 0.5 pt `#A3A7AA` rules, numbers right-aligned with units in the header, charts styled as above.
- **Email and signatures.** Verdana (Tahoma as alternate), the signature block and banner sizes from guideline section 9; never embed the logo at less than the minimum screen size.
- **Web pages and HTML.** Open Sans from Google Fonts; the tokens below; square corners; the logo top-left or top-right with clear space; eyebrows in dark blue caps; call-outs on the pale panel.

```css
:root{
  --nm-blue:#0C2B82; --nm-navy:#071435; --nm-mid:#3A68C5; --nm-bright:#0091DA; --nm-green:#509E2F;
  --nm-gold:#FCAF17; --nm-pale:#D9E8EC; --nm-pale-80:#E1EDF0; --nm-pale-50:#ECF3F6; --nm-grey:#A3A7AA;
  --nm-font:"Open Sans","Segoe UI",Arial,sans-serif; --nm-accent-font:"Montserrat",var(--nm-font);
}
body{font-family:var(--nm-font);color:#000}
h1{font-weight:700;color:var(--nm-blue)} .nm-eyebrow{font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:var(--nm-blue)}
.nm-quote{font-family:var(--nm-accent-font)} .nm-panel{background:var(--nm-pale);border-radius:0}
.nm-dark{background:var(--nm-navy);color:#fff}
```

Contrast pairs apply everywhere: no gold on white, no normal-weight bright blue or green text on white.
