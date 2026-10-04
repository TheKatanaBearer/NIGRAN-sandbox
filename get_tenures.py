import requests
from bs4 import BeautifulSoup

url = "https://na.gov.pk/en/questions.php?type=list"
headers = {"User-Agent": "nigran-sandbox (student project; hamzakhattak188@gmail.com)"}
r = requests.get(url, headers=headers, timeout=30)
soup = BeautifulSoup(r.text, "html.parser")

for s in soup.find_all("select"):
    print("SELECT name =", s.get("name"), "| id =", s.get("id"))
    for o in s.find_all("option"):
        print("   ", o.get("value"), "->", o.get_text(strip=True))