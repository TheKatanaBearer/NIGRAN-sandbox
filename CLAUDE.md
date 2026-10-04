# NIGRAN sandbox: briefing for the coding agent

## What this is
Throwaway scaffold for NIGRAN, a planned public tracker of National Assembly of Pakistan records. A final-year CS project. Read NOTES.md first: it holds everything verified so far. This repo is for learning how na.gov.pk and its PDFs behave. A formal repo comes later.

## Decisions already made (do not reopen)
- Source is na.gov.pk only. Credit it and link every record to its source PDF.
- Publish derived data only. Never commit or republish PDFs (data/ and out/ are gitignored).
- Phase 1 sources, in this order: questions, bulletins, Orders of the Day, bills/acts lists, attendance.
- Debates are PARKED (about 72% Urdu, text layer is garbled). Use only their English table of contents later.
- The owner will not contact the NA Secretariat.
- Tone is descriptive. No scores or rankings of members.

## Crawling rules
- At least 10 seconds between requests (robots.txt Crawl-delay).
- Send the User-Agent with the owner's contact email on every request.
- Cache every download and never fetch a file twice. Files range from 0.4 MB to 92 MB.
- Ask before any bulk download of more than about 20 files.

## Data rules
- Never use the date as a key. Use site_id or pdf_url. One date can have two PDFs.
- Filter PDF pages by script share: drop pages with more Arabic-script than Latin characters, and flag near-empty pages (under 50 characters) for review. Never load flagged pages silently.
- Every row stores source_url and retrieved_on.
- PDF links in listing pages are relative. Resolve with urljoin against https://na.gov.pk/en/questions.php.

## Parser lessons (question PDFs)
- Header lines look like "93. Ms. Name" with or without a colon, and an optional * or @ prefix. A header only counts if the next line starts with "(Deferred" or "Will ".
- Replies can be answered, "Transferred to ...", "Reply not Received", or "Disallowed ...". Store as status.
- "be pleased to refer to <earlier question> and to state" exists. Store the earlier question as refers_to.
- ALWAYS verify with the phrase check: count of "be pleased to" in the text must match the number of questions parsed. A mismatch means missed or merged questions.
- Question numbers are not in order. Replies run across pages. Strip (cid:NNN) junk.

## Working style
- Work in small steps. After each step, print a short summary with counts and any anomalies.
- Never claim something works without running it. Report errors plainly.
- Update NOTES.md with every new finding.