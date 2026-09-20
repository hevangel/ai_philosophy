"""Orchestrate the camoufox in-container download flow in polite chunks.

Each chunk: compute pending books -> run the browser flow inside the container
(real anti-detect Firefox, organic clicks) -> copy book_NNNN.<ext> files out ->
rename to final names -> merge flow state into the batch state json.
Sleeps between chunks. Writes progress to a log file.

Requires a running docker container with camoufox and a Playwright server
reachable inside at ws://localhost:9222/hkej (image kb-camoufox:latest on this
machine, container name kb_camoufox, noVNC on host port 7900). The flow script
is piped in over `docker exec -i ... python -` — no shell involved, because
spawning "bash" from Python on Windows resolves to WSL's System32\bash.exe,
which drops positional args and breaks shell redirects.

Usage:
  py -3 chunk_loop.py --books books.json --dest ./corpus
  py -3 chunk_loop.py --books books.json --dest ./corpus --container kb_camoufox \
      --chunk 25 --hours 24 --skip-report match_report.json
"""
import argparse
import json
import random
import re
import shutil
import subprocess
import time
from pathlib import Path

rng = random.SystemRandom()


def log(msg, log_file: Path):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def docker_exec_stdin(container: str, script: str, args: str = "", timeout: int = 7200):
    cmd = ["docker", "exec", "-i", container, "python", "-"] + ([args] if args else [])
    return subprocess.run(cmd, input=script, capture_output=True, text=True,
                          timeout=timeout, shell=False)


def ensure_container_support(container: str, books_bytes: bytes, workdir: str, log_file: Path):
    """The flow reads <workdir>/books.json, and container restarts wipe /tmp.
    Without this check a dead container fails every chunk instantly with a
    FileNotFoundError that the log filter used to swallow."""
    chk = subprocess.run(
        ["docker", "exec", container, "sh", "-c",
         f"test -f {workdir}/books.json && echo ok"],
        capture_output=True, text=True, shell=False, timeout=60)
    if (chk.stdout or "").strip() == "ok":
        return
    log(f"container {workdir}/books.json missing (container restarted?) — re-uploading", log_file)
    up = subprocess.run(
        ["docker", "exec", "-i", container, "sh", "-c",
         f"mkdir -p {workdir} && cat > {workdir}/books.json"],
        input=books_bytes, capture_output=True, shell=False, timeout=60)
    if up.returncode != 0:
        log(f"re-upload failed rc={up.returncode}: {(up.stderr or '')[:120]}", log_file)
    else:
        log("re-uploaded books.json to container", log_file)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--books", type=Path, required=True)
    ap.add_argument("--dest", required=True)
    ap.add_argument("--state", type=Path, help="batch state json (default: batch_state.json next to --books)")
    ap.add_argument("--skip-report", type=Path,
                    help="match_report.json-format file; nums with status 'copied' are skipped")
    ap.add_argument("--log", type=Path, help="log file (default: chunk_loop_log.txt next to --state)")
    ap.add_argument("--container", default="kb_camoufox")
    ap.add_argument("--flow-script", type=Path, help="default: camoufox_flow.py next to this script")
    ap.add_argument("--ext", default="epub", help="desired file extension the flow hunts for")
    ap.add_argument("--chunk", type=int, default=25)
    ap.add_argument("--hours", type=float, default=24.0)
    ap.add_argument("--workdir", default="/tmp/libgen", help="scratch dir inside the container")
    ap.add_argument("--dl-dir", default="/tmp/libgen_dl", help="download dir inside the container")
    ap.add_argument("--min-wait", type=float, default=240, help="min minutes between chunks")
    ap.add_argument("--max-wait", type=float, default=420, help="max minutes between chunks")
    args = ap.parse_args()

    here = Path(__file__).parent
    dest = Path(args.dest).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    state_path = args.state or args.books.with_name("batch_state.json")
    log_file = args.log or state_path.with_name("chunk_loop_log.txt")
    flow_script = args.flow_script or (here / "camoufox_flow.py")
    flow_name_re = re.compile(rf"book_\d{{4}}\.{re.escape(args.ext)}")

    start = time.time()
    log(f"=== chunk loop start (chunk={args.chunk}, max {args.hours} h, container={args.container}) ===",
        log_file)
    while (time.time() - start) < args.hours * 3600:
        state = json.loads(state_path.read_text(encoding="utf-8"))
        books = json.loads(args.books.read_text(encoding="utf-8"))
        done = {int(k) for k, v in state.items() if v.get("status") in ("done", "no_result")}
        copied: set[int] = set()
        if args.skip_report and args.skip_report.exists():
            report = json.loads(args.skip_report.read_text(encoding="utf-8"))
            copied = {int(r["num"]) for r in report if r.get("status") == "copied"}
        pending = [b for b in books if b["num"] not in done and b["num"] not in copied]
        log(f"pending: {len(pending)}", log_file)
        if not pending:
            log("queue empty, done", log_file)
            break

        chunk = pending[:args.chunk]
        nums = ",".join(str(b["num"]) for b in chunk)
        log(f"running chunk: {nums}", log_file)
        try:
            ensure_container_support(args.container, args.books.read_bytes(), args.workdir, log_file)
            script = flow_script.read_text(encoding="utf-8")
            flow_args = f"{nums} {args.ext}" if args.ext != "epub" else nums
            r = docker_exec_stdin(args.container, script, flow_args)
            out = (r.stdout or "") + (r.stderr or "")
            for line in out.splitlines():
                if ("OK ->" in line or "no epub" in line or "no GET" in line
                        or "no mirror" in line or "invalid" in line
                        or "rror" in line or "Traceback" in line):
                    log("  " + line.strip(), log_file)
        except subprocess.TimeoutExpired:
            log("chunk timed out; continuing with what landed", log_file)
        except Exception as e:
            log(f"chunk error: {type(e).__name__}: {str(e)[:120]}", log_file)

        # copy everything out of the container
        get_ls = subprocess.run(
            ["docker", "exec", args.container, "ls", "-1", args.dl_dir],
            capture_output=True, text=True, shell=False)
        names = [n.strip() for n in (get_ls.stdout or "").splitlines()
                 if flow_name_re.fullmatch(n.strip())]
        flow_state = {}
        try:
            st = subprocess.run(
                ["docker", "exec", args.container, "cat", f"{args.workdir}/flow_state.json"],
                capture_output=True, text=True, shell=False, timeout=60)
            flow_state = json.loads(st.stdout or "{}")
        except Exception:
            pass

        batch_state = json.loads(state_path.read_text(encoding="utf-8"))
        books_by_num = {b["num"]: b for b in books}
        copied_out = 0
        extracted_ok = []
        for name in names:
            m = re.search(r"\d{4}", name)
            if not m:
                continue
            num = int(m.group())
            book = books_by_num.get(num)
            if not book:
                continue
            out_file = (Path.cwd() / name).resolve()
            ok = False
            try:
                # name is whitelist-validated (book_NNNN.<ext>); pull bytes via
                # native docker.exe. No shell: spawning "bash" from Python
                # resolves to WSL's System32\bash.exe, which drops the
                # positional args, making shell redirects unusable here.
                r = subprocess.run(
                    ["docker", "exec", args.container, "cat", f"{args.dl_dir}/{name}"],
                    capture_output=True, timeout=300)
                ok = (r.returncode == 0 and len(r.stdout) > 15000)
                if ok:
                    out_file.write_bytes(r.stdout)
            except subprocess.TimeoutExpired:
                log(f"  #{num:03d} extract timeout, keeping file in container", log_file)
            if ok:
                # rename into final pretty name
                safe_main = "".join(c if c not in '\\/:*?"<>|' else "_" for c in book["title"]).strip()
                safe_sub = "".join(c if c not in '\\/:*?"<>|' else "_" for c in (book.get("subtitle") or "")).strip()
                pretty = f"{num:03d} - {safe_main}" + (f" - {safe_sub}" if safe_sub else "") + f".{args.ext}"
                shutil.move(str(out_file), str(dest / pretty))
                batch_state[str(num)] = {"status": "done", "file": pretty, "ext": args.ext}
                copied_out += 1
                extracted_ok.append(name)
                log(f"  #{num:03d} saved -> {pretty}", log_file)
            else:
                log(f"  #{num:03d} extraction failed, keeping file in container", log_file)
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
        state_path.write_text(
            json.dumps(batch_state, indent=2, ensure_ascii=False), encoding="utf-8")
        # clean container download dir: only files successfully extracted
        if extracted_ok:
            subprocess.run(["docker", "exec", args.container, "sh", "-c",
                            f"cd {args.dl_dir} && rm -f " + " ".join(extracted_ok)],
                           shell=False, timeout=60)
        log(f"chunk done: {copied_out} new files", log_file)

        wait = rng.uniform(args.min_wait, args.max_wait)
        log(f"sleeping {wait / 60:.0f} min before next chunk", log_file)
        time.sleep(wait)
    log("=== chunk loop end ===", log_file)


if __name__ == "__main__":
    main()
