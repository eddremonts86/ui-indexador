// The proof: how each section of this page was found, read from build-log.json, and the components it
// installed, read from the source tree itself. FileTree: @magicui/file-tree.
import { File, Folder, Tree } from "@/components/ui/file-tree"
import log from "../../build-log.json"

type Candidate = { item: string; similarity?: number | null; license?: string | null }
type Entry = { section: string; queries: { query: string; mode: string }[]; candidates: Candidate[];
  chosen?: string | null; composed?: boolean; why?: string; rejected?: Record<string, string> }

const files = Object.keys(import.meta.glob("/src/components/**/*.{ts,tsx}"))
  .map((p) => p.replace("/src/", "").split("/"))

type Node = { [name: string]: Node }
const tree: Node = {}
for (const parts of files) parts.reduce((n, part) => (n[part] ??= {}), tree)

function render(node: Node, path = ""): React.ReactNode[] {
  return Object.entries(node).sort(([a, x], [b, y]) => (Object.keys(y).length > 0 ? 1 : 0) - (Object.keys(x).length > 0 ? 1 : 0) || a.localeCompare(b))
    .map(([name, kids]) => {
      const id = `${path}/${name}`
      return Object.keys(kids).length
        ? <Folder key={id} value={id} element={name}>{render(kids, id)}</Folder>
        : <File key={id} value={id}><span>{name}</span></File>
    })
}

export function Built() {
  const sections = (log.sections as Entry[]).filter((s) => s.chosen || s.composed)
  return (
    <section id="built-with-itself" className="mx-auto max-w-6xl scroll-mt-16 px-4 py-20 sm:py-28">
      <p className="text-xs tracking-wider text-muted-foreground uppercase">Built with itself</p>
      <h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">This page is the demo</h2>
      <p className="mt-4 max-w-2xl text-muted-foreground">
        Every section was searched for through ui-indexador&apos;s MCP server; the pieces were installed with the
        command it returned. Two sections are composed around or without an installed piece, and say why. Results as of the crawl of {log.catalog_built}, indexer commit <code>{log.indexer_commit}</code>.
      </p>
      <div className="mt-10 grid gap-8 lg:grid-cols-[1.6fr_1fr]">
        <ol className="divide-y rounded-xl border">
          {sections.map((s) => (
            <li key={s.section} className="p-4">
              <div className="flex flex-wrap items-baseline justify-between gap-2">
                <h3 className="text-sm font-medium text-foreground">{s.section}</h3>
                <code className="text-xs text-brand">{s.chosen ?? "composed by hand"}</code>
              </div>
              <p className="mt-1 text-xs text-muted-foreground">
                asked: {s.queries.map((q) => `"${q.query}"`).join(", ")}
              </p>
              <p className="mt-1 text-xs text-muted-foreground">
                top: {s.candidates.slice(0, 3).map((c) => `${c.item}${c.similarity ? ` (${c.similarity.toFixed(2)})` : ""}`).join(" · ")}
              </p>
              {s.why && <p className="mt-2 text-xs text-foreground/80">{s.why}</p>}
            </li>
          ))}
        </ol>
        <div className="self-start rounded-xl border p-2 lg:sticky lg:top-20">
          <p className="px-2 pt-2 text-xs tracking-wider text-muted-foreground uppercase">What got installed</p>
          <Tree className="mt-2 h-[28rem]" initialExpandedItems={["/components", "/components/blocks", "/components/ui"]}>
            {render(tree)}
          </Tree>
        </div>
      </div>
    </section>
  )
}
