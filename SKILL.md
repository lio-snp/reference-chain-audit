---
name: reference-chain-audit
description: Agent-first skill for auditing thesis or paper references end-to-end. Verify existence, local claim relevance, and DOI or URL landing correctness before final APA or GB/T cleanup. Use when Codex, Claude Code, or a similar agent should drive the audit and optionally call helper scripts when they actually save time.
---

# Reference Chain Audit

Use this skill when an agent needs to audit cited references for a thesis, paper, report, or literature review.

The skill is built around one evidence chain:

1. the cited item exists
2. the local claim is supported by the abstract, official summary, or dataset description
3. the DOI or URL lands on the correct page for that exact item

This is a skill first and a script bundle second.

- The agent should own the reasoning and the final judgment.
- The bundled scripts are optional helpers.
- Do not force the user into a script-heavy workflow if the agent can do the work directly from the available files and context.

## Default Agent Posture

By default, the agent should:

1. identify the cited items and local citation context
2. audit existence, relevance, and landing correctness
3. separate evidence-chain failures from style-only issues
4. produce a clear audit report with keep, revise, replace, or remove decisions

The agent may use helper scripts when they reduce manual work, but the scripts are not the product. The product is a defensible audit decision.

## What Counts As Pass / Fail

A reference passes only if all of the following are true:

- The paper, book, dataset, software release, or official resource exists.
- The abstract or official summary supports the local claim where it is cited.
- The DOI or URL reaches the correct landing page for that exact item.

The following do not count as full confirmation on their own:

- the link string exists in a BibTeX entry or reference-manager export
- the domain looks plausible
- a DOI resolves somewhere, but the resolved page does not match the cited item
- a script hits anti-bot protection before final confirmation
- the reference is formatted correctly in APA or GB/T 7714, but the underlying item or landing page is wrong

## Recommended Agent Workflow

### 1. Gather the local citation evidence

Find where each reference is used and what the nearby sentence is actually claiming.

- If the writing stack is LaTeX, the agent may call `scripts/extract_citation_contexts.py`.
- If the writing stack is not LaTeX, the agent may build or request `citation_contexts.json` manually.
- If the source references are exported as CSL JSON, the agent may call `scripts/import_csl_json.py` to bridge them into BibTeX plus a contexts skeleton.

### 2. Normalize the reference metadata

Get the cited set into a form the agent can inspect reliably.

- BibTeX is the easiest packaged path.
- For LaTeX workflows, the agent may call `scripts/subset_cited_bib.py`.
- For non-TeX workflows, the agent may import CSL JSON or manually normalize the cited references.

### 3. Audit the evidence chain

For each cited item, check:

- existence
- local claim relevance
- landing correctness

Use primary or authoritative pages whenever possible.

### 4. Handle style separately

APA, GB/T 7714, Chicago, and similar styles belong to a follow-up formatting layer.

- Style issues do not override evidence-chain failures.
- Fix citation style after the evidence chain is clean.

### 5. Write the decision report

Use `references/report-template.md` when a structured report is useful.

The final report should clearly distinguish:

- evidence-chain failures
- style-only follow-up items
- recommended actions

## Optional Helper Scripts

These scripts exist to accelerate specific subtasks. They are optional.

- `scripts/run_reference_chain_audit.py`
  - wrapper for the standard extraction and matrix-building flow
  - useful when the workspace already fits the packaged assumptions
- `scripts/extract_citation_contexts.py`
  - extracts TeX citation contexts
- `scripts/subset_cited_bib.py`
  - writes a cited-only BibTeX subset
- `scripts/import_csl_json.py`
  - converts CSL JSON into BibTeX, a citekey mapping, and an optional contexts skeleton
- `scripts/extract_pdf_links.py`
  - extracts hyperlinks embedded in the compiled PDF
- `scripts/link_browser_probe.py`
  - optionally confirms landing pages in a browser
- `scripts/build_reference_audit_matrix.py`
  - builds a review matrix from metadata plus contexts

Use them when they save time. Skip them when direct agent reasoning is faster or the user only needs a light audit.

## When To Read References

- Read `references/decision-rules.md` before deciding whether to keep, replace, or remove a DOI or URL.
- Read `references/style-scope.md` when APA, GB/T 7714, or another style guide is in scope.
- Read `references/report-template.md` when producing a final audit report.

## Scope Boundaries

This skill is strongest when the agent has at least one of the following:

- the draft text with local citation context
- BibTeX or equivalent metadata
- a compiled PDF with embedded reference links
- a CSL JSON export from Zotero or a similar manager

The packaged automation is currently strongest for:

- LaTeX citation extraction
- BibTeX metadata handling
- CSL JSON import into BibTeX plus citekey mapping
- PDF hyperlink extraction

That is a tooling boundary, not a reasoning boundary. The agent can still apply the audit rules outside those exact formats.

## Default Policy

- Prefer stable official landings over search-result or session-based links.
- For Chinese journal articles, prefer official journal abstract pages or stable DOI landings. Avoid CNKI tokenized long URLs.
- For non-Chinese journal articles, prefer DOI canonical links or publisher landing pages.
- For datasets and software, prefer official release or repository pages.
- If the correct landing page cannot be confirmed, remove or replace DOI or URL instead of leaving a risky link.
- Perform evidence-chain audit first, then fix APA, GB/T 7714, or other style-specific punctuation and formatting.
