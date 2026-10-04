import pdfplumber

with pdfplumber.open("data/test_old.pdf") as pdf:
    for n in (0, 4):
        print(f"=============== PAGE {n + 1} ===============")
        print(pdf.pages[n].extract_text())