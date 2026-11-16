---
type: programmatic
focus: outputs
weight: 1
---

`check_deck.py` passes on the delivered deck against its template (the grep on FAIL lines decides, whatever the exit code).

Run from the run's output directory with `$SKILL_DIR` set to the skill root. Passes when the script exits 0.

```bash
out=$(python3 "$SKILL_DIR/scripts/check_deck.py" water-strategy.pptx --template executive_summary --deck-name "Newmont – Water Stewardship Strategy")
echo "$out"
! echo "$out" | grep -q "^FAIL"
```
