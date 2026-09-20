"""Orchestrate the camoufox in-container download flow in polite chunks.

Each chunk: compute pending books -> run flow inside the container (real
anti-detect Firefox, organic clicks) -> copy book_NNNN.epub files out ->
rename to final names -> merge flow state into batch_state.json.
Sleeps between chunks. Writes progress to chunk_loop_log.txt.
"""
import json
import random
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
DEST = Path(r"B:\ai_philosophy\philosophy_pop_culture")
OUT = HERE / "dl_out"
PY = r"B:\ai_agents\.venv\Scripts\python.exe"
CONTAINER = "kb_camoufox"
LOG = HERE / "chunk_loop_log.txt"
rng = random.SystemRandom()


def log(msg):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def docker_exec_stdin(script: str, args: str = "", timeout: int = 7200):
    cmd = ["docker", "exec", "-i", CONTAINER, "python", "-"] + ([args] if args else [])
    return subprocess.run(cmd, input=script, capture_output=True, text=True,
                          timeout=timeout, shell=False)


def ensure_container_support():
    """The flow reads /tmp/libgen/books.json, and container restarts wipe /tmp.
    Without this check a dead container fails every chunk instantly with a
    FileNotFoundError that the log filter used to swallow."""
    chk = subprocess.run(
        ["docker", "exec", CONTAINER, "sh", "-c",
         "test -f /tmp/libgen/books.json && echo ok"],
        capture_output=True, text=True, shell=False, timeout=60)
    if (chk.stdout or "").strip() == "ok":
        return
    log("container /tmp/libgen/books.json missing (container restarted?) — re-uploading")
    payload = (HERE / "books.json").read_bytes()
    up = subprocess.run(
        ["docker", "exec", "-i", CONTAINER, "sh", "-c",
         "mkdir -p /tmp/libgen && cat > /tmp/libgen/books.json"],
        input=payload, capture_output=True, shell=False, timeout=60)
    if up.returncode != 0:
        log(f"re-upload failed rc={up.returncode}: {(up.stderr or '')[:120]}")
    else:
        log("re-uploaded books.json to container")


def main():
    chunk_size = int(sys.argv[1]) if len(sys.argv) > 1 else 25
    max_hours = float(sys.argv[2]) if len(sys.argv) > 2 else 24.0
    start = time.time()

    log(f"=== chunk loop start (chunk={chunk_size}, max {max_hours} h) ===")
    while (time.time() - start) < max_hours * 3600:
        state = json.loads((HERE / "batch_state.json").read_text(encoding="utf-8"))
        books = json.loads((HERE / "books.json").read_text(encoding="utf-8"))
        report = json.loads((HERE / "match_report.json").read_text(encoding="utf-8"))
        done = {int(k) for k, v in state.items() if v.get("status") in ("done", "no_result")}
        copied = {r["num"] for r in report if r.get("status") == "copied"}
        # books already fetched by the browser flow but not yet merged? check dl_out
        pending = [b for b in books if b["num"] not in done and b["num"] not in copied]
        log(f"pending: {len(pending)}")
        if not pending:
            log("queue empty, done")
            break

        chunk = pending[:chunk_size]
        nums = ",".join(str(b["num"]) for b in chunk)
        log(f"running chunk: {nums}")
        try:
            ensure_container_support()
            script = (HERE / "camoufox_flow.py").read_text(encoding="utf-8")
            r = docker_exec_stdin(script, nums)
            out = (r.stdout or "") + (r.stderr or "")
            for line in out.splitlines():
                if ("OK ->" in line or "no epub" in line or "no GET" in line
                        or "no mirror" in line or "invalid" in line
                        or "rror" in line or "Traceback" in line):
                    log("  " + line.strip())
        except subprocess.TimeoutExpired:
            log("chunk timed out; continuing with what landed")
        except Exception as e:
            log(f"chunk error: {type(e).__name__}: {str(e)[:120]}")

        # copy everything out of the container
        get_ls = subprocess.run(
            ["docker", "exec", CONTAINER, "ls", "-1", "/tmp/libgen_dl"],
            capture_output=True, text=True, shell=False)
        names = [n.strip() for n in (get_ls.stdout or "").splitlines()
                 if re.fullmatch(r"book_\d{4}\.epub", n.strip())]
        flow_state = {}
        try:
            st = subprocess.run(
                ["docker", "exec", CONTAINER, "cat", "/tmp/libgen/flow_state.json"],
                capture_output=True, text=True, shell=False, timeout=60)
            flow_state = json.loads(st.stdout or "{}")
        except Exception:
            pass

        batch_state = json.loads((HERE / "batch_state.json").read_text(encoding="utf-8"))
        books_by_num = {b["num"]: b for b in books}
        copied_out = 0
        extracted_ok = []
        for name in names:
            m = name.replace("book_", "").replace(".epub", "")
            if not m.isdigit():
                continue
            num = int(m)
            book = books_by_num.get(num)
            if not book:
                continue
            out_file = (OUT / name).resolve()
            if out_file.parent != OUT:
                raise ValueError("extracted path escaped dl_out")
            ok = False
            try:
                # name is whitelist-validated (book_\d{4}.epub); pull bytes via
                # native docker.exe. No shell: spawning "bash" from Python
                # resolves to WSL's System32\bash.exe, which drops the
                # positional args, making shell redirects unusable here.
                r = subprocess.run(
                    ["docker", "exec", CONTAINER, "cat", f"/tmp/libgen_dl/{name}"],
                    capture_output=True, timeout=300)
                ok = (r.returncode == 0 and len(r.stdout) > 15000)
                if ok:
                    out_file.write_bytes(r.stdout)
            except subprocess.TimeoutExpired:
                log(f"  #{num:03d} extract timeout")
                ok = (rc.returncode == 0 and out_file.exists()
                      and out_file.stat().st_size > 15000)
            except subprocess.TimeoutExpired:
                log(f"  #{num:03d} extract timeout")
            if ok:
                # rename into final pretty name
                safe_main = "".join(c if c not in '\\/:*?"<>|' else "_" for c in book["title"]).strip()
                safe_sub = "".join(c if c not in '\\/:*?"<>|' else "_" for c in (book.get("subtitle") or "")).strip()
                pretty = f"{num:03d} - {safe_main}" + (f" - {safe_sub}" if safe_sub else "") + ".epub"
                shutil.move(str(out_file), str(DEST / pretty))
                batch_state[str(num)] = {"status": "done", "file": pretty, "ext": "epub"}
                copied_out += 1
                extracted_ok.append(name)
                log(f"  #{num:03d} saved -> {pretty}")
            else:
                log(f"  #{num:03d} extraction failed, keeping file in container")
        # merge remaining flow state (no_result / pending_retry / failed markers)
        for k, v in flow_state.items():
            if not isinstance(v, dict) or v.get("status") == "done":
                continue
            cur = batch_state.get(k)
            # a no_result verdict outranks an earlier transient pending_retry,
            # so permanently-absent books stop being retried every chunk
            if cur is None or (v.get("status") == "no_result"
                               and cur.get("status") == "pending_retry"):
                batch_state[k] = v
        (HERE / "batch_state.json").write_text(
            json.dumps(batch_state, indent=2, ensure_ascii=False), encoding="utf-8")
        # clean container download dir: only files successfully extracted
        if extracted_ok:
            subprocess.run(["docker", "exec", CONTAINER, "sh", "-c",
                            "cd /tmp/libgen_dl && rm -f " + " ".join(extracted_ok)],
                           shell=False, timeout=60)
        log(f"chunk done: {copied_out} new epubs")

        wait = rng.uniform(240, 420)
        log(f"sleeping {wait / 60:.0f} min before next chunk")
        time.sleep(wait)
    log("=== chunk loop end ===")


if __name__ == "__main__":
    main()
