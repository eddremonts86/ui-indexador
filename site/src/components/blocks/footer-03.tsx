import type * as React from 'react';

import { AI_OS_URL } from '@/lib/links';
import { cn } from '@/lib/utils';

const ENTER =
  'animate-in fade-in slide-in-from-bottom-4 duration-500 ease-[cubic-bezier(0.22,1,0.36,1)] fill-mode-both motion-reduce:animate-none';

const stagger = (index: number): React.CSSProperties => ({ animationDelay: `${index * 60}ms` });

interface FooterLink {
  label: string;
  href: string;
}

interface FooterColumn {
  label: string;
  links: readonly FooterLink[];
}

const COLUMNS: readonly FooterColumn[] = [
  {
    label: 'Product',
    links: [
      { label: 'How it works', href: '#how-it-works' },
      { label: 'Search', href: '#search' },
      { label: 'Integrate', href: '#integrate' },
      { label: 'Built with itself', href: '#built-with-itself' },
      { label: 'Source on GitHub', href: 'https://github.com/eddremonts86/ui-indexador' },
    ],
  },
];

const API_ENDPOINTS = [
  { label: '/health', href: '/health', note: 'counts and index status' },
  { label: '/facets', href: '/facets', note: 'kinds, types, layouts, features' },
  { label: 'registries', href: '/docs.html?doc=registries', note: 'ranked registries, read as a page' },
  { label: 'design gallery', href: '/docs.html?doc=index', note: 'layout patterns, read as a page' },
];

interface BrandMarkProps {
  className?: string;
}

const BrandMark = ({ className }: BrandMarkProps) => {
  return (
    <span aria-hidden className={cn('font-mono text-lg leading-none text-brand', className)}>&gt;_</span>
  );
};

const Footer03 = () => {
  return (
    <footer data-slot="footer" className="w-full border-t border-border bg-muted/10 p-2">
      <div className="pt-12 pb-2 md:pb-12">
        <div className="mx-auto max-w-6xl px-4">
          <div className="mb-8 grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-[1.6fr_1fr]">
            <div data-slot="footer-brand" className={ENTER}>
              <span className="mb-3 inline-flex items-center gap-2 text-base font-semibold tracking-tight text-foreground">
                <BrandMark />
                ui-indexador
              </span>
              <p className="mb-4 max-w-sm text-sm text-muted-foreground">
                An index of every shadcn registry item, searchable by meaning, for the agent that writes your UI. This page was built with it.
              </p>
            </div>

            {COLUMNS.map((column, index) => (
              <div key={column.label} data-slot="footer-column" style={stagger(index + 1)} className={ENTER}>
                <h3 className="mb-4 font-semibold text-foreground">{column.label}</h3>
                <ul className="space-y-3 text-sm">
                  {column.links.map((link) => (
                    <li key={link.label}>
                      <a
                        href={link.href}
                        className="text-muted-foreground transition-colors duration-150 hover:text-foreground"
                      >
                        {link.label}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div
            data-slot="footer-api"
            style={stagger(3)}
            className={cn(ENTER, 'mb-6 rounded-xl border border-border bg-card p-6')}
          >
            <p className="text-xs tracking-wider text-muted-foreground uppercase">Plain HTTP, no MCP needed</p>
            <h3 className="mt-2 text-lg font-semibold tracking-tight text-foreground">The same index over HTTP</h3>
            <p className="mt-1 max-w-xl text-sm text-muted-foreground">
              Runs on your machine at 127.0.0.1:3040. Every endpoint returns JSON or markdown.
            </p>
            <ul className="mt-5 grid gap-2 font-mono text-sm sm:grid-cols-2 lg:grid-cols-4">
              {API_ENDPOINTS.map((ep) => (
                <li key={ep.href}>
                  <a
                    href={ep.href}
                    className="flex flex-col rounded-md border border-border/60 px-3 py-2 text-foreground transition-colors duration-150 hover:border-brand/60 hover:text-brand"
                  >
                    {ep.label}
                    <span className="font-sans text-xs text-muted-foreground">{ep.note}</span>
                  </a>
                </li>
              ))}
            </ul>
          </div>

          <div
            data-slot="footer-ai-os"
            style={stagger(3)}
            className={cn(
              ENTER,
              'mb-10 flex flex-col gap-4 rounded-xl border border-brand/40 bg-brand/5 p-6 md:flex-row md:items-center md:justify-between',
            )}
          >
            <div>
              <p className="text-xs tracking-wider text-brand uppercase">Another project by the same author</p>
              <h3 className="mt-2 text-lg font-semibold tracking-tight text-foreground">AI-OS: the agent setup behind this page</h3>
              <p className="mt-1 max-w-xl text-sm text-muted-foreground">
                Skills, rules, memory and MCP servers, linked into every AI CLI on your machine with one command.
              </p>
            </div>
            <div className="flex shrink-0 flex-wrap gap-3 text-sm">
              <a
                href="#ai-os"
                className="rounded-md border border-border px-4 py-2 text-foreground transition-colors duration-150 hover:bg-muted"
              >
                Setup guide
              </a>
              <a
                href={AI_OS_URL}
                className="rounded-md bg-primary px-4 py-2 font-medium text-primary-foreground transition-opacity duration-150 hover:opacity-90"
              >
                Visit AI-OS
              </a>
            </div>
          </div>

          <div data-slot="footer-bottom" style={stagger(4)} className={cn(ENTER, 'border-t border-border/50 pt-8')}>
            <div className="flex flex-col items-center justify-between md:flex-row">
              <div className="mb-4 flex flex-col items-center gap-4 md:mb-0 md:flex-row">
                <p className="text-start text-sm text-muted-foreground">Indexed items belong to their authors under their own licences. Theme: tweakcn darkmatter (Apache-2.0).</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer03;
