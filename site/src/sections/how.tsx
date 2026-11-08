// The pipeline, with @karaui/how-it-works.
import { Database, Network, ScanSearch, Server } from "lucide-react"

import { HowItWorks } from "@/components/motion/how-it-works"

const steps = [
  { id: "crawl", icon: <Database className="size-4" />, title: "Crawl",
    description: "Every registry in the shadcn directory, plus the ones you add, read from its registry.json: names, types, categories, dependencies." },
  { id: "classify", icon: <ScanSearch className="size-4" />, title: "Classify",
    description: "Each block's source is read for its layout and features; licences, frameworks and mirrors are tagged; registries are ranked by stars, size and health." },
  { id: "embed", icon: <Network className="size-4" />, title: "Embed",
    description: "A local model turns each item into a vector, so a description finds it by meaning. Only new or changed items are embedded again." },
  { id: "serve", icon: <Server className="size-4" />, title: "Serve",
    description: "An MCP server and an HTTP API answer your agent with ranked candidates and their install commands. A job on your machine refreshes it every day." },
]

export function How() {
  return (
    <section id="how-it-works" className="mx-auto max-w-6xl scroll-mt-16 px-4 py-20 sm:py-28">
      <HowItWorks
        eyebrow="How it works"
        heading="From hundreds of registries to one answer"
        description="The directory lists them; nobody can search across them. The index reads all of them so your agent does not have to."
        steps={steps}
      />
    </section>
  )
}
