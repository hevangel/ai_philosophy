"""SOCKS5 proxy pool over SSH dynamic tunnels (ssh -D).

Adapted from chanmainvest knowledge_base src/kb/scrapers/proxy.py
(same hygiene rules: free-port binding, ExitOnForwardFailure backstop,
taskkill /F /T teardown on Windows, dead-tunnel reaping).

Hosts are passed in by the caller, e.g. batch_download.py --ssh-hosts
oc1.example.com,oc2.example.com — one worker thread per tunnel, so the local
residential IP never talks to the mirror directly.
"""
import socket
import subprocess
import sys
import time


_BASE_PORT = 1081
_READY_TIMEOUT = 12.0


class ProxyPool:
    """Round-robin pool of SSH dynamic-forward (SOCKS5) tunnels."""

    def __init__(self, hosts: list[str], base_port: int = _BASE_PORT) -> None:
        self.hosts = list(hosts)
        self.base_port = base_port
        self._procs: list[tuple[str, int, subprocess.Popen]] = []
        self._urls: list[str] = []
        self._idx = 0

    def __enter__(self) -> "ProxyPool":
        self.start()
        return self

    def __exit__(self, *exc) -> None:
        self.stop()

    def start(self) -> list[str]:
        for i, host in enumerate(self.hosts):
            port = self._next_free_port(self.base_port + i)
            url = f"socks5://127.0.0.1:{port}"
            try:
                proc = subprocess.Popen(
                    ["ssh", "-D", str(port), "-N",
                     "-o", "ExitOnForwardFailure=yes",
                     "-o", "ServerAliveInterval=15",
                     "-o", "ServerAliveCountMax=2",
                     "-o", "TCPKeepAlive=yes",
                     "-o", "ConnectTimeout=10",
                     "-o", "StrictHostKeyChecking=accept-new",
                     host],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    **self._popen_kwargs(),
                )
            except FileNotFoundError:
                print("[proxy] ssh not found on PATH; cannot open tunnels", flush=True)
                break
            if self._wait_ready(port):
                self._procs.append((host, port, proc))
                self._urls.append(url)
                print(f"[proxy] tunnel up: {host} -> {url} (pid {proc.pid})", flush=True)
            else:
                self._kill_proc(proc)
                print(f"[proxy] tunnel FAILED for {host} on port {port} (skipped)", flush=True)
        if not self._urls:
            print("[proxy] no tunnels came up", flush=True)
        return list(self._urls)

    def stop(self) -> None:
        for host, port, proc in self._procs:
            if proc.poll() is None:
                self._kill_proc(proc)
                print(f"[proxy] tunnel down: {host} -> 127.0.0.1:{port}", flush=True)
        self._procs.clear()
        self._urls.clear()
        self._idx = 0

    def next(self) -> str | None:
        self._reap()
        if not self._urls:
            return None
        url = self._urls[self._idx % len(self._urls)]
        self._idx += 1
        return url

    def _reap(self) -> None:
        self._procs = [e for e in self._procs if e[2].poll() is None]
        self._urls = [f"socks5://127.0.0.1:{port}" for _, port, _ in self._procs]
        if self._urls:
            self._idx %= len(self._urls)

    @property
    def urls(self) -> list[str]:
        return list(self._urls)

    @staticmethod
    def _wait_ready(port: int, timeout: float = _READY_TIMEOUT) -> bool:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=1.0):
                    return True
            except OSError:
                time.sleep(0.3)
        return False

    @staticmethod
    def _next_free_port(preferred: int) -> int:
        for port in range(preferred, preferred + 64):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]

    @staticmethod
    def _popen_kwargs() -> dict:
        if sys.platform == "win32":
            return {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
        return {"start_new_session": True}

    @staticmethod
    def _kill_proc(proc: subprocess.Popen) -> None:
        if sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        else:
            proc.kill()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass
