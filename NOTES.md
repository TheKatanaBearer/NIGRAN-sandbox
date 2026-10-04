# NIGRAN sandbox notes

## Site rules
- Source: na.gov.pk (National Assembly of Pakistan). Credit the site, link every record to its source PDF.
- robots.txt asks for Crawl-delay: 10 seconds. Use a User-Agent with my contact email.
- Plan: publish derived data only, do not republish PDFs.

## Questions listing (VERIFIED)
- Page: https://na.gov.pk/en/questions.php?type=list
- Dropdowns fill via plain GET requests, no browser needed:
  - years:    /en/includes/getpartlimentyears.php?tenure_id=N
  - sessions: /en/includes/getpartlimentyears.php?Tenure_ID=N&ParYear_id=Y
  - sittings: /en/includes/getpartlimentyears.php?tenureid=N&py_id=Y&session_id=
    (empty session_id = all sittings in that year)
- Returns an HTML table: date + PDF link
- PDF links are relative (../uploads/documents/questions/XXXX.pdf). Resolve against https://na.gov.pk/en/questions.php (urljoin), NOT against /includes/
- Tenure ids (from the tenure dropdown): 21 = 2024-2029 | 20 = 2018-2023 | 11 = 2013-2018 | 1 = 2008-2013 (not needed)
- Parliamentary year ids differ per tenure, so never hardcode them:
  - 2024-2029: 72, 73, 74 (3 years so far)
  - 2018-2023: 67 to 71 (5 years)
  - 2013-2018: 6, 7, 8, 65, 66 (5 years)
- Session ids (486 to 525) are from the 2024 house only. Not needed: an empty session_id returns the whole year.

## Question index (BUILT and CHECKED)
- Script: build_question_index.py -> index/question_index.csv
- Columns: tenure, year, date, site_id, pdf_url
- Takes about 3 to 4 minutes (10 s delay per request)
- 633 sittings with a question list:
  - 2013-2018: 292
  - 2018-2023: 218
  - 2024-2029: 123 so far (latest = 28 Aug 2026, end of 29th Session)
- Sittings per calendar year: 2013: 36 | 2014: 53 | 2015: 57 | 2016: 67 | 2017: 53 | 2018: 43 | 2019: 38 | 2020: 35 | 2021: 50 | 2022: 46 | 2023: 32 | 2024: 38 | 2025: 53 | 2026: 32
  (2018 = 26 from the old house + 17 from the new house)
- CSV check passed: no blank cells, all dates parse, all dates inside their tenure's range, no duplicate URLs, all links are https na.gov.pk/uploads/documents/questions/*.pdf
- The 21 Aug 2026 file (6a880279aefbf_149.pdf) is in the index (site_id 987)
- Gotchas:
  - Same date can have TWO PDFs (6 cases, e.g. 26 Feb 2014, 15 Jan 2015). Different files and site_ids, probably separate question groups. NEVER use the date as a key. Use site_id or the URL.
  - First question list of each house comes late: 29 Jul 2013, 24 Sep 2018, 1 Apr 2024.
  - 7 rows fall on a weekend (19-20 Oct 2024, 14-15 Sep 2024, 9 Apr 2022, 3 Apr 2022, 13 Aug 2022). Look like real special sittings, not yet opened.
- Not yet checked: whether the list has gaps vs sittings actually held

## Question PDFs: one file tested per tenure (test_old_pdf.py <tenure>)
| Tenure | File | Size | Pages | Urdu pages | Near-empty pages |
|---|---|---|---|---|---|
| 2013-2018 | 21 Jan 2016 | 0.4 MB | 41 | none | none |
| 2018-2023 | 29 Oct 2020 | 0.4 MB | 36 | none | none |
| 2024-2029 | 14 Nov 2025 | 10.8 MB | 215 | none | 3, 4, 18, 71 |
| 2024-2029 | 21 Aug 2026 | 92 MB | 301 | 33-69 (Urdu translation) | 6 image-only pages |
- Only ONE file per tenure so far. Urdu blocks and big sizes are NOT a whole-house feature (14 Nov 2025 has none), so filter PAGE BY PAGE on every file.
- The test script counts Arabic, Arabic Supplement and both presentation-form ranges (an earlier version only counted \u0600-\u06FF).
- 21 Aug 2026 file layout:
  - pp 1-32 English oral questions + replies: CLEAN, core data
  - pp 33-69 Urdu translation: garbled text layer, DROP
  - pp 70-301 annexure tables: OCR noise, image-only pages. Store link only

## Question PDF format (checked on 2016 and 2026 files)
- Header: "(28th Session)", "QUESTIONS FOR ORAL ANSWERS AND THEIR REPLIES", "to be held on <date>". 2026 headers also show the group, e.g. "(4th Group, 29th Session)"
- Each question: number, optional * (starred), member name, optional "(Deferred on dd-mm-yyyy)", "Will the Minister for X be pleased to state", sub-parts (a)(b)(c), then reply starting "Minister for X (Name):"
- Parser quirks to handle:
  1. "@" before the number = transferred from another ministry. Store as a flag.
  2. Some questions have no reply, only "Transferred to ... for answer on Next Rota Day". Store as a status, not an answer.
  3. Question numbers are NOT in order (99 then 50).
  4. "(cid:147)" junk replaces bullet symbols. Strip with \(cid:\d+\)
  5. Ministry names wrap across lines. Match the reply start across lines.
  6. Replies run across pages. Remove page numbers/headers, then read the whole file as one stream.
  7. "Annexure has been placed in the National Assembly Library" = annexure not online.
- 2016 text layer is clean, no OCR errors seen

## Other PDF findings
- Orders of the Day: English pages first, then Urdu translation, DROP the Urdu
- Supplementary Orders of the Day: scanned + OCR errors, Urdu page extracts as Latin junk. Needs a word-quality check
- Bulletins: all English (checked by me, not yet by script)
- Bills: English first, Urdu translation after (checked by me, not yet by script)
- Debates: ~72% Urdu, text layer garbled (Jameel Noori Nastaleeq, no Unicode map). PARKED.
  Use only the English table of contents, leave lists, motions, resolutions + deep links to the PDF

## Rules for the extractor
- Filter pages by Arabic-script share, keep English pages
- Add a dictionary-word ratio check to catch OCR junk
- Flag low-text pages for review instead of loading them silently
- Every row stores source_url + retrieved_on
- Cache downloads, never fetch the same file twice (file sizes range from 0.4 MB to 92 MB)
- Key rows on site_id / pdf_url, never on date alone

## Still UNVERIFIED
- Attendance PDFs (layout, present-only list)
- Bulletins and bills: not yet run through the script
- Text quality of 2018-2023 and 2025 question files (language checked, layout not yet read)
- What the two-PDFs-per-date cases are
- What the 4 near-empty pages in the 14 Nov 2025 file contain
- Whether every 2013-2026 sitting has a PDF (index lists 633, gaps unchecked)
- Bill lists: introduced lists only seen for 2024 onward
- Permission for public redistribution in writing

## Done so far
- venv, git, repo pushed to GitHub (private), README and .gitignore added
- Found listing endpoints, tenure ids, year ids
- Built and checked the question index (633 sittings)
- Tested one question PDF per tenure

## Next
1. Write the question parser on the 2016 file (simplest layout)
2. Run it on 2020, 2025 and the first 32 pages of the 2026 file
3. Spot-check 20 parsed questions against the PDF
4. Check the two-PDFs-per-date cases
5. Attendance: find the listing endpoint, test one PDF