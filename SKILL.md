---
name: reference-chain-audit
description: Audit cited references end-to-end before final style cleanup: verify the cited item exists, the local claim is supported by the abstract or official summary, and the DOI or URL lands on the correct item page. Use when checking thesis or paper references across LaTeX/BibTeX workflows, validating PDF hyperlinks, importing CSL JSON metadata for non-TeX workflows, or separating evidence-chain failures from style-only issues such as APA or GB/T 7714 formatting.
---

# Reference Chain Audit

Use this skill when the goal is to make every cited reference satisfy the same three-step chain:

1. The item exists.
2. Its abstract, official summary, or dataset description supports the local citing sentence.
3. The DOI or URL lands on the correct page for that exact item.

This skill is about reference evidence, not just reference formatting. A citation that looks correct in APA or GB/T 7714 can still fail if the linked item is wrong, irrelevant to the local claim, or points to an unstable landing page.

## Scope

### Evidence-chain audit

A reference passes only if all three checks are true:

1. `existence`
2. `local claim relevance`
3. `landing correctness`

### Style follow-up

APA, GB/T 7714, Chicago, and similar styles are handled as a separate formatting layer.

- Style issues do not override evidence-chain failures.
- Style cleanup happens after the existence, relevance, and landing checks are complete.
- Packaged tooling in this skill is LaTeX/BibTeX-first, but the decision rules also apply to Word, Zotero, EndNote, CSL JSON, or RIS workflows if citation contexts are supplied separately.

## Workflow

1. Build or supply the cited set and citation contexts.
- For LaTeX workflows, run `scripts/extract_citation_contexts.py` on the main TeX file.
- For non-TeX workflows, prepare an equivalent `citation_contexts.json` and pass it to the wrapper with `--contexts-json`.
- If your references start as CSL JSON, first run `scripts/import_csl_json.py` to generate BibTeX plus a contexts skeleton.
- The context file should identify each citekey and the local sentence or paragraph where it is cited.

2. Prepare the cited metadata set.
- For LaTeX plus BibTeX workflows, run `scripts/subset_cited_bib.py` on the master `.bib`.
- For CSL JSON workflows, use `scripts/import_csl_json.py` to convert the export into BibTeX and a citekey mapping.
- For other writing stacks, export or convert the cited references into a BibTeX file when possible.
- Treat BibTeX here as a practical metadata carrier, not as a requirement imposed by the audit logic itself.

3. Run Bib-Check if a local clone exists.
- Preferred resolution order is:
  - `--bibcheck-root`
  - `$BIBCHECK_ROOT`
  - `<skill>/_external/Bib-Check`
- Run offline first if network is unavailable.
- Run online only when the environment permits.
- Bib-Check is a screening stage, not the final decision stage.
- The wrapper routes `BIBCHECK_CACHE_DIR` into the output directory to avoid default user-home cache assumptions.

4. Build the verification matrix.
- Run `scripts/build_reference_audit_matrix.py`.
- This merges reference metadata, citation contexts, and optional PDF hyperlink evidence into one JSON matrix.

5. Verify landing pages.
- Extract the hyperlinks embedded in the compiled PDF with `scripts/extract_pdf_links.py`.
- If Playwright is installed and browser verification is needed, run `scripts/link_browser_probe.py`.
- If Playwright is not available, do not mark the link as fully confirmed just because the string looks valid.

6. Apply decision rules.
- Read `references/decision-rules.md`.
- Chinese and non-Chinese references follow different link policies.
- Read `references/style-scope.md` when APA, GB/T 7714, or another citation style is part of scope.
- If the correct DOI or URL cannot be confirmed, remove it rather than keeping a risky link.

7. Write or update the audit report.
- Use `references/report-template.md`.
- Findings should separate:
  - existence
  - local claim relevance
  - landing correctness
  - final action
  - style-only follow-up

## What Counts As Pass / Fail

A reference passes only if all of the following are true:
- The paper, book, dataset, software release, or official resource exists.
- The abstract or official summary supports the claim where it is cited.
- The DOI or URL reaches the correct landing page for that exact item.

The following do not count as full confirmation on their own:
- The link string exists in the reference manager export.
- The domain looks plausible.
- Bib-Check returned only a warning.
- A DOI resolves somewhere, but the page title does not match the cited item.
- A script hits anti-bot protection before the final landing page and no browser confirmation follows.
- The entry is formatted correctly in APA or GB/T 7714, but the linked item is not actually the cited one.

## Bundled Scripts

- `scripts/extract_citation_contexts.py`
  - Recursively parses the main TeX file and all `\input` / `\include` files.
  - Outputs actual cited keys and local context snippets.
- `scripts/subset_cited_bib.py`
  - Writes a cited-only BibTeX file for focused checking.
- `scripts/import_csl_json.py`
  - Imports a CSL JSON export into BibTeX, a citekey mapping, and an optional citation-context skeleton.
- `scripts/extract_pdf_links.py`
  - Extracts external hyperlinks from the compiled PDF and saves page-level evidence.
- `scripts/build_reference_audit_matrix.py`
  - Merges BibTeX fields, citation contexts, and optional PDF link evidence into one matrix.
- `scripts/link_browser_probe.py`
  - Optional Playwright-based final landing-page probe when browser automation is available.
- `scripts/run_reference_chain_audit.py`
  - Wrapper for the standard sequence above.
  - Supports either `--main-tex` or precomputed `--contexts-json` so non-TeX workflows can reuse the audit rules.

## When To Read References

- Read `references/decision-rules.md` before deciding whether to keep, replace, or remove a DOI or URL.
- Read `references/style-scope.md` when citation-style requirements such as APA or GB/T 7714 are in scope.
- Read `references/report-template.md` when producing the final verification report.

## Default Output

Prefer writing audit artifacts into the paper build directory, for example:
- `writing/paper/build/citation_contexts.json`
- `writing/paper/build/cited_subset.bib`
- `writing/paper/build/pdf_reference_links.json`
- `writing/paper/build/reference_audit_matrix.json`
- `writing/paper/build/reference_audit_report.md`

## Default Policy

- Prefer stable official landings over session-based links.
- For Chinese journal articles, prefer official journal abstract pages or stable DOI landings. Avoid CNKI tokenized long URLs.
- For non-Chinese journal articles, prefer DOI canonical links or publisher landing pages.
- For datasets and software, prefer official data-release or repository pages.
- If the correct landing page cannot be confirmed, remove DOI or URL instead of leaving a likely wrong one.
- Perform evidence-chain audit first, then fix style-specific output such as APA or GB/T 7714 punctuation, casing, and type markers.
