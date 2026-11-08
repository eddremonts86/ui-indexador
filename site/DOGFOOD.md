# Dogfooding ui-indexador while building its own landing

What using the indexer to build this page showed about the indexer. Fixed items say where; the rest are
follow-ups, not done in the landing Spec.

## Fixed in Block 2 (before any piece was chosen)

Measured on the 16 section queries (`docs/landing-queries-2026-11-08.txt` before,
`docs/landing-queries-2026-11-08-after-fixes.txt` after; top 6 results each, 96 rows).

| Finding | Fix | Before → after |
|---|---|---|
| `@registrydirectory` republishes other registries' items as `<source>/<item>`; 14,286 of its 22,682 items were exact copies of an item already indexed under its own registry, so results came twice | Copies of an indexed source item are dropped from the served catalog (`indexer._catalog`) | Catalog served: 119,335 → 105,057 items. `@registrydirectory` rows in the 16 queries: 23 → 9 |
| A mirrored item showed the mirror's stars (78) and licence (MIT), not the author's: a licence it does not have | The remaining 8,396 mirrored items carry `mirror_of`, no stars, no licence, a `license_note`; they rank slightly below first-party items | The 9 mirror rows now say "mirror of @…" instead of "MIT ★78" |
| No way to keep Vue/Svelte/Solid items out of a React project | `framework` tag from the item's dependencies, else its registry's description; filter defaults to react | 6,327 Vue, 174 Solid, 164 Svelte, 74 React Native items no longer show by default |
| No licence filter | `osi_only=1` keeps items whose registry licence is OSI (MIT, Apache-2.0, BSD, ISC, MPL-2.0, 0BSD, Unlicense); mirrors are excluded because their licence is unverified | Unknown-licence rows went up, 13 → 19: rows that used to borrow the mirror's "MIT" now show their real, unknown licence |

## Follow-ups (not fixed here)

- The licence is per registry (from its GitHub repo): 95 of 323 registries have none detected and 24 say
  `NOASSERTION`. A per-item licence (from the item JSON or the repo file) would make `osi_only` keep more.
- The weakest section query was the closing call to action ("with background beams"): the matches are plain
  CTA panels, the description words that matter ("beams") are rarely in item descriptions.
- **Next.js-only items look like plain React.** `@uiception/hero-section-v1` imports `next/image` and reads the
  disk with `node:fs`; `next` is a peer, not a dependency, so the framework tag says react and it fails in Vite.
  The `--deep` crawl reads every block's source and could tag `next/` and `node:` imports as `framework: next`.
- **Items that bring their own styling system.** `@astryx` command palette items need `@astryxdesign/core` and
  StyleX. A `styling` tag (tailwind / stylex / css-modules) from dependencies would let a search exclude them.
- **The `kind` tag is too noisy to show to people.** In the hero's live search, `@kokonutui/seat-map` came back
  as `kanban/board`, `@ns-ui/seatmap-ascii-pick` as `pricing`, a booking form as `testimonials`. The page shows
  the item `type` (block / component / ui), which comes from the registry, instead. Kinds are first-match
  regexes on names and descriptions; an embedding-nearest-label classifier would beat them.
- **More Next.js-only pieces, found at build time.** `@navui/faqs-section-two` imports `next/link` (one line,
  replaced by `<a>`). Same follow-up as above: tag `next/` imports during the `--deep` crawl.
- **Undeclared dependencies.** `@magicui/file-tree` (23k-star registry) imports `@radix-ui/react-accordion` and
  `@/components/ui/scroll-area` but declares neither, so `shadcn add` leaves a build that fails. The deep crawl
  could compare an item's imports with its declared dependencies and flag the gap.
- **Fixed: the MCP server broke on a fresh install.** `pip install mcp` now pulls mcp 2.x, where `FastMCP` is
  `MCPServer` and host/port moved to `run()`. Found by running the page's own Claude Code snippet in a clean
  venv; `mcp_server.py` supports both, `requirements.txt` added, stdio and HTTP checked on 1.30.0 and 2.3.0.
