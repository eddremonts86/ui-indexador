// Live counts from the API (health + facets). NumberTicker: @fancy-ui/number-ticker.
import { useEffect, useState } from "react"

import { NumberTicker } from "@/components/ui/fancy/components/number-ticker"
import { api } from "@/lib/api"

export function Numbers() {
  const [stats, setStats] = useState<{ label: string; value: number }[] | null>(null)
  useEffect(() => {
    Promise.all([api.health(), api.facets()])
      .then(([h, f]) => setStats([
        { label: "items indexed", value: h.items ?? 0 },
        { label: "registries ranked", value: h.registries ?? 0 },
        { label: "blocks", value: f.types.block ?? 0 },
        { label: "theme presets", value: h.themes ?? 0 },
      ]))
      .catch(() => setStats(null))
  }, [])
  if (!stats) return null
  return (
    <section aria-label="The index today" className="border-y bg-card/40">
      <dl className="mx-auto grid max-w-6xl grid-cols-2 gap-px px-4 md:grid-cols-4">
        {stats.map((s) => (
          <div key={s.label} className="px-4 py-10 text-center">
            <dd className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
              <NumberTicker value={s.value} duration={1600} className="tabular-nums" />
            </dd>
            <dt className="mt-2 text-xs tracking-wider text-muted-foreground uppercase">{s.label}</dt>
          </div>
        ))}
      </dl>
    </section>
  )
}
