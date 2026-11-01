# Galaxy hunt

Nine stars from an automated search of public sky surveys, including Gaia DR3, for brightness changes that are not already in the published record. Every rating on the pages is the search’s own.

- `index.html`: one intro paragraph (what was searched, and that the ratings are self-vetted) and the list of candidates. Candidates 1, 2, 15, 16, 17, 18 and 19 come first. Candidates 3 and 4 are weak and stay at the end, under their own heading.
- `<folder>/index.html`: one page per candidate. The folder names are the search’s names.
- `finder.jpg`, `lightcurve.jpg`, and, where the search made them, `decam_i_epochs.jpg`, `decam_z_epochs.jpg` and `epochs_r.jpg`: the figures, next to the page that uses them. They are JPEGs made from the search’s PNGs, flattened onto white, kept under about 400 KB, with the original pixel size so the labels stay readable.

The pages use the same header, footer and figure styles as the Mars candidates (`galaxy-fig`, `galaxy-list`, `galaxy-facts` in `css/site.css`).

## Adding a candidate

1. Put its JPEGs in a new folder `vibe-projects/galaxy/<folder>/`.
2. Copy the newest candidate folder and replace the title and the text between `<div class="page" id="content">` and the footer. Leave the header and the footer as they are. Say only what that candidate’s notes say.
3. Add one line to the list in `index.html`, in the order the page should be read. The number is written into the line. The rating is `Promising`, `Promising (as a new microlensing event)` or `Weak`, and it matches the candidate’s page.
4. From the repository root, run `python3 tools/site.py nav`. Besides the nav and the footer, it rewrites the previous/next links at the bottom of every Galaxy hunt page, following the order of the lists in `index.html`.
