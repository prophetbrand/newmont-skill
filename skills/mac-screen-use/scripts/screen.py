#!/usr/bin/env python3
"""Thin macOS screen-use helper for the mac-screen-use skill.

Built on tools that ship with macOS (`screencapture`, `osascript`/System Events)
so it works with no installs. If pyobjc is present it uses the Accessibility API
for `find` and Vision for OCR; otherwise it says so and falls back.

Commands (run `screen.py <command> -h` for options):
  doctor        check permissions and dependencies; never fails, just reports
  info          screen size, Retina scale, frontmost app and its windows
  screenshot    capture screen, a region or the frontmost window to a PNG
  find          locate text on screen via Accessibility, then OCR; prints centre
  click         click at point coordinates (optionally double or right)
  type          type literal text via System Events keystrokes
  paste         put text on the clipboard and press cmd+v (best for long text)
  key           press a chord such as cmd+shift+s or return
  wait          poll until text appears, a window title exists or a file exists

All coordinates are in screen points (not Retina pixels), origin top-left.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

DEFAULT_SHOT_DIR = Path(os.environ.get("SCREEN_USE_DIR", Path.cwd() / "screen-use-run"))

KEY_CODES = {
    "return": 36, "enter": 36, "tab": 48, "space": 49, "delete": 51, "backspace": 51,
    "escape": 53, "esc": 53, "left": 123, "right": 124, "down": 125, "up": 126,
    "home": 115, "end": 119, "pageup": 116, "pagedown": 121, "forwarddelete": 117,
    "f1": 122, "f2": 120, "f3": 99, "f4": 118, "f5": 96, "f6": 97, "f7": 98, "f8": 100,
    "f9": 101, "f10": 109, "f11": 103, "f12": 111,
}
MODIFIERS = {"cmd": "command down", "command": "command down", "shift": "shift down",
             "alt": "option down", "option": "option down", "ctrl": "control down",
             "control": "control down"}


# --------------------------------------------------------------------------- utils
def run(cmd: list[str], timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def osascript(script: str, timeout: int = 30) -> tuple[bool, str]:
    proc = run(["osascript", "-e", script], timeout=timeout)
    out = (proc.stdout or proc.stderr).strip()
    return proc.returncode == 0, out


def applescript_str(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def try_import(name: str):
    try:
        return __import__(name)
    except Exception:  # noqa: BLE001 - any import failure means "not available"
        return None


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def emit(obj) -> None:
    print(json.dumps(obj, indent=2, default=str))


# --------------------------------------------------------------------------- screen info
@dataclass(frozen=True)
class ScreenInfo:
    width_pt: int
    height_pt: int
    scale: float


def screen_info() -> ScreenInfo:
    appkit = try_import("AppKit")
    if appkit:
        s = appkit.NSScreen.mainScreen()
        f = s.frame()
        return ScreenInfo(int(f.size.width), int(f.size.height), float(s.backingScaleFactor()))
    ok, out = osascript('tell application "Finder" to get bounds of window of desktop')
    if ok:
        _, _, w, h = [int(x) for x in out.split(", ")]
        return ScreenInfo(w, h, _probe_scale(w))
    return ScreenInfo(0, 0, 1.0)


def _probe_scale(width_pt: int) -> float:
    """Capture a 1x1 region and compare pixel width to point width."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        path = tmp.name
    try:
        proc = run(["screencapture", "-x", "-R", f"0,0,{width_pt},1", path])
        if proc.returncode != 0:
            return 1.0
        px = _png_size(Path(path))[0]
        return round(px / width_pt, 2) if width_pt else 1.0
    finally:
        Path(path).unlink(missing_ok=True)


def _png_size(path: Path) -> tuple[int, int]:
    import struct
    with path.open("rb") as fh:
        head = fh.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return (0, 0)
    w, h = struct.unpack(">II", head[16:24])
    return (w, h)


def frontmost() -> dict:
    ok, app = osascript('tell application "System Events" to return name of first process whose frontmost is true')
    if not ok:
        return {"app": None, "windows": [], "error": app}
    ok, wins = osascript(
        f'tell application "System Events" to tell process {applescript_str(app)} to return name of every window')
    return {"app": app, "windows": [w for w in wins.split(", ") if w] if ok else [], "error": None if ok else wins}


# --------------------------------------------------------------------------- doctor
def host_process_chain() -> list[str]:
    """Walk parent processes so the user knows which app to grant permission to."""
    chain, pid = [], os.getpid()
    for _ in range(12):
        proc = run(["ps", "-o", "ppid=,comm=", "-p", str(pid)])
        if proc.returncode != 0 or not proc.stdout.strip():
            break
        ppid, comm = proc.stdout.strip().split(None, 1)
        chain.append(Path(comm).name)
        if ppid in ("0", "1"):
            break
        pid = ppid
    return chain


def check_accessibility() -> tuple[str, str]:
    hi = try_import("HIServices") or try_import("ApplicationServices")
    if hi and hasattr(hi, "AXIsProcessTrusted"):
        return ("ok" if hi.AXIsProcessTrusted() else "missing"), "AXIsProcessTrusted"
    ok, out = osascript(
        'tell application "System Events" to tell (first process whose frontmost is true) '
        'to return count of windows')
    if ok:
        return "ok", "System Events could read windows"
    if "assistive" in out or "-1719" in out or "not allowed" in out:
        return "missing", out
    return "unknown", out


def check_screen_recording() -> tuple[str, str]:
    quartz = try_import("Quartz")
    if quartz and hasattr(quartz, "CGPreflightScreenCaptureAccess"):
        return ("ok" if quartz.CGPreflightScreenCaptureAccess() else "missing"), "CGPreflightScreenCaptureAccess"
    return "unknown", "install pyobjc-framework-Quartz to check; without permission captures show only the wallpaper"


def doctor(_args) -> int:
    chain = host_process_chain()
    report = {
        "macos": run(["sw_vers", "-productVersion"]).stdout.strip(),
        "python": sys.version.split()[0],
        "host_process_chain": chain,
        "grant_permissions_to": next((p for p in chain if p.endswith((".app", "Terminal", "iTerm2", "Claude", "Code", "Cursor"))
                                      or p in ("Terminal", "iTerm2", "Claude", "Electron")), chain[-1] if chain else "?"),
        "permissions": {},
        "builtin_tools": {},
        "optional_tools": {},
        "python_modules": {},
    }
    acc, acc_note = check_accessibility()
    rec, rec_note = check_screen_recording()
    report["permissions"]["accessibility"] = {"status": acc, "note": acc_note,
        "grant_at": "System Settings > Privacy & Security > Accessibility"}
    report["permissions"]["screen_recording"] = {"status": rec, "note": rec_note,
        "grant_at": "System Settings > Privacy & Security > Screen & System Audio Recording"}
    for tool in ("osascript", "screencapture", "pbcopy", "open"):
        report["builtin_tools"][tool] = "ok" if shutil.which(tool) else "MISSING"
    for tool, hint in (("cliclick", "brew install cliclick"), ("peekaboo", "brew install openclaw/tap/peekaboo"),
                       ("tesseract", "brew install tesseract"), ("playwright", "pip install playwright && playwright install"),
                       ("hs", "brew install --cask hammerspoon")):
        report["optional_tools"][tool] = "ok" if shutil.which(tool) else f"not installed ({hint})"
    for mod, pkg in (("Quartz", "pyobjc-framework-Quartz"), ("ApplicationServices", "pyobjc-framework-ApplicationServices"),
                     ("Vision", "pyobjc-framework-Vision"), ("AppKit", "pyobjc-framework-Cocoa")):
        report["python_modules"][mod] = "ok" if try_import(mod) else f"not installed (pip install {pkg})"
    info = screen_info()
    report["screen"] = asdict(info)
    report["frontmost"] = frontmost()
    missing = [k for k, v in report["permissions"].items() if v["status"] == "missing"]
    report["verdict"] = ("ready" if not missing and acc == "ok" else
                         f"grant {', '.join(missing) or 'permissions (status unknown)'} to {report['grant_permissions_to']} and re-run")
    emit(report)
    return 0


# --------------------------------------------------------------------------- screenshot
def screenshot(args) -> int:
    if args.out:
        out = Path(args.out)
    else:
        DEFAULT_SHOT_DIR.mkdir(parents=True, exist_ok=True)
        out = DEFAULT_SHOT_DIR / f"{stamp()}-{args.label or 'shot'}.png"
    cmd = ["screencapture", "-x"]
    if args.region:
        cmd += ["-R", args.region]
    elif args.window:
        wid = _front_window_id()
        if wid:
            cmd += ["-l", str(wid)]
    cmd.append(str(out))
    proc = run(cmd)
    if proc.returncode != 0:
        emit({"ok": False, "error": proc.stderr.strip()})
        return 1
    emit({"ok": True, "path": str(out), "pixels": _png_size(out), "scale": screen_info().scale})
    return 0


def _front_window_id() -> int | None:
    quartz = try_import("Quartz")
    if not quartz:
        return None
    front = frontmost().get("app")
    opts = quartz.kCGWindowListOptionOnScreenOnly | quartz.kCGWindowListExcludeDesktopElements
    for w in quartz.CGWindowListCopyWindowInfo(opts, quartz.kCGNullWindowID) or []:
        if w.get("kCGWindowOwnerName") == front and w.get("kCGWindowLayer", 1) == 0:
            return int(w["kCGWindowNumber"])
    return None


# --------------------------------------------------------------------------- find text
@dataclass(frozen=True)
class Hit:
    text: str
    x: float
    y: float
    w: float
    h: float
    source: str

    @property
    def centre(self) -> tuple[int, int]:
        return int(self.x + self.w / 2), int(self.y + self.h / 2)


def find_via_ax(needle: str, app: str | None) -> list[Hit]:
    hi = try_import("ApplicationServices")
    appkit = try_import("AppKit")
    if not (hi and appkit):
        return []
    hits: list[Hit] = []
    for running in appkit.NSWorkspace.sharedWorkspace().runningApplications():
        if app and running.localizedName() != app:
            continue
        if not app and running.activationPolicy() != 0:
            continue
        _walk_ax(hi, hi.AXUIElementCreateApplication(running.processIdentifier()), needle.lower(), hits, 0)
        if len(hits) > 50:
            break
    return hits


def _ax_attr(hi, el, name):
    err, val = hi.AXUIElementCopyAttributeValue(el, name, None)
    return val if err == 0 else None


def _walk_ax(hi, el, needle, hits, depth) -> None:
    if depth > 40:
        return
    label = " ".join(str(_ax_attr(hi, el, a) or "") for a in ("AXTitle", "AXValue", "AXDescription", "AXHelp"))
    if needle in label.lower():
        pos, size = _ax_attr(hi, el, "AXPosition"), _ax_attr(hi, el, "AXSize")
        if pos is not None and size is not None:
            foundation = try_import("Foundation")
            p, s = _ax_point(foundation, hi, pos), _ax_point(foundation, hi, size, is_size=True)
            if p and s:
                hits.append(Hit(label.strip()[:120], p[0], p[1], s[0], s[1], "accessibility"))
    for child in _ax_attr(hi, el, "AXChildren") or []:
        _walk_ax(hi, child, needle, hits, depth + 1)


def _ax_point(foundation, hi, value, is_size=False):
    try:
        ok, out = hi.AXValueGetValue(value, hi.kAXValueCGSizeType if is_size else hi.kAXValueCGPointType, None)
        if ok:
            return (out.width, out.height) if is_size else (out.x, out.y)
    except Exception:  # noqa: BLE001
        return None
    return None


def find_via_ocr(needle: str) -> tuple[list[Hit], str]:
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        shot = Path(tmp.name)
    run(["screencapture", "-x", str(shot)])
    info = screen_info()
    try:
        vision = try_import("Vision")
        if vision:
            return _ocr_vision(vision, shot, needle, info), "vision"
        if shutil.which("tesseract"):
            return _ocr_tesseract(shot, needle, info), "tesseract"
        return [], "no OCR available (pip install pyobjc-framework-Vision, or brew install tesseract)"
    finally:
        shot.unlink(missing_ok=True)


def _ocr_vision(vision, shot: Path, needle: str, info: ScreenInfo) -> list[Hit]:
    foundation = try_import("Foundation")
    url = foundation.NSURL.fileURLWithPath_(str(shot))
    handler = vision.VNImageRequestHandler.alloc().initWithURL_options_(url, None)
    request = vision.VNRecognizeTextRequest.alloc().init()
    request.setRecognitionLevel_(getattr(vision, 'VNRequestTextRecognitionLevelAccurate', 0))
    handler.performRequests_error_([request], None)
    px_w, px_h = _png_size(shot)
    hits = []
    for obs in request.results() or []:
        cand = obs.topCandidates_(1)
        if not cand:
            continue
        text = cand[0].string()
        if needle.lower() in text.lower():
            bb = obs.boundingBox()  # normalised, origin bottom-left
            x = bb.origin.x * px_w / info.scale
            y = (1 - bb.origin.y - bb.size.height) * px_h / info.scale
            hits.append(Hit(text, x, y, bb.size.width * px_w / info.scale, bb.size.height * px_h / info.scale, "ocr-vision"))
    return hits


def _ocr_tesseract(shot: Path, needle: str, info: ScreenInfo) -> list[Hit]:
    proc = run(["tesseract", str(shot), "stdout", "--psm", "11", "tsv"], timeout=120)
    hits, words = [], needle.lower().split()
    rows = [r.split("\t") for r in proc.stdout.splitlines()[1:] if r.count("\t") >= 11]
    for i, r in enumerate(rows):
        seq = [x[11].lower() for x in rows[i:i + len(words)]]
        if seq == words:
            xs = [int(x[6]) for x in rows[i:i + len(words)]]; ys = [int(x[7]) for x in rows[i:i + len(words)]]
            ws = [int(x[8]) for x in rows[i:i + len(words)]]; hs = [int(x[9]) for x in rows[i:i + len(words)]]
            x0, y0 = min(xs), min(ys)
            x1, y1 = max(a + b for a, b in zip(xs, ws)), max(a + b for a, b in zip(ys, hs))
            hits.append(Hit(" ".join(seq), x0 / info.scale, y0 / info.scale, (x1 - x0) / info.scale, (y1 - y0) / info.scale, "ocr-tesseract"))
    return hits


def find(args) -> int:
    hits = find_via_ax(args.text, args.app)
    note = "accessibility" if hits else None
    if not hits and not args.ax_only:
        hits, note = find_via_ocr(args.text)
    emit({"query": args.text, "method": note, "count": len(hits),
          "hits": [{**asdict(h), "centre": h.centre} for h in hits[:args.limit]]})
    return 0 if hits else 1


# --------------------------------------------------------------------------- input
def click(args) -> int:
    x, y = args.x, args.y
    quartz = try_import("Quartz")
    if quartz:
        _click_quartz(quartz, x, y, args.double, args.right)
    else:
        kind = "right click" if args.right else "click"
        ok, out = osascript(f'tell application "System Events" to {kind} at {{{x}, {y}}}')
        if ok and args.double:
            ok, out = osascript(f'tell application "System Events" to click at {{{x}, {y}}}')
        if not ok:
            emit({"ok": False, "error": out}); return 1
    time.sleep(args.settle)
    emit({"ok": True, "clicked": [x, y], "double": args.double, "right": args.right})
    return 0


def _click_quartz(q, x, y, double, right):
    down, up, button = ((q.kCGEventRightMouseDown, q.kCGEventRightMouseUp, q.kCGMouseButtonRight) if right
                        else (q.kCGEventLeftMouseDown, q.kCGEventLeftMouseUp, q.kCGMouseButtonLeft))
    pt = q.CGPointMake(x, y)
    q.CGEventPost(q.kCGHIDEventTap, q.CGEventCreateMouseEvent(None, q.kCGEventMouseMoved, pt, button))
    time.sleep(0.05)
    for n in range(2 if double else 1):
        for kind in (down, up):
            ev = q.CGEventCreateMouseEvent(None, kind, pt, button)
            q.CGEventSetIntegerValueField(ev, q.kCGMouseEventClickState, n + 1)
            q.CGEventPost(q.kCGHIDEventTap, ev)
            time.sleep(0.03)


def type_text(args) -> int:
    ok, out = osascript(f'tell application "System Events" to keystroke {applescript_str(args.text)}')
    emit({"ok": ok, "typed_chars": len(args.text), "error": None if ok else out})
    return 0 if ok else 1


def paste(args) -> int:
    text = Path(args.file).read_text() if args.file else args.text
    subprocess.run(["pbcopy"], input=text, text=True, check=True)
    ok, out = osascript('tell application "System Events" to keystroke "v" using command down')
    emit({"ok": ok, "pasted_chars": len(text), "error": None if ok else out})
    return 0 if ok else 1


def key(args) -> int:
    parts = [p.strip().lower() for p in args.chord.split("+")]
    mods = [MODIFIERS[p] for p in parts if p in MODIFIERS]
    keys = [p for p in parts if p not in MODIFIERS]
    if len(keys) != 1:
        emit({"ok": False, "error": "chord needs exactly one non-modifier key"}); return 1
    using = f" using {{{', '.join(mods)}}}" if mods else ""
    k = keys[0]
    action = f"key code {KEY_CODES[k]}" if k in KEY_CODES else f"keystroke {applescript_str(k)}"
    ok, out = osascript(f'tell application "System Events" to {action}{using}')
    emit({"ok": ok, "chord": args.chord, "error": None if ok else out})
    return 0 if ok else 1


# --------------------------------------------------------------------------- wait
def wait(args) -> int:
    deadline = time.time() + args.timeout
    while True:
        found = _wait_condition(args)
        if found:
            emit({"ok": True, "matched": found, "waited_s": round(args.timeout - (deadline - time.time()), 1)})
            return 0
        if time.time() > deadline:
            emit({"ok": False, "error": f"timeout after {args.timeout}s", "frontmost": frontmost()})
            return 1
        time.sleep(args.interval)


def _wait_condition(args):
    if args.file and Path(args.file).exists():
        return {"file": args.file}
    if args.window_title:
        fm = frontmost()
        if any(args.window_title.lower() in w.lower() for w in fm.get("windows", [])):
            return {"window": args.window_title, "app": fm["app"]}
    if args.app and frontmost().get("app") == args.app:
        return {"app": args.app}
    if args.text:
        hits = find_via_ax(args.text, None) or (find_via_ocr(args.text)[0] if not args.ax_only else [])
        if hits:
            return {"text": args.text, "centre": hits[0].centre, "source": hits[0].source}
    return None


# --------------------------------------------------------------------------- cli
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor").set_defaults(fn=doctor)
    sub.add_parser("info").set_defaults(fn=lambda a: (emit({"screen": asdict(screen_info()), "frontmost": frontmost()}), 0)[1])
    s = sub.add_parser("screenshot"); s.add_argument("--out"); s.add_argument("--label")
    s.add_argument("--region", help="x,y,w,h in points"); s.add_argument("--window", action="store_true", help="frontmost window only")
    s.set_defaults(fn=screenshot)
    f = sub.add_parser("find"); f.add_argument("text"); f.add_argument("--app"); f.add_argument("--ax-only", action="store_true")
    f.add_argument("--limit", type=int, default=10); f.set_defaults(fn=find)
    c = sub.add_parser("click"); c.add_argument("x", type=int); c.add_argument("y", type=int)
    c.add_argument("--double", action="store_true"); c.add_argument("--right", action="store_true")
    c.add_argument("--settle", type=float, default=0.3); c.set_defaults(fn=click)
    t = sub.add_parser("type"); t.add_argument("text"); t.set_defaults(fn=type_text)
    pa = sub.add_parser("paste"); pa.add_argument("text", nargs="?", default=""); pa.add_argument("--file"); pa.set_defaults(fn=paste)
    k = sub.add_parser("key"); k.add_argument("chord", help="e.g. cmd+shift+s, return, escape"); k.set_defaults(fn=key)
    w = sub.add_parser("wait"); w.add_argument("--text"); w.add_argument("--window-title"); w.add_argument("--app"); w.add_argument("--file")
    w.add_argument("--timeout", type=float, default=30); w.add_argument("--interval", type=float, default=1.0)
    w.add_argument("--ax-only", action="store_true"); w.set_defaults(fn=wait)
    return p


def main(argv=None) -> int:
    if sys.platform != "darwin":
        emit({"ok": False, "error": "macOS only"}); return 2
    args = build_parser().parse_args(argv)
    try:
        return args.fn(args)
    except subprocess.TimeoutExpired as exc:
        emit({"ok": False, "error": f"timed out: {exc.cmd}"}); return 1
    except Exception as exc:  # noqa: BLE001 - report, never crash the agent loop
        emit({"ok": False, "error": f"{type(exc).__name__}: {exc}"}); return 1


if __name__ == "__main__":
    sys.exit(main())
