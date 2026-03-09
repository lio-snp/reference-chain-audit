# Reference Chain Audit

A Codex skill and script bundle for auditing references end-to-end before final citation-style cleanup.

It checks three things for every cited item:

1. the cited item exists
2. the local claim is supported by the abstract, official summary, or dataset description
3. the DOI or URL lands on the correct page for that exact item

This repository is intended for thesis and paper workflows where a reference is not considered safe just because a DOI or URL is present.

## Positioning

This repository is best described as:

- style-agnostic at the audit and decision-rule layer
- LaTeX/BibTeX-first in the packaged automation
- usable with non-TeX workflows when citation contexts are supplied separately

It is not a general-purpose citation formatter. APA, GB/T 7714, Chicago, and similar styles are handled as a follow-up layer after the evidence chain is verified.

## What It Audits

A reference passes only if all three checks are satisfied:

- `existence`
- `local claim relevance`
- `landing correctness`

Examples of failures:

- the DOI resolves to a different paper
- the URL is a tokenized CNKI session link
- the title exists, but the cited sentence overclaims what the source actually studies
- the reference is formatted correctly in APA or GB/T 7714, but points to the wrong item

## Workflow Types

### 1. LaTeX plus BibTeX workflow

This is the most fully supported path.

- parse TeX citation commands
- build a cited-only BibTeX subset
- optionally extract hyperlinks from the compiled PDF
- build an audit matrix for manual or semi-automated review
- optionally run a browser probe for final landing-page confirmation

### 2. Non-TeX workflow

Word, Zotero, EndNote, CSL JSON, RIS, and mixed writing stacks can still use the audit logic.

Minimum practical inputs:

- a `citation_contexts.json` file that maps citekeys to local citation snippets
- a BibTeX export, or a metadata source converted into BibTeX
- optional compiled PDF for embedded-link evidence

The wrapper supports this path through `--contexts-json`.

## Citation Styles: APA and GB/T 7714

This repository does consider style requirements, but only as a separate layer.

### APA

Typical style-only issues include:

- capitalization and sentence-case versus title-case cleanup
- italics and punctuation
- retrieval date formatting

These do not override evidence-chain failures.

### GB/T 7714

Typical style-only issues include:

- type markers such as `[J]`, `[M]`, or `[EB/OL]`
- full-width versus half-width punctuation
- author presentation rules required by the target institution

These do not override evidence-chain failures.

For more, see:

- `references/style-scope.md`
- `references/decision-rules.md`

## Repository Layout

```text
reference-chain-audit/
├── SKILL.md
├── README.md
├── requirements.txt
├── requirements-optional.txt
├── agents/
│   └── openai.yaml
├── examples/
│   └── non_tex/
│       ├── README.md
│       └── citation_contexts.sample.json
├── references/
│   ├── decision-rules.md
│   ├── report-template.md
│   └── style-scope.md
└── scripts/
    ├── build_reference_audit_matrix.py
    ├── extract_citation_contexts.py
    ├── extract_pdf_links.py
    ├── link_browser_probe.py
    ├── run_reference_chain_audit.py
    └── subset_cited_bib.py
```

## Installation

### Core dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Optional browser probing

```bash
pip install -r requirements-optional.txt
python -m playwright install chromium
```

## Quick Start

### LaTeX plus BibTeX

```bash
python3 scripts/run_reference_chain_audit.py \
  --main-tex writing/paper/main.tex \
  --bib writing/paper/references.bib \
  --pdf writing/paper/build/main.pdf \
  --outdir writing/paper/build/reference_audit
```

### Non-TeX workflow

```bash
python3 scripts/run_reference_chain_audit.py \
  --contexts-json examples/non_tex/citation_contexts.sample.json \
  --bib writing/paper/references.bib \
  --outdir writing/paper/build/reference_audit
```

### Optional Bib-Check stage

If you have a local clone of Bib-Check, the wrapper can use it from:

1. `--bibcheck-root`
2. `$BIBCHECK_ROOT`
3. `<repo>/_external/Bib-Check`

Example:

```bash
python3 scripts/run_reference_chain_audit.py \
  --main-tex writing/paper/main.tex \
  --bib writing/paper/references.bib \
  --outdir writing/paper/build/reference_audit \
  --run-bibcheck \
  --bibcheck-root /path/to/Bib-Check
```

## Outputs

Typical outputs include:

- `citation_contexts.json`
- `cited_subset.bib`
- `pdf_reference_links.json`
- `reference_audit_matrix.json`
- a report based on `references/report-template.md`

## Decision Policy

Default policy highlights:

- prefer stable official landing pages over search or session pages
- prefer DOI canonical links or official publisher pages for non-Chinese references
- prefer official journal abstract pages or stable DOI landings for Chinese references
- avoid tokenized CNKI links
- if the correct landing page cannot be confirmed, remove or replace DOI or URL instead of keeping a risky link

## Boundaries

Current packaged automation is strongest for:

- LaTeX citation extraction
- BibTeX metadata handling
- PDF hyperlink extraction

If you want deeper support for Word, Zotero, CSL JSON, or RIS workflows, the next practical extension is to add importers that generate `citation_contexts.json` and normalized metadata automatically.

## Roadmap

Reasonable next additions:

- CSL JSON importer
- RIS importer
- style-only checker for APA and GB/T 7714
- richer matching between PDF links and reference metadata

## Codex Skill Usage

This repository is structured as a Codex skill.

- `SKILL.md` defines when and how the skill should be used
- `agents/openai.yaml` provides metadata for agent packaging
- `references/` contains the decision rules and reporting templates used by the skill

## Publishing Guidance

If you promote this repository on GitHub, describe it as:

- reference evidence audit
- style-agnostic at the rule layer
- LaTeX/BibTeX-first starter tooling

That description is accurate and sets the right expectation for APA, GB/T 7714, and non-TeX workflows.
