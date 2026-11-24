# evo_licsrv.py — fake EVO licence server (v2.0) — local + Render ready
#
# The activation path in EVO 2.0 (FUN_1400140a0) is soft-validated:
#   POST <endpoint>/activate  {"key":"%s","machineId":"%s"}
#   response JSON with a truthy "success" key  ->  DAT_140104514 = 3 (licensed)
# No signature, no challenge, no machineId echo required. expiresAt /
# serverNow are optional; absent => lease flag = 1, duration = 0.
#
# Any EVO 2.0 build pointed at this server via
#     EVO_AUTH_ENDPOINT=https://<your-service>.onrender.com
# licenses itself through its own code. /activate answers success; every
# other path 404s so the injector falls back to the embedded payload (the
# binary's own documented fallback).
#
# Local:   python evo_licsrv.py            -> http://127.0.0.1:8007/activate
# Render:  bind host/port come from $PORT (Render sets it); see render.yaml
import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Render sets PORT (and expects 0.0.0.0); local default stays 127.0.0.1:8007
HOST = os.environ.get("HOST", "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1")
PORT = int(os.environ.get("PORT") or (sys.argv[1] if len(sys.argv) > 1 else 8007))
EXPIRES_AT_MS = 4102444800000  # 2100-01-01


class Handler(BaseHTTPRequestHandler):
    def _respond(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/health"):
            # Render health check target — keeps the service awake-friendly
            self._respond(200, {"service": "evo-licsrv", "ok": True,
                                "activate": "/activate"})
        else:
            self._respond(404, {"error": "not_found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length:
            self.rfile.read(length)
        if self.path.startswith("/activate"):
            self._respond(200, {
                "success": True,
                "expiresAt": EXPIRES_AT_MS,
                "serverNow": int(time.time() * 1000),
            })
        else:
            self._respond(404, {"error": "not_found"})

    def log_message(self, fmt, *args):
        sys.stdout.write("[licsrv] %s %s\n" % (self.address_string(), fmt % args))
        sys.stdout.flush()


def main():
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    print("[licsrv] fake EVO licence server on http://%s:%d/activate" % (HOST, PORT), flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
