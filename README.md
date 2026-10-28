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
3. Run `python3 tools/site.py ai-proofs` and commit. The page lists entries newest first; numbers never change.

## Navigation

The primary nav is duplicated on every page. To change it, edit `NAV` in `tools/site.py` and run `python3 tools/site.py nav`; it rewrites every page with the right `../` prefix and `aria-current`.
