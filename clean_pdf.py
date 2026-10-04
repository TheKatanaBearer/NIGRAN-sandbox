import csv, os, re, sys, requests, pdfplumber

HEADERS = {"User-Agent": "nigran-sandbox (student project; hamzakhattak188@gmail.com)"}
URDU = re.compile(r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]")
LATIN = re.compile(r"[A-Za-z]")

frag = sys.argv[1]   # part of the PDF filename, e.g. 1453359597_497
rows = csv.DictReader(open("index/question_index.csv", encoding="utf-8"))
row = next(r for r in rows if frag in r["pdf_url"])
print("File:", row["date"], row["pdf_url"])

os.makedirs("data", exist_ok=True)
path = f"data/{row['site_id']}.pdf"
if not os.path.exists(path):
    r = requests.get(row["pdf_url"], headers=HEADERS, timeout=120)
    open(path, "wb").write(r.content)

kept, skipped = [], []
with pdfplumber.open(path) as pdf:
    for i, p in enumerate(pdf.pages, 1):
        t = p.extract_text() or ""
        u, l = len(URDU.findall(t)), len(LATIN.findall(t))
        if u > l or u + l < 50:
            skipped.append(i)
        else:
            kept.append(t)

text = "\n".join(kept)
text = re.sub(r"\(cid:\d+\)", "", text)
text = re.sub(r"(?m)^\s*\d{1,3}\s*$\n?", "", text)   # lines that are only a page number
text = re.sub(r"[ \t]+", " ", text)

os.makedirs("out", exist_ok=True)
out = f"out/{row['site_id']}.txt"
open(out, "w", encoding="utf-8").write(text)
print("pages kept:", len(kept), "| skipped:", skipped)
print("characters:", len(text), "| saved to", out)