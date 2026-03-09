# Decision Rules

## Goal

Every cited item must satisfy one chain:

1. `existence`
2. `abstract relevance`
3. `landing correctness`

Only after all three are aligned can the reference be treated as fully verified.

Citation style is a separate layer. APA, GB/T 7714, Chicago, and similar formatting rules do not override failures in existence, relevance, or landing correctness.

## 1. Existence

Treat an item as existing only if at least one authoritative source confirms it:

- DOI registry metadata
- publisher landing page
- official journal abstract page
- official conference proceedings page
- official data release page
- official repository or documentation page for software or data items

If the title, author list, year, and venue do not line up, mark it unresolved.

## 2. Abstract Relevance

Use the abstract, official summary, or dataset description to judge the citing sentence.

### High relevance

- The cited sentence and the abstract are directly aligned.
- Example: a paper on tail risk is cited to support tail-risk measurement.

### Medium relevance

- The paper is related, but the citing sentence is broader than the abstract.
- Keep only if the prose is softened.

### Low relevance

- The citing sentence claims more than the paper actually studies.
- Revise the thesis text or replace the citation.

## 3. Landing Correctness

The DOI or URL must land on the page for the same item.

### Full confirmation

- Final page title matches the reference title, or
- The official page clearly identifies the same item by title and metadata.

### Not enough

- A redirect exists but lands on a different paper.
- The URL opens a search result, tokenized session page, or generic portal page.
- The DOI resolves, but the resolved item title does not match.
- Anti-bot or access-check blocks the request and no browser confirmation follows.

## 4. Chinese vs Non-Chinese Policy

## Chinese references

Preferred order:

1. official journal abstract page
2. stable DOI landing
3. official institutional page

Avoid:

- CNKI tokenized long URLs
- temporary portal links
- search-result pages
- URLs that require session state to identify the paper

If the DOI points to the wrong paper, delete the DOI from the reference record rather than keeping it.

## Non-Chinese references

Preferred order:

1. DOI canonical landing
2. publisher page
3. official proceedings page
4. DBLP, OpenReview, PMLR, or JMLR only when they are the authoritative public landing for that item

For conference papers, official proceedings or OpenReview pages are acceptable if they clearly match the cited title.

## 5. Anti-Bot Handling

Do not mark a link as fully verified just because the domain is correct.

If script-based access hits anti-bot protection:

1. try a browser probe if Playwright is available
2. inspect the final visible page title
3. compare title and metadata with the reference record

If the final landing still cannot be confirmed:

- mark the landing as unresolved
- replace the URL if a stable official page is available
- otherwise remove DOI or URL from the reference record

## 6. Final Actions

### Keep as is

- existence confirmed
- abstract relevance high
- landing correct

### Revise prose only

- existence confirmed
- landing correct
- relevance only medium

### Replace DOI or URL

- existence confirmed
- content relevant
- current landing wrong or unstable
- a better official landing exists

### Remove DOI or URL

- existence confirmed
- content relevant
- no correct or stable landing can be confirmed

### Replace citation

- existence confirmed
- landing correct or fixable
- cited content is low relevance or cite stretch
