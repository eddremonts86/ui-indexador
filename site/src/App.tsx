import { lazy, Suspense } from "react"

import { Hero01 } from "@/components/hero-01"
import { Navbar } from "@/components/navbar"
import { Numbers } from "@/sections/numbers"

// Below the fold: loaded after the hero so the first screen paints from a small bundle.
const Rest = lazy(() => import("@/sections/rest"))
const Footer = lazy(() => import("@/components/blocks/footer-03"))

export default function App() {
  return (
    <>
      <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:z-[60] focus:p-3">Skip to content</a>
      <Navbar />
      <main id="main" className="bg-background text-foreground">
        <Hero01 />
        <Numbers />
        <Suspense fallback={<div className="min-h-screen" />}>
          <Rest />
        </Suspense>
      </main>
      <Suspense fallback={null}>
        <Footer />
      </Suspense>
    </>
  )
}
