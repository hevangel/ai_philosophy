"""Per-book PDF download driver — OS-enforced ceiling per book.

Replaces chunk_loop for the textbook PDF pass. The in-container sequential
flow wedges irrecoverably (busy-spin inside Playwright C-level calls that
SIGALRM cannot interrupt), so each book now runs as its OWN container
invocation under the container's `timeout` command: a wedged book dies at
12 minutes, the driver records pending_retry and moves on.

Per book: docker exec -i kb_camoufox timeout 720 python - <num>  (flow piped
on stdin; reads books.json + flow_state.json in /tmp/libgen_tb_pdf) ->
copy out book_NNNN.pdf -> merge state -> politeness sleep. Cleans flow_*
partial downloads before each attempt. A 15-min pause every 5 books.
Exits when batch_state_pdf3.json has no pending_retry books.
"""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(r"B:\ai_philosophy")
TB = REPO / "sratchpad" / "textbook_index"
STATE = TB / "batch_state_pdf3.json"
BOOKS = TB / "books_pdf3.json"
FLOW = TB / "camoufox_flow_tb_pdf.py"
DRIVER_LOG = TB / "pdf2_log.txt"
CONTAINER = "kb_camoufox"
WORKDIR = "/tmp/libgen_tb_pdf"
DLDIR = "/tmp/libgen_tb_pdf_dl"
BOOK_TIMEOUT = "720"
BOOK_GAPS = [45, 90]
BIG_EVERY = 5
BIG_PAUSE = [600, 900]


def log(msg):
    line = "[%s] %s" % (time.strftime("%m-%d %H:%M:%S"), msg)
    print(line, flush=True)
    with DRIVER_LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def container_setup():
    subprocess.run(["docker", "exec", CONTAINER, "mkdir", "-p", WORKDIR, DLDIR],
                   capture_output=True)
    subprocess.run(["docker", "exec", "-i", CONTAINER,
                    "sh", "-c", "cat > %s/books.json" % WORKDIR],
                   input=BOOKS.read_bytes(), capture_output=True)
    # reset per-run flow state (host state is authoritative)
    subprocess.run(["docker", "exec", CONTAINER, "rm", "-f",
                    "%s/flow_state.json" % WORKDIR], capture_output=True)


def clean_partials():
    subprocess.run(["docker", "exec", CONTAINER, "sh", "-c",
                    "cd %s && rm -f flow_*.pdf flow_*.epub" % DLDIR],
                   capture_output=True)


def attempt(num, ext):
    flow = FLOW.read_text(encoding="utf-8")
    cmd = ["docker", "exec", "-i", CONTAINER, "timeout", "--kill-after=10",
           BOOK_TIMEOUT, "python", "-", str(num), ext]
    r = subprocess.run(cmd, input=flow, capture_output=True, text=True,
                       timeout=780)
    return (r.stdout or "") + (r.stderr or "")


def read_state():
    r = subprocess.run(["docker", "exec", CONTAINER, "cat",
                        "%s/flow_state.json" % WORKDIR],
                       capture_output=True, text=True)
    try:
        return json.loads(r.stdout or "{}")
    except json.JSONDecodeError:
        return {}


def copy_out(num, ext):
    name = "book_%04d.%s" % (int(num), ext)
    r = subprocess.run(["docker", "exec", CONTAINER, "cat",
                        "%s/%s" % (DLDIR, name)], capture_output=True)
    if r.returncode != 0 or not r.stdout:
        return False
    if ext == "pdf" and r.stdout[:5] != b"%PDF-":
        return False
    if ext == "epub" and r.stdout[:2] != b"PK":
        return False
    books = json.loads(BOOKS.read_text(encoding="utf-8"))
    title = next(b["title"] for b in books if b["num"] == int(num))
    safe = re.sub(r'[<>:"/\\|?*]+', " ", title).strip()
    sub = "epub" if ext == "epub" else "pdf"
    dest = REPO / "data" / "philosophy_readings" / sub / (
        "%03d - %s.%s" % (int(num), safe, ext))
    dest.write_bytes(r.stdout)
    subprocess.run(["docker", "exec", CONTAINER, "rm", "-f",
                    "%s/%s" % (DLDIR, name)], capture_output=True)
    return True


def main():
    rng = __import__("random").SystemRandom()
    subprocess.run(["docker", "restart", CONTAINER], capture_output=True)
    time.sleep(120)
    container_setup()
    while True:
        state = json.loads(STATE.read_text(encoding="utf-8"))
        pending = sorted((int(k) for k, v in state.items()
                          if isinstance(v, dict) and v.get("status") == "pending_retry"))
        if not pending:
            log("queue empty, done")
            return
        for i, num in enumerate(pending):
            log("book %03d (queue position %d/%d)" % (num, i + 1, len(pending)))
            clean_partials()
            got = False
            for ext in ("epub", "pdf"):
                try:
                    out = attempt(num, ext)
                    for line in out.splitlines():
                        if any(k in line for k in ("OK ->", "no ", "timeout",
                                                   "rror", "watchdog",
                                                   "invalid")):
                            log("  [%s] %s" % (ext, line.strip()[:130]))
                except subprocess.TimeoutExpired:
                    log("  book %03d [%s]: host-side kill" % (num, ext))
                st = read_state().get(str(num), {})
                status = st.get("status") if isinstance(st, dict) else None
                if status == "done" and copy_out(num, ext):
                    log("  book %03d: DONE as %s" % (num, ext))
                    state[str(num)] = {"status": "done"}
                    got = True
                    break
                if status == "no_result" and ext == "epub":
                    log("  book %03d: no epub on mirror, trying pdf" % num)
                    continue
                if status == "no_result":
                    state[str(num)] = {"status": "no_result"}
                    log("  book %03d: no_result on mirror (epub+pdf)" % num)
                    break
            if not got:
                state[str(num)] = {"status": "pending_retry"}
                log("  book %03d: failed this attempt" % num)
            STATE.write_text(json.dumps(state, indent=1, ensure_ascii=False),
                             encoding="utf-8")
            if i < len(pending) - 1:
                gap = (rng.uniform(*BIG_PAUSE) if (i + 1) % BIG_EVERY == 0
                       else rng.uniform(*BOOK_GAPS))
                log("  sleeping %.0f s" % gap)
                time.sleep(gap)
        log("queue cycle complete")


if __name__ == "__main__":
    main()
