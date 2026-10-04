import requests, time, csv, os
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://na.gov.pk/en/includes/getpartlimentyears.php"
PAGE = "https://na.gov.pk/en/questions.php"
HEADERS = {"User-Agent": "nigran-sandbox (student project; hamzakhattak188@gmail.com)"}
DELAY = 10
TENURES = {21: "2024-2029", 20: "2018-2023", 11: "2013-2018"}

def get(params):
    r = requests.get(BASE, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    time.sleep(DELAY)
    return r.text

rows = []
for tid, tlabel in TENURES.items():
    soup = BeautifulSoup(get({"tenure_id": tid}), "html.parser")
    years = [(o["value"], o.get_text(strip=True))
             for o in soup.find_all("option") if o.get("value")]
    print(tlabel, "years:", years)
    for yid, ylabel in years:
        s = BeautifulSoup(get({"tenureid": tid, "py_id": yid, "session_id": ""}),
                          "html.parser")
        n = 0
        for tr in s.find_all("tr"):
            tds = tr.find_all("td")
            a = tr.find("a", href=True)
            if len(tds) >= 3 and a:
                rows.append({
                    "tenure": tlabel,
                    "year": ylabel,
                    "date": tds[1].get_text(strip=True),
                    "site_id": a.get("title", ""),
                    "pdf_url": urljoin(PAGE, a["href"]),
                })
                n += 1
        print("  ", ylabel, "->", n, "sittings")

os.makedirs("index", exist_ok=True)
with open("index/question_index.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["tenure", "year", "date", "site_id", "pdf_url"])
    w.writeheader()
    w.writerows(rows)
print("TOTAL sittings:", len(rows))