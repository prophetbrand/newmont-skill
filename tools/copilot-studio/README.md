# Copilot Studio driver

A persistent headful Chromium (Playwright) kept open by a tiny local server, so a person can sign in once and scripted steps reuse the session.

```bash
pip install playwright && python3 -m playwright install chromium
cd tools/copilot-studio && python3 pwsrv.py &      # opens Chromium with profile/ next to it
./pw goto https://copilotstudio.microsoft.com/     # sign in by hand in the window
./pw clickrole link Agents
./pw upload "[role=dialog] input[type=file]" ../../dist/newmont-brand-copilot-studio.zip
./pw fillrole textbox "Message Newmont Brand Agent" "put this into slides for the QBR ..."
./pw download newmont-q3-2026-qbr.pptx ./deck.pptx
```

Commands: `goto`, `shot`, `snap`, `text`, `click`, `clickrole`, `fill`, `fillrole`, `type`, `press`, `wait`, `eval`, `url`, `title`, `tabs`, `upload`, `download`, `rec start <dir>` / `rec stop <out.mp4>` (DevTools screencast stitched with ffmpeg), `quit`. The profile folder holds the sign-in; it is gitignored. Never type credentials through this tool.

## Running an eval case against an agent

```bash
python3 runner.py routing-qbr-detailed-view dv run-1 [record.mp4]   # case name, agent (dv|es|all), run folder name
```

`runner.py` reads `evals/<case>/prompt.md`, attaches the files its "Input files:" line names, starts a new Preview chat, sends the prompt, waits until the reply is stable, downloads every attachment and writes `prompt.txt`, `transcript.txt`, `snap.txt`, `run.json` and screenshots under `$CS_SUITE_DIR/<case>/<run>/` (default `suite/` beside this file). Set the agent ids in `AGENTS` at the top. `AGENTS` also has `all` (Newmont Brand Agent, the combined package); `python3 runner.py <case> all run-1` runs a case on it. The 18 November 2026 suite results are in `docs/copilot/copilot-studio/RESULTS-2026-11-18-suite.md`.
