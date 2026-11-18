"""Run one eval case against a Copilot Studio agent Preview via pwsrv. usage: runner.py <case> <dv|es> <run-n> [record.mp4]"""
import json, socket, sys, os, re, time, pathlib
S = pathlib.Path(os.environ.get('CS_SUITE_DIR', pathlib.Path(__file__).parent / 'suite'))
REPO = pathlib.Path('/Users/bpatel/dev/newmont-skill')
ENV = 'https://copilotstudio.microsoft.com/environments/Default-a12924b0-f5f1-41a0-b960-ea4369327201/agents/'
AGENTS = {'dv': ('d609469a-453c-4c62-9d0b-a0c4929fffbb', 'Newmont Brand – Detailed View'),
          'es': ('c91e44ed-7c1b-49bd-9ef5-206f1c55d574', 'Newmont Brand – Executive Summary'),
          'all': ('67f5c22e-3661-4121-ac7a-433f407e8ba7', 'Newmont Brand Agent')}
def pw(*a):
    s = socket.create_connection(('127.0.0.1', 8765), timeout=300)
    s.sendall((json.dumps({'op': a[0], 'args': [str(x) for x in a[1:]]}) + '\n').encode()); b = b''
    while not b.endswith(b'\n'):
        c = s.recv(65536)
        if not c: break
        b += c
    r = json.loads(b)
    if not r['ok']: raise RuntimeError(r['err'][-800:])
    return r['out']
def log_text(): return pw('eval', "(document.querySelector('[role=log]')||{}).innerText||''")
def busy():
    return pw('eval', """(()=>{const b=[...document.querySelectorAll('button')].map(x=>(x.getAttribute('aria-label')||x.innerText||'').trim());
      return b.some(t=>/^stop/i.test(t)) || !!document.querySelector('[role=progressbar]');})()""")
def main():
    case, which, run = sys.argv[1], sys.argv[2], sys.argv[3]; rec = sys.argv[4] if len(sys.argv) > 4 else None
    aid, aname = AGENTS[which]
    out = S / case / run; out.mkdir(parents=True, exist_ok=True)
    body = (REPO / 'evals' / case / 'prompt.md').read_text()
    body = re.sub(r'^---.*?---\s*', '', body, flags=re.S).strip()
    (out / 'prompt.txt').write_text(body)
    files = []
    m = re.search(r'^Input files:\s*(.+)$', body, re.M)
    if m: files = [str(REPO / 'evals' / case / 'files' / f.strip()) for f in m.group(1).split(',')]
    pw('goto', ENV + aid + '/preview'); time.sleep(6)
    if rec: pw('rec', 'start', str(out / 'rec')); time.sleep(1)
    pw('clickrole', 'button', 'New chat'); time.sleep(4)
    if files:
        pw('upload', 'input[type=file]', files[0]) if len(files) == 1 else [pw('upload', 'input[type=file]', f) for f in files]
        time.sleep(5)
    pw('click', '[aria-label^="Message"]')
    lines = body.split('\n')
    for i, ln in enumerate(lines):
        if ln: pw('type', ln)
        if i < len(lines) - 1: pw('press', 'Shift+Enter')
    time.sleep(1); pw('shot', str(out / 'composed.png'))
    pw('press', 'Enter'); t0 = time.time(); time.sleep(10)
    last, stable = '', 0
    while time.time() - t0 < 1500:
        time.sleep(15); cur = log_text(); b = busy()
        if cur == last and not b: stable += 1
        else: stable = 0
        last = cur
        if stable >= 2: break
    el = time.time() - t0
    (out / 'transcript.txt').write_text(last)
    pw('shot', str(out / 'final.png'))
    snap = pw('snap', '80000'); (out / 'snap.txt').write_text(snap)
    credits = re.search(r'status: (\d+ credits)', snap)
    names = sorted(set(re.findall(r'button "([^"]+\.(?:pptx|docx|html|json|py|md|txt|xlsx|png|jpg|pdf))"', snap)))
    got = []
    for n in names:
        try: pw('download', n, str(out / n)); got.append(n)
        except Exception as e: (out / 'download-errors.txt').open('a').write(n + ': ' + str(e)[-300:] + '\n')
    if rec: pw('rec', 'stop', rec)
    meta = {'case': case, 'agent': aname, 'run': run, 'seconds': round(el), 'credits': credits.group(1) if credits else None, 'attachments': got, 'input_files': files}
    (out / 'run.json').write_text(json.dumps(meta, indent=1)); print(json.dumps(meta))
if __name__ == '__main__': main()
