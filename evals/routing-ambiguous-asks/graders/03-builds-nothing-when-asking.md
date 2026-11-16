---
type: programmatic
focus: outputs
weight: 1
---

When the run stopped to ask, it built nothing.

Run from the run's output directory with `$SKILL_DIR` set to the skill root. Passes when the script exits 0.

```bash
if [ -f questions.md ]; then ! ls *.pptx >/dev/null 2>&1; fi
```
