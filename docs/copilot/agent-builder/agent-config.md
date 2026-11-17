# Newmont brand agent: Agent Builder configuration

Prepared by Prophet, 17 November 2026, for a test build in Prophet's own Microsoft 365 tenant before Newmont's tenant is available. Every field below maps to the Agent Builder **Configure** tab seen in the screen recording (Name, Description, Instructions, Skills, Knowledge, Web search, Suggested prompts) and in the Copilot web app at https://m365.cloud.microsoft (Agents & Skills > New agent > Skip to configure). Limits are from Microsoft Learn; sources and page dates are listed at the end.

## 1. Name, description, instructions

| Field | Value | Limit |
|---|---|---|
| Name | `Newmont Brand Agent` | 30 characters [L1] |
| Icon | Leave the default for the test build. Do not upload the Newmont logo: no approved stand-alone logo file exists in the sources | PNG, 192 x 192, 1 MB [L1] |
| Model (response mode) | Auto (default) | [L1] |
| Description | The text below | 1,000 characters [L1] |
| Instructions | The fenced block in `agent-instructions.md` (fallback: `agent-instructions-short.md`) | 8,000 characters [L1, L6] |

Description (paste as is, 439 characters):

```text
Builds Newmont PowerPoint decks on the approved templates. Use it for any request to create, update or restyle a deck, presentation or slides, including "put this into slides for the QBR". It picks the Detailed View template for business and performance reporting and the Executive Summary template for strategy and storytelling, asks one question when a request fits both, and follows the Newmont Brand Identity Guidelines (October 2025).
```

The description is what Copilot uses to pick the agent for a task and what users see in the Agent Store [L1]; keep the deck verbs in it.

## 2. Suggested prompts (starter prompts)

Five, each taken from `evals/<case>/prompt.md`. The builder's prompt rows have a title and a message. The message is the first line of the eval prompt; during testing paste the full prompt into the chat instead (see `test-plan.md`), because the full briefs are long and starter prompt length limits are not documented for Agent Builder.

| # | Title | Message (from the eval prompt) | Eval case | Expected template and behaviour |
|---|---|---|---|---|
| 1 | QBR slides | put this into slides for the QBR | routing-qbr-detailed-view | Detailed View (QBR cue); with no content attached it asks for the figures, deck name and date |
| 2 | Strategy explainer | Build a short deck explaining our water stewardship strategy to site leaders. | routing-strategy-exec-summary | Executive Summary (strategy, explainer); asks for content, deck name and date |
| 3 | Safety deck | put together a newmont deck on our Q3 safety performance for the exec team | underspecified-deck-asks-first | Detailed View (performance), stated not asked; one numbered message of at most six questions; nothing built |
| 4 | Project update | Make a project progress update deck for the Ahafo expansion. | routing-ambiguous-asks | Fits both lists: asks only the template question, default Executive Summary |
| 5 | Restyle a deck | This deck came back from the agency and it looks off-brand for Newmont. Can you fix it so it follows the Newmont system? Keep all the content. | fix-off-brand-deck | Path `restyle: existing deck`; Executive Summary by default (or Detailed View with a stated reason); attach `evals/fix-off-brand-deck/files/off-brand.pptx` |

## 3. Knowledge

Add exactly the three approved files, by these exact names (they are the names the instructions tell the agent to look for):

| Role | File name | Size on Prophet's machine |
|---|---|---|
| Guidelines | `Brand Guidelines October 2025.pdf` | 10.5 MB |
| Detailed View template | `Newmont_PPT Template_Detailed View_Feb_2026.pptx` | 73.5 MB |
| Executive Summary template | `Newmont_PPT Template_Executive Summary_Feb_2026.pptx` | 13.5 MB |

The local copies are in `brand-sources/` (not committed; see `brand-sources/README.md`). They are Newmont's confidential files: keep them in a Prophet site restricted to the test team.

**Where to host them (recommended): one SharePoint document library folder.** Create a site such as `NewmontBrandAgentTest` (private, members: the Prophet testers), and a folder `Brand Sources` in its Documents library holding only the three files. In the builder, Knowledge > **+ Add knowledge** > browse (**Attach cloud files**) > the site > select the three files. This mirrors the skill's "one configured location" and lets the missing-source test remove a file from one place.

- Why SharePoint over the other options: SharePoint allows 100 files per agent and keeps existing permissions and sensitivity labels; renames and deletions are picked up [L2]. OneDrive works the same way with a 50-file limit [L2]; use it only if no SharePoint site is available. Uploading from the device embeds the files in the agent (20 files, .pptx up to 512 MB) and anyone with access to the agent can get answers grounded in them, and deleting one requires editing the agent [L2]; avoid it for this test.
- Typing a URL instead of browsing: a SharePoint URL must include the site path, no query parameters [L2]. Browsing is less error-prone.
- Wait until no file shows **Preparing** before testing [L2].
- .pptx and .pdf are supported knowledge file types (.pptx up to 512 MB) [L2], so the 73.5 MB Detailed View template is within limits.
- **Only use specified sources**: turn on. It prioritises the three files but does not block general knowledge [L2].
- **Reference people in organization**: turn off (not needed).

**What knowledge does and does not give the agent.** Knowledge is retrieval over the files' text. The agent can quote the guidelines and see layout and sample-slide text, but it does not receive the template file to build on, a version, or a "file missing" error. Microsoft documents no way for code interpreter to open a knowledge file as a template. Whether the agent can build a .pptx on the template at all is the main question the test plan answers.

## 4. Capabilities and other toggles

| Setting | Value | Note |
|---|---|---|
| Web search (**Search all websites**, under Knowledge) | **Off** | Brand values must come from the three files only. The toggle is hidden if the admin has turned off "Allow web search in Copilot" [L6] |
| Create documents, charts, and code (code interpreter) | **On** | Needed for any .pptx output. One Learn page says it is always on in Agent Builder [L4]; the build page and training unit show it as a toggle [L1, L6]. Record what the tenant shows |
| Create images (image generator) | **Off** | The brand rules forbid generated photos |
| Skills (**+ Add**) | **None** for the first test build | See section 5 |

## 5. What "Skills" means in the builder

"Skills" in the Configure panel is **not** Copilot connectors or actions. A skill is a .zip package holding a `SKILL.md` (name and description in YAML front matter, instructions under 20,000 characters) plus optional resource files and scripts [L3]. Agent Builder limits: 8 skills per agent, 50 MB per .zip, 25 MB per file, 350 files, directory depth 3; scripts (.py and others) run in a sandbox with no network and no package installs, using only preinstalled packages, which Microsoft does not list [L5]. Copilot connectors are added under Knowledge; Agent Builder cannot author actions at all, and Microsoft points to copying the agent to Copilot Studio for connectors, actions and workflows [L1].

The repository's skill cannot be uploaded as is: `SKILL.md` is 33,606 characters (limit 20,000) and the Detailed View template is 73.5 MB (limit 25 MB per file). An optional later experiment (spike validation item H) is a cut-down skill package: the short instructions, `scripts/`, and the 13.5 MB Executive Summary template only, to find out whether python-pptx is preinstalled. Do not run it until the plain build has been tested, and do not edit `SKILL.md` for it.

## 6. What the builder cannot do

| Requirement (from the user story) | Agent Builder | Consequence for the test |
|---|---|---|
| Build every slide on a named layout of the template | Not controllable. The agent sees knowledge as text, not as a template file; code interpreter output is whatever its Python produces, and python-pptx availability is unconfirmed [L4, L5] | Expect an outline with layout names, or a .pptx that does not use the template's master. `check_deck.py` will show which |
| Log activation path, template, reason, source versions | No logging the builder exposes. Purview audit records Copilot interactions with the agent name, not the template or reasons (spike S17) | The `LOG |` line at the end of each reply is the only per-request record; testers copy it |
| Read files from one configured location and fail loudly when one is missing | Knowledge is retrieval; a removed file is silently absent | Test 11 checks whether the instruction "stop if a file is missing" works; expect it to be unreliable |
| Record source versions | Not available (no eTag, hash or version in knowledge) | The reply can only name the edition from the file name |
| Enforce routing | Instructions only, not enforced | Routing tests run three times to catch drift |
| Activate on any deck request | The user must pick or @-mention the agent; no implicit routing documented (spike section 2.1) | Tests open the agent first |
| Return the deck | Code interpreter files are hosted for the active session only, then deleted [L4] | Download every deck in the same session |
| Share with Newmont users | Sharing is per user or group, or org-wide via a toggle the admin can disable; org catalog publishing needs admin approval [L7] | See `test-plan.md`, unknowns |

**Workaround (the spike's primary path).** Copy the agent's instructions to a Copilot Studio agent published to the Microsoft 365 Copilot and Teams channels, with one tool (an MCP server or HTTP action) calling a small Prophet-built service on Azure that runs this repository's `route_template.py`, `brand_sources.py` (with a Microsoft Graph resolver reading the one SharePoint library and logging id, eTag and version), `newmont_deck.py` and `check_deck.py`, saves the deck to SharePoint and returns the link on an Adaptive Card. That path gives named layouts, version logging, loud failure and per-request logs; activation remains explicit. Full findings: `docs/copilot/copilot-integration-spike.md` on branch `claude/copilot-integration-spike-d970a5` (sections 2.3, 3 and 4). The Agent Builder agent described here is a quick, zero-code baseline to measure against that path, not a replacement for it.

## Sources (Microsoft Learn, seen 17 November 2026)

- L1 Build agents in Agent Builder, ms.date 2026-11-16: https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/agent-builder-build-agents
- L2 Add knowledge sources to an agent in Agent Builder, ms.date 2026-09-30 (updated 2026-11-16): https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-add-knowledge
- L3 Add skills to your declarative agent in Agent Builder, ms.date 2026-11-16: https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/agent-builder-add-skills
- L4 Code interpreter capability for declarative agents, ms.date 2026-11-09: https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/code-interpreter
- L5 Skills in declarative agents, ms.date 2026-11-11: https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-skills
- L6 Explore the components of an agent (training unit), ms.date 2026-09-28: https://learn.microsoft.com/en-us/training/modules/build-manage-no-code-copilot-agent-sharepoint/3-explore-agent-components
- L7 Share and manage agents built in Agent Builder, ms.date 2026-11-12: https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/agent-builder-share-manage-agents
