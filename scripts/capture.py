#!/usr/bin/env python3
"""Add a page to the design gallery: first screen + full page, compressed, with measurements.

  .venv/bin/python capture.py <url> <slug> [--dir sites|blocks] [--wait 3000] [--dark]

Needs Playwright: .venv/bin/pip install playwright && .venv/bin/playwright install chromium

Writes data/<dir>/<slug>-hero.jpg (1440x900) and <dir>/<slug>-full.jpg (0.5 scale, height capped),
then prints one data/INDEX.md row stub with the measured content width and h1 size. Fill in the
pattern and the notes by hand: a measurement is evidence, a description is judgement.
"""

import argparse
import subprocess
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
MEASURE = """() => {
  const vis = e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 ? r : null; };
  const main = document.querySelector('main') || document.body;
  const text = [...document.querySelectorAll('p, li, h2, h3')].map(vis).filter(Boolean)
    .reduce((a, r) => r.width > a.width ? r : a, {width: 0, left: 0});
  const h1 = document.querySelector('h1');
  return { main: Math.round(vis(main)?.width || 0), text: Math.round(text.width), textX: Math.round(text.left),
           h1: h1 ? getComputedStyle(h1).fontSize : 'none', bg: getComputedStyle(document.body).backgroundColor };
}"""


def jpeg(png, out):
    subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "70", str(png), "--out", str(out)],
                   check=True, capture_output=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("slug")
    ap.add_argument("--dir", default="sites", choices=["sites", "blocks"])
    ap.add_argument("--wait", type=int, default=3000, help="ms after load, for intro animations")
    ap.add_argument("--dark", action="store_true")
    a = ap.parse_args()
    out = HERE.parent / "data" / a.dir
    out.mkdir(exist_ok=True)
    with sync_playwright() as p, tempfile.TemporaryDirectory() as tmp:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1440, "height": 900}, color_scheme="dark" if a.dark else "light")
        pg.goto(a.url, wait_until="load", timeout=45000)
        pg.wait_for_timeout(a.wait)
        m = pg.evaluate(MEASURE)
        pg.screenshot(path=f"{tmp}/hero.png")
        full = b.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=0.5,
                          color_scheme="dark" if a.dark else "light")
        full.goto(a.url, wait_until="load", timeout=45000)
        full.wait_for_timeout(a.wait)
        h = min(full.evaluate("document.documentElement.scrollHeight"), 9000)
        full.screenshot(path=f"{tmp}/full.png", clip={"x": 0, "y": 0, "width": 1440, "height": h}, full_page=True)
        b.close()
        jpeg(f"{tmp}/hero.png", out / f"{a.slug}-hero.jpg")
        jpeg(f"{tmp}/full.png", out / f"{a.slug}-full.jpg")
    print(f"| {a.slug} | {a.url} | main {m['main']} · text col {m['text']} (x{m['textX']}) | h1 {m['h1']} | {m['bg']} | PATTERN | NOTES |")


if __name__ == "__main__":
    main()
