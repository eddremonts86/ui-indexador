'use client';

import * as React from 'react';
import { ArrowRight, Check, CircleAlert, CircleCheck, X } from 'lucide-react';

import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group';

const ENTER =
  'animate-in fade-in slide-in-from-bottom-4 duration-500 ease-[cubic-bezier(0.22,1,0.36,1)] fill-mode-both motion-reduce:animate-none';
// Replays when a panel leaves display:none on small screens.
const SWAP =
  'animate-in fade-in slide-in-from-bottom-1 duration-250 ease-[cubic-bezier(0.22,1,0.36,1)] fill-mode-both motion-reduce:animate-none';

const stagger = (index: number): React.CSSProperties => ({ animationDelay: `${index * 60}ms` });

const VIEW_VALUES = ['before', 'after'] as const;

type View = (typeof VIEW_VALUES)[number];

const isView = (value: unknown): value is View => VIEW_VALUES.some((option) => option === value);

const BEFORE = [
  'The agent writes a pricing table from what it half-remembers',
  'No keyboard handling, no right-to-left, dark mode bolted on late',
  'You review 300 lines that a registry already had, better',
  'Next week it writes a slightly different one for the next page',
] as const;

const AFTER = [
  'The agent asks the index for "pricing table with a monthly/yearly toggle"',
  'It gets ranked candidates, each with its licence and install command',
  'One npx shadcn add puts a proven component in your repo',
  'You review content and tokens, not structure somebody invented'
] as const;

const OUTCOMES = [
  { value: '1 query', label: 'from a description to ranked candidates' },
  { value: '1 command', label: 'to install the one you choose' },
  { value: '0 lines', label: 'of component code stored by the index' },
] as const;

const Comparison03 = () => {
  const [view, setView] = React.useState<View>('after');

  return (
    <section data-slot="comparison" className="bg-background py-20 sm:py-28" aria-labelledby="comparison-03-heading">
      <div className="mx-auto w-full max-w-5xl px-4">
        <div data-slot="comparison-header" className="max-w-2xl">
          <p className={cn(ENTER, 'text-xs text-muted-foreground uppercase')}>Why it exists</p>
          <h2
            id="comparison-03-heading"
            style={stagger(1)}
            className={cn(ENTER, 'mt-3 text-3xl font-semibold tracking-tight sm:text-4xl')}
          >
            The same pricing table, built two ways
          </h2>
        </div>

        <ToggleGroup
          data-slot="comparison-switch"
          type="single"
          variant="outline"
          value={view}
          onValueChange={(next) => {
            if (isView(next)) setView(next);
          }}
          aria-label="Show"
          style={stagger(2)}
          className={cn(ENTER, 'mt-10 w-full md:hidden')}
        >
          <ToggleGroupItem value="before" className="flex-1">
            Before
          </ToggleGroupItem>
          <ToggleGroupItem value="after" className="flex-1">
            After
          </ToggleGroupItem>
        </ToggleGroup>

        <div
          data-slot="comparison-panels"
          style={stagger(3)}
          className={cn(
            ENTER,
            'mt-4 grid gap-px overflow-hidden rounded-md border border-border bg-border md:mt-12 md:grid-cols-2',
          )}
        >
          <div
            data-slot="comparison-before"
            className={cn('bg-background p-7 sm:p-8 md:block', view === 'before' ? 'block' : 'hidden')}
          >
            <div className={SWAP}>
              <div className="flex items-center gap-2">
                <CircleAlert aria-hidden className="size-4 text-muted-foreground" />
                <h3 className="text-xs text-muted-foreground uppercase">From memory</h3>
              </div>
              <ul className="mt-6 flex flex-col gap-4">
                {BEFORE.map((item) => (
                  <li key={item} className="flex gap-3 text-sm text-muted-foreground">
                    <X aria-hidden className="mt-0.5 size-4 shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div
            data-slot="comparison-after"
            className={cn('bg-card p-7 sm:p-8 md:block', view === 'after' ? 'block' : 'hidden')}
          >
            <div className={SWAP}>
              <div className="flex items-center gap-2">
                <CircleCheck aria-hidden className="size-4" />
                <h3 className="text-xs uppercase">From the index</h3>
              </div>
              <ul className="mt-6 flex flex-col gap-4">
                {AFTER.map((item) => (
                  <li key={item} className="flex gap-3 text-sm">
                    <Check aria-hidden className="mt-0.5 size-4 shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        <div
          data-slot="comparison-outcomes"
          style={stagger(4)}
          className={cn(ENTER, 'mt-10 flex flex-col items-start justify-between gap-6 sm:flex-row sm:items-center')}
        >
          <dl className="flex flex-wrap items-baseline gap-x-8 gap-y-3">
            {OUTCOMES.map((outcome) => (
              <div key={outcome.value} className="flex items-baseline gap-2">
                <dt className="text-xs text-muted-foreground">{outcome.label}</dt>
                <dd className="order-first text-sm font-semibold tracking-tight">{outcome.value}</dd>
              </div>
            ))}
          </dl>
          <Button asChild variant="outline" className="group">
            <a href="#built-with-itself">
              See how this page was built
              <ArrowRight className="size-3.5 transition-transform duration-150 group-hover:translate-x-0.5 rtl:rotate-180 rtl:group-hover:-translate-x-0.5" />
            </a>
          </Button>
        </div>
      </div>
    </section>
  );
};

export default Comparison03;
