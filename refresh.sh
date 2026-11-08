#!/usr/bin/env bash
#
# Rebuild the index: rank the registries, crawl every item, embed what changed.
# The HTTP server and the MCP server pick up the new files on the next request (no restart).
#
#   bash refresh.sh            # all three steps (~15 min, most of it the --deep crawl)
#   bash refresh.sh --quick    # skip --deep (no layout tags), ~1 min
#
# Each step only replaces its file when it succeeds; the crawl also refuses to shrink the catalog by more
# than 20% (a network blip must not wipe the index). Run daily by schedule/install.sh.

set -euo pipefail
cd "$(dirname "$0")"
PY="${UI_INDEXER_PYTHON:-.venv/bin/python}"
[ -x "$PY" ] || PY=python3
DEEP="--deep"; [ "${1:-}" = "--quick" ] && DEEP=""
step() { printf '\n[%s] %s\n' "$(date +%H:%M:%S)" "$*"; }

step "1/3 rank registries (shadcn directory + data/extra-registries.json)"
if command -v gh >/dev/null && gh auth status >/dev/null 2>&1; then
  "$PY" scripts/rank-registries.py --out data
else
  echo "gh is missing or not logged in: kept the current ranking (stars need the GitHub API)"
  [ -f data/registries.json ] || { echo "no data/registries.json to fall back on" >&2; exit 1; }
fi

step "2/3 crawl every item ${DEEP:+(with layout tags)}"
"$PY" scripts/survey-registries.py catalog $DEEP --out data

step "3/3 embed new and changed items"
if curl -sf -m 5 "${UI_INDEXER_OLLAMA:-http://localhost:11434}/api/tags" >/dev/null; then
  "$PY" scripts/embed-catalog.py
else
  echo "Ollama is not answering: embeddings not updated (new items are found by keyword until the next run)"
fi

step "done"
"$PY" -c 'import indexer, json; print(json.dumps(indexer.health()))'
