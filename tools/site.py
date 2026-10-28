#!/usr/bin/env python3
"""Site maintenance.  Run from the repo root.

  python3 tools/site.py nav        rewrite the primary nav on every page
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


MONTHS = "January February March April May June July August September October November December".split()
STATUSES = ("refereed", "partial result", "raw draft", "polished")   # badge styles live in css/site.css


def problems(e, seen):
    if any(k not in e for k in ("n", "date", "title", "status", "pdf")):
        return ["needs n, date, title, status and pdf"]
    out = [] if e["n"] not in seen else ["number %d is used twice" % e["n"]]
    seen.add(e["n"])
    try: date.fromisoformat(e["date"])
    except ValueError: out.append("date %r is not YYYY-MM-DD" % e["date"])
    if e["status"] not in STATUSES: out.append("status %r is not one of %s" % (e["status"], ", ".join(STATUSES)))
    out += ["missing file ai-proofs/" + h for _, h in [("PDF", e["pdf"])] + e.get("files", [])
            if not os.path.isfile(os.path.join(ROOT, "ai-proofs", h))]
    return out


def entry_html(e):
    y, m, d = map(int, e["date"].split("-"))
    files = [("PDF", e["pdf"])] + [tuple(f) for f in e.get("files", [])]
    links = " · ".join('<a href="%s">%s</a>' % (html.escape(h), t) for t, h in files)
    note = e["line"] + " " if e.get("line") else ""
    return ('<li id="{n}" value="{n}"><a class="ap-n" href="#{n}">{n}</a>'
            '<a class="ap-title" href="{pdf}">{title}</a>'
            '<span class="ap-side"><time datetime="{date}">{when}</time> <span class="badge {cls}">{status}</span></span>'
            '<span class="ap-note">{note}<span class="ap-files">[{links}]</span></span></li>').format(
        n=e["n"], pdf=html.escape(e["pdf"]), title=e["title"], date=e["date"], when="%s %d, %d" % (MONTHS[m - 1][:3], d, y),
        cls=e["status"].replace(" ", "-"), status=e["status"], note=note, links=links)


def build_ai_proofs():
    entries = json.load(open(os.path.join(ROOT, "ai-proofs/entries.json"), encoding="utf-8"))
    seen = set()
    for e in entries:
        for msg in problems(e, seen): print("WARNING: entry %s: %s" % (e.get("n", "?"), msg))
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
    if cmd in ("nav", "all"): fix_nav()
