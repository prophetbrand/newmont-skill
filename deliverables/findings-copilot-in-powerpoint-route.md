# Copilot in PowerPoint: the in-app route, 18 November 2026

Question: can the Newmont brand agent run from the Copilot pane inside PowerPoint, as the client note assumes ("a skill deployed from the Microsoft 365 admin center, used from the Copilot pane while building a deck")?

## What Microsoft ships (documentation, checked 18 Nov 2026)

| Surface | Mechanism | Status | Source |
|---|---|---|---|
| Copilot pane in PowerPoint | **Organization skills for Copilot in PowerPoint**: an admin uploads a zip (SKILL.md, Microsoft 365 app manifest v1.30, icons) in the admin center under Agents, scoped to users or groups; users pick it under "Choose skills". Personal skills can be added from the pane (stored in OneDrive/Skills). Brand Kits can carry skills. Text files including .py and .js are accepted; PNG, PDF and nested zips are not. No documentation says scripts execute or that a generated .pptx can be returned into the open deck. | Windows GA Sept 2026 (MC1478961); Mac tracked separately (MC1478960); web was a Frontier preview (MC1463509) | support.microsoft.com/en-us/powerpoint/copilot/deploy-organization-skills-for-copilot-in-powerpoint; …/copilot-in-powerpoint-skills |
| Brand Kit | Templates, colours, fonts, logos, voice and skills, set up at copilot.cloud.microsoft/create/brandkit; a brand manager marks one Official; "strict brand adherence" locks Copilot to the template's layouts | GA; needs the paid Copilot licence | support.microsoft.com/en-us/microsoft-365-copilot/create-and-manage-official-brand-kits-in-the-microsoft-365-copilot-app |
| Declarative agents (Agent Builder) in the pane | @mention in Word and PowerPoint; the agent reads the open deck as text only and cannot create or change slides (the only write action is inserting an image through an API plugin) | GA | learn.microsoft.com/microsoft-365/copilot/extensibility/declarative-agent-document-interaction |
| Copilot Studio agents in the pane | Custom engine agents "aren't supported in Outlook, Word, Excel, PowerPoint" | n/a | learn.microsoft.com/microsoft-365/copilot/extensibility/known-issues |
| Copilot Cowork | A product (GA 16 June 2026, Anthropic models): long-running tasks in the Copilot app, not inside Office panes; writes files to OneDrive/SharePoint; up to 50 custom skills | GA, off by default, credits billing | learn.microsoft.com/copilot/cowork |

Microsoft's own warning in the Chat skills guide: "Don't infer availability… in one product from a successful test in the other."

## What the Prophet tenant showed (live, bpatel@prophet.com)

| Check | Result |
|---|---|
| PowerPoint on the web, Copilot pane | Opens, offers "Create a presentation about topic", "Add a slide", "Create a branded presentation". Footer reads **M365 Copilot (Basic)** with an Upgrade link. The pane sits in a nested frame the built-in browser cannot click into, so "Choose skills" could not be exercised there. |
| PowerPoint for Mac (desktop) | The Home ribbon has Designer and the **Claude** add-in button, and no Copilot button (`desktop-ribbon-no-copilot.png`). Copilot in the Office apps needs the paid licence. |
| Brand Kit page | "Your license doesn't include Brand Kits. To upgrade, contact your admin." |
| Copilot app, Agents | "No agents found": the two Studio drafts are not published, so nothing is listed. |
| Microsoft 365 admin center, Agents | "Your account doesn't have permission to view or manage this page." |

So the in-app route cannot be tested from this account: the tenant has Copilot Chat (Basic), not Microsoft 365 Copilot, and no admin role. Everything proven so far (the suite, the recordings, the packages) is the Copilot Chat route through Copilot Studio.

## What the in-app route would take

1. A Microsoft 365 Copilot licence on at least one test account (Prophet or Newmont) and a tenant admin to upload the organization skill and, if used, mark a Brand Kit Official.
2. A different package. The PowerPoint skill is a SKILL.md that steers Microsoft's own slide generator; our package relies on three things not documented there: Python execution, the two .pptx templates inside the zip, and returning a built .pptx. The templates would move into a Brand Kit (with strict brand adherence) and the skill would carry the routing, intake, layout and copy rules as text. The checker, run record and source-version stamping have no equivalent in that route.
3. A rerun of the eval suite against that pane, since Microsoft's generator, not our kit, would be placing the content.

## Implications for the SOW and the client note

- The SOW should name the surface: "the Brand Agent in Copilot Chat (Copilot Studio)". If Newmont expects it inside PowerPoint, that is a second deliverable with its own licence and admin prerequisites, and assumption 3 (automatic routing) still does not hold on either surface; the user picks the agent, skill or brand.
- The note's line "testing the PowerPoint route alongside it" should read "the PowerPoint route needs a Microsoft 365 Copilot licence and admin access that Prophet does not have; we need a Newmont test account or a confirmation of which surface they expect".
- The "Claude" button in PowerPoint for Mac is the Claude for PowerPoint add-in, a third route worth raising if Newmont has Claude access: the full skill, templates and scripts included, already runs on Claude at 97 to 100% on the suite.
