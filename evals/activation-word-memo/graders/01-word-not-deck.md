---
type: programmatic
focus: outputs
weight: 1
---

A .docx was produced and no deck was built.

Run from the run's output directory with `$SKILL_DIR` set to the skill root. Passes when the script exits 0.

```bash
ls safety-memo.docx >/dev/null && ! ls *.pptx >/dev/null 2>&1
```
