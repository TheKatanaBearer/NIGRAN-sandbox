import csv, os, re, sys, requests, pdfplumber

HEADERS = {"User-Agent": "nigran-sandbox (student project; your-email@example.com)"}
URDU = re.compile(r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]")
LATIN = re.compile(r"[A-Za-z]")

tenure = sys.argv[1]   # e.g. 2024-2029
rows = [r for r in csv.DictReader(open("index/question_index.csv", encoding="utf-8"))
        if r["tenure"] == tenure]
row = rows[len(rows) // 2]
print("Testing:", row["date"], row["pdf_url"])

os.makedirs("data", exist_ok=True)
path = f"data/{row['site_id']}.pdf"
if not os.path.exists(path):
    r = requests.get(row["pdf_url"], headers=HEADERS, timeout=120)
    open(path, "wb").write(r.content)
print("size MB:", round(os.path.getsize(path) / 1e6, 1))

tu = tl = 0
urdu_pages, empty_pages = [], []
with pdfplumber.open(path) as pdf:
    print("pages:", len(pdf.pages))
    for i, p in enumerate(pdf.pages, 1):
        t = p.extract_text() or ""
        u, l = len(URDU.findall(t)), len(LATIN.findall(t))
        tu += u; tl += l
        if u > 50: urdu_pages.append(i)
        if u + l < 50: empty_pages.append(i)
print("urdu chars:", tu, "| latin chars:", tl)
print("pages with Urdu:", urdu_pages)
print("near-empty pages:", empty_pages)