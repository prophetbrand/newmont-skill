# Newmont brand agent in Agent Builder: test plan

Prepared by Prophet, 17 November 2026. Scope: create the agent described in `agent-config.md` in Prophet's Microsoft 365 tenant, run the 14 cases from `evals/`, and check every produced deck locally. This is a baseline for the Agent Builder route; the spike's evaluation plan (`docs/copilot/copilot-evaluation-plan.md` on branch `claude/copilot-integration-spike-d970a5`) covers the Copilot Studio and Brand Kit routes. Screen-automation tooling for the macOS desktop app is being researched in a separate session and is not repeated here.

## 1. Before you start

- A Prophet account with a Microsoft 365 Copilot licence (code interpreter, which any .pptx output depends on, needs a Copilot licence or Copilot Chat without metered usage [code interpreter page, Microsoft Learn, 2026-11-09]).
- The SharePoint folder `Brand Sources` with the three approved files, set up as in `agent-config.md` section 3.
- This repository on the tester's Mac on branch `feat/template-routing-oct2025-guidelines`, Python 3 with python-pptx, and the three files in `brand-sources/`. Check: `python3 -P scripts/brand_sources.py` prints all three roles.
- A results folder outside the repository, one subfolder per case and run: `<results>/<case>/run-<n>/`.

## 2. Creating the agent

### 2.1 Manual steps (from the recording; same in the web app)

1. Open Microsoft 365 Copilot: desktop app (macOS) or https://m365.cloud.microsoft in a browser. Sign in with the Prophet account.
2. Sidebar **Agents** > **Agent Builder** (web: **Agents & Skills** > **New agent**). If the Describe chat opens, choose **Skip to configure**.
3. **Name**: `Newmont Brand Agent`.
4. **Description**: paste from `agent-config.md` section 1.
5. **Instructions**: paste the fenced block from `agent-instructions.md`. Do not click **Suggest improvements**. If the box refuses the length, paste `agent-instructions-short.md` and note "short" in the results.
6. **Skills**: add nothing.
7. **Knowledge** > **+ Add knowledge**: browse to the `Brand Sources` folder and select the three files. Turn on **Only use specified sources**. Wait until none shows **Preparing**.
8. **Web search**: off. **Create documents, charts, and code**: on if the toggle is shown. **Create images**: off.
9. **Suggested prompts**: add the five title and message rows from `agent-config.md` section 2.
10. Check the validation note "Name, description, and instructions cannot be blank" has cleared, open **Preview** (web: **Try it**) and run suggested prompt 3 once as a smoke test.
11. Select **Create**. The agent is private to its creator until shared. Do not share it beyond the test team and do not submit it to the org catalog.
12. Screenshot the Configure panel and save it as `<results>/config.png`.

### 2.2 Automation options, ranked

Automation is for repeat runs (three runs per case, re-creating the agent after instruction changes). In every option a person signs in; the automation never types a password, MFA code or approves a sign-in prompt.

| Rank | Option | When | SSO and MFA handling |
|---|---|---|---|
| 1a (preferred) | **Copilot web app in the Claude desktop app's built-in browser.** Claude opens https://m365.cloud.microsoft in the browser pane, and the tester signs in there; Claude then drives the Configure form and the chat with the browser tools (find, form input, click, read page) | First runs and anything that needs judgement while watching: the knowledge picker, unexpected dialogs, reading replies | Human gate: Claude stops at login.microsoftonline.com, the tester completes password, MFA and "Stay signed in?", then tells Claude to continue. Session cookies stay in the pane for later runs; when a redirect to the sign-in page reappears, Claude stops again. Check early whether a deck download from the pane lands on disk; if not, download it from the same chat in a normal browser |
| 1b | **Copilot web app driven by Playwright** (headed Chromium, persistent profile directory outside the repository) | Scripted repeat runs of the 14 prompts once the flow is known | Human gate: the script opens the sign-in page headed and waits (for example `page.waitForURL('**/m365.cloud.microsoft/**', { timeout: 0 })`) while the tester signs in; the profile keeps the session. Before each case the script checks for a redirect to login.microsoftonline.com and pauses for the tester. Never store credentials in the script or the repository. Capture downloads with `page.waitForEvent('download')` and save them to `<results>/<case>/run-<n>/` |
| 2 | **Microsoft 365 Copilot desktop app on macOS via screen automation** | Only if the web app lacks Agent Builder or behaves differently in Prophet's tenant | The app signs in through the macOS Microsoft account broker; the tester signs in once by hand before the run and handles any re-prompt. Tooling is being chosen in the separate screen-automation session |

Selectors for 1a and 1b: use accessible names and visible labels (buttons **New agent**, **Skip to configure**, **Create**; fields **Name**, **Description**, **Instructions**), not CSS classes, which change between Copilot releases. Fill the Instructions box in one operation, not keystroke by keystroke. The knowledge file picker opens in a separate frame; doing that step by hand is acceptable.

## 3. Test cases

How to run each case: open a **new chat** with the agent (select it in the sidebar or @-mention it), paste the full text of `evals/<case>/prompt.md` below its YAML front matter, attach the listed input files, and answer a question only where the case says so. Each case runs three times, in separate chats. Save a screenshot or copied transcript of every reply and any file the agent offers, in the same session (code interpreter files are deleted when the session ends).

Expected template and behaviour come from each case's `case.yaml`, adapted to what an Agent Builder agent can do. "Behaviour pass" covers activation, routing, questions and honesty, which the agent can meet. "Deck" is graded separately in section 4 because building on the template is not expected to work.

| # | Case (`evals/`) | Attach | Expected template | Expected activation and behaviour | Behaviour pass rule |
|---|---|---|---|---|---|
| 1 | underspecified-deck-asks-first | none | Detailed View, stated not asked | Activates (`direct`); one numbered message, at most six questions, content first, each with a default; nothing built | No deck; questions ≤ 6 and include the figures and deck name/date; no question about fonts, colours, photos or template; LOG says asked: yes |
| 2 | just-go-with-placeholders | none | Detailed View | Builds without asking; every figure a bracketed placeholder; no picture layouts; 8-slide default outline | No question asked; no invented statistic (any digit outside brackets that is not in the prompt fails); template Detailed View |
| 3 | routing-qbr-detailed-view | none | Detailed View (QBR cue) | Path `indirect: put into slides`; no template question; Detailed View layouts | Template Detailed View, not asked; every figure as given, none added; LOG path is `indirect` |
| 4 | routing-strategy-exec-summary | none | Executive Summary | No question; Statement, Three Column Panels, Two Column Comparison, table, Thank you Opt 1 | Template Executive Summary, not asked; bracketed dates kept and listed |
| 5 | routing-ambiguous-asks | none | Asks; default Executive Summary | Exactly one question, the template question; reply "Executive Summary" to continue | First reply asks only the template question; after the answer the deck is Executive Summary. Fails if it silently picks Detailed View or asks anything else |
| 6 | complete-brief-deck | none | Executive Summary (named) | No questions; six slides in the given order | No question; six slides listed in order with the right layout types; text verbatim |
| 7 | long-content-must-split | none | Executive Summary (project update) | No questions; workstreams split over two column slides; seven risks on comparison slides; decision on Statement | All six workstreams and seven risks present; splits stated; same slide count and layouts in all three runs |
| 8 | photo-backdrop-and-phases | `evals/photo-backdrop-and-phases/files/backdrop.jpg`, `people.jpg` | Executive Summary (plan) | Big statement with image using backdrop.jpg; process as timeline table or declared free-form; Thank you Opt 5 with people.jpg | Uses the given photos only, untinted; no generated or fetched image; free-form slide named if used |
| 9 | financial-template-two-slides | none | Detailed View (departs from the "executive summary" wording with a reason) or the one template question | Two content slides, no cover or closing; placeholders for every figure | Two slides only; Detailed View with a stated reason, or only the template question; every figure bracketed |
| 10 | fix-off-brand-deck | `evals/fix-off-brand-deck/files/off-brand.pptx` | Executive Summary by default (Detailed View with a reason accepted) | Path `restyle: existing deck`; may ask only for deck name and date | Every sentence kept word for word, in order, on its slide; no slide added; a list of changes; title rewrites offered separately |
| 11 | missing-source-stops | none; before the run, move `Newmont_PPT Template_Executive Summary_Feb_2026.pptx` out of the `Brand Sources` folder and refresh Knowledge until it is gone | Executive Summary (strategy), which is missing | Stops, names the missing file and where it is expected, builds nothing | No deck or outline; names the missing file. Restore the file and wait for it to finish preparing before the next case |
| 12 | activation-word-memo | none | None (guidelines only) | Path `explicit other product: Word`; no router question; says no approved Word template exists; three points verbatim | No template question; .docx offered or content given with the guideline sections named; LOG path `explicit other product: Word` |
| 13 | html-one-pager | none | None (guidelines only) | Explicit other product: HTML; Open Sans, palette only, flat, callout on #D9E8EC | No question; text verbatim; only palette colours in the HTML; no gold text on white |
| 14 | off-palette-request | none | None (guidelines only) | Uses the sponsor teal #008080 only for the banner and says in one line that it departs from the palette | Teal kept on the banner only; no refusal or lecture; one-line departure note |

A case passes on behaviour when all three runs meet its rule. Routing cases (1 to 5, 9) fail if the template differs between runs. Record the instructions version (full or short) with every run.

## 4. Checking a produced deck

1. Download the .pptx the agent offers into `<results>/<case>/run-<n>/deck.pptx`. If the agent offers only an outline, save the reply text as `outline.md` and record output class C (below); there is nothing to check.
2. From the repository root, with the three templates in `brand-sources/`:

```bash
python3 -P scripts/brand_sources.py
python3 -P scripts/check_deck.py "<results>/<case>/run-<n>/deck.pptx" \
  --template <detailed_view|executive_summary> --deck-name "<deck name>" \
  [--required-text <file>] [--expect-slides <n>] [--free-form-slides <list>] \
  --out "<results>/<case>/run-<n>/check.json"
python3 -P scripts/inspect_pptx.py "<results>/<case>/run-<n>/deck.pptx" > "<results>/<case>/run-<n>/inspect.json"
```

- `--template`: the template the case expects (section 3). If the agent chose the other one, run the checker for the one it claims and record the routing miss separately.
- `--deck-name`: as given in the prompt: case 3 "Newmont – Q3 2026 QBR", case 4 "Newmont – Water Stewardship Strategy", case 5 "Newmont – Ahafo Expansion Update", case 6 "Newmont – Ahafo North Ramp-up Review", case 7 "Newmont – Cadia Expansion Update", case 8 "Newmont – Haul Truck Autonomy Plan". For cases 2, 9 and 10, use the name the agent proposed in its reply.
- `--required-text`: `evals/complete-brief-deck/files/required-text.txt` (case 6), `evals/long-content-must-split/files/required-text.txt` (7), `evals/photo-backdrop-and-phases/files/required-text.txt` (8), `evals/fix-off-brand-deck/files/off-brand-text.txt` (10). `--expect-slides 6` for case 6, `2` for case 9.
- Cases 12 to 14: open the .docx or .html by eye; for HTML, check colours against the CSS tokens in `SKILL.md` ("Other formats") and the required-text files in `evals/html-one-pager/` and `evals/off-palette-request/`.

3. Classify the output:

| Class | Meaning | How to tell |
|---|---|---|
| A | .pptx built on the template's master and named layouts | `check_deck.py` passes the theme and layout checks |
| B | .pptx produced but not on the template (generic theme, rebuilt look) | Theme or layout FAILs; `inspect.json` shows layouts like "Title and Content" from a default master |
| C | Honest outline, no file, says it cannot use the template | Reply text |
| D | Claims the template was used but it was not, or invents figures | Class B evidence plus a reply that says otherwise; or digits not in the prompt |

Class D is a defect in every case. Class C is the expected honest outcome under the instructions if the agent cannot open the template.

4. Record for every run: template the agent named, template in the file (theme name from `check.json`), layouts used (from `inspect.json`), source files and editions the agent named versus `brand_sources.py` locally, whether it asked and what, the LOG line as given, checker PASS/FAIL counts, and the output class.

## 5. Results table (copy per test round)

| Date | Tester | Surface (web / desktop / Playwright / Claude browser) | Instr. (full / short) | Case | Run | LOG present | Activation path | Template expected | Template named | Template in file | Asked (expected / actual) | Output class | Checker FAILs | Layouts used | Sources named | Behaviour pass | Notes / evidence path |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| | | | | 1 underspecified-deck-asks-first | 1 | | | Detailed View | | n/a | yes / | | n/a | | | | |
| | | | | | | | | | | | | | | | | | |

Summary per round: cases passing on behaviour (of 14), runs by output class (A/B/C/D), routing agreement across runs, and every defect with its evidence path.

## 6. Unknown until Newmont's tenant is available

- **Org scoping.** Who may see and use the agent. Agent Builder agents are private until shared; owners can share with people or groups, or turn on org-wide sharing, which admins control under Microsoft 365 admin center > Agents > Settings > Sharing (All users by default, specific users or groups, or no users); access to agents at all is under Agents > Settings > User access [Share and manage agents built in Agent Builder, Microsoft Learn, 2026-11-12]. Newmont's settings for both are unknown.
- **Admin approval.** Publishing to the org catalog ("Built by your org" in the Agent Store) needs admin review in the Microsoft 365 admin center; sharing does not [same source]. Newmont's approver and review process are unknown, and whether Newmont permits user-built agents at all.
- **SharePoint location.** Which Newmont site and library will hold the three approved files, who owns it, and whether every intended user has read access: the agent answers only from files the user can open. Restricted Content Discovery, sensitivity labels with user-defined permissions or extract rights disabled, and Double Key Encryption would stop the files being used [Add knowledge sources, Microsoft Learn, 2026-09-30].
- **Licences.** Which Newmont users have Microsoft 365 Copilot licences; unlicensed users may not get code interpreter output or SharePoint-grounded answers.
- **Policies.** The "Allow web search in Copilot" setting, Information Barriers (which stop end users adding skills), and data-residency rules for any embedded files.
- **Whether the agent can build on the template at all.** If this round shows only classes B and C, the Agent Builder route cannot meet the named-layout criterion, and the decision moves to the spike's Copilot Studio plus service path.
