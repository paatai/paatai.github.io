# Build notes

Static HTML/CSS only. Shared stylesheet: `css/site.css`. Shared nav is duplicated on each page.

## Portrait

`images/paata.jpg` is a real JPEG portrait (copied from `/workspace/paatai-photo.jpg`, about 20 KB). The Google Sites `googleusercontent` photo URL returned HTTP 403, so that original file was used instead of a monogram placeholder.

## Page list

Root:

- `index.html` — hero, research sentence, awards, students, VAPs, organization teaser, 2026 papers
- `papers.html` — 74 papers from the Google home page, grouped by year newest first
- `talks.html` — talks 2012–2026, including 2024 (no traveling due to childbirth)
- `teaching.html` — courses with cleaned UCI / Canvas / NCSU URLs
- `math211.html` — MATH 211A (Spring 2020) notes and syllabus
- `students.html` — UCI students and VAPs with paper links
- `slides.html` — talk slides
- `coauthors.html` — alphabetical co-authors (Joris Roos, not Joos)
- `organization.html` — HIM 2024, summer/fall schools, AIM, Clay, Math CEO pentominoes

Schools (`schools/`):

- Quantum 2021: overview, participants, topics, schedule, pictures
- Learning 2022: overview, participants, topics, pictures, slides (schedule is an external Google Sheet)
- Heat 2023: overview, participants, topics, schedule, pictures

## Could not transfer

- School photograph files themselves: Google user-content image URLs return 403. Picture pages link to the original Google Site galleries (`/pic-quantum`, `/pic-learning`, `/pic-heatflow`).
- 2022 Mar. AGT&A Seminar: the dump marks `[video]` but no unique video URL was captured (IPAM and the three ICERM talks have videos).
- Nika Areshidze: no homepage or paper links in the dump.
- Heat school: a Slides heading existed on the Google page with no linked slides page in the scrape.
- MathJax: paper titles use HTML (`L<sup>p</sup>`) so they render without JavaScript.

## Design

Warm paper background `#f6f1e8`, ink navy `#1a2744`, rust `#b44a24`. Fraunces + Source Sans 3. Hero with name on the left and a rounded-rectangle portrait on the right; sticky top nav; no left circular sidebar; no accordion toggles; footer copyright only.
