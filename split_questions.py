import csv, re, sys

site_id = sys.argv[1]
idx = next(r for r in csv.DictReader(open("index/question_index.csv", encoding="utf-8"))
           if r["site_id"] == site_id)
text = open(f"out/{site_id}.txt", encoding="utf-8").read()
text = re.sub(r"(?m)^\s*-:\d+:-\s*$", "", text)          # page markers like -:3:-

START = re.compile(r"(?m)^(@)?\s*(\d{1,4})\.\s*(\*)?\s*([^\n:]{3,80}):?[ \t]*$")
REPLY = re.compile(r"(?m)^(?:Minister|Prime Minister|Parliamentary Secretary|"
                   r"Advis[eo]r|Special Assistant|Senator|Chairman)[^:?]{0,200}:")

def clean(s):
    return " ".join(s.split())

starts = []
for m in START.finditer(text):
    nxt = text[m.end():].lstrip()[:20]
    if nxt.startswith("(Deferred") or nxt.startswith("Will "):
        starts.append(m)

rows = []
for i, m in enumerate(starts):
    end = starts[i + 1].start() if i + 1 < len(starts) else len(text)
    b = text[m.end():end]
    if i + 1 == len(starts):
        b = re.split(r"(?m)^Islamabad,", b)[0]
    b = b.strip()

    d = re.search(r"\(Deferred on ([^)]+)\)", b[:200])
    intro = re.search(r"Will\s+the\s+(.+?)\s+be\s+pleased\s+to\s+(?:refer\s+to\s+(.+?)\s+and\s+to\s+)?state", b, re.S)
    asked_to = clean(intro.group(1)) if intro else ""
    refers_to = clean(intro.group(2)) if intro and intro.group(2) else ""
    after = b[intro.end():] if intro else b

    rep = REPLY.search(after)
    tr = re.search(r"Transferred to (.+?) for answer", after, re.S)
    nr = re.search(r"(?i)reply\s+not\s+received\.?", after)
    dis = re.search(r"(?i)disallowed[^\n]*", after)
    if rep:
        q, label, reply, status = after[:rep.start()], clean(rep.group(0)[:-1]), after[rep.end():], "answered"
    elif tr:
        q, label, reply, status = after[:tr.start()], clean(tr.group(1)), after[tr.start():], "transferred"
    elif nr:
        q, label, reply, status = after[:nr.start()], "", after[nr.start():], "no_reply"
    elif dis:
        q, label, reply, status = after[:dis.start()], "", after[dis.start():], "disallowed"
    else:
        q, label, reply, status = after, "", "", "unparsed"

    rows.append({
        "site_id": site_id, "sitting_date": idx["date"], "source_url": idx["pdf_url"],
        "q_number": m.group(2), "starred": bool(m.group(3)), "transferred_in": bool(m.group(1)),
        "member": clean(m.group(4)), "deferred_on": d.group(1) if d else "",
        "asked_to": asked_to,"refers_to": refers_to, "question_text": clean(q).lstrip(": ").strip(), "status": status,
        "reply_label": label, "reply_text": clean(reply),
    })

out = f"out/{site_id}_questions.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

from collections import Counter
print("questions found:", len(rows), "| saved to", out)
print("status:", dict(Counter(r["status"] for r in rows)))
print("starred:", sum(r["starred"] for r in rows),
      "| transferred_in (@):", sum(r["transferred_in"] for r in rows),
      "| deferred:", sum(1 for r in rows if r["deferred_on"]))
print("numbers:", [r["q_number"] for r in rows][:25])
dups = [n for n, c in Counter(r["q_number"] for r in rows).items() if c > 1]
print("duplicate numbers:", dups)
for r in rows[:2] + rows[-1:]:
    print("-----")
    print(r["q_number"], "|", r["member"], "|", r["asked_to"], "|", r["status"])
    print("Q:", r["question_text"][:160])
    print("A:", r["reply_label"], "|", r["reply_text"][:160])
    print("with a reference to an earlier question:", sum(1 for r in rows if r["refers_to"]))