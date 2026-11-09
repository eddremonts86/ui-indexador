// Official AI-OS site. Set VITE_AI_OS_URL at build time to override; the fallback is the current site.
export const AI_OS_URL: string =
  (import.meta.env.VITE_AI_OS_URL as string | undefined)?.trim() || "https://ai-os.eduardoinerarte.dk"
