# Galaxy hunt

Twelve stars from public sky surveys, including Gaia DR3, that seem to have brightened, faded or wobbled in ways that are not already in the published record. Every probability on the pages is an estimate of the chance that the claim is real and previously unrecorded; none has been checked by outside experts.

- `index.html`: one intro paragraph, then three lists numbered 1 to 12 in display order, highest probability first inside each list. Unexplained changes are 1 to 6, possible new microlensing events are 7 to 10, and possible hidden companions are 11 and 12.
- `<folder>/index.html`: one page per candidate. The folder name starts with that display number and keeps the Gaia DR3 id (`3-fading-4296242940002232704`).
- `finder.jpg`, `lightcurve.jpg`, and, where they exist, `decam_i_epochs.jpg`, `decam_z_epochs.jpg` and `epochs_r.jpg`: the figures, next to the page that uses them. They are JPEGs made from the original PNG figures, flattened onto white, kept under about 400 KB, with the original pixel size so the labels stay readable.

The pages use the same header, footer and figure styles as the Mars candidates (`galaxy-fig`, `galaxy-list`, `galaxy-facts` in `css/site.css`).

## Adding a candidate

1. Put its JPEGs in a new folder `vibe-projects/galaxy/<folder>/`.
2. Copy the newest candidate folder and replace the title and the text between `<div class="page" id="content">` and the footer. Leave the header and the footer as they are. Say only what that candidate’s notes say.
3. Add one line to the right list in `index.html`. The number is written into the line, and the lists stay sorted by probability. The probability is the text of the `galaxy-rating` element on that line, and the same text in the `galaxy-rating` element under the title of the candidate’s page, written `about 60%`. Those two strings are the only places the probability is stated.
4. From the repository root, run `python3 tools/site.py nav`. Besides the nav and the footer, it rewrites the previous/next links at the bottom of every Galaxy hunt page, following the order of the lists in `index.html`.
