import {
  Bot,
  Braces,
  Code,
  Cpu,
  FolderPlus,
    Palette,
  Plug,
  RefreshCw,
  ScanSearch,
  Server,
  ShieldCheck,
  Terminal,
  Trophy,
} from "lucide-react"

import { cn } from "@/lib/utils"
import { Marquee } from "@/components/ui/marquee"
import { Section, SectionHeader } from "@/components/ui/section"
import { StatusDot } from "@/components/ui/status-dot"

const bars = [38, 52, 44, 68, 58, 76, 62, 88, 72, 96]
const integrations = [Terminal, Bot, Code, Braces, Cpu, Server, Plug]

const secondaryFeatures = [
  { icon: RefreshCw, title: "Re-indexed every day", body: "A launchd job re-crawls at 11:30 and refuses to shrink the index by more than 20% in one run." },
  { icon: FolderPlus, title: "Add your own registry", body: "One command adds a registry the directory does not list; it is checked before it is saved." },
  { icon: Palette, title: "Themes included", body: "42 tweakcn presets with their vibes, each returned as CSS variables ready to paste." },
]

function Cell({
  icon: Icon,
  title,
  description,
  className,
  children,
}: {
  icon: React.ElementType
  title: string
  description: string
  className?: string
  children: React.ReactNode
}) {
  return (
    <div className={cn("group flex flex-col bg-card", className)}>
      <div className="relative flex h-56 items-center justify-center overflow-hidden border-b">
        {children}
      </div>
      <div className="p-6">
        <div className="flex items-center gap-2">
          <Icon className="size-4" />
          <h3 className="font-medium">{title}</h3>
        </div>
        <p className="mt-2 text-sm leading-6 text-muted-foreground">{description}</p>
      </div>
    </div>
  )
}

export function Features01({ id = "features" }: { id?: string }) {
  return (
    <Section id={id}>
      <SectionHeader
        eyebrow="What it does"
        title="An index, not another component library."
        description="It hosts no code and competes with no registry. It makes all of them searchable for the agent that writes your UI."
      />

      <div className="mt-16 grid grid-cols-1 gap-px overflow-hidden rounded-2xl border bg-border md:grid-cols-3">
        <Cell
          icon={ScanSearch}
          title="Search by meaning"
          description="Local embeddings match &quot;buy flight tickets&quot; to booking forms, checkouts and boarding passes that never say &quot;flight&quot;. Keyword search when Ollama is off."
          className="md:col-span-2"
        >
          <div className="flex h-32 w-full max-w-md items-end gap-2 px-8">
            {bars.map((height, i) => (
              <span
                key={i}
                style={{ height: `${height}%` }}
                className="flex-1 origin-bottom rounded-sm bg-foreground/10 transition-transform duration-500 group-hover:scale-y-105 last:bg-foreground"
              />
            ))}
          </div>
        </Cell>

        <Cell
          icon={Trophy}
          title="Ranked by proof of use"
          description="GitHub stars, size and endpoint health order the registries, so the established piece comes first."
        >
          <div className="relative flex size-40 items-center justify-center">
            {[100, 72, 44].map((size) => (
              <span
                key={size}
                style={{ width: `${size}%`, height: `${size}%` }}
                className="absolute rounded-full border border-dashed"
              />
            ))}
            {[
              "top-3 left-1/2",
              "top-1/2 right-2",
              "bottom-6 left-6",
              "top-10 left-8",
            ].map((position) => (
              <span key={position} className={cn("absolute size-1.5 rounded-full bg-foreground/40", position)} />
            ))}
            <StatusDot tone="neutral" className="size-3" />
          </div>
        </Cell>

        <Cell
          icon={ShieldCheck}
          title="Licences you can check"
          description="Every result names its licence; osi_only keeps what you can ship, and mirrors never borrow another site&apos;s MIT."
        >
          <div className="relative flex items-center justify-center">
            <span className="absolute size-36 rounded-3xl border bg-muted/40 transition-transform duration-500 group-hover:rotate-6" />
            <span className="absolute size-24 rounded-2xl border bg-card transition-transform duration-500 group-hover:-rotate-6" />
            <span className="relative flex size-12 items-center justify-center rounded-xl bg-foreground text-background">
              <ShieldCheck className="size-5" />
            </span>
          </div>
        </Cell>

        <Cell
          icon={Plug}
          title="Speaks MCP and HTTP"
          description="Eight MCP tools for Claude Code, Codex, Cursor or VS Code, and the same queries over plain HTTP for anything else."
          className="md:col-span-2"
        >
          <div className="flex w-full flex-col gap-3">
            {[false, true].map((reverse) => (
              <Marquee key={String(reverse)} reverse={reverse} fade duration="28s" gap="0.75rem">
                {integrations.map((Icon, i) => (
                  <span
                    key={i}
                    className="flex size-14 items-center justify-center rounded-xl border bg-card shadow-xs"
                  >
                    <Icon className="size-5 text-muted-foreground" />
                  </span>
                ))}
              </Marquee>
            ))}
          </div>
        </Cell>
      </div>

      <div className="mt-12 grid grid-cols-1 gap-8 sm:grid-cols-3">
        {secondaryFeatures.map(({ icon: Icon, title, body }) => (
          <div key={title} className="flex gap-3">
            <Icon className="mt-0.5 size-4 shrink-0" />
            <div>
              <h3 className="text-sm font-medium">{title}</h3>
              <p className="mt-1 text-sm leading-6 text-muted-foreground">{body}</p>
            </div>
          </div>
        ))}
      </div>
    </Section>
  )
}
