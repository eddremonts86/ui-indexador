import { ArrowRight } from "lucide-react"
import { useEffect, useState } from "react"

import { Button } from "@/components/ui/button"
import { BlurFade } from "@/components/ui/blur-fade"
import { GridPattern } from "@/components/ui/grid-pattern"
import { Marquee } from "@/components/ui/marquee"
import { Section } from "@/components/ui/section"
import { ShimmerButton } from "@/components/ui/shimmer-button"
import { SearchPreview } from "@/components/search-preview"
import { api, fmt, type Health, type Registry } from "@/lib/api"

export function Hero01({ id = "hero" }: { id?: string }) {
  const [health, setHealth] = useState<Health | null>(null)
  const [registries, setRegistries] = useState<Registry[]>([])
  useEffect(() => {
    api.health().then(setHealth).catch(() => {})
    api.registries(24).then((r) => setRegistries(r.items)).catch(() => {})
  }, [])

  return (
    <Section id={id} spacing="none" className="overflow-hidden">
      <GridPattern
        width={48}
        height={48}
        squares={[[4, 2], [10, 1], [16, 3], [7, 6], [20, 5], [2, 8]]}
        className="[mask-image:radial-gradient(ellipse_70%_55%_at_50%_0%,white,transparent)]"
      />
      <div className="relative flex flex-col items-center px-4 pt-20 text-center sm:pt-28">
        <BlurFade>
          <a
            href="#built-with-itself"
            className="inline-flex items-center gap-2 rounded-full border bg-card py-1 pr-3 pl-1 text-xs transition-colors hover:bg-accent"
          >
            <span className="shrink-0 rounded-full bg-primary px-2 py-0.5 font-medium whitespace-nowrap text-primary-foreground">
              {health?.built ?? "live"}
            </span>
            <span className="text-muted-foreground">
              {fmt(health?.items)} items · {fmt(health?.registries)} registries<span className="max-sm:hidden"> · re-indexed daily</span>
            </span>
            <ArrowRight className="size-3 text-muted-foreground" />
          </a>
        </BlurFade>
        {/* Not faded in: the headline is the largest paint, an entrance animation would delay it. */}
        <h1 className="mt-8 max-w-5xl text-4xl font-semibold tracking-tighter text-balance sm:text-5xl md:text-6xl">
            Your AI builds UI from memory. Give it the whole shadcn ecosystem.
          </h1>
        <BlurFade delay={0.2}>
          <p className="mx-auto mt-6 max-w-xl text-lg text-balance text-muted-foreground">
            ui-indexador indexes every component and block of 300+ shadcn registries, ranks them by proof of
            use, and lets your agent find the right one by meaning. Then it installs it with one command.
          </p>
        </BlurFade>
        <BlurFade
          delay={0.3}
          className="mt-10 flex flex-col items-center gap-3 sm:flex-row"
        >
          <ShimmerButton onClick={() => document.getElementById("integrate")?.scrollIntoView({ behavior: "smooth" })}>
            Add it to your agent
            <ArrowRight className="size-4" />
          </ShimmerButton>
          <Button variant="outline" size="lg" className="rounded-full" asChild>
            <a href="#search">Try a search</a>
          </Button>
        </BlurFade>
        <BlurFade delay={0.35}>
          <p className="mt-4 text-xs text-muted-foreground">
            MCP server and HTTP API · runs on your machine · no account, no cloud
          </p>
        </BlurFade>
        <BlurFade delay={0.45} offset={24} className="mt-16 w-full max-w-5xl">
          <SearchPreview />
        </BlurFade>
      </div>
      <div className="relative pt-20 pb-24 sm:pb-32">
        <p className="text-center font-mono text-xs tracking-wider text-muted-foreground uppercase">
          The registries it ranks highest today
        </p>
        <Marquee fade pauseOnHover gap="3.5rem" duration="30s" className="mt-8">
          {registries.map((r) => (
            <a
              key={r.name}
              href={r.homepage}
              className="text-lg font-semibold tracking-tight whitespace-nowrap text-muted-foreground/80 hover:text-foreground"
            >
              {r.name}
            </a>
          ))}
        </Marquee>
      </div>
    </Section>
  )
}
