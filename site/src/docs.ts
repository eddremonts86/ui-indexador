import "./index.css"
import "./docs.css"
import { marked } from "marked"

// Trusted input: these are the files and JSON this project serves (server.py), so rendering them as HTML is fine.
const DOCS = {
  registries: { file: "/registries.md", title: "Registries, ranked by proof of use" },
  index: { file: "/index.md", title: "Design gallery" },
} as const

const main = document.getElementById("doc")!
const fail = (msg: string) => {
  main.innerHTML = `<p class="doc-status">${msg}</p>`
}

// ── JSON endpoints (/health, /facets, /registries, …) ──────────────────────────────

type Json = null | boolean | number | string | Json[] | { [key: string]: Json }
const isObject = (v: Json): v is { [key: string]: Json } => typeof v === "object" && v !== null && !Array.isArray(v)
const isPrimitive = (v: Json) => v === null || typeof v !== "object"
const esc = (s: unknown) =>
  String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!)
const label = (k: string) => k.replace(/_/g, " ")
const fmt = (v: Json) => (typeof v === "number" ? v.toLocaleString("en-US") : v === null ? "—" : esc(v))

function renderValue(v: Json): string {
  if (isPrimitive(v)) return `<span>${fmt(v)}</span>`
  if (Array.isArray(v)) {
    if (v.length && v.every(isObject)) {
      const cols = [...new Set(v.flatMap((row) => Object.keys(row as object)))]
      const head = cols.map((c) => `<th>${esc(label(c))}</th>`).join("")
      const body = v
        .map((row) => `<tr>${cols.map((c) => `<td>${cellText((row as { [k: string]: Json })[c])}</td>`).join("")}</tr>`)
        .join("")
      return `<div class="doc-table"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`
    }
    return `<ul>${v.map((x) => `<li>${renderValue(x)}</li>`).join("")}</ul>`
  }
  const entries = Object.entries(v)
  // A map of counts (facets: kinds, frameworks, …): one bar per key, widest first.
  if (entries.length && entries.every(([, x]) => typeof x === "number")) {
    const max = Math.max(...entries.map(([, x]) => x as number)) || 1
    const rows = [...entries]
      .sort(([, a], [, b]) => (b as number) - (a as number))
      .map(
        ([k, x]) =>
          `<li class="bar"><span class="bar-label">${esc(k)}</span><span class="bar-track"><span class="bar-fill" style="width:${(((x as number) / max) * 100).toFixed(1)}%"></span></span><span class="bar-value">${fmt(x)}</span></li>`,
      )
      .join("")
    return `<ul class="bars">${rows}</ul>`
  }
  // A flat object (health): a key/value list.
  if (entries.every(([, x]) => isPrimitive(x))) {
    return `<dl class="kv">${entries.map(([k, x]) => `<div><dt>${esc(label(k))}</dt><dd>${fmt(x)}</dd></div>`).join("")}</dl>`
  }
  // Mixed object: its scalar fields as one key/value list, then one titled section per nested key.
  const scalars = entries.filter(([, x]) => isPrimitive(x))
  const nested = entries.filter(([, x]) => !isPrimitive(x))
  const top = scalars.length ? renderValue(Object.fromEntries(scalars)) : ""
  return top + nested.map(([k, x]) => `<section class="sub"><h2>${esc(label(k))}</h2>${renderValue(x)}</section>`).join("")
}

function cellText(v: Json | undefined): string {
  if (v === undefined) return "—"
  if (isPrimitive(v)) return fmt(v)
  return `<code>${esc(JSON.stringify(v))}</code>`
}

async function renderJson() {
  const path = location.pathname + location.search
  const raw = path + (location.search ? "&" : "?") + "format=json"
  document.title = `${location.pathname} · ui-indexador`
  const res = await fetch(path, { headers: { Accept: "application/json" } })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = (await res.json()) as Json
  main.innerHTML = `
    <div class="doc-head">
      <h1><code>${esc(location.pathname)}</code></h1>
      <a class="doc-raw" href="${esc(raw)}">raw JSON</a>
    </div>
    ${renderValue(data)}`
}

// ── markdown files (/registries.md, /index.md) via ?doc= ──────────────────────────

async function renderDoc() {
  const requested = new URLSearchParams(location.search).get("doc") ?? "registries"
  const doc = requested in DOCS ? DOCS[requested as keyof typeof DOCS] : DOCS.registries
  document.title = `${doc.title} · ui-indexador`
  const res = await fetch(doc.file)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  main.innerHTML = marked.parse(await res.text(), { async: false }) as string
  // Wide tables scroll inside a bordered box instead of breaking the page width.
  main.querySelectorAll("table").forEach((table) => {
    const wrap = document.createElement("div")
    wrap.className = "doc-table"
    table.replaceWith(wrap)
    wrap.append(table)
  })
}

const run = location.pathname === "/docs.html" ? renderDoc() : renderJson()
run.catch(() => fail("Could not load this page. Is the index server running?"))
