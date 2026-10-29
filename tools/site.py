#!/usr/bin/env python3
"""Site maintenance.  Run from the repo root.

  python3 tools/site.py nav        rewrite the primary nav and the footer on every page and the year links on talks.html
  python3 tools/site.py ai-proofs  rebuild ai-proofs/index.html from ai-proofs/entries.json
  python3 tools/site.py all        both
"""
import html, json, os, re, sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAV = [("Home", "index.html"), ("Papers", "papers.html"), ("Talks", "talks.html"),
       ("Teaching", "teaching.html"), ("Students", "students.html"), ("Slides", "slides.html"),
       ("Co-authors", "coauthors.html"), ("Organization", "organization.html"), ("Awards", "awards.html"),
       ("Vibe projects", "vibe-projects/index.html"), ("AI proofs", "ai-proofs/index.html")]
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


def pages():
    for d, _, fs in os.walk(ROOT):
        if "/.git" in d: continue
        for f in fs:
            if f.endswith(".html"):
                rel = os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, "/")
                if not rel.startswith(SKIP): yield rel


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


MONTHS = "January February March April May June July August September October November December".split()
STATUSES = ("refereed", "partial result", "raw draft", "polished")   # badge styles live in css/site.css


def is_date(s):
    try: return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", s)) and bool(date.fromisoformat(s))
    except (TypeError, ValueError): return False


def problems(e, seen):
    if not isinstance(e, dict) or any(k not in e for k in ("n", "date", "title", "status", "pdf")):
        return ["needs n, date, title, status and pdf"]
    out = []
    if type(e["n"]) is not int: out.append("n %r is not a whole number" % (e["n"],))
    elif e["n"] in seen: out.append("number %d is used twice" % e["n"])
    else: seen.add(e["n"])
    if not is_date(e["date"]): out.append("date %r is not a real YYYY-MM-DD date" % (e["date"],))
    if e["status"] not in STATUSES: out.append("status %r is not one of %s" % (e["status"], ", ".join(STATUSES)))
    files = e.get("files", [])
    if not (isinstance(files, list) and all(isinstance(f, list) and len(f) == 2 for f in files)):
        out.append('files must be a list of ["label", "path"] pairs'); files = []
    out += ["missing file ai-proofs/%s" % h for h in [e["pdf"]] + [f[1] for f in files]
            if not os.path.isfile(os.path.join(ROOT, "ai-proofs", str(h)))]
    return out


def entry_html(e):
    y, m, d = map(int, e["date"].split("-"))
    files = [("PDF", e["pdf"])] + [tuple(f) for f in e.get("files", [])]
    links = " · ".join('<a href="%s">%s</a>' % (html.escape(h), t) for t, h in files)
    note = e["line"] + " " if e.get("line") else ""
    return ('<li id="{n}" value="{n}"><a class="ap-n" href="#{n}">{n}</a> '
            '<a class="ap-title" href="{pdf}">{title}</a> '
            '<span class="ap-side"><time datetime="{date}">{when}</time> <span class="badge {cls}">{status}</span></span> '
            '<span class="ap-note">{note}<span class="ap-files">[{links}]</span></span></li>').format(
        n=e["n"], pdf=html.escape(e["pdf"]), title=e["title"], date=e["date"], when="%s %d, %d" % (MONTHS[m - 1][:3], d, y),
        cls=e["status"].replace(" ", "-"), status=e["status"], note=note, links=links)


def build_ai_proofs():
    entries = json.load(open(os.path.join(ROOT, "ai-proofs/entries.json"), encoding="utf-8"))
    seen, bad = set(), []
    for i, e in enumerate(entries):
        who = "entry %d" % e["n"] if isinstance(e, dict) and type(e.get("n")) is int else "entry number %d in the file" % (i + 1)
        bad += ["%s: %s" % (who, msg) for msg in problems(e, seen)]
    if bad:
        print("\n".join("ERROR: " + b for b in bad))
        sys.exit("ai-proofs/index.html was left unchanged; fix ai-proofs/entries.json and run again")
    entries.sort(key=lambda e: (e["date"], e["n"]), reverse=True)   # newest first
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
    if cmd in ("nav", "all"): fix_nav(); fix_footer(); fix_years()
