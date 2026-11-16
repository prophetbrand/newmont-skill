---
type: programmatic
focus: outputs
weight: 1
---

The run record `ahafo-review.pptx.run.json` exists and names the template (`executive_summary`), the three source versions and one layout per slide.

Run from the run's output directory with `$SKILL_DIR` set to the skill root. Passes when the script exits 0.

```bash
python3 - ahafo-review.pptx <<'EOF'
import json, sys
r = json.load(open(sys.argv[1] + '.run.json'))
want = 'executive_summary'
assert r['template'] in ('detailed_view', 'executive_summary'), r['template']
assert want is None or r['template'] == want, r['template']
assert set(r['sources']) == {'guidelines', 'detailed_view', 'executive_summary'}, r.get('sources')
assert r['layouts_used'] and len(r['layouts_used']) == r['slides'], r['layouts_used']
print('ok', r['template'], r['layouts_used'])
EOF
```
