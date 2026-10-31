# Mars candidates

- `index.html`: the intro (what was searched, how, caveat, credits) and the list of candidates, one line each in candidate order. The `id`s on the first fourteen lines are the section anchors of the old one-page version, so old links such as `index.html#arsia-sulci` still land on the right line. The old page's two group headings, `#strong` and `#promising`, are ids on the links of candidates 4 and 11, where those groups began. New lines need no `id`.
- `candidate-NN/index.html`: one page per candidate, `candidate-01` to `candidate-14`.
- `*.jpg`: the figures, all in this folder; candidate pages use them as `../<file>.jpg`. The existing file names keep the search's lead numbers, which are not the candidate numbers (for example `lead16_…` belongs to candidate 10).

## Adding a candidate

1. Put its figures in this folder, for example `candidate15_<place>_pair_web.jpg`, `…_epochs_web.jpg` and `…_context_web.jpg` (and `…_hirise_web.jpg` if there is a HiRISE view).
2. Copy the newest candidate folder, for example `candidate-14/` to `candidate-15/`. In the copy, change the `<title>` and replace everything between `<div class="page" id="content">` and the `</div>` just before the footer with the template below. Leave the header and the footer as they are.
3. Add one line at the end of the list in `index.html`. The list has no automatic numbering: the number is written into the line, so it always matches the candidate's page. The rating is `Strong` or `Promising` (shown in capitals) and, with the confidence, is the same as on the candidate's page:

   ```html
   <li><a href="candidate-15/index.html">Candidate 15: Place name</a> <span class="mars-meta">12.345°&nbsp;N, 67.890°&nbsp;E · <span class="mars-rating">Strong</span> · roughly&nbsp;70%</span></li>
   ```

4. From the repository root, run `python3 tools/site.py nav`. Besides the nav and the footer, it rewrites the previous/next links at the bottom of every candidate page, so candidate 14 gets its link to 15.

The Mars entry in `vibe-projects/index.html` gives the number of candidates ("Fourteen dark spots"); update it too.

## Page template

`mars-wide` lets a figure fill the column; without it a figure is at most 32rem wide, so a tall strip fits on the screen. Use it for the before/after pair, for epoch strips with three images per row, and for HiRISE views. `width` and `height` are the image's own pixel size. Only the first figure loads without `loading="lazy"`. Optional extras: a `Nearby` row naming a candidate close by, and a HiRISE figure after the context view.

```html
<p><a href="../index.html">← Possible new impact sites on Mars</a></p>
<h1 class="page-title">Candidate 15: Place name</h1>
<p class="mars-tag">Strong · roughly 70%</p>
<figure class="mars-fig mars-wide"><img src="../candidate15_place_pair_web.jpg" width="1600" height="983" alt="What the two close-ups show, for readers who cannot see them.">
<figcaption>The same 600 × 600 m in Month YYYY and Month YYYY, under the same sun. NASA/JPL-Caltech/MSSS.</figcaption></figure>
<p><strong>What changed.</strong> What appeared, how big it is, and between which dates.</p>
<p><strong>Why it may be a new impact.</strong> The evidence: absent under the same sun, unchanged in later images, its shape.</p>
<dl class="mars-facts">
<dt>Location</dt><dd>12.345°&nbsp;N, 67.890°&nbsp;E</dd>
<dt>Absent</dt><dd>Dates of the images without the spot</dd>
<dt>Present</dt><dd>Dates of the images with the spot</dd>
<dt>Size</dt><dd>Dark spot about 40 m across</dd>
<dt>Confidence</dt><dd>Strong candidate; roughly 70% that it is a new impact.</dd>
<dt>Caveat</dt><dd>Its own weak points, if any. Like every candidate here, it is unconfirmed: see the <a href="../index.html#caveat">caveat</a>.</dd>
</dl>
<figure class="mars-fig mars-wide"><img src="../candidate15_place_epochs_web.jpg" width="1600" height="1244" loading="lazy" alt="What the epoch images show.">
<figcaption>All N CTX images of the same 2 × 2 km patch, YYYY to YYYY. NASA/JPL-Caltech/MSSS.</figcaption></figure>
<figure class="mars-fig"><img src="../candidate15_place_context_web.jpg" width="1600" height="1676" loading="lazy" alt="What the wider view shows.">
<figcaption>A 12 × 12 km view. NASA/JPL-Caltech/MSSS.</figcaption></figure>
<p class="mars-pager"><a href="../index.html">All candidates</a></p>
```
