import csv, re, sys
from collections import Counter

site_id = sys.argv[1]
text = open(f"out/{site_id}.txt", encoding="utf-8").read()
rows = list(csv.DictReader(open(f"out/{site_id}_questions.csv", encoding="utf-8")))

flat = " ".join(text.split())
print("'be pleased to state' in text:", len(re.findall(r"be pleased to state", flat)),
      "| questions parsed:", len(rows))
print("status:", dict(Counter(r["status"] for r in rows)))

found = {r["q_number"] for r in rows}
START = re.compile(r"(?m)^(@)?\s*(\d{1,4})\.\s*(\*)?\s*([^\n:]{3,80}):?[ \t]*$")
print("\nquestion-start-looking lines NOT captured:")
n = 0
for m in START.finditer(text):
    if m.group(2) not in found:
        n += 1
        print("  ", m.group(0).strip(), "->", " ".join(text[m.end():m.end() + 80].split()))
print("count:", n)

print("\nstill UNPARSED:")
for r in rows:
    if r["status"] == "unparsed":
        print("-----", r["q_number"], r["member"])
        print("END:", r["question_text"][-200:])