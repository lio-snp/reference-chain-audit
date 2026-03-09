# Style Scope

## Why This File Exists

This skill audits the evidence chain behind each reference. Citation style is a separate concern.

A reference can be:

- correctly formatted in APA or GB/T 7714 but still fail the audit because it cites the wrong item or uses a bad landing page
- evidence-chain correct but still need style cleanup before submission

Treat these as two layers:

1. evidence-chain validity
2. final style formatting

## What The Packaged Tooling Supports Today

The bundled scripts are strongest in LaTeX plus BibTeX workflows:

- `scripts/extract_citation_contexts.py` parses TeX citation commands
- `scripts/subset_cited_bib.py` creates a cited-only BibTeX subset
- `scripts/build_reference_audit_matrix.py` merges metadata, contexts, and optional PDF link evidence
- `scripts/extract_pdf_links.py` inspects compiled PDF hyperlinks
- `scripts/run_reference_chain_audit.py` now accepts either `--main-tex` or `--contexts-json`

This means the skill is best described as:

- style-agnostic at the audit and decision-rule level
- LaTeX/BibTeX-first in the packaged starter tooling

## Using The Skill Outside LaTeX

For Word, Zotero, EndNote, CSL JSON, RIS, or mixed workflows, the audit still applies if you provide equivalent inputs.

Minimum practical inputs:

- `citation_contexts.json` with citekeys and local citing snippets
- a BibTeX export or another metadata source that can be converted into BibTeX for the matrix-building scripts
- optional compiled PDF if you want embedded-link evidence

If you cannot produce a BibTeX export, you can still apply the decision rules manually, but some packaged scripts will be less useful.

## APA Notes

Treat these as style-level concerns unless they change the identity of the cited item:

- title case or sentence case adjustments
- italics and punctuation
- author separator details
- retrieval date formatting

Evidence-chain requirements still override style:

- prefer canonical DOI links such as `https://doi.org/...`
- do not keep a DOI that resolves to the wrong item just because the APA string looks complete
- use retrieval dates mainly for changing web resources, not static journal articles

## GB/T 7714 Notes

Treat these as style-level concerns unless they change the identity of the cited item:

- reference type markers such as `[J]`, `[M]`, or `[EB/OL]`
- punctuation style and full-width versus half-width conventions
- author name presentation and ordering rules required by the target institution

Evidence-chain requirements still override style:

- do not keep CNKI tokenized long URLs just to satisfy the appearance of a complete entry
- prefer stable DOI landings or official journal pages when they identify the same item
- if the landing cannot be confirmed, remove or replace the DOI or URL before polishing GB/T punctuation

## Recommended GitHub Positioning

If you publish this skill, describe it as:

- a reference evidence audit skill
- style-agnostic at the rule layer
- LaTeX/BibTeX-first in the packaged automation

That framing is more accurate than claiming full automatic support for every citation manager or every style guide.
