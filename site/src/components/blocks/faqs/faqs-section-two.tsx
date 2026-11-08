import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'

const faqItems = [
  { id: 'code', question: 'Does it store or serve component code?',
    answer: 'No. It stores what each registry says about its items: name, type, description, categories, dependencies, and for blocks a layout read from the source. Every result points at the original with its npx shadcn@latest add command, and the shadcn CLI fetches the code from the registry itself.' },
  { id: 'licence', question: 'Can I use what it finds commercially?',
    answer: 'It depends on the item, which is why each result names its licence. Licences are read per registry from its GitHub repository; osi_only=1 keeps MIT, Apache-2.0, BSD and similar. Items a mirror republishes carry no licence until you check the original.' },
  { id: 'shadcn', question: 'Is this a shadcn product?',
    answer: 'No. It is an independent index that reads the public shadcn registry directory and the registries it lists, plus any you add yourself.' },
  { id: 'cloud', question: 'Does it need a cloud service or an API key?',
    answer: 'No. The index, the HTTP API and the MCP server run on your machine. Semantic search uses a local Ollama model (nomic-embed-text); without it, search falls back to keywords and says so.' },
  { id: 'language', question: 'Which languages can I search in?',
    answer: 'English works best: the embedding model and almost every registry description are English. Describe one piece at a time ("airport autocomplete"), not the whole page.' },
  { id: 'fresh', question: 'How fresh is it?',
    answer: 'It re-crawls every registry once a day and only re-embeds what changed. The date of the last crawl is at the top of this page, read from the API.' },
  { id: 'add', question: 'Can I add my own registry?',
    answer: 'Yes: scripts/add-registry.py @name "https://site.com/r/{name}.json". The registry is checked before it is saved and joins the index on the next refresh.' },
]

export default function FAQsTwo() {
  return (
    <section id="faq" className="relative overflow-hidden py-16 md:py-24">
      <div className="relative mx-auto max-w-5xl px-6">
        <div className="mx-auto flex max-w-2xl flex-col items-center text-center">
          <h2 className="mt-4 text-4xl font-semibold tracking-tight text-foreground">
            Frequently asked questions
          </h2>

          <p className="mt-4 text-lg text-balance text-muted-foreground">
            What it does, what it does not, and where its limits are.
          </p>
        </div>

        <div className="mx-auto mt-10 max-w-3xl rounded-2xl border border-border bg-background p-2 shadow-xs backdrop-blur">
          <Accordion type="single" collapsible className="space-y-2">
            {faqItems.map((item) => (
              <AccordionItem
                key={item.id}
                value={item.id}
                className="group rounded-xl border-transparent px-4 transition-colors data-[state=open]:bg-muted"
              >
                <AccordionTrigger className="cursor-pointer gap-4 text-left hover:no-underline">
                  <span className="text-base font-medium text-foreground">{item.question}</span>
                </AccordionTrigger>

                <AccordionContent className="pb-4">
                  <p className="text-sm leading-6 text-pretty text-muted-foreground">
                    {item.answer}
                  </p>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>

        <p className="mx-auto mt-8 max-w-xl text-center text-sm text-muted-foreground">
          The <a href="https://github.com/eddremonts86/ui-indexador#readme" className="font-medium text-foreground underline underline-offset-2">README</a> covers every endpoint, filter and data file.
        </p>
      </div>
    </section>
  )
}
