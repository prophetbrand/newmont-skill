---
type: programmatic
focus: outputs
weight: 1
---

The run record `$(ls *.pptx | head -1).run.json` exists and names the template (`detailed_view`), the three source versions and one layout per slide.

Run from the run's output directory with `$SKILL_DIR` set to the skill root. Passes when the script exits 0.

```bash
python3 - $(ls *.pptx | head -1) <<'EOF'
import json, sys
r = json.load(open(sys.argv[1] + '.run.json'))
want = 'detailed_view'
assert r['template'] in ('detailed_view', 'executive_summary'), r['template']
assert want is None or r['template'] == want, r['template']
assert set(r['sources']) == {'guidelines', 'detailed_view', 'executive_summary'}, r.get('sources')
assert r['layouts_used'] and len(r['layouts_used']) == r['slides'], r['layouts_used']
print('ok', r['template'], r['layouts_used'])
EOF
```
