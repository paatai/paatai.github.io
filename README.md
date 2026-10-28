# paatai.github.io

Personal academic website of [Paata Ivanisvili](https://www.math.uci.edu/), Professor of Mathematics at the University of California, Irvine.

This repository is the source for **https://paatai.github.io** (GitHub user **paatai**).

## Publish on GitHub Pages

1. Create a **public** repository named `paatai/paatai.github.io`.
2. Push this folder to the `main` branch (the site root is the repository root: `index.html` must sit at the top level).
3. On GitHub: **Settings → Pages → Build and deployment**.
4. Set **Source** to **Deploy from a branch**, branch **main**, folder **/ (root)**.
5. After a minute or two the site is served at https://paatai.github.io.

No Jekyll build is required; these are plain static files. A `.nojekyll` file is included so GitHub Pages will not run Jekyll.

Content was transferred from the Google Site https://sites.google.com/view/paata/home (papers, talks, teaching, students, slides, co-authors, and summer/fall schools).

## Adding an AI proof

1. Put the files in a new folder `ai-proofs/<slug>/` (PDF, plus TeX / code zip if any; each file under 100 MB).
2. Append one object to `ai-proofs/entries.json` with the next number `n`:
   `{"n": 19, "date": "YYYY-MM-DD", "title": "...", "status": "refereed | partial result | raw draft | polished", "line": "one honest sentence: what is proved, what is open", "pdf": "<slug>/<file>.pdf", "files": [["TeX", "<slug>/<file>.tex"], ["code", "<slug>/code.zip"]]}`
   Paths are relative to `ai-proofs/`. Use `refereed` only if an independent referee rated the proof valid.
3. Run `python3 tools/site.py ai-proofs` and commit. The page lists entries newest first; numbers never change, and each entry has a permanent link `ai-proofs/#<n>`. The script first checks every entry (all fields present, a whole-number `n` used once, a real `YYYY-MM-DD` date, a known status, `files` as label/path pairs, every file present); if anything is wrong it prints what and leaves the page unchanged.

## Navigation

The primary nav is duplicated on every page. To change it, edit `NAV` in `tools/site.py` and run `python3 tools/site.py nav`; it rewrites every page with the right `../` prefix and `aria-current`. On wide screens `css/site.css` lays the eleven items out in six columns, i.e. rows of six and five (`repeat(6, auto)` under `nav.primary ul`); revisit that if the number of items changes. Up to 660px wide the items wrap in balanced rows instead, and the `clamp()` font size and padding in that media query keep them to three rows on phones from 320px up; check a 375px-wide screen after adding an item.

The year links under the title of `talks.html` are rebuilt by the same command from the year headings (`<h2 class="year" id="t2027">2027</h2>`), so after adding a new year, run `python3 tools/site.py nav`.

## Clock on the home page

The home page shows `clock/` in an iframe as `clock/index.html#embed=1`, the last thing on the page: full width below the header, down to the bottom of the screen. The clock draws on `#000`, the same black as the site, so the iframe has no visible edge. With `embed=1` the clock:

- lets vertical swipes scroll the page and pinches zoom it, while a sideways drag turns a ball; a touch that rests on a ball for a quarter of a second grabs it, and that drag turns the ball in any direction (the mouse drags as before, and the wheel scrolls the page);
- stacks HH over MM, with the seconds below and bigger balls, when its box is tall and narrow (a phone held upright);
- pauses while scrolled out of view, and snaps instead of rotating when the visitor prefers reduced motion.

Opened directly, `clock/` keeps its one-row layout.
