import re, sys

site_id = sys.argv[1]
text = open(f"out/{site_id}.txt", encoding="utf-8").read()
text = re.sub(r"(?m)^\s*-:\d+:-\s*$", "", text)

START = re.compile(r"(?m)^(@)?\s*(\d{1,4})\.\s*(\*)?\s*([^\n:]{3,80}):?[ \t]*$")
PHRASE = re.compile(r"be\s+pleased\s+to\s+(?:state|refer)")

starts = []
for m in START.finditer(text):
    nxt = text[m.end():].lstrip()[:20]
    if nxt.startswith("(Deferred") or nxt.startswith("Will "):
        starts.append(m)

def ctx(s, a, b):
    return " ".join(s[max(0, a - 150):b + 60].split())

print("question headers found:", len(starts))
before = PHRASE.findall(text[:starts[0].start()])
print("phrases BEFORE the first question:", len(before))

for i, m in enumerate(starts):
    end = starts[i + 1].start() if i + 1 < len(starts) else len(text)
    block = text[m.end():end]
    hits = list(PHRASE.finditer(block))
    if len(hits) != 1:
        print("\n===== question", m.group(2), "|", m.group(4), "| phrases in block:", len(hits))
        for h in hits:
            print("   ...", ctx(block, h.start(), h.end()))