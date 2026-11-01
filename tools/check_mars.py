#!/usr/bin/env python3
"""Check the Mars pages against the hunt's final list.  Run from anywhere:

  python3 tools/check_mars.py          check vibe-projects/mars/ against vibe-projects/mars/candidates.csv
  python3 tools/check_mars.py --ocr    also read the label printed on every figure (needs the tesseract program)

For each of the 166 leads it checks the line on index.html and the page candidate-NNN/index.html: number, title and
place, coordinates (3 decimals), rating, probability, the formation window and image counts, size, HiRISE statements,
figures (files exist, belong to the lead, sizes match) and the previous/next links.  It also checks the summary
sentences on index.html, the redirects from the old candidate-NN/ addresses and every link on the Mars pages and on vibe-projects/index.html.
It prints one line per lead and exits with status 1 if anything is wrong.
"""
import csv, datetime, html, math, os, re, shutil, struct, subprocess, sys, tempfile
from decimal import Decimal, ROUND_HALF_UP

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARS = os.path.join(ROOT, "vibe-projects", "mars")
MONTHS = "January February March April May June July August September October November December".split()
NUMWORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
            "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15}
COMPASS = {"N": "north", "S": "south", "E": "east", "W": "west", "NE": "north-east", "NW": "north-west",
           "SE": "south-east", "SW": "south-west", "NNE": "north-north-east", "NNW": "north-north-west",
           "SSE": "south-south-east", "SSW": "south-south-west", "ENE": "east-north-east", "ESE": "east-south-east",
           "WNW": "west-north-west", "WSW": "west-south-west"}
DESCRIPTIVE = ("rayed dark spot", "twin dark spot", "large irregular patch", "cluster of dots", "large rayed dark spot",
               "cluster", "rayed spot with satellite dots", "spot with a tail", "formed Sep-Dec 2023",
               "dot beside a small crater")        # parentheses in CSV names that describe the spot, not the place
INSIGHT = (4.502, 135.623)                         # Bickel et al. (2025) searched within 50 degrees of the lander
EXTRA_FIGURES = {"lead1_control_hirise_targeted_site_web.jpg"}   # the hunt's control figure for lead 1


def read(path):
    with open(path, encoding="utf-8") as f: return f.read()


def text(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s)).replace("\xa0", " ")).strip()


def dates_in(s):
    return [datetime.date(int(y), MONTHS.index(m) + 1, int(d)).isoformat()
            for d, m, y in re.findall(r"\b(\d{1,2}) (%s) (\d{4})\b" % "|".join(MONTHS), s)]


def months_only(s):
    """'September 2018' mentions that are not part of a full date."""
    return re.findall(r"(?<!\d )\b(?:%s) \d{4}\b" % "|".join(MONTHS), re.sub(r"\b\d{1,2} (?:%s) \d{4}\b" % "|".join(MONTHS), " ", s))


def count_ok(s, dates, n):
    """Do the dates in s (plus images given by month only, by a count such as 'four earlier images', or a second
    image of the same day, 'CTX and HiRISE') add up to the CSV's number of images?"""
    k = len(dates) + len(months_only(s)) + len(re.findall(r"CTX and HiRISE", s))
    phrase = [NUMWORDS[w] for w in re.findall(r"\b(%s) (?:earlier |later |more )?images\b" % "|".join(NUMWORDS), s)]
    return n in (k, len(dates)) or n in phrase or (phrase and len(dates) + sum(phrase) == n)


def long_date(iso):
    return "%d %s %s" % (int(iso[8:]), MONTHS[int(iso[5:7]) - 1], iso[:4])


def r3(x): return Decimal(x).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
def pct(p): return int((Decimal(p) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def location(row):
    lat, lon = Decimal(row["lat"]), Decimal(row["lon"])
    loc = "%s° %s, %s° E" % (abs(r3(lat)), "N" if lat >= 0 else "S", r3(lon))
    return loc, ("%s° W" % (Decimal(360) - r3(lon)) if lon > 180 else None)


def numbers(s):
    t = s.lower()
    out = set(re.findall(r"\d+(?:\.\d+)?", t))
    out |= {str(v) for w, v in NUMWORDS.items() if re.search(r"\b%s\b" % w, t)}
    return out


def size_numbers(size_m):
    s = re.sub(r"\b[A-Z]\d{2}\b", " ", size_m)                     # CTX image codes such as V14
    return set(re.findall(r"\d+(?:\.\d+)?", re.sub(r"\((?:N-S|E-W)\)", " ", s)))


def place_words(name):
    """Words of a CSV name that the page title must contain."""
    n = name
    for d in DESCRIPTIVE: n = n.replace("(%s)" % d, " ")
    need = ["candidate %s" % m for m in re.findall(r"\b[Ll]ead (\d+)\b", n)]
    n = re.sub(r"\b[Ll]ead \d+\b", " ", n)
    need += [m + " km" for m in re.findall(r"(\d+(?:\.\d+)?) km", n)]
    for w in re.findall(r"\b[A-Z][A-Za-z]*\b", n):
        if w in COMPASS: need.append(COMPASS[w])
        elif w == "E": continue
        else: need.append(w.lower())
    return need


def jpeg_size(path):
    with open(path, "rb") as f:
        data = f.read()
    i = 2
    while i < len(data):
        if data[i] != 0xFF: i += 1; continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack(">HH", data[i + 5:i + 9]); return w, h
        i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    return None


def insight_distance(row):
    a = math.radians
    la, lo = float(row["lat"]), float(row["lon"])
    c = (math.sin(a(la)) * math.sin(a(INSIGHT[0])) + math.cos(a(la)) * math.cos(a(INSIGHT[0])) * math.cos(a(lo - INSIGHT[1])))
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def hirise_images(row):
    """(date, 'before'|'after') for each HiRISE image of the spot listed in the CSV."""
    h = row["hirise"]
    if h.startswith("none"): return []
    out = []
    for d in re.findall(r"\d{4}-\d{2}-\d{2}", h):
        out.append((d, "before" if d <= row["last_absent"] else "after"))
    return out


def ocr_label(path):
    """The first line printed on a figure, read with tesseract."""
    try:
        from PIL import Image
    except ImportError:
        return None
    im = Image.open(path).convert("L")
    w, h = im.size
    top = im.crop((0, 0, w, max(40, int(h * 0.07))))
    top = top.resize((top.width * 2, top.height * 2))
    with tempfile.NamedTemporaryFile(suffix=".png") as t:
        top.save(t.name)
        r = subprocess.run(["tesseract", t.name, "-", "--psm", "6"], capture_output=True, text=True,
                           env=dict(os.environ, OMP_THREAD_LIMIT="1"))
    return r.stdout


def check_page(n, row, slug, use_ocr):
    errs = []
    folder = "candidate-%03d" % n
    path = os.path.join(MARS, folder, "index.html")
    if not os.path.isfile(path): return ["page %s/index.html is missing" % folder], None
    s = read(path)
    body = s.split('<div class="page" id="content">', 1)[-1].split("<footer", 1)[0]
    rating, p = row["rating"].capitalize(), pct(row["p_new_impact"])
    m = re.search(r'<h1 class="page-title">Candidate (\d+): (.*?)</h1>', body)
    title = text(m.group(2)) if m else ""
    if not m or int(m.group(1)) != n: errs.append("heading is not 'Candidate %d: ...'" % n)
    t = re.search(r"<title>(.*?)</title>", s)
    if not t or text(t.group(1)) != "Mars candidate %d: %s — Paata Ivanisvili" % (n, title):
        errs.append("<title> does not match the heading")
    for w in place_words(row["name"]):
        if w not in title.lower(): errs.append("title lacks %r of the CSV name %r" % (w, row["name"]))
    tag = re.search(r'<p class="mars-tag">(.*?)</p>', body)
    if not tag or text(tag.group(1)) != "%s · roughly %d%%" % (rating, p):
        errs.append("tag %r, expected %r" % (text(tag.group(1)) if tag else None, "%s · roughly %d%%" % (rating, p)))
    facts = {text(k): v for k, v in re.findall(r"<dt>(.*?)</dt><dd>(.*?)</dd>", body, flags=re.S)}
    loc, west = location(row)
    want = loc + (" (%s)" % west if west else "")
    if text(facts.get("Location", "")) != want:
        errs.append("location %r, expected %r" % (text(facts.get("Location", "")), want))
    ab, pr = dates_in(text(facts.get("Absent", ""))), dates_in(text(facts.get("Present", "")))
    na, np_ = int(float(row["n_images_absent"])), int(float(row["n_images_present"]))
    na_ok = count_ok(text(facts.get("Absent", "")), ab, na)
    np_ok = count_ok(text(facts.get("Present", "")), pr, np_)
    if not ab or max(ab) != row["last_absent"]: errs.append("last image without the spot %s, CSV %s" % (max(ab) if ab else None, row["last_absent"]))
    if not pr or min(pr) != row["first_present"]: errs.append("first image with the spot %s, CSV %s" % (min(pr) if pr else None, row["first_present"]))
    if ab != sorted(ab) or pr != sorted(pr): errs.append("dates not in order")
    if not na_ok: errs.append("images without the spot: %r does not give the CSV's %d" % (text(facts.get("Absent", "")), na))
    if not np_ok: errs.append("images with the spot: %r does not give the CSV's %d" % (text(facts.get("Present", "")), np_))
    miss = [x for x in sorted(size_numbers(row["size_m"]), key=float)
            if x not in numbers(text(facts.get("Size", ""))) and str(int(float(x))) not in numbers(text(facts.get("Size", "")))]
    if miss: errs.append("size lacks %s of the CSV size %r" % (", ".join(miss), row["size_m"]))
    conf = "%s candidate; roughly %d%% that it is a new impact." % (rating, p)
    if text(facts.get("Confidence", "")) != conf: errs.append("confidence %r, expected %r" % (text(facts.get("Confidence", "")), conf))
    page_text = text(body)
    imgs = re.findall(r'<img src="\.\./([^"]+)" width="(\d+)" height="(\d+)"', body)
    hi = hirise_images(row)
    if not hi:
        m = re.search(r"(?:nearest edge|edge) ([\d.]+) km", row["hirise"])
        sent = "It lies outside every footprint of the high-resolution HiRISE camera; the nearest ends %s km away." % m.group(1)
        if sent not in page_text: errs.append("missing the HiRISE sentence %r" % sent)
        if any("_hirise_web" in f for f, _, _ in imgs): errs.append("HiRISE figure on a page whose spot HiRISE never imaged")
    else:
        if "outside every footprint" in page_text: errs.append("says it lies outside HiRISE footprints, but the CSV lists %s" % row["hirise"])
        for d, when in hi:
            if long_date(d) not in page_text: errs.append("HiRISE image of %s not mentioned" % long_date(d))
        if all(w == "before" for _, w in hi) and not re.search(r"before the spots? formed", page_text):
            errs.append("does not say the HiRISE image predates the spot")
        if any(w == "after" for _, w in hi) != any("_hirise_web" in f for f, _, _ in imgs):
            errs.append("HiRISE figure present/absent does not match the CSV")
    kinds = set()
    for f, w, h in imgs:
        fp = os.path.join(MARS, f)
        if not os.path.isfile(fp): errs.append("figure %s does not exist" % f); continue
        if f not in EXTRA_FIGURES and not f.startswith("lead%d_%s_" % (n, slug)):
            errs.append("figure %s does not belong to lead %d (%s)" % (f, n, slug))
        km = re.search(r"_(pair|epochs|context|zoom|zoom_4x|hirise|check|hirise_check|tail_check|moc_2002)_web\.jpg$", f)
        kinds.add(km.group(1) if km else f)
        if jpeg_size(fp) != (int(w), int(h)): errs.append("figure %s is %s, page says %sx%s" % (f, jpeg_size(fp), w, h))
        if use_ocr and km and km.group(1) in ("pair", "epochs", "context", "hirise", "zoom"):
            lab = ocr_label(fp) or ""
            mm = re.search(r"L[eo][ae]d\s*(\d+)", lab)
            if mm and int(mm.group(1)) != n: errs.append("figure %s is labelled lead %s" % (f, mm.group(1)))
    if not {"epochs", "context"} <= kinds: errs.append("page lacks its epochs or context figure")
    if n in DIFFERENT_SUN:
        for pat in (r"similar sun", r"sun as high", r"sun \d+(?:\.\d+)?(?: to \d+)?° (?:lower|higher)", r"same sun"):
            if re.search(pat, page_text): errs.append("says %r, but its two pair images were taken under different light" % re.search(pat, page_text).group(0))
    pager = re.search(r'<p class="mars-pager">(.*?)</p>', body, flags=re.S)
    want = ['<a href="../index.html">All candidates</a>']
    if n > 1: want.insert(0, '<a href="../candidate-%03d/index.html" rel="prev">← Candidate %d</a>' % (n - 1, n - 1))
    if n < 166: want.append('<a href="../candidate-%03d/index.html" rel="next">Candidate %d →</a>' % (n + 1, n + 1))
    if not pager or pager.group(1) != " · ".join(want): errs.append("previous/next links are wrong")
    return errs, title


def numbers_after(s, start):
    """Candidate numbers in the sentence of s that begins with start."""
    i = s.find(start)
    if i < 0: return None
    j = s.find(".", i + len(start))
    while j > 0 and s[j - 1].isdigit() and s[j + 1:j + 2].isdigit(): j = s.find(".", j + 1)
    return [int(x) for x in re.findall(r"\b(\d{1,3})\b(?!°| km| m\b)", text(s[i:j]))]


def check_index(rows, titles, review, hirise_fig):
    errs = []
    s = read(os.path.join(MARS, "index.html"))
    t = text(s)
    c = {k: sum(r["rating"] == k for r in rows.values()) for k in ("STRONG", "PROMISING", "WEAK")}
    want = "It found %d leads: %d strong, %d promising and %d weak." % (len(rows), c["STRONG"], c["PROMISING"], c["WEAK"])
    if want not in t: errs.append("summary does not say %r" % want)
    items = re.findall(r'<li[^>]*><a[^>]*href="(candidate-(\d{3})/index\.html)">Candidate (\d+): (.*?)</a> <span class="mars-meta">(.*?) · '
                       r'<span class="mars-rating">(\w+)</span> · roughly&nbsp;(\d+)%</span></li>', s)
    if [int(i[2]) for i in items] != list(range(1, len(rows) + 1)): errs.append("list is not numbered 1 to %d" % len(rows))
    seen = {"STRONG": 0, "PROMISING": 0, "WEAK": 0}
    for href, folder, num, title, loc, rating, p in items:
        n = int(num); row = rows.get(n)
        if not row: continue
        if int(folder) != n: errs.append("line %d links to %s" % (n, href))
        if text(title) != titles.get(n): errs.append("line %d title differs from its page" % n)
        if text(loc) != location(row)[0]: errs.append("line %d location %r, CSV %r" % (n, text(loc), location(row)[0]))
        if rating.upper() != row["rating"]: errs.append("line %d rating %s, CSV %s" % (n, rating, row["rating"]))
        if int(p) != pct(row["p_new_impact"]): errs.append("line %d probability %s%%, CSV %d%%" % (n, p, pct(row["p_new_impact"])))
        seen[rating.upper()] = seen.get(rating.upper(), 0) + 1
    if seen != c: errs.append("list has %s, CSV %s" % (seen, c))
    after = sorted(n for n, r in rows.items() if any(w == "after" for _, w in hirise_images(r)))
    before = sorted(n for n, r in rows.items() if hirise_images(r) and all(w == "before" for _, w in hirise_images(r)))
    got = numbers_after(t, "All but ")
    if got is None or sorted(set(got) - {len(after) + len(before)}) != sorted(after + before):
        errs.append("HiRISE sentence lists %s, CSV gives %s after the spot formed and %s before" % (got, after, before))
    if hirise_fig != after: errs.append("pages with a HiRISE figure %s differ from %s" % (hirise_fig, after))
    m = re.search(r"the views of candidates (.*?), and the HiRISE panels of the independent checks of (.*?)\)", t)
    if not m or [int(x) for x in re.findall(r"\d+", m.group(1))] != after:
        errs.append("credit line names HiRISE views of %s, pages show %s" % (m.group(1) if m else None, after))
    got = numbers_after(t, "Thirty-five of the candidates")
    if got is None or sorted(set(got)) != review or len(review) != 35:
        errs.append("review sentence lists %s, pages with a check figure are %s" % (got, review))
    area = sorted(n for n, r in rows.items() if insight_distance(r) <= 50)
    got = numbers_after(t, "of the candidates here, numbers")
    if got is None or sorted(got) != area: errs.append("Bickel sentence lists %s, leads within 50° of InSight are %s" % (got, area))
    late = sorted(n for n in area if rows[n]["last_absent"] >= "2023-01-01")
    got = numbers_after(t, "Numbers ")
    if got is None or sorted(got) != late: errs.append("'formed after' sentence lists %s, expected %s" % (got, late))
    return errs, len(items)


def check_links():
    errs = []
    ids = {}
    for d, _, fs in os.walk(MARS):
        for f in fs:
            if f.endswith(".html"): ids[os.path.normpath(os.path.join(d, f))] = None
    ids[os.path.normpath(os.path.join(ROOT, "vibe-projects", "index.html"))] = None
    for p in list(ids): ids[p] = set(re.findall(r'\bid="([^"]+)"', read(p)))
    for p in ids:
        s = read(p)
        for attr, url in re.findall(r'\b(href|src)="([^"]+)"', s):
            if re.match(r"(https?:|mailto:|data:|#$)", url): continue
            u, _, frag = url.partition("#")
            target = os.path.normpath(os.path.join(os.path.dirname(p), u)) if u else p
            if not os.path.exists(target): errs.append("%s: %s %s does not exist" % (os.path.relpath(p, ROOT), attr, url)); continue
            if frag and target in ids and frag not in ids[target]: errs.append("%s: no id %r in %s" % (os.path.relpath(p, ROOT), frag, u or "the page"))
        m = re.search(r'http-equiv="refresh" content="0; url=([^"]+)"', s)
        if m and not os.path.isfile(os.path.normpath(os.path.join(os.path.dirname(p), m.group(1)))):
            errs.append("%s redirects to a missing page" % os.path.relpath(p, ROOT))
    for c in range(1, 91):                 # the addresses used before the renumbering
        p = os.path.join(MARS, "candidate-%02d" % c, "index.html")
        if not os.path.isfile(p): errs.append("old address candidate-%02d/ no longer resolves" % c)
    return errs


# Leads whose before/after pair figure the hunt re-captioned on 1 November 2026: the two images were not taken under
# a similar sun (incidence more than 5° or azimuth more than 20° apart), so no page text may say they were.
DIFFERENT_SUN = {12, 21, 32, 44, 48, 49, 53, 54, 63, 75, 77, 82, 85, 86, 88, 89, 90, 93, 96, 98, 99, 103, 104, 107,
                 108, 121, 122, 125, 133, 142, 143, 145, 151, 152, 153, 155, 157}


def main():
    use_ocr = "--ocr" in sys.argv
    if use_ocr and not shutil.which("tesseract"): sys.exit("--ocr needs the tesseract program")
    rows = {int(r["candidate_id"][1:]): r for r in csv.DictReader(open(os.path.join(MARS, "candidates.csv"), newline="", encoding="utf-8"))
            if r["candidate_id"].startswith("L")}
    if sorted(rows) != list(range(1, len(rows) + 1)): sys.exit("candidates.csv: leads are not numbered 1 to %d" % len(rows))
    bad, titles, review, hfig = 0, {}, [], []
    for n in sorted(rows):
        row = rows[n]
        slugs = re.findall(r"lead%d_(.+?)_(?:epochs|pair|context|zoom|hirise)\.png" % n, row["figures"])
        errs, title = check_page(n, row, slugs[0] if slugs else "?", use_ocr)
        titles[n] = title
        s = read(os.path.join(MARS, "candidate-%03d" % n, "index.html")) if title is not None else ""
        if re.search(r'(?<!hirise)(?<!tail)_check_web\.jpg"', s): review.append(n)
        if "_hirise_web.jpg" in s: hfig.append(n)
        print("candidate %3d  %-9s %s" % (n, row["rating"].lower(), "PASS" if not errs else "FAIL"))
        for e in errs: print("      - " + e)
        bad += bool(errs)
    ierrs, nitems = check_index(rows, titles, review, hfig)
    lerrs = check_links()
    print("index.html: %d lines, %s" % (nitems, "PASS" if not ierrs else "FAIL"))
    for e in ierrs: print("      - " + e)
    print("links: %s" % ("PASS" if not lerrs else "FAIL"))
    for e in lerrs: print("      - " + e)
    print("%d of %d lead pages pass%s" % (len(rows) - bad, len(rows), " (figure labels read with OCR)" if use_ocr else ""))
    sys.exit(1 if bad or ierrs or lerrs else 0)


if __name__ == "__main__":
    main()
