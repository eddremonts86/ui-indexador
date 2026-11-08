#!/usr/bin/env python3
"""ui-indexador HTTP API: read-only, JSON. The same queries are offered over MCP by mcp_server.py.

  python3 server.py [--port 3040] [--host 127.0.0.1]      (env: UI_INDEXER_PORT, UI_INDEXER_HOST)

  /health                                             data counts, or what is missing
  /items?q=&kind=&type=&registry=&layout=&feature=&dep=&mode=auto|semantic|keyword&include_hidden=&framework=react&osi_only=&limit=&offset=
                                                      search EVERY indexed component and block (install command included);
                                                      semantic by meaning when embeddings + Ollama are there
  /facets                                             the kinds, types, layouts, features you can filter by
  /registries?category=&q=&limit=                     ranked registries
  /blocks?kind=&layout=&tone=&registry=&min_fit=&q=   hand-scored blocks from the surveys
  /captures?dir=sites|blocks&kind=&q=                 screenshots, each with a /files/ url
  /themes?q=&vibe=   /themes/<name>                   tweakcn presets; one preset with tokens and CSS
  /index.md, /registries.md                           curated notes (markdown)
  /files/<path>                                       a file under data/
  /, /assets/...                                      the landing page (site/dist), when built

Standard library only; semantic search also needs numpy (requirements.txt).
"""

import argparse
import gzip
import json
import mimetypes
import os
from functools import lru_cache
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

import indexer
from indexer import DATA

SITE = (Path(__file__).resolve().parent / "site" / "dist").resolve()
COMPRESSIBLE = {"application/json", "text/html", "text/javascript", "application/javascript", "text/css",
                "text/markdown", "image/svg+xml"}


@lru_cache(maxsize=64)
def _gzip(body):
    return gzip.compress(body, 6)

ROUTES = {
    "/health": lambda q: indexer.health(),
    "/items": lambda q: indexer.items(q.get("q"), q.get("kind"), q.get("type"), q.get("registry"), q.get("layout"),
                                      q.get("feature"), q.get("dep"), q.get("limit"), q.get("offset"),
                                      q.get("mode", "auto"), q.get("include_hidden", False), q.get("framework", "react"),
                                      q.get("osi_only", False)),
    "/facets": lambda q: indexer.facets(),
    "/registries": lambda q: indexer.registries(q.get("category"), q.get("q"), q.get("limit")),
    "/blocks": lambda q: indexer.blocks(q.get("kind"), q.get("layout"), q.get("tone"), q.get("registry"),
                                        q.get("min_fit"), q.get("q"), q.get("limit")),
    "/captures": lambda q: indexer.captures(q.get("dir"), q.get("kind"), q.get("q"), q.get("limit")),
    "/themes": lambda q: indexer.themes(q.get("q"), q.get("vibe")),
}


class Handler(BaseHTTPRequestHandler):
    server_version = "ui-indexador/2"

    def send(self, code, body, ctype="application/json; charset=utf-8", cache=None):
        if isinstance(body, str):
            body = body.encode()
        elif not isinstance(body, bytes):
            body = json.dumps(body, ensure_ascii=False, indent=1).encode()
        gz = (len(body) > 1024 and "gzip" in self.headers.get("Accept-Encoding", "")
              and ctype.split(";")[0] in COMPRESSIBLE)
        if gz:
            body = _gzip(body)
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Vary", "Accept-Encoding")
        if gz:
            self.send_header("Content-Encoding", "gzip")
        if cache:
            self.send_header("Cache-Control", cache)
        self.end_headers()
        self.wfile.write(body)

    @staticmethod
    def site_file(path):
        """A file of the built landing (site/dist), never outside it."""
        target = (SITE / unquote(path).lstrip("/")).resolve()
        return target if target.is_relative_to(SITE) and target.is_file() else None

    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        path = u.path.rstrip("/") or "/"
        try:
            if path == "/":  # the landing page when it is built (site/dist), the health JSON otherwise
                index = SITE / "index.html"
                if index.is_file():
                    self.send(200, index.read_bytes(), "text/html; charset=utf-8", cache="no-cache")
                else:
                    self.send(200, indexer.health())
            elif path in ROUTES:
                self.send(200, ROUTES[path](q))
            elif path.startswith("/themes/"):
                self.send(200, indexer.theme(unquote(path.removeprefix("/themes/"))))
            elif path in ("/index.md", "/registries.md"):
                self.send(200, indexer.notes(path.lstrip("/")), "text/markdown; charset=utf-8")
            elif path.startswith("/files/"):
                target = (DATA / unquote(path.removeprefix("/files/"))).resolve()
                if not target.is_relative_to(DATA) or not target.is_file():
                    raise FileNotFoundError(path)
                self.send(200, target.read_bytes(), mimetypes.guess_type(target.name)[0] or "application/octet-stream")
            elif (asset := self.site_file(path)) is not None:  # Vite puts a content hash in every /assets/ name
                immutable = path.startswith("/assets/")
                self.send(200, asset.read_bytes(), mimetypes.guess_type(asset.name)[0] or "application/octet-stream",
                          cache="public, max-age=31536000, immutable" if immutable else "no-cache")
            else:
                self.send(404, {"error": "not found", "see": "/health"})
        except FileNotFoundError as e:
            self.send(404 if "missing" not in str(e) else 503, {"error": str(e) if "missing" in str(e) else "not found"})
        except ValueError as e:
            self.send(400, {"error": str(e)})

    def log_message(self, fmt, *args):
        pass


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--port", type=int, default=int(os.environ.get("UI_INDEXER_PORT", 3040)))
    ap.add_argument("--host", default=os.environ.get("UI_INDEXER_HOST", "127.0.0.1"))
    a = ap.parse_args()
    srv = ThreadingHTTPServer((a.host, a.port), Handler)
    print(f"ui-indexador on http://{a.host}:{a.port}", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
