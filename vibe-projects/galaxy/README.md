# Galaxy hunt

Fifty-eight candidates from public sky surveys, including Gaia DR3: stars, and one star-like spot on old photographic plates, that seem to have brightened, faded or wobbled in ways that are not already in the published record. Every probability on the pages is an estimate of the chance that the claim is real and previously unrecorded; none has been checked by outside experts. Candidate 58's dimming has already been published, so its rating text is `already published` instead of a percentage.

- `index.html`: one intro paragraph, then four lists, highest probability first inside each list. Candidates are numbered 1, 2, 3 and so on in the order they appear on the page: unexplained changes are 1 to 8, possible new microlensing events are 9 to 12, possible hidden companions are 13 to 23, and stars that dimmed for months are 24 to 58.
- `<folder>/index.html`: one page per candidate. The folder name starts with that display number and keeps the Gaia DR3 id (`3-fading-4296242940002232704`, `24-dimming-3062085079575847296`).
- `finder.jpg`, `lightcurve.jpg`, and, where they exist, `decam_i_epochs.jpg`, `decam_z_epochs.jpg`, `epochs_r.jpg`, `ztf_before_during.jpg`, `tess.jpg`, `orbit.jpg` and `cutouts.jpg`: the figures, next to the page that uses them. They are JPEGs made from the original PNG figures, flattened onto white, kept under about 400 KB (the densest light curve, candidate 25's, is about 450 KB, and candidate 55's twenty-sector TESS figure is about 590 KB), with the original pixel size so the labels stay readable. The bold title line of each finder chart and light curve gives the display number and the probability, so it has to be redrawn if either changes. Where the title of another figure starts with a number, it is the display number too.

The pages use the same header, footer and figure styles as the Mars candidates (`galaxy-fig`, `galaxy-list`, `galaxy-facts` in `css/site.css`).

## Adding a candidate

1. Put its JPEGs in a new folder `vibe-projects/galaxy/<folder>/`.
2. Copy the newest candidate folder and replace the title and the text between `<div class="page" id="content">` and the footer. Leave the header and the footer as they are. Say only what that candidate’s notes say.
3. Add one line to the right list in `index.html`. The lists stay sorted by probability, and the numbers always run 1, 2, 3 and so on down the page, so a candidate inserted in the middle takes the number of its position and every later candidate moves up by one: rename those folders, and update the numbers in their titles, in the lines of `index.html`, in cross-references on other pages and in the figure titles. Leave a short redirect page in each old folder so old links keep working. The probability is the text of the `galaxy-rating` element on that line, and the same text in the `galaxy-rating` element under the title of the candidate’s page, written `about 60%`. Those two strings are the only places the probability is stated.
4. From the repository root, run `python3 tools/site.py nav`. Besides the nav and the footer, it rewrites the previous/next links at the bottom of every Galaxy hunt page, following the order of the lists in `index.html`.
