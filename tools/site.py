#!/usr/bin/env python3
"""Site maintenance.  Run from the repo root.

  python3 tools/site.py nav        rewrite the primary nav and the footer on every page, the year links on talks.html
                                   and the previous/next links on the Mars and Galaxy hunt candidate pages
  python3 tools/site.py ai-proofs  rebuild ai-proofs/index.html from ai-proofs/entries.json
  python3 tools/site.py all        both
"""
import html, json, os, re, sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAV = [("Home", "index.html"), ("Papers", "papers.html"), ("Talks", "talks.html"),
       ("Teaching", "teaching.html"), ("Students", "students.html"), ("Slides", "slides.html"),
       ("Co-authors", "coauthors.html"), ("Organization", "organization.html"), ("Awards", "awards.html"),
       ("Vibe projects", "vibe-projects/index.html"), ("Vibe proofs", "ai-proofs/index.html")]
SKIP = ("clock/", "3dpoints/")          # stand-alone pages without the site header
FOOTER = ('<footer class="site">\n'
          '  <p>This site was created with AI and is maintained by the author’s assistants.</p>\n'
          '</footer>')                   # the hairline above the sentence is footer.site's top border in css/site.css


def current(rel):
    if rel.startswith("schools/"): return "organization.html"
    if rel.startswith("vibe-projects/"): return "vibe-projects/index.html"
    if rel.startswith("ai-proofs/"): return "ai-proofs/index.html"
    if rel == "math211.html": return "teaching.html"
    return rel


def nav_html(rel):
    pre = "../" * rel.count("/")
    cur = current(rel)
    items = "".join('<li><a href="%s%s"%s>%s</a></li>' % (pre, h, ' aria-current="page"' if h == cur else "", t)
                    for t, h in NAV)
    return '<nav class="primary" aria-label="Primary"><ul>%s</ul></nav>' % items


def is_redirect(path):
    with open(path, encoding="utf-8") as fh:
        return 'http-equiv="refresh"' in fh.read()


def pages():
    for d, _, fs in os.walk(ROOT):
        if "/.git" in d: continue
        for f in fs:
            if f.endswith(".html"):
                rel = os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, "/")
                if not rel.startswith(SKIP) and not is_redirect(os.path.join(ROOT, rel)): yield rel   # redirects of old URLs have no header


def fix_nav():
    n = 0
    for rel in sorted(pages()):
        p = os.path.join(ROOT, rel); s = open(p, encoding="utf-8").read()
        t, k = re.subn(r'<nav class="primary" aria-label="Primary">.*?</nav>', lambda m: nav_html(rel), s, flags=re.S)
        if k != 1: print("WARNING: %d navs in %s" % (k, rel)); continue
        if t != s: open(p, "w", encoding="utf-8").write(t); n += 1
    print("nav updated on %d pages" % n)


def fix_footer():
    n = 0
    for rel in sorted(pages()):
        p = os.path.join(ROOT, rel); s = open(p, encoding="utf-8").read()
        t, k = re.subn(r'<footer class="site">.*?</footer>', lambda m: FOOTER, s, flags=re.S)
        if k == 0: t, k = re.subn(r'(?=</article>)', lambda m: FOOTER + "\n\n", s)   # a page without one gets it last in the folio
        if k != 1: print("WARNING: %d footers in %s" % (k, rel)); continue
        if t != s: open(p, "w", encoding="utf-8").write(t); n += 1
    print("footer updated on %d pages" % n)


def fix_years():
    p = os.path.join(ROOT, "talks.html"); s = open(p, encoding="utf-8").read()
    years = re.findall(r'<h2 class="year" id="t(\d{4})">', s)
    links = "".join('<li><a href="#t%s">%s</a></li>' % (y, y) for y in years)
    t, k = re.subn(r'(<nav class="jump" aria-label="Years"><ul>).*?(</ul></nav>)', lambda m: m.group(1) + links + m.group(2), s)
    if k != 1: print("WARNING: no year links found in talks.html"); return
    if t != s: open(p, "w", encoding="utf-8").write(t)
    print("talks: %d year links" % len(years))


def fix_mars_pager():
    d = os.path.join(ROOT, "vibe-projects/mars")
    cands = sorted((int(m.group(1)), f) for f in os.listdir(d) for m in [re.fullmatch(r"candidate-(\d{3})", f)]
                   if m and os.path.isfile(os.path.join(d, f, "index.html")))   # candidate-NN (two digits) only redirect old URLs
    n = 0
    for i, (num, f) in enumerate(cands):
        links = ['<a href="../index.html">All candidates</a>']
        if i > 0: links.insert(0, '<a href="../%s/index.html" rel="prev">← Candidate %d</a>' % (cands[i - 1][1], cands[i - 1][0]))
        if i + 1 < len(cands): links.append('<a href="../%s/index.html" rel="next">Candidate %d →</a>' % (cands[i + 1][1], cands[i + 1][0]))
        p = os.path.join(d, f, "index.html"); s = open(p, encoding="utf-8").read()
        t, k = re.subn(r'<p class="mars-pager">.*?</p>', lambda m: '<p class="mars-pager">%s</p>' % " · ".join(links), s, flags=re.S)
        if k != 1: print("WARNING: %d pagers in vibe-projects/mars/%s/index.html" % (k, f)); continue
        if t != s: open(p, "w", encoding="utf-8").write(t); n += 1
    print("mars: %d candidate pages, previous/next links updated on %d" % (len(cands), n))


def fix_galaxy_pager():
    """Previous/next links follow the order of the lists on galaxy/index.html."""
    d = os.path.join(ROOT, "vibe-projects/galaxy")
    index_path = os.path.join(d, "index.html")
    if not os.path.isfile(index_path):
        return
    index = open(index_path, encoding="utf-8").read()
    seen, cands = set(), []
    for folder, num in re.findall(r'<a href="([0-9][^"]*)/index\.html">Candidate (\d+):', index):
        if folder in seen:
            continue
        seen.add(folder)
        cands.append((folder, int(num)))
    n = 0
    for i, (folder, num) in enumerate(cands):
        links = ['<a href="../index.html">All candidates</a>']
        if i > 0:
            links.insert(0, '<a href="../%s/index.html" rel="prev">← Candidate %d</a>' % (cands[i - 1][0], cands[i - 1][1]))
        if i + 1 < len(cands):
            links.append('<a href="../%s/index.html" rel="next">Candidate %d →</a>' % (cands[i + 1][0], cands[i + 1][1]))
        p = os.path.join(d, folder, "index.html")
        if not os.path.isfile(p):
            print("WARNING: missing vibe-projects/galaxy/%s/index.html" % folder)
            continue
        s = open(p, encoding="utf-8").read()
        t, k = re.subn(r'<p class="galaxy-pager">.*?</p>', lambda m: '<p class="galaxy-pager">%s</p>' % " · ".join(links), s, flags=re.S)
        if k != 1:
            print("WARNING: %d pagers in vibe-projects/galaxy/%s/index.html" % (k, folder))
            continue
        if t != s:
            open(p, "w", encoding="utf-8").write(t)
            n += 1
    print("galaxy: %d candidate pages, previous/next links updated on %d" % (len(cands), n))


MONTHS = "January February March April May June July August September October November December".split()
STATUSES = ("verified", "refereed", "partial result", "raw draft", "polished")   # badge styles live in css/site.css


def is_date(s):
    try: return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", s)) and bool(date.fromisoformat(s))
    except (TypeError, ValueError): return False


def problems(e, seen):
    if not isinstance(e, dict) or any(k not in e for k in ("n", "title", "status", "pdf")):
        return ["needs n, title, status and pdf"]
    out = []
    if type(e["n"]) is not int: out.append("n %r is not a whole number" % (e["n"],))
    elif e["n"] in seen: out.append("number %d is used twice" % e["n"])
    else: seen.add(e["n"])
    # A posted date is required, except an entry marked "undated": true, which must not carry a date at all.
    undated = e.get("undated", False)
    if type(undated) is not bool: out.append("undated %r is not true or false" % (undated,))
    elif undated and "date" in e: out.append("an undated entry must not include a date")
    elif not undated and not is_date(e.get("date")):
        out.append("date %r is not a real YYYY-MM-DD date" % (e.get("date"),))
    if e["status"] not in STATUSES: out.append("status %r is not one of %s" % (e["status"], ", ".join(STATUSES)))
    files = e.get("files", [])
    if not (isinstance(files, list) and all(isinstance(f, list) and len(f) == 2 for f in files)):
        out.append('files must be a list of ["label", "path"] pairs'); files = []
    if type(e.get("lean", False)) is not bool: out.append("lean %r is not true or false" % (e["lean"],))
    elif e.get("lean") and not any("lean" in str(f[0]).lower() for f in files):
        out.append('"lean": true needs the Lean files in files, with "Lean" in their label')
    out += ["missing file ai-proofs/%s" % h for h in [e["pdf"]] + [f[1] for f in files]
            if not os.path.isfile(os.path.join(ROOT, "ai-proofs", str(h)))]
    return out


def entry_html(e):
    files = [("PDF", e["pdf"])] + [tuple(f) for f in e.get("files", [])]
    links = " · ".join('<a href="%s">%s</a>' % (html.escape(h), t) for t, h in files)
    note = e["line"] + " " if e.get("line") else ""
    lean = ' <span class="badge lean">Lean</span>' if e.get("lean") else ""
    if is_date(e.get("date")):
        y, m, d = map(int, e["date"].split("-"))
        posted = '<time datetime="%s">%s %d, %d</time> ' % (e["date"], MONTHS[m - 1][:3], d, y)
    else:
        posted = ""
    return ('<li id="{n}" value="{n}"><a class="ap-n" href="#{n}">{n}</a> '
            '<a class="ap-title" href="{pdf}">{title}</a> '
            '<span class="ap-side">{posted}<span class="badge {cls}">{status}</span>{lean}</span> '
            '<span class="ap-note">{note}<span class="ap-files">[{links}]</span></span></li>').format(
        n=e["n"], pdf=html.escape(e["pdf"]), title=e["title"], posted=posted,
        cls=e["status"].replace(" ", "-"), status=e["status"], lean=lean, note=note, links=links)


def build_ai_proofs():
    entries = json.load(open(os.path.join(ROOT, "ai-proofs/entries.json"), encoding="utf-8"))
    seen, bad = set(), []
    for i, e in enumerate(entries):
        who = "entry %d" % e["n"] if isinstance(e, dict) and type(e.get("n")) is int else "entry number %d in the file" % (i + 1)
        bad += ["%s: %s" % (who, msg) for msg in problems(e, seen)]
    if bad:
        print("\n".join("ERROR: " + b for b in bad))
        sys.exit("ai-proofs/index.html was left unchanged; fix ai-proofs/entries.json and run again")
    # Newest first by entry number. Dates and undated flags do not affect list order.
    expected = set(range(1, len(entries) + 1))
    if seen != expected:
        missing = sorted(expected - seen)
        extra = sorted(seen - expected)
        msgs = []
        if missing: msgs.append("missing numbers: %s" % ", ".join(map(str, missing)))
        if extra: msgs.append("unexpected numbers: %s" % ", ".join(map(str, extra)))
        print("\n".join("ERROR: " + m for m in msgs))
        sys.exit("ai-proofs/index.html was left unchanged; fix ai-proofs/entries.json and run again")
    entries.sort(key=lambda e: e["n"], reverse=True)
    rows = [entry_html(e) for e in entries]
    block = ('<p class="ap-count">%d entries, newest first</p>\n<ol class="ap-list">\n%s\n</ol>\n'
             % (len(rows), "\n".join(rows)))
    p = os.path.join(ROOT, "ai-proofs/index.html"); s = open(p, encoding="utf-8").read()
    s = re.sub(r"(<!-- BEGIN ENTRIES[^>]*-->\n).*?(<!-- END ENTRIES -->)", lambda m: m.group(1) + block + m.group(2), s, flags=re.S)
    open(p, "w", encoding="utf-8").write(s)
    print("ai-proofs: %d entries" % len(rows))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd in ("ai-proofs", "all"): build_ai_proofs()
    if cmd in ("nav", "all"): fix_nav(); fix_footer(); fix_years(); fix_mars_pager(); fix_galaxy_pager()
