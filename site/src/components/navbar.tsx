// Composed around an installed piece: the indexed navbars were mega-menus or WebGL pieces; the GitHub star button
// is @elements/github-star-button, added once the repo went public (see build-log.json).
import { GitHubStarButton } from "@/components/elements/github-star-button"
import { Button } from "@/components/ui/button"

const links = [
  ["How it works", "#how-it-works"],
  ["Search", "#search"],
  ["Integrate", "#integrate"],
  ["FAQ", "#faq"],
] as const

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b bg-background/80 backdrop-blur">
      <nav aria-label="Main" className="mx-auto flex h-14 max-w-6xl items-center gap-6 px-4">
        <a href="#" className="text-sm font-semibold tracking-tight text-foreground">
          ui<span className="text-brand">-</span>indexador
        </a>
        <ul className="ml-auto hidden items-center gap-6 text-sm text-muted-foreground md:flex">
          {links.map(([label, href]) => (
            <li key={href}><a href={href} className="hover:text-foreground">{label}</a></li>
          ))}
        </ul>
        <GitHubStarButton owner="eddremonts86" repo="ui-indexador" variant="outline" className="ml-auto max-sm:hidden md:ml-0" aria-label="Star ui-indexador on GitHub" />
        <Button asChild size="sm" className="ml-auto sm:ml-0">
          <a href="#integrate">Add to your agent</a>
        </Button>
      </nav>
    </header>
  )
}
