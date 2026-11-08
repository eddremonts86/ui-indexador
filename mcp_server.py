#!/usr/bin/env python3
"""ui-indexador over MCP: the same read-only queries as the HTTP API, as tools an agent calls directly.

  .venv/bin/python mcp_server.py            # stdio: the client starts it
  .venv/bin/python mcp_server.py --http     # streamable HTTP on 127.0.0.1:3041/mcp (a long-running service)

Needs the `mcp` package, 1.x or 2.x (requirements.txt). It installs nothing: every result carries the
`npx shadcn@latest add @registry/item` command, and shadcn's own CLI/MCP fetches the code.
"""

import argparse
import os

import indexer

HOST = os.environ.get("UI_INDEXER_HOST", "127.0.0.1")
PORT = int(os.environ.get("UI_INDEXER_MCP_PORT", 3041))
try:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("ui-indexador", host=HOST, port=PORT)
    HTTP_KW = {}
except ModuleNotFoundError:  # mcp 2.x renamed FastMCP to MCPServer and moved host/port to run()
    from mcp.server.mcpserver import MCPServer

    mcp = MCPServer("ui-indexador")
    HTTP_KW = {"host": HOST, "port": PORT}


@mcp.tool()
def search_items(q: str = "", kind: str = "", type: str = "", registry: str = "", layout: str = "",
                 feature: str = "", dep: str = "", limit: int = 25, offset: int = 0, mode: str = "auto",
                 include_hidden: bool = False, framework: str = "react", osi_only: bool = False) -> dict:
    """Search every indexed shadcn registry component and block (100k+ items, 300 registries).
    q is searched by meaning (semantic, local embeddings): describe the piece in English, one piece per call
    ("airport autocomplete", "passenger count stepper", "flight checkout"), not the whole page.
    mode: auto | semantic | keyword. Icons/logos and examples are hidden unless kind/type or include_hidden asks.
    framework: react (default) | vue | svelte | solid | react-native | any. osi_only: only verifiable OSI licences.
    A result with mirror_of was republished by another registry: its licence is unverified, check the source.
    Filters combine. kind: hero, pricing, auth, dashboard, sidebar, table, chart, form, chat/ai... (see list_facets).
    type: block | component | ui | example. layout (blocks): split-text-media, centered-text, bento-grid...
    feature: motion, glass, shader3d, marquee... dep: an npm package (e.g. motion, recharts).
    Results come best match first (similarity, then a literal keyword hit, then registry rank) with the install command."""
    return indexer.items(q, kind, type, registry, layout, feature, dep, limit, offset, mode, include_hidden,
                         framework, osi_only)


@mcp.tool()
def list_facets() -> dict:
    """The kinds, types, layouts and features the catalog can be filtered by, with counts."""
    return indexer.facets()


@mcp.tool()
def list_registries(category: str = "", q: str = "", limit: int = 30) -> dict:
    """Ranked shadcn registries (score from GitHub stars, size and endpoint health), best first."""
    return indexer.registries(category, q, limit)


@mcp.tool()
def curated_blocks(kind: str = "", layout: str = "", tone: str = "", min_fit: int = 0, q: str = "", limit: int = 50) -> dict:
    """Hand-classified blocks from the design surveys, with a 1-5 fit score and a preview URL."""
    return indexer.blocks(kind, layout, tone, None, min_fit, q, limit)


@mcp.tool()
def list_captures(dir: str = "", kind: str = "", q: str = "") -> dict:
    """Captured 1440x900 screenshots of real sites and registry blocks. Each url is a path on the HTTP API
    (prefix it with UI_INDEXER_URL, default http://127.0.0.1:3040)."""
    return indexer.captures(dir or None, kind, q)


@mcp.tool()
def design_notes() -> str:
    """The curated pattern notes: how proven sites use the screen, measured, with what to borrow."""
    return indexer.notes("index.md")


@mcp.tool()
def search_themes(q: str = "", vibe: str = "") -> dict:
    """tweakcn theme presets (palette, fonts, radius). vibe: minimal, professional, playful, elegant, tech..."""
    return indexer.themes(q, vibe)


@mcp.tool()
def get_theme(name: str) -> dict:
    """One theme preset: full light/dark tokens plus CSS variables ready to paste into globals.css."""
    return indexer.theme(name)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--http", action="store_true", help="streamable HTTP instead of stdio")
    if ap.parse_args().http:
        mcp.run(transport="streamable-http", **HTTP_KW)
    else:
        mcp.run(transport="stdio")
