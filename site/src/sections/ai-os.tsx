// The agent setup this project's author runs on. Install line from the ai-os README (npx @edd_remonts/create-ai-os).
import { CodeBlock } from "@/components/velora/code-block"
import { AI_OS_URL } from "@/lib/links"

const tabs = [
  { name: "Install", language: "bash", code: "npx @edd_remonts/create-ai-os   # clones ai-os and runs the installer for your system" },
]

export function AiOs() {
  return (
    <section id="ai-os" className="mx-auto max-w-6xl scroll-mt-16 px-4 py-20 sm:py-28">
      <p className="text-xs tracking-wider text-muted-foreground uppercase">Same setup, your machine</p>
      <h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">The agent behind this page runs on AI-OS</h2>
      <p className="mt-4 max-w-2xl text-muted-foreground">
        AI-OS is the open-source setup this project was built with: one repo with the skills, rules, memory and MCP
        servers, linked into Claude Code, Codex, Gemini, Antigravity, Hermes and MiniMax, so every agent on your
        machine works the same way. It also lets your agent search this index. Want it on your machine?
      </p>
      <div className="mt-10 grid gap-8 lg:grid-cols-[1.5fr_1fr]">
        <div className="min-w-0 self-start">
          <CodeBlock tabs={tabs} lineNumbers={false} />
          <p className="mt-3 text-sm text-muted-foreground">
            Official site and docs at{" "}
            <a href={AI_OS_URL} className="text-brand underline underline-offset-2">{AI_OS_URL.replace(/^https?:\/\//, "")}</a>. The first run takes 30 to 60
            minutes, mostly downloads.
          </p>
        </div>
        <ul className="divide-y border-y text-sm">
          <li className="py-2.5">
            <span className="text-foreground">One set of skills and rules</span>
            <span className="block text-xs text-muted-foreground">Linked into every AI CLI on the machine.</span>
          </li>
          <li className="py-2.5">
            <span className="text-foreground">Memory that survives sessions</span>
            <span className="block text-xs text-muted-foreground">A local knowledge graph, no API key needed.</span>
          </li>
          <li className="py-2.5">
            <span className="text-foreground">Backups and health checks</span>
            <span className="block text-xs text-muted-foreground">Scheduled on macOS; you hear about it only on failure.</span>
          </li>
        </ul>
      </div>
    </section>
  )
}
