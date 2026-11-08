# Design gallery

Real pages and registry blocks, captured at 1440x900 and measured, so a design starts from what proven
sites and components do instead of from memory. Look here before picking a
layout, and add to it whenever a design task researches new references.

- `sites/` holds real pages, as `<slug>-hero.jpg` (first screen) and `<slug>-full.jpg` (full page at 0.5 scale).
- `blocks/` holds registry components and templates, one capture each.
- Add one with `.venv/bin/python scripts/capture.py <url> <slug> [--dir blocks] [--wait ms] [--dark]`. It prints the
  measured row stub; fill in the pattern and the notes by hand.
- Captures are references, not assets. Never ship another site's design; take the pattern, not the look.
- The measurements are from `getBoundingClientRect` at capture time, and sites change. Each section says when it
  was captured.

## Patterns (2026-11-06, personal profile sites)

| Pattern | Sites | How it uses a 1440 screen |
|---|---|---|
| Single narrow column | emilkowal-ski, paco-me, antfu-me, jhey-dev, adamwathan-me | A 600–656 px column, so about 55% of the screen stays empty. Works only with very little content |
| Sticky identity left, content scrolls right | brittanychiang-com (reference), delba-dev, leerob-com | A 1184 container: a sticky 561 column with name, role, pitch, section nav and socials, next to a 607 column that scrolls |
| Measured column in a full-width frame | chanhdai-com, jhey-dev, www-joshwcomeau-com | Text stays at 768–1100 px, while grid rules or a banner run out to the edges |
| Full-bleed editorial | elliott-mangham-dev (restrained), stefanvitasovic-dev, gianlucagradogna-com, rauno-me | 1400+ px: multi-column fact bands, split screens, horizontal project tracks |

What reads as a personal profile:
- The name comes first.
- The voice is first person.
- Proof is named employers and projects in sentences or chips.
- A small photo (40–160 px).
- A dated timeline and dated writing.
- Contact is plain email or socials.

None of these sites use feature grids, testimonials or a pair of call-to-action buttons.

## sites/ (captured 2026-11-06)

| Slug | Hero content | Layout | Measured at 1440 | h1 | Colour |
|---|---|---|---|---|---|
| brittanychiang-com | Name, role, pitch, section nav, socials; no photo | Sticky identity left, scrolling right | Container 1184; left 561 (sticky), right 607 | 48px/700 | Dark navy, one teal accent |
| leerob-com | Handle, first-person bio (Default/Long toggle) | Text left, tall illustration right | Text column 600; content spans 49–1291 | 42px serif | White, monochrome |
| rauno-me | Name + role + employers sentence in a card | Full-bleed, scroll-driven horizontal cards | h1 box 771 | 32px | Grey, one yellow accent |
| emilkowal-ski | Name + "Design Engineer" small, "Today" status | Narrow centred column | main 644 | none | Off-white, monochrome |
| paco-me | Name, short pitch, past employer | Narrow column; lists split into 3 sub-columns | Text column 640 | 16px | White, monochrome, serif italics |
| www-joshwcomeau-com | Illustrated banner, hidden h1 | Articles + sidebar | Container 1100, article 627 | 32px hidden | Sky banner, several accents |
| chanhdai-com | Avatar, name, tagline, role, location, local time, contacts, GitHub heatmap | 768 column with blueprint rules out to the edges | Text column 766 | 32px | White, monochrome |
| adamwathan-me | 80px photo, name, nav, first-person bio | Narrow column, offset left | Text column 640 | 24px | White, monochrome |
| jhey-dev | Name, mono role, bio with proof links, doodle | Narrow column, grid fading out to the right | main 600 | 72px/300 | White, one red underline |
| antfu-me | Name, first-person intro, project chips | Narrow centred column, line art at the edges | Text column 656 | 36px/800 | White, coloured project logos |
| delba-dev | "Portfolio", job-seeking line, "Let's talk", About card with photo | Work list left, About card right | Text column 587; content 249–1169 | 30px serif | Warm off-white, monochrome |
| stefanvitasovic-dev | Giant name, role, bio, email (Awwwards SOTD 2025) | Full-bleed single screen, WebGL half | Content 1400 | 90px | Warm grey, one blue accent |
| elliott-mangham-dev | 5-column mono band: Intro, Position, Recognition, Brands, Connect; 40px headshot (Awwwards SOTD Dec 2025) | Full-bleed 5-column grid, project strip | Content 20–1400 | none | Near-black, purple dots |
| gianlucagradogna-com | Name, location, role over a B/W portrait (Awwwards SOTD Jan 2025) | Full-bleed split screen | main 1440, portrait 882 | 42px | Dark, photographic |

Notes on the captures:
- elliott-mangham-dev: the full-page capture shows its preloader; the hero was retaken after 9 s.
- stefanvitasovic-dev: the page does not scroll, so the full capture is the same screen.

## blocks/ (captured 2026-11-06, for a developer profile site)

"Fit" is fit for a precise, quiet senior-engineer profile that uses the full width (1 = poor, 5 = strong). A "(doc)" capture
is the registry docs page with the live preview in view.

| File | Registry / item | Licence | Layout at 1440 | Fit |
|---|---|---|---|---|
| ncdai-hero-01 | @ncdai hero-01 (chanhdai.com/preview/hero-01) | MIT | Headline, subcopy, 2 buttons and tech icons on the left; a golden-spiral line grid fills the right half; full-bleed hairlines | 5 |
| ncdai-experience-01 | @ncdai experience-01 | MIT | Company rows with collapsible roles (type, period, duration), bullets, mono chips, hairline grid | 5 |
| ncdai-work-experience (doc) | @ncdai work-experience | MIT | Same pattern as experience-01, narrower | 4 |
| ncdai-github-contributions (doc) | @ncdai github-contributions | MIT | Grayscale yearly heatmap with total and legend | 4 |
| ncdai-home, -full | chanhdai.com home | MIT | 768 column inside full-bleed blueprint hairlines, mono info grid, contribution graph | 3 |
| uil-portfolio-experience, -full | @ui-layouts portfolio-experience | MIT | Huge heading; each role is a 3-column row: company + impact, meta + stack chips, prose. Uses ~1150 px | 4 |
| uil-about-me | @ui-layouts about-me | MIT | 3 columns: tall portrait, prose + CTA, tilted photos | 2 |
| uil-work-experience, -full | @ui-layouts work-experience | MIT | Centred 650 px card timeline, then stat cards | 2 |
| uil-sticky-hero-section, -full | @ui-layouts sticky-hero-section | MIT | Tilted photo panel on scroll, gradient wordmark | 1 |
| uil-sticky-gallery, -full | @ui-layouts sticky-gallery | MIT | Dark 3-column photo grid with a sticky middle column | 1 |
| uil-timeline-animation (doc) | @ui-layouts timeline-animation | MIT | Scroll-reveal wrapper, not a layout | 2 |
| uil-about-experience, -full | @ui-layouts about-experience | MIT | Photo banner and collage, corporate | 1 |
| magicui-portfolio, -full | @magicui portfolio template | MIT | 620 px column: name + round photo, prose, dated work list, floating dock | 3 |
| magicui-hero-video-dialog (doc) | @magicui hero-video-dialog | MIT | Video thumbnail that opens a modal; a widget | 2 |
| cult-hero-color-panels (doc) | @cult-ui hero-color-panels | MIT | Split hero with a loud multicolour shader | 2 |
| cult-hero-dithering (doc) | @cult-ui hero-dithering | MIT | Split hero with a dithered spiral; one accent if recoloured | 3 |
| astryx-side-gallery | @astryx template-side-gallery | MIT | Asymmetric split: copy + stat row left, 3x3 photo collage right | 3 |
| astryx-gallery-hero | @astryx template-gallery-hero | MIT | Centred headline over 3 tall photos | 2 |
| astryx-centered-hero | @astryx template-centered-hero | MIT | Centred headline over one wide photo | 2 |
| reactbits-profile-card (doc) | @react-bits ProfileCard | NOASSERTION | Tilting holographic photo card | 1 |
| scb-heroes-composite, scb-hero-0N | @shadcnui-blocks hero-01..08 | MIT | Generic SaaS heroes, centred or split with an empty media slot | 2 |
| scb-profiles-composite, scb-profile-0N | @shadcnui-blocks profile-01..04 | MIT | Avatar cards, app-like | 2 |
| shadcn-portfolio-template, -full | akash3444/portfolio-template | check the repo | Pill nav, centred headline over a faint grid, ~770 px | 3 |

Not captured: magicui.design/docs/templates (404 at capture time; the template pages work); React Bits portfolio
templates (paid, pro.reactbits.dev).

## Registry survey (2026-11-06, developer profile site)

How it was done:
- `scripts/survey-registries.py` found 14,775 section items across 309 registries. 4,382 of them are hero,
  profile, about, experience or project items in 146 registries, and 4,062 had their source classified.
- Three reviewers then opened the galleries of those 146 registries, using sitemap URLs where they existed, and
  classified every block they saw: 442 blocks in 94 registries. The rows are in `survey/blocks-2026-11-06.csv`.
- The 41 blocks that scored fit 4–5 are in `blocks/` under their registry and item name. "Fit" means fit for a
  precise, quiet, full-width senior-engineer profile.

What the market looks like, as counted from the screenshots:

| Kind | Most common | Best fit (fit ≥ 4) |
|---|---|---|
| Hero (254) | centred text 84, split text + media 56, big-type editorial 25, shader/3D 24 | big-type editorial 5, text-only left 4. Centred and shader heroes almost never fit a profile |
| Experience (49) | vertical timeline 29, horizontal strip 8, accordion roles 6 | vertical timeline 8 (balick timeline-01: sticky heading + year rail), accordion roles 4 (ncdai/heyompatil experience-01) |
| Projects (44) | featured case study 10, card grid 9, list rows 8 | list rows 5 (ssych and bjork-ui project-index, tween-ui hover-reveal) |
| About / profile (63) | profile cards 22, fact band 7 | fact band (uiception portfolio-v2: identity + bio, then Notes / Projects / Experience in 3 columns) |

Overall:
- Fit scores ran 1: 136, 2: 171, 3: 94, 4: 36, 5: 5.
- Only 23 blocks show a person photo.
- 90 are full-bleed.

Stars do not predict fit. The best personal-portfolio sets (balick, uiception, heyompatil) have under 5 stars; ncdai is
the exception, with 2.4k.

Licences of the standouts:
- MIT: balick, uiception, heyompatil, ncdai, payload-components, uai, tween-ui, ui-layouts, cortexcn.
- No licence found, so check before use: ssych, bjork-ui, hairline, lema-ds, nusaiba, miseui, paceui.

## Extra survey (2026-11-06, sandbox renders)

Each item was installed with `shadcn add` into a scratch Vite + shadcn app and rendered there, so this covers items
with no preview page. 716 items were tried, 439 classified (`survey/blocks-extra.csv`), and 255 failed (render
errors, install errors, single UI parts, paywalled). Only blocks with fit 3 or more have an image, filed by kind under
`blocks/<kind>/` (hero, profile, about, experience, projects, testimonials, contact, navigation).

- Fit: 1: 171, 2: 196, 3: 56, 4: 14, 5: 2.
- Layouts: centred text 99, split text + media 75, full-bleed image 54, card grid 35, shader/3D 21, big-type
  editorial 14.

Strongest new finds:
- `experience/registrydirectory-shadcnblocks-experience1` (date, role and logo on hairline rows).
- `about/registrydirectory-beste-ui-about70` (an editorial year-by-year story).
- `profile/registrydirectory-shadcn-ui-blocks-portfolio-portfolio-about-and-skills-about-me`.
- `projects/registrydirectory-shadcn-ui-blocks-portfolio-portfolio-case-studies-accordion-expandable-case-studies`.
- `hero/flx-hero-05`, `hero/flx-hero-07` (monochrome big type).

Not covered yet:
- Hero is done; the other kinds were only partly reached.
- Testimonials, contact, footer and navigation have barely been started.

To resume, rerun the inventory with `scripts/survey-registries.py`, then render the remainder the same way.
