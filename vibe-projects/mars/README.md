# Mars candidates

- `index.html`: the intro (what was searched, how, caveat, credits) and the list of candidates, one line each, numbered 1 to 166. Candidate N is lead N of the hunt, the number printed on its figures, so the list is in the order the search found them. The `id`s on fourteen of the lines (for example `#arsia-sulci` on candidate 1) are the section anchors of the old one-page version, so old links such as `index.html#arsia-sulci` still land on the right line; the old page's two group headings, `#strong` and `#promising`, are ids on the links of candidates 4 and 6, where those groups began.
- `candidate-NNN/index.html`, with a three-digit number: one page per candidate, `candidate-001` to `candidate-166`.
- `candidate-NN/index.html`, with a two-digit number (`candidate-01` to `candidate-90`): redirects from the numbering used until November 2026, when the candidates were numbered in the order they were added to the site. Each sends the visitor to the same lead's page under its new number. `tools/site.py nav` leaves them alone. Do not reuse these folder names.
- `candidates.csv`: the hunt's final list, unchanged: the 166 leads (`candidate_id` L1 to L166) and the 339 candidates it rejected or found to be already known. Every position, date, size, rating and probability on the pages comes from it.
- `*.jpg`: the figures, all in this folder; candidate pages use them as `../<file>.jpg`. Each file name starts with the lead number and the hunt's short name for the place, as in the CSV's `figures` column: `leadN_<place>_<kind>_web.jpg`. The kinds are `pair` (before/after close-up), `epochs` (every CTX image of the 2 × 2 km patch), `context` (12 × 12 km), `zoom`, `hirise`, `moc_2002`, and for the 35 candidates of the independent review `check`, `hirise_check` and `tail_check`. The one exception is `lead1_control_hirise_targeted_site_web.jpg`, the sanity check on candidate 1's page.

## Checking the pages

From the repository root, run `python3 tools/check_mars.py`. It compares every line of the list and every candidate page with `candidates.csv` (number, title and place, coordinates to three decimals, rating, probability, the dates and number of images without and with the spot, size, what the page says about HiRISE, and that every figure exists, belongs to the lead and has the right size), checks the counts and the lists of candidates in the intro of `index.html` (they are marked `<span data-count="…">` and `<span data-list="…">`, so keep those spans when rewording the intro), the previous/next links and every link on the Mars pages and on `vibe-projects/index.html`, and ends with a line such as "166 of 166 lead pages pass". It exits with status 1 if anything is wrong. With `--ocr` it also reads the lead number printed on every figure (it needs the `tesseract` program).

## Adding or changing a candidate

1. Put its figures in this folder, named as above, for example `lead167_<place>_pair_web.jpg`, `…_epochs_web.jpg` and `…_context_web.jpg` (and `…_hirise_web.jpg` if there is a HiRISE view). The lead must be in `candidates.csv`.
2. Copy the newest candidate folder, for example `candidate-166/` to `candidate-167/`. In the copy, change the `<title>` and replace everything between `<div class="page" id="content">` and the `</div>` just before the footer with the template below. Leave the header and the footer as they are.
3. Add one line at the end of the list in `index.html`. The list has no automatic numbering: the number is written into the line, so it always matches the candidate's page. The title, rating (`Strong`, `Promising` or `Weak`, shown in capitals) and probability are the same as on the candidate's page, and so are the coordinates, except that the list gives the east longitude only (the page adds the west longitude in brackets east of 180° E):

   ```html
   <li><a href="candidate-167/index.html">Candidate 167: Place name</a> <span class="mars-meta">12.345°&nbsp;N, 67.890°&nbsp;E · <span class="mars-rating">Strong</span> · roughly&nbsp;70%</span></li>
   ```

4. From the repository root, run `python3 tools/site.py nav`. Besides the nav and the footer, it rewrites the previous/next links at the bottom of every candidate page, so candidate 166 gets its link to 167.
5. Run `python3 tools/check_mars.py` and fix whatever it reports.

The Mars entry in `vibe-projects/index.html` says the hunt is finished (166 leads: 80 strong, 81 promising, 5 weak). Update it, and the counts in the intro of `index.html`, when that changes.

## Page template

Write the numbers exactly as in `candidates.csv`: the coordinates rounded to three decimals (and, east of 180° E, the west longitude in brackets), the rating, `p_new_impact` as "roughly N%", every date of the images the CSV counts without the spot (the last is `last_absent`) and with it (the first is `first_present`), and every number of `size_m`. When the CSV's `hirise` field starts with "none", the caveat ends with the sentence below, with the distance from that field; otherwise it says which HiRISE images cover the spot and when.

`mars-wide` lets a figure fill the column; without it a figure is at most 32rem wide, so a tall strip fits on the screen. Use it for the before/after pair, for epoch strips with three images per row (five or more images) or a single row (two), and for HiRISE, zoom and check figures. `width` and `height` are the image's own pixel size. Only the first figure loads without `loading="lazy"`. The pair caption says "under a similar sun" only when the figure itself says so. Optional extras: a `Nearby` row naming a candidate close by, a HiRISE figure after the context view, and an independent check figure (`mars-wide`, caption starting `<strong>Independent check.</strong>`) after that, followed by any further figures of the check, just before the previous/next links.

```html
<p><a href="../index.html">← Possible new impact sites on Mars</a></p>
<h1 class="page-title">Candidate 167: Place name</h1>
<p class="mars-tag">Strong · roughly 70%</p>
<figure class="mars-fig mars-wide"><img src="../lead167_place_pair_web.jpg" width="1600" height="983" alt="What the two close-ups show, for readers who cannot see them.">
<figcaption>The same 500 × 500 m in Month YYYY and Month YYYY, under a similar sun. The arrow marks the new spot. NASA/JPL-Caltech/MSSS.</figcaption></figure>
<p><strong>What changed.</strong> What appeared, how big it is, and between which dates.</p>
<p><strong>Why it may be a new impact.</strong> The evidence: absent in earlier images that would have shown it, unchanged in later images, its shape.</p>
<dl class="mars-facts">
<dt>Location</dt><dd>12.345°&nbsp;N, 67.890°&nbsp;E</dd>
<dt>Absent</dt><dd>Dates of the images without the spot</dd>
<dt>Present</dt><dd>Dates of the images with the spot</dd>
<dt>Size</dt><dd>Dark spot about 40 m across</dd>
<dt>Confidence</dt><dd>Strong candidate: roughly 70% likely to be a new impact.</dd>
<dt>Caveat</dt><dd>Its own weak points, if any. No image from the high-resolution HiRISE camera covers it; the nearest ends 12 km away. Like every candidate here, it is unconfirmed: see the <a href="../index.html#caveat">caveat</a>.</dd>
</dl>
<figure class="mars-fig"><img src="../lead167_place_epochs_web.jpg" width="1600" height="1866" loading="lazy" alt="What the epoch images show.">
<figcaption>Four CTX images of the same 2 × 2 km patch, YYYY to YYYY. NASA/JPL-Caltech/MSSS.</figcaption></figure>
<figure class="mars-fig"><img src="../lead167_place_context_web.jpg" width="1600" height="1676" loading="lazy" alt="What the wider view shows.">
<figcaption>A 12 × 12 km view from Month YYYY. The dashed box is the 2 × 2 km patch. NASA/JPL-Caltech/MSSS.</figcaption></figure>
<p class="mars-pager"><a href="../index.html">All candidates</a></p>
```
