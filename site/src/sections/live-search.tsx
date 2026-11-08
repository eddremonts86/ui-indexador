import { SearchPreview } from "@/components/search-preview"

export function LiveSearch() {
  return (
    <section id="search" className="mx-auto max-w-5xl scroll-mt-16 px-4 py-20 sm:py-28">
      <p className="text-xs tracking-wider text-muted-foreground uppercase">Try it</p>
      <h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">Search the way your agent does</h2>
      <p className="mt-4 max-w-2xl text-muted-foreground">
        One piece at a time, in plain English. This box calls the same <code className="text-foreground">/items</code> endpoint
        your agent calls through MCP, with <code className="text-foreground">osi_only</code> on.
      </p>
      <div className="mt-10">
        <SearchPreview limit={8} autoType={false} filters initial="pricing table with monthly yearly toggle" />
      </div>
    </section>
  )
}
