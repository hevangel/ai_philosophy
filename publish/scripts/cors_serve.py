"""CORS-enabled static server for in-page file fetch (PhilArchive upload workaround).

Serves the given directory with Access-Control-Allow-Origin: * so the
philarchive.org page can fetch the manuscript PDF and attach it to the
uploader's file input via DataTransfer.
"""
import http.server
import socketserver
import sys
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8126
ROOT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".").resolve()


class CORSHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


if __name__ == "__main__":
    with socketserver.TCPServer(("127.0.0.1", PORT), CORSHandler) as httpd:
        httpd.allow_reuse_address = True
        sys.stderr.write("CORS server on http://127.0.0.1:%d serving %s\n" % (PORT, ROOT))
        httpd.serve_forever()
