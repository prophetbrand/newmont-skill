# macOS automation tooling (verified 2026-11-17)

Every entry below was checked on 2026-11-17 against its repo, PyPI, Homebrew or vendor docs. "Last activity" is the GitHub `pushed_at`, release date or PyPI upload date seen that day. Tools that could not be confirmed as alive were dropped or marked **archived** so the skill does not recommend them. Re-verify before relying on anything more than a year after that date.

## Pick by target

| Target | First choice | Fallback |
|---|---|---|
| Web app (Copilot web, SharePoint, Jira, any SaaS) | Session browser tools (`mcp__Claude_Browser__*`, Claude in Chrome) or Playwright | Full screen use only for native dialogs or an Electron shell without a reachable DOM |
| Native scriptable app (Keynote, Pages, Numbers, Finder, Mail, Office for Mac) | AppleScript / JXA via `osascript` | System Events GUI scripting, then screen use |
| App with an accessibility tree but no dictionary | System Events GUI scripting, pyobjc AX API, Peekaboo `see` | Screen use |
| Canvas, game, remote desktop, screen-share window, system notification banner | Screen use (`scripts/screen.py`, Peekaboo, cliclick) | None |

## Built into macOS (no install)

| Tool | Use for | Permission | Notes |
|---|---|---|---|
| `osascript` (AppleScript / JXA) | Driving scriptable apps; System Events GUI scripting (`tell application "System Events" to tell process "X" …`); `keystroke`, `key code`, `click at {x,y}` | Accessibility for GUI scripting, keystrokes and clicks | Apple's guide: https://developer.apple.com/library/archive/documentation/LanguagesUtilities/Conceptual/MacAutomationScriptingGuide/AutomatetheUserInterface.html (updated 2016-06-13; paths say "System Preferences", now System Settings). Error `-25211` / `-1728` / `1002` means the host app lacks Accessibility. |
| `screencapture` | `-x` silent, `-R x,y,w,h` region, `-l <windowid>` one window, `-o` no shadow | Screen Recording for other apps' windows | Output is 2x pixels on Retina. `-R` and `-l` do not combine (https://github.com/python-pillow/Pillow/issues/9070). |
| `pbcopy` / `pbpaste` | Put long text on the clipboard, then paste with cmd+v | none | Far more reliable than `keystroke` for multi-line instructions. |
| `open -a "App"` / `open <url>` | Launch or focus an app, open a URL in the default browser | none | |

## Browser automation

| Tool | URL | Last activity | Install | Notes |
|---|---|---|---|---|
| Session browser tools (`mcp__Claude_Browser__*`) and Claude in Chrome (`mcp__claude-in-chrome__*`) | this app | n/a | already loaded / deferred | Prefer these in an interactive session: the human can sign in in the same pane, and Claude in Chrome reuses the user's real Chrome profile (and its Microsoft SSO extension) which satisfies Conditional Access policies a fresh profile cannot. |
| Playwright (Node and Python) | https://github.com/microsoft/playwright | v1.65.1 released 2026-11-13; PyPI 1.65.2 | `pip install playwright && playwright install` or `npm i -D playwright` | For scripted, repeatable runs. Use `launch_persistent_context(user_data_dir, headless=False, channel="chrome")` with an empty dedicated folder (automating the default Chrome profile is unsupported; https://playwright.dev/python/docs/api/class-browsertype) so a human completes MFA once and cookies persist. `storage_state` save/load for shorter-lived sessions; never commit it (https://playwright.dev/docs/auth). No macOS permissions needed. |
| agent-browser (Vercel) | https://github.com/vercel-labs/agent-browser | pushed 2026-11-17 | `npm i -g agent-browser` | Browser automation CLI built for agents; alternative to raw Playwright. |

**Microsoft SSO facts.** Entra sign-in hosts: `login.microsoftonline.com`, `login.microsoft.com`, `login.windows.net`, `device.login.microsoftonline.com`, `autologon.microsoftazuread-sso.com`, `*.auth.microsoft.com`, `*.msauth.net`, `*.msftauth.net`, `*.phonefactor.net`; consumer `login.live.com` (https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges, data 2026-10-30). Federated tenants add an ADFS host (`…/adfs/ls/`) or Okta (`<org>.okta.com`, `<org>.okta-emea.com`, `<org>.oktapreview.com`, or a custom domain). Authenticator number matching is mandatory, so a human must be present for MFA (https://learn.microsoft.com/en-ie/Entra/Identity/Authentication/how-to-mfa-number-match). Conditional Access "require compliant device" needs the device certificate; Chrome on macOS needs the Microsoft Single Sign On extension plus the Enterprise SSO plug-in, so a fresh Playwright profile may be blocked and the user's own browser (Claude in Chrome) or `channel="msedge"` may be required (https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-grant, 2026-10-06).

## Native-app and screen-use tools

| Tool | URL | Last activity | Install | Use for | Caveats |
|---|---|---|---|---|---|
| pyobjc (Quartz, ApplicationServices, Vision, Cocoa) | https://pypi.org/project/pyobjc-framework-Quartz/ | 13.0 released 2026-10-30 | `pip install pyobjc-framework-Quartz pyobjc-framework-ApplicationServices pyobjc-framework-Vision pyobjc-framework-Cocoa` | CGEvent clicks and keys, `AXIsProcessTrusted`, `CGPreflightScreenCaptureAccess`, AX tree walking, Vision OCR (`VNRecognizeTextRequest`) | What `scripts/screen.py` uses when present. Accessibility and Screen Recording. |
| Peekaboo | https://github.com/openclaw/Peekaboo (moved from steipete) | pushed 2026-11-17, v4.9.9 | `brew install openclaw/tap/peekaboo`; MCP: `npx -y @steipete/peekaboo` | Agent-oriented CLI: `peekaboo see` returns an annotated screenshot plus element IDs; `click`, `type`, `scroll`, `app`, `window` subcommands; MCP server mode | macOS 15+. Screen Recording and Accessibility. Best all-in-one once installed. |
| cliclick | https://github.com/BlueM/cliclick | pushed 2025-08-23, brew 5.1 | `brew install cliclick` | One-line clicks, drags, key presses from a shell | Host terminal needs Accessibility; 5.1 warns on stderr when missing. |
| macapptree | https://github.com/MacPaw/macapptree | pushed 2026-09-21, PyPI 0.0.2 | `pip install macapptree` | Dump an app's accessibility tree to JSON for element lookup | Early version. Accessibility. |
| pynput | https://github.com/moses-palmer/pynput | v1.8.2, 2026-05-12 | `pip install pynput` | Keyboard and mouse control from Python | Accessibility; listeners need Input Monitoring. |
| Hammerspoon | https://github.com/Hammerspoon/hammerspoon | 1.1.1 released 2026-02-26, pushed 2026-07-08 | `brew install --cask hammerspoon` | Lua desktop automation, window management, `hs` CLI via `hs.ipc` | macOS 13+. Accessibility. Use for persistent hotkeys and window layouts, not one-off agent runs. |
| tesseract | https://tesseract-ocr.github.io | brew 5.5.4 | `brew install tesseract` | OCR fallback when pyobjc Vision is not installed | Slower and less accurate than Vision on screen text. |

**Not recommended (archived or stale):** atomacos (archived, last push 2024-02-29), pyautogui (no release since 2023-05-24; Retina coordinate mismatch), browser-use/macOS-use (archived 2025-03-05), supermemoryai/apple-mcp (archived 2025-08-11), steipete/macos-automator-mcp (archived, last push 2026-09-13), baryhuang/mcp-remote-macos-use (no push since 2025-06-10). mediar-ai/terminator is Windows-focused.

## Anthropic computer use

| Item | URL | Notes |
|---|---|---|
| `computer` tool (API) | https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool | Current toolset `computer_toolset_20260801` (17 member tools, no beta header) for Claude 5.5 models; `computer_20251124` with header `computer-use-2025-11-24` for the 4.x models. The loop is: screenshot, model picks an action, execute, screenshot again. |
| Reference loop | https://github.com/anthropics/claude-quickstarts/tree/main/computer-use-demo | pushed 2026-11-06. Runs in a Linux container, so it is a pattern reference, not a macOS runner. |
| Claude Code built-in `computer-use` MCP server | https://code.claude.com/docs/en/computer-use | Enable in `/mcp`. Research preview; interactive sessions only; one session holds the lock; needs Accessibility and Screen Recording granted to the terminal or Claude app, restart after granting. |

## MCP servers for desktop control

| Server | URL | Last push | Notes |
|---|---|---|---|
| Peekaboo MCP | see above | 2026-11-17 | Same tool as the CLI. |
| mediar-ai/mcp-server-macos-use | https://github.com/mediar-ai/mcp-server-macos-use | 2026-09-30 | OS-level open/click/type tools. |
| AB498/computer-control-mcp | https://github.com/AB498/computer-control-mcp | 2026-11-04 | Built on pyautogui and RapidOCR, so it inherits pyautogui's Retina caveats. |
| trycua/cua | https://github.com/trycua/cua | 2026-11-17 | Sandboxed computer-use agents and benchmarks; heavier than this skill needs. |
| screenpipe | https://github.com/screenpipe/screenpipe | 2026-11-17 | Records screen history for agent context; not a controller. |

## Permissions

| Permission | Grant at | Needed by |
|---|---|---|
| Accessibility | System Settings > Privacy & Security > Accessibility (https://support.apple.com/guide/mac-help/mh43185/26/mac) | GUI scripting, synthetic clicks and keystrokes, AX tree reads |
| Screen & System Audio Recording | System Settings > Privacy & Security > Screen & System Audio Recording (https://support.apple.com/guide/mac-help/mchld6aa7d23/26/mac) | Screenshots of other apps' windows, Peekaboo `see` |
| Input Monitoring | System Settings > Privacy & Security > Input Monitoring | Only for key/mouse listeners (pynput listeners) |

Permission attaches to the **host process**, not the script: grant it to Terminal, iTerm2, the Claude desktop app, VS Code or whatever launches the Python. `scripts/screen.py doctor` prints the process chain and names the app to grant. Some grants need an admin account, and the host app usually needs a restart after a new grant.

## Example-specific facts

- **Copilot Agent Builder**: web app is moving to `copilot.cloud.microsoft` (old `m365.cloud.microsoft` redirects; MC1454108, 2026-08-13). Start with the "New agent" button, choose "Skip to configure" for the Configure tab. Fields: Name (30 chars), Description (1,000), Instructions (8,000), Knowledge, capability toggles, Starter prompts; tabs Describe, Configure, Try it. Match UI by visible text, not position (https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/agent-builder-build-agents, 2026-11-16). The macOS desktop app is Chromium-based (MC1457084, 2026-08-18) but Playwright cannot attach to it; use the browser.
- **Keynote export**: `export front document to (POSIX file "/abs/path/deck.pptx") as Microsoft PowerPoint`, inside `with timeout of 1200 seconds`; document must be open, no slideshow playing (https://iworkautomation.com/keynote/document-export.html).
- **Teams notifications**: new Teams on Mac posts native Notification Center banners. Banner text is not exposed to AppleScript on macOS 15+ and the notification database is TCC-protected (https://9to5mac.com/2024/09/01/security-bite-apple-addresses-privacy-concerns-around-notification-center-database-in-macos-sequoia/). The practical check is a timed screenshot of the top-right banner area plus a Vision OCR read, with Teams' Activity feed as the fallback.
