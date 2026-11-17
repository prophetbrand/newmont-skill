# mac-screen-use

A Claude Code skill that makes macOS screen automation ("computer use") disciplined and repeatable. Versioned copy; the live install is `~/.claude/skills/mac-screen-use/`.

What it does when invoked with a task:

1. **Need gate**: states whether screen control is needed at all. API or CLI, then browser automation (session browser tools, Claude in Chrome, Playwright), then AppleScript/System Events, then full screen use.
2. **Question gate**: one numbered message for only what the task cannot proceed without; defaults for the rest.
3. **Plan**: per step, the action, the observation that confirms it, the recovery, and whether it is a stop-and-confirm step. SSO pages are detected by host and handed to the human. Permission preflight via `doctor`.
4. **Execute** with `scripts/screen.py` (screenshot, find text via accessibility or OCR, click, type, paste, key chords, wait) verifying after every action.
5. **Report**: what was done, each stop and who approved, screenshots kept, what could not be verified.

Files:

- `SKILL.md`: the gates, plan format, worked examples (Copilot agent builder, Keynote export, Teams notification) and reply format.
- `references/tooling.md`: macOS automation tools verified on 2026-11-17 with URLs, dates, install commands and when to use which.
- `scripts/screen.py`: stdlib-only helper on top of `screencapture` and `osascript`; uses pyobjc for accessibility, Vision OCR and CGEvent input when installed.

Quick start:

```bash
cp -R skills/mac-screen-use ~/.claude/skills/
python3 ~/.claude/skills/mac-screen-use/scripts/screen.py doctor
```

`doctor` reports which permissions are missing and which host app (Terminal, the Claude app, VS Code) to grant them to; it never fails. Never run it, or any other command here, as a way to enter credentials: the skill hands sign-in, MFA and CAPTCHAs to the human.
