// The ui-indexador HTTP API this page describes. Same origin in production (server.py serves both);
// proxied to :3040 by the Vite dev server.

export type Item = {
  registry: string
  name: string
  type: string
  kind: string
  install: string
  description?: string
  license?: string | null
  mirror_of?: string
  similarity?: number
  registry_stars?: number | null
  homepage?: string
}

export type Search = { total: number; mode: "semantic" | "keyword"; built?: string; note?: string; items: Item[] }
export type Health = { ok: boolean; built?: string; items?: number; registries?: number; themes?: number }
export type Registry = { name: string; homepage: string; stars: number; items: number; score: number; category: string }

async function get<T>(path: string, signal?: AbortSignal): Promise<T> {
  const r = await fetch(path, { signal })
  if (!r.ok) throw new Error(`${path}: ${r.status}`)
  return r.json() as Promise<T>
}

export const api = {
  search: (q: string, params: Record<string, string> = {}, signal?: AbortSignal) =>
    get<Search>(`/items?${new URLSearchParams({ q, limit: "4", ...params })}`, signal),
  health: () => get<Health>("/health"),
  registries: (limit = 24) => get<{ items: Registry[] }>(`/registries?limit=${limit}`),
  facets: () => get<{ total: number; registries: number; kinds: Record<string, number>; types: Record<string, number> }>("/facets"),
}

export const fmt = (n?: number) => (n == null ? "…" : n.toLocaleString("en-US"))
