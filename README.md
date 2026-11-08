# ui-indexador

**Your AI builds UI from memory. Give it the whole shadcn ecosystem.**

ui-indexador indexes every component and block of the shadcn registry ecosystem (about 105,000 items from 320+
registries), ranks the registries by proof of use, and lets an AI agent find the right piece **by meaning** through
an MCP server or a plain HTTP API. Every result carries its licence and the `npx shadcn@latest add @registry/item`
command that installs it. It stores no component code: the shadcn CLI fetches it from the original registry.

Its own landing page (`site/`) was built with it: every section was searched for through its MCP server, and the
page shows the queries, the candidates and what was chosen.

## Quick start

```bash
git clone https://github.com/eddremonts86/ui-indexador && cd ui-indexador
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # mcp (1.x or 2.x) + numpy
ollama pull nomic-embed-text      # optional: semantic search (keyword search works without it)
bash refresh.sh                   # build the index: rank registries (needs `gh auth login`), crawl, embed (~15 min)
.venv/bin/python server.py        # http://127.0.0.1:3040  (API + landing page once site/ is built)
.venv/bin/python test_server.py   # smoke test: every endpoint + the MCP tool list
```

Add it to your agent (stdio; the client starts it):

```bash
claude mcp add ui-indexador -- "$PWD/.venv/bin/python" "$PWD/mcp_server.py"     # Claude Code
```

Codex (`~/.codex/config.toml`):

```toml
[mcp_servers.ui-indexador]
command = "/path/to/ui-indexador/.venv/bin/python"
args = ["/path/to/ui-indexador/mcp_server.py"]
```

Or over HTTP: `.venv/bin/python mcp_server.py --http` serves MCP on `http://127.0.0.1:3041/mcp`.

Environment: `UI_INDEXER_PORT` / `UI_INDEXER_HOST` (3040 / 127.0.0.1), `UI_INDEXER_MCP_PORT` (3041),
`UI_INDEXER_OLLAMA` (`http://localhost:11434`), `UI_INDEXER_EMBED_MODEL` (`nomic-embed-text`).

## What it answers

| MCP tool | HTTP | Returns |
|---|---|---|
| `search_items` | `/items?q=&kind=&type=&registry=&layout=&feature=&dep=&mode=&include_hidden=&limit=&offset=` | every indexed item, best match first, with install command |
| `list_facets` | `/facets` | the kinds, types, layouts and features to filter by, with counts |
| `list_registries` | `/registries?category=&q=` | ranked registries (stars, size, endpoint health) |
| `curated_blocks` | `/blocks?kind=&layout=&tone=&min_fit=` | hand-classified blocks with a 1-5 fit score |
| `list_captures` | `/captures?dir=&kind=` | 1440x900 screenshots of real sites and blocks (`/files/...`) |
| `design_notes` | `/index.md` | curated layout patterns, measured |
| `search_themes`, `get_theme` | `/themes?q=&vibe=`, `/themes/<name>` | tweakcn presets; one preset with tokens and CSS variables |
| | `/health` | counts, or which data file is missing |

## The landing page (`site/`)

Vite + React 19 + Tailwind 4 + shadcn (Radix), built from registry components found with this app through its
MCP server: `site/build-log.json` records every query, candidate and choice and the page renders it ("Built with
itself"); `site/THIRD_PARTY.md` lists the installed items and licences; `site/DOGFOOD.md` what building it taught
about the indexer.

```bash
cd site && pnpm install && pnpm build    # site/dist (not committed); server.py then serves it at /
pnpm dev                                 # 127.0.0.1:3042, API paths proxied to :3040
```

`server.py` serves `site/dist` at `/` (gzip, immutable cache for hashed `/assets/`), and the health JSON at `/`
when the site is not built. The page reads live numbers from `/health` and `/facets` and searches `/items`.

## Which registries are indexed, and adding more

- `GET /registries` (MCP `list_registries`) lists every indexed registry with homepage, stars, licence, score and
  `source` (`directory` = the official shadcn directory, `manual` = added by hand). `/registries.md` groups them.
  `/items?registry=@name` lists one registry's items; `/facets` counts everything.
- Add one the directory does not list (yours, a small one, or the official `@shadcn` set, already added):

  ```bash
  python3 scripts/add-registry.py @name "https://site.com/r/{name}.json" [--homepage URL] [--description TEXT]
  python3 scripts/add-registry.py --list
  python3 scripts/add-registry.py --remove @name
  ```

  The URL is the item template from the registry's `components.json` entry. It is checked (the index must answer
  with items) and saved in `data/extra-registries.json` (committed); it joins the index on the next refresh.

## Refresh

`bash refresh.sh` ranks the registries (directory + extras; needs `gh` logged in for stars, otherwise keeps the
current ranking), crawls every item with layout tags, and embeds only what changed (skipped if Ollama is down).
`--quick` skips the layout crawl. The servers see the new files on the next request.

The crawl refuses to shrink the catalog by more than 20% in one run, so a network blip keeps yesterday's index.

## Run it as a service (macOS)

`bash schedule/install.sh` installs three per-user launchd agents: `ui-indexador.api` (server.py on :3040, kept
alive), `ui-indexador.mcp` (MCP over HTTP on :3041/mcp, kept alive) and `ui-indexador.refresh` (refresh.sh daily
at 11:30, a notification on failure, logs in `logs/` for 14 days). `--run-now` also starts a refresh, `--status`,
`--uninstall`. On Linux, run the same three commands under systemd or cron.

## How the index is made

1. `scripts/rank-registries.py --out data`: the shadcn directory (ui.shadcn.com/r/registries.json) plus
   `extra-registries.json`, ranked by GitHub stars, size and endpoint health → `registries.json` / `.md`
   (generated, needs `gh`).
2. `scripts/survey-registries.py catalog --out data`: every item of every ranked registry from its
   `registry.json` (name, type, categories, dependencies), tagged with a kind by its name and description.
   `--deep` also fetches each block's source and tags its layout and visual features. Generated, not committed.
3. `scripts/fetch-themes.py`: tweakcn presets (Apache-2.0) plus vibes/keywords from shadcn-ui-mcp-server (MIT).
4. Hand work: `scripts/capture.py` screenshots (kept local, not in git: they are captures of other people's
   sites), the survey CSVs and `INDEX.md`.

Kinds and layouts are heuristics from names and code: use them to narrow, then look before choosing.

## Search

- **Semantic** (default when available): `q` is embedded with the local Ollama (`nomic-embed-text`, first 256
  Matryoshka dimensions) and compared with every item's name, title, description, kind and categories, so
  "buy flight tickets" finds booking, checkout and boarding-pass pieces that never say "flight". The 300 nearest
  items join the literal keyword hits; a keyword hit and a strong registry break near-ties. English queries work
  best. Needs `data/embeddings.npy`, numpy and Ollama with `nomic-embed-text` pulled (`UI_INDEXER_OLLAMA`, default `http://localhost:11434`).
- **Keyword** (`mode=keyword`, or the fallback when semantic is unavailable; the response says why in `note`):
  every word of `q` must start a word in the item's text.
- Icons/logos (~43k) and examples are hidden unless `kind=icon/logo`, `type=example` or `include_hidden=1`.
- `framework=react` by default (from each item's dependencies, else its registry's description); `vue`, `svelte`,
  `solid`, `react-native`, … or `any`.
- `osi_only=1` keeps items whose registry has an OSI licence. Licences are per registry.
- Mirrors: `@registrydirectory` republishes other registries' items. A copy of an item indexed under its own
  registry is not served; the rest carry `mirror_of` and no licence or stars (those would be the mirror's).

Bound to 127.0.0.1 by default (`--host` / `UI_INDEXER_HOST` to change it). There is no auth: do not expose it
as is. Not yet: a hosted instance, per-item licences, detection of Next.js-only items (see `site/DOGFOOD.md`).


## Licence

MIT (see `LICENSE`); bundled third-party data and components are listed in `NOTICE` and `site/THIRD_PARTY.md`.
Indexed items belong to their authors under their own licences.
