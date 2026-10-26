"""Drive the textbook PDF pass: one chunk_loop window per fresh browser.

Each cycle: docker restart kb_camoufox (clears zombie contexts that wedge
the shared browser after a chunk or two) -> run chunk_loop with a window
sized for exactly one chunk -> chunk_loop does its chunk then its built-in
4-7 h politeness sleep, and the window expires -> next cycle. Exits when
batch_state_pdf3.json has no pending_retry books left (or after MAX_CYCLES).
"""
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(r"B:\ai_philosophy")
STATE = REPO / "sratchpad" / "textbook_index" / "batch_state_pdf3.json"
LOG = REPO / "sratchpad" / "textbook_index" / "pdf_driver_log.txt"
CONTAINER = "kb_camoufox"
MAX_CYCLES = 8


def log(msg):
    line = "[%s] %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def pending_count():
    state = json.loads(STATE.read_text(encoding="utf-8"))
    return sum(1 for v in state.values() if v.get("status") == "pending_retry")


def main():
    for cycle in range(1, MAX_CYCLES + 1):
        n = pending_count()
        log("cycle %d: %d pending" % (cycle, n))
        if n == 0:
            log("queue empty, done")
            return
        log("restarting container for fresh browser")
        subprocess.run(["docker", "restart", CONTAINER], check=True,
                       capture_output=True)
        # the container's Playwright server needs time to bind the WS
        # endpoint AND finish booting the internal browser — 18s caused a
        # whole chunk of instant goto failures
        time.sleep(120)
        cmd = [sys.executable,
               str(REPO / ".agents" / "skills" / "libgen-download" / "scripts" / "chunk_loop.py"),
               "--books", "sratchpad/textbook_index/books_pdf3.json",
               "--dest", "data/philosophy_readings/pdf",
               "--state", "sratchpad/textbook_index/batch_state_pdf3.json",
               "--log", "sratchpad/textbook_index/chunk_loop_pdf3_log.txt",
               "--container", CONTAINER,
               "--workdir", "/tmp/libgen_tb_pdf",
               "--dl-dir", "/tmp/libgen_tb_pdf_dl",
               "--flow-script", "sratchpad/textbook_index/camoufox_flow_tb_pdf.py",
               "--ext", "pdf", "--chunk", "5", "--hours", "2.6"]
        log("launching chunk window")
        subprocess.run(cmd, cwd=str(REPO))
        log("chunk window ended")
    log("max cycles reached")


if __name__ == "__main__":
    main()
