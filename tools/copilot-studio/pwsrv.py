"""Persistent headful Playwright browser as a tiny JSON-over-TCP server (localhost only).
Commands: rec start <dir> [fps] | rec stop <out.mp4> | goto url | shot path [full] | snap [max] | text | click sel|text=.. | fill sel text | type text | press key |
wait sel|ms | eval js | url | title | tabs | upload sel path | quit"""
import json, socket, sys, os, time, traceback, base64, subprocess
REC = {'cdp': None, 'dir': None, 'frames': []}
def rec_start(page, d, fps):
    os.makedirs(d, exist_ok=True); REC.update(cdp=page.context.new_cdp_session(page), dir=d, frames=[])
    def on_frame(ev):
        fn = os.path.join(d, 'f%06d.jpg' % len(REC['frames'])); open(fn, 'wb').write(base64.b64decode(ev['data']))
        REC['frames'].append((fn, ev['metadata']['timestamp'])); REC['cdp'].send('Page.screencastFrameAck', {'sessionId': ev['sessionId']})
    REC['cdp'].on('Page.screencastFrame', on_frame)
    REC['cdp'].send('Page.startScreencast', {'format': 'jpeg', 'quality': 70, 'maxWidth': 1440, 'maxHeight': 900, 'everyNthFrame': 1})
def rec_stop(out):
    cdp = REC['cdp']; cdp.send('Page.stopScreencast'); time.sleep(0.5); cdp.detach(); REC['cdp'] = None
    fr = REC['frames']
    if not fr: return 'no frames'
    lst = os.path.join(REC['dir'], 'list.txt')
    with open(lst, 'w') as f:
        for i, (fn, ts) in enumerate(fr):
            dur = (fr[i+1][1] - ts) if i+1 < len(fr) else 1.5
            f.write("file '%s'\nduration %.3f\n" % (os.path.basename(fn), max(dur, 0.04)))
        f.write("file '%s'\n" % os.path.basename(fr[-1][0]))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2,fps=15',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '23', out], check=True)
    return '%s (%d frames, %.1fs)' % (out, len(fr), fr[-1][1] - fr[0][1])
from playwright.sync_api import sync_playwright
PROFILE = os.path.join(os.path.dirname(__file__), 'profile'); PORT = 8765
os.makedirs(PROFILE, exist_ok=True)
def main():
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(PROFILE, headless=False, channel=None,
              viewport={'width': 1440, 'height': 900}, args=['--disable-blink-features=AutomationControlled'])
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        srv = socket.socket(); srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(('127.0.0.1', PORT)); srv.listen(1); print('ready', flush=True)
        while True:
            conn, _ = srv.accept(); data = b''
            while not data.endswith(b'\n'):
                chunk = conn.recv(65536)
                if not chunk: break
                data += chunk
            try:
                cmd = json.loads(data.decode()); op = cmd['op']; a = cmd.get('args', [])
                page = ctx.pages[-1]
                if op == 'rec':
                    out = rec_start(page, a[1], int(a[2]) if len(a) > 2 else 10) or 'recording' if a[0] == 'start' else rec_stop(a[1])
                elif op == 'goto': page.goto(a[0], wait_until='domcontentloaded', timeout=60000); time.sleep(2); out = page.url
                elif op == 'shot': page.screenshot(path=a[0], full_page=len(a) > 1); out = a[0]
                elif op == 'snap':
                    out = page.locator('body').aria_snapshot()[: int(a[0]) if a else 20000]
                elif op == 'text': out = page.inner_text('body')[: int(a[0]) if a else 20000]
                elif op == 'click':
                    loc = page.get_by_text(a[0][5:], exact=False).first if a[0].startswith('text=') else page.locator(a[0]).first
                    loc.click(timeout=15000); time.sleep(1.5); out = 'clicked'
                elif op == 'clickrole':
                    page.get_by_role(a[0], name=a[1], exact=False).first.click(timeout=15000); time.sleep(1.5); out = 'clicked'
                elif op == 'fill': page.locator(a[0]).first.fill(a[1], timeout=15000); out = 'filled'
                elif op == 'fillrole': page.get_by_role(a[0], name=a[1]).first.fill(a[2], timeout=15000); out = 'filled'
                elif op == 'type': page.keyboard.type(a[0]); out = 'typed'
                elif op == 'press': page.keyboard.press(a[0]); time.sleep(1); out = 'pressed'
                elif op == 'wait':
                    if a[0].isdigit(): time.sleep(int(a[0]) / 1000); out = 'waited'
                    else: page.wait_for_selector(a[0], timeout=int(a[1]) if len(a) > 1 else 30000); out = 'found'
                elif op == 'eval': out = page.evaluate(a[0])
                elif op == 'url': out = page.url
                elif op == 'title': out = page.title()
                elif op == 'tabs': out = [pg.url for pg in ctx.pages]
                elif op == 'upload': page.locator(a[0]).first.set_input_files(a[1]); out = 'uploaded'
                elif op == 'download':  # download <button text> <save path>
                    with page.expect_download(timeout=120000) as dl:
                        page.get_by_role('button', name=a[0], exact=False).first.click()
                    dl.value.save_as(a[1]); out = a[1]
                elif op == 'quit': conn.sendall(b'{"ok":true,"out":"bye"}\n'); conn.close(); ctx.close(); return
                else: out = 'unknown op ' + op
                conn.sendall((json.dumps({'ok': True, 'out': out}) + '\n').encode())
            except Exception as e:
                conn.sendall((json.dumps({'ok': False, 'err': traceback.format_exc()[-1500:]}) + '\n').encode())
            conn.close()
if __name__ == '__main__': main()
