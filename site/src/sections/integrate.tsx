// Copy-paste setup for each client. Every snippet was run before it was published (see build-log.json).
// CodeBlock: @velora/code-block.
import { CodeBlock } from "@/components/velora/code-block"

const PATH = "/path/to/ui-indexador"
const REPO = "https://github.com/eddremonts86/ui-indexador"

const tabs = [
  { name: "Claude Code", language: "bash",
    code: `git clone ${REPO} && cd ui-indexador
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # mcp 1.x or 2.x, numpy
bash refresh.sh   # build the index once (see the last tab)
claude mcp add ui-indexador -- ${PATH}/.venv/bin/python ${PATH}/mcp_server.py
claude mcp list   # ui-indexador: ... - ✔ Connected` },
  { name: "Codex", language: "bash",
    code: `# ~/.codex/config.toml  (same venv as the Claude Code tab)
[mcp_servers.ui-indexador]
command = "${PATH}/.venv/bin/python"
args = ["${PATH}/mcp_server.py"]
# codex mcp list  ->  ui-indexador ... enabled` },
  { name: "VS Code / Cursor", language: "json",
    code: `// .vscode/mcp.json  (Cursor: .cursor/mcp.json with "mcpServers" instead of "servers")
// Not run on the machine that built this page: check it against your editor's MCP docs.
{
  "servers": {
    "ui-indexador": {
      "type": "stdio",
      "command": "${PATH}/.venv/bin/python",
      "args": ["${PATH}/mcp_server.py"]
    }
  }
}` },
  { name: "HTTP", language: "bash",
    code: `python3 ${PATH}/server.py   # http://127.0.0.1:3040, standard library only
curl "http://127.0.0.1:3040/items?q=airport+autocomplete&osi_only=1&limit=3"
curl "http://127.0.0.1:3040/facets"
# MCP over HTTP instead of stdio: .venv/bin/python mcp_server.py --http  (127.0.0.1:3041/mcp)` },
  { name: "Build the index", language: "bash",
    code: `cd ${PATH}
bash refresh.sh                  # rank, crawl every item, embed (needs gh and Ollama for the full run)
bash schedule/install.sh         # then every day at 11:30 (macOS launchd)
python3 scripts/add-registry.py @mine "https://example.com/r/{name}.json"` },
]

const tools = [
  ["search_items", "every item, by meaning or keyword, with filters and the install command"],
  ["list_facets", "the kinds, types, layouts and features you can filter by"],
  ["list_registries", "registries ranked by stars, size and health"],
  ["curated_blocks", "hand-classified blocks with a 1-5 fit score"],
  ["list_captures", "screenshots of real sites and blocks"],
  ["design_notes", "measured layout patterns from proven sites"],
  ["search_themes", "theme presets by vibe"],
  ["get_theme", "one preset as CSS variables"],
] as const

export function Integrate() {
  return (
    <section id="integrate" className="mx-auto max-w-6xl scroll-mt-16 px-4 py-20 sm:py-28">
      <p className="text-xs tracking-wider text-muted-foreground uppercase">Integrate</p>
      <h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">One MCP server. Any agent.</h2>
      <p className="mt-4 max-w-2xl text-muted-foreground">
        Register it once and your agent can search before it writes. Anything that cannot speak MCP gets the same
        answers over HTTP.
      </p>
      <div className="mt-10 grid gap-8 lg:grid-cols-[1.5fr_1fr]">
        <div className="min-w-0 self-start">
          <p className="mb-3 rounded-lg border bg-card px-4 py-3 text-sm text-muted-foreground">
            <span className="text-foreground">Getting it:</span> open source, MIT, on{" "}
            <a href={REPO} className="text-brand underline underline-offset-2">GitHub</a>. Clone it, build the index
            once, then point your agent at it. <code>/path/to/ui-indexador</code> below is where you cloned it.
          </p>
          <CodeBlock tabs={tabs} lineNumbers={false} />
        </div>
        <div>
          <h3 className="text-sm font-medium text-foreground">The eight tools your agent gets</h3>
          <ul className="mt-4 divide-y border-y text-sm">
            {tools.map(([name, what]) => (
              <li key={name} className="py-2.5">
                <code className="text-brand">{name}</code>
                <span className="block text-xs text-muted-foreground">{what}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  )
}
