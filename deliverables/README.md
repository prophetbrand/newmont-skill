# Newmont brand agent: deliverables

Everything Newmont IT needs to stand the agent up, in one folder. Nothing here depends on the rest of this repository; the repository is the source and the test harness.

## What is here

| Folder or file | What it is | Use it for |
|---|---|---|
| `copilot-studio/newmont-brand/` | The skill package for Microsoft Copilot Studio, unpacked (12.6 MB). `SKILL.md`, `scripts/`, `references/`, `brand-sources.json`, `brand-values.json`, and `brand-sources/` with derived copies of the three approved brand files: Brand Guidelines October 2025 and the two Feb 2026 PowerPoint templates, Detailed View and Executive Summary, both in one package. | The Copilot Studio agent (the tested and published route) |
| `copilot-studio/instructions.txt` | The text to paste into the agent's Instructions editor in Copilot Studio (7,900 characters). | Same agent |
| `agent-builder/newmont-brand/` | The same skill packaged for Agent Builder in the Microsoft 365 Copilot app, unpacked (32 MB; Agent Builder allows larger files, so only the Detailed View template is trimmed). | Only if Newmont prefers a user-created agent in the Copilot app instead of Copilot Studio |
| `agent-builder/instructions.txt` | The text to paste into an Agent Builder agent's Instructions box (7,997 characters, limit 8,000). | Same |
| `results/copilot-studio-suite.md` and `.xlsx` | The 14-case evaluation on Copilot Studio: results, repeatability over three runs, what was fixed, the one-agent package and the publish. The workbook has every verdict with its evidence. | Acceptance evidence |
| `results/copilot-in-powerpoint-route.md` | What it would take to run the agent from the Copilot pane inside PowerPoint (organization skills, Brand Kit, licence and admin prerequisites), with sources. | Deciding whether that second route is wanted |

Both hosts take the skill as a zip. Make it from inside the `newmont-brand` folder so `SKILL.md` sits at the zip's root:

```bash
cd deliverables/copilot-studio/newmont-brand && zip -r -X ../newmont-brand.zip . -x '.DS_Store'
```

Recordings of agent creation, skill upload and a Preview build are in `../docs/copilot/copilot-studio/video/` (four clips, 37 MB).

## Setting up the Copilot Studio agent

Copilot Studio, the credit-powered **Agent** type, in Newmont's environment. About ten minutes.

1. **Agents > New agent.** Name it (for example "Newmont Brand Agent"). Open the **Build** page.
2. **Instructions.** Paste the whole of `copilot-studio/instructions.txt` into the Instructions editor. Paste as plain text so the paragraph breaks survive; if the editor collapses it into one paragraph, paste it again paragraph by paragraph.
3. **Skills > Add skill > Upload a skill.** Choose the zip made from `copilot-studio/newmont-brand/` (command above). The skill appears as `newmont-brand` after 10 to 20 seconds. Leave Tools and Knowledge as they are, or remove "Search all websites" and "Work IQ" if Newmont wants the agent limited to the package (every test ran with the defaults present; nothing used them).
4. **Model.** The tests ran on the default, "Auto". If a specific model is required, set it here before testing.
5. **Preview.** Start a new chat and send a brief (examples below). A deck takes about two minutes and costs about 50 Copilot Credits. Downloads from the Preview save under an internal id with no extension: rename the file to the deck's name with `.pptx` to open it.
6. **Publish.** Add the **Teams + Microsoft 365** channel (availability: Microsoft Copilot and Microsoft Teams, which cannot be changed later), fill in the channel's About info (description and publisher), then Publish. Sharing, endorsement and company-wide availability are done by Newmont IT in the Microsoft 365 admin center.

## Trying it

Three briefs that show the main behaviours. Each should finish with the deck, the build script and a run record attached, and a reply that opens with the template chosen and why, then lists the three source files with their editions and shas.

- **Routes to Detailed View, no questions:** "Put together a short deck on Q3 2026 safety performance for the site leadership meeting. Deck name "Newmont – Q3 2026 Safety Performance", cover date November 2026, save as q3-safety.pptx. KPIs, Q3 vs Q2 vs target: TRIFR 1.0 / 1.2 / 1.0; Lost-time injuries 2 / 4 / 2. Highlights: ... Risks and mitigations: ... / ..."
- **Routes to Executive Summary, no questions:** "Build a short deck explaining our water stewardship strategy to site leaders. Deck name "Newmont – Water Stewardship Strategy", cover date November 2026. Headline: "..." Three priorities: ..."
- **Stops to ask:** "Make a project progress update deck for the Ahafo expansion ..." matches both templates, so the agent asks which one and offers a default.

A thin brief ("a safety deck for Q3") gets one round of questions, including "Roughly how many slides? Default: 8". A request for an off-brand deck to be fixed gets it rebuilt on the routed template with a list of what changed.

## What the agent does, in one paragraph

It opens the approved template inside its sandbox and builds every slide as an instance of one of the template's named layouts, so fonts, colours, footers and slide numbers come from the master. It applies the Brand Identity Guidelines for what the template does not set (charts, photography, contrast pairs, legal name). It runs a checker on the finished deck and attaches a run record naming the template, the layouts used and the version (sha) of each approved file. It keeps the person's words verbatim, asks only when a brief is incomplete, and decides small things itself. It cannot render previews in the Copilot Studio sandbox, so it says so and asks the person to open the deck.

## Updating the brand files

The package carries derived copies of the approved files (sample slides and re-edit originals removed, PDF images downsampled) to fit Copilot Studio's size cap; text, masters, layouts and theme are unchanged, and the run record cites the approved file's sha. When a guideline or template is refreshed, the package is rebuilt from the new files with `scripts/package_for_copilot.py --profile copilot-studio` in this repository, then uploaded in place of the old skill (remove the skill, Add skill, Upload). The Instructions do not change for a file refresh.

## Known limits on Copilot Studio

- No LibreOffice in the sandbox, so no rendered previews; the checker still runs.
- The request log folder is read-only there; the reply's LOG line and the run record are the trace.
- Attachment downloads in the Preview lose their file name (rename to `.pptx`). Behaviour in Teams is untested.
- Outputs vary between runs; over three runs of the 14 cases, 92% of the skill's own checks passed and 9 of 11 repeated cases gave identical verdicts every time.
