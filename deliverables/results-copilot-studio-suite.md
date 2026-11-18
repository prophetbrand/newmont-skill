# Copilot Studio: the full eval suite, 18 November 2026

The same 14 cases that ran on Claude ([evals/RESULTS-2026-11-17-evening.md](../../../evals/RESULTS-2026-11-17-evening.md)) ran on Microsoft Copilot Studio's credit-powered Agent type in the Prophet, Inc. default environment, driven with the Playwright driver in `tools/copilot-studio/` (`runner.py` sends the case prompt and its input files to the agent's Preview, waits, downloads every attachment, saves the transcript). Graded by Claude Fable 5.1 from the downloaded files, the transcripts and locally rendered pages, with the same per-case graders as the Claude suite. Workbook: [evals/RESULTS-2026-11-18-copilot-studio.xlsx](../../../evals/RESULTS-2026-11-18-copilot-studio.xlsx) (Summary, Findings, one sheet per case with every verdict and its evidence).

## Set-up

Two draft agents, because the Preview caps a skill at about 15 MB of zip members and the two templates do not fit together:

| Agent | Package | Instructions |
|---|---|---|
| Newmont Brand – Detailed View | `dist/newmont-brand-copilot-studio-dv.zip` | `agent-instructions.md` (this folder) |
| Newmont Brand – Executive Summary | `dist/newmont-brand-copilot-studio-es.zip` | same |

Each case ran on the agent whose template its router picks. Three cases (two safety decks, the restyle) route to Detailed View; on the Executive Summary agent they stopped correctly, said the template is not in the package and offered the other, and those stops are not in the totals. Cases with input files (two photos, the agency deck) had them attached through the Preview's upload button and they reached the sandbox.

Host rules the graders applied: one template per package (a run record can only name what is there); no LibreOffice (a render grader passes when the reply says the render was skipped and the locally rendered pages show no overflow); no request log (the sandbox log folder is read-only, so trace graders read the reply's LOG line and the `.run.json` attachment); delivery is attachments on the reply.

## Update, later on 18 November: one agent

The packager now strips the JPEG XR "hdphoto" picture originals from the derived templates. The `.wdp` parts are kept only for re-editing picture corrections; the flattened JPEG that displays stays. That takes Detailed View from 5.3 to 3.5 MB and Executive Summary from 7.1 to 3.5 MB, so one package holds both templates at 12.6 MB of members, about 16.8 million characters against the 20 million cap. LibreOffice renders of every affected layout (cover, thank-you, highlights) are pixel-identical before and after; the PowerPoint render check was not completed.

The package was attached to the existing draft "Newmont Brand Agent" (id 67f5c22e-3661-4121-ac7a-433f407e8ba7) with the Studio Instructions. The Preview started and three routing cases ran once each:

| Case | Result | Checks |
|---|---|---|
| routing-qbr-detailed-view | built on Detailed View | 6/7 |
| routing-strategy-exec-summary | built on Executive Summary | 5/6 |
| routing-ambiguous-asks | stopped and asked | 6/6 |

That is 17/19. Both misses are the reply's source line. The QBR reply named only the template it used, not both templates the run record lists. The strategy reply cited the trimmed copies' fingerprints as the versions and gave the approved shas only as a mismatch note. Decks, layouts, verbatim text, checker and run records passed. Run folders and GRADES.md are in the session scratchpad under `cs-suite/one-agent`.

Fix and rerun, same day: the packager now stamps each derived copy with the approved file's sha (`approved_sha256_12` in the package's `brand-sources.json`), `brand_sources.py` reports it as the version ("Feb 2026 (approved sha b186e9dd0245; derived copy sha 57356d867d10)"), and the reply rule in SKILL.md and both Instructions files says to name every resolved source, both templates included. Reruns on the same agent: routing-qbr-detailed-view 7/7, routing-strategy-exec-summary 6/6; with the question case, 19/19.

Published, 18 November, about 10:50: the Teams + Microsoft 365 channel was added (available in Microsoft Copilot and Microsoft Teams, which cannot be changed after publishing) and "Newmont Brand Agent" published successfully on the first try, so the 12.6 MB combined package is under the published-agent cap too. Nothing was shared. The Teams app page shows it as "Built using Microsoft Copilot Studio" with the Studio default description, because the channel's About info was left blank; the Copilot app's agent list and store did not list it within the first minutes. Preview downloads save under the attachment's blob id with no extension (rename to the deck's name to open); whether Teams keeps the file name is untested.

## Results

| | Checks | Passed | Rate |
|---|---|---|---|
| First pass, 14 cases, one run each | 102 | 91 | 89% |
| Three runs of the 11 file-producing cases plus the 3 single-run question or stop cases | 270 | 235 | 87% |
| Same, host-caused failures excluded (15: the run-record grader on one-template packages) | 255 | 235 | 92% |
| Claude, same 14 cases, three runs, before its own fixes | 306 | 296 | 97% |
| Fix runs after the four fixes below (6 cases, one run each) | 43 | 41 | 95% |

Repeatability: 9 of the 11 three-run cases gave the same verdict on every grader in all three runs. The flips: the QBR reply once omitted the "other template not in this package" line and once split the risk/mitigation lines at the slash; the HTML page's logo was present in one run and omitted in two; the memo's header lines were verbatim in one run of three; the flyer reply stated the skipped render in one run of three.

Timing: 45 runs, 70 to 175 seconds each, median 130; about 97 minutes of Preview time in all. Credits were not captured by the harness (the Preview's counter lags); the earlier test measured about 60 Copilot Credits per deck build.

## What the suite found and what changed

| # | Finding | Cases | Fix | Verified |
|---|---|---|---|---|
| 1 | The run record carried `sources_error` instead of the sources used: `brand_log` resolved all three roles at once, and a one-template package made that raise | every deck case | `scripts/brand_log.py` resolves one role at a time; `sources` lists what was found, `sources_error` only what is missing; test added | long-content fix run record lists both sources found |
| 2 | HTML pages broke the type and panel rules (gold eyebrow and white title on a dark band, dark call-out panel, recased heading); the restyle reply gave no title-rewrite list: the packager dropped the "Restyling an existing deck" and "Other formats" sections, so the agent never saw the HTML tokens or the restyle rules | html-one-pager, off-palette-request, fix-off-brand-deck | both sections ship in `references/skill-layouts-and-brand-rules.md` with a required pointer in the packaged SKILL.md (which stays under 20,000 characters); the "Not in this package" note is gone; test added | html-one-pager 6/8 to 8/8; fix-off-brand 7/8 to 8/8; the flyer's panel rule passes |
| 3 | A thin brief got no "roughly how many slides" question: the pasted Instructions told the agent to decide the count without asking, against SKILL.md's intake example | underspecified-deck-asks-first | the Instructions (Agent Builder file, 7,993 characters, and the new Copilot Studio file) decide the count only for a complete brief and add the question when asking | 6/7 to 7/7 |
| 4 | DECISION REQUESTED went into the Statement layout's off-slide title, invisible on the slide | long-content-must-split | `references/layouts-executive-summary.md` and the SKILL.md layout row say a label goes in the body's first line | 6/8 to 8/8 |
| 5 | Memo header labels recased to caps and the quotation marks dropped (Claude also failed this once in three) | activation-word-memo | none; the verbatim rule covers it | fix run 6/6 |
| 6 | Flyer fix run: the reply did not say the render was skipped, and the logo placeholder text is `#333` | off-palette-request | none yet | 4/6, watch next run |

Both Studio agents now carry the fixed Instructions and the rebuilt packages. `dist/newmont-brand-copilot-skill.zip` (Agent Builder) was rebuilt with the same sections.

## Compared with Claude

On the skill's own behaviour (host-caused checks excluded) Studio reached 92% before the fixes and 95% on the fix runs, against Claude's 97% before its fixes and 100% on its reruns. The remaining gaps are model judgment on soft rules: the verbatim rule in Word and HTML, stating the skipped render, and one-off choices such as a logo omitted. Routing, intake questions, the missing-source stop, placeholder decks, photo handling, slide splitting and every checker rule behaved the same on both hosts.

## Recordings

`video/` next to this note: `clip1-create-dv-agent.mp4` (new agent, name, Instructions, skill upload, save), `clip2-create-es-agent.mp4` (the same for the second agent), `clip3-preview-build.mp4` (the QBR brief in Preview, the reply and the attachment download), `clip4-update-instructions-and-swap-skill.mp4` (replacing the Instructions, deleting the skill, uploading the rebuilt package). Recorded through Chromium's DevTools screencast by `pwsrv.py` (`rec start <dir>` / `rec stop <out.mp4>`), stitched with ffmpeg at 1440×900.

## Still open

- Published-agent size cap, Teams channel delivery and sharing inside Newmont's tenant: untested.
- The sandbox log folder is read-only, so the request log never persists; the reply's LOG line and the `.run.json` attachment are the record on this host.
- Credits per run are not captured by the harness.
- Teams delivery of the published agent (file names on download, install for others): untested.
