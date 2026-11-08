import type * as React from 'react';

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
  {
    label: 'API',
    links: [
      { label: 'Health', href: '/health' },
      { label: 'Facets', href: '/facets' },
      { label: 'Registries', href: '/registries.md' },
      { label: 'Design notes', href: '/index.md' },
    ],
  },
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
          <div className="mb-8 grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-[1.6fr_1fr_1fr]">
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

          <div data-slot="footer-bottom" style={stagger(3)} className={cn(ENTER, 'border-t border-border/50 pt-8')}>
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
