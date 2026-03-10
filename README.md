# Reference Chain Audit

English | [简体中文](README_zh.md)

An agent-first skill for Codex, Claude Code, and similar coding agents to audit references end-to-end before final citation-style cleanup.

It packages a reusable reference-audit skill together with optional helper scripts for extraction, normalization, and evidence gathering.

## What This Repo Is

This repo gives an agent a simple job:

1. verify the cited item exists
2. verify the local claim is actually supported
3. verify the DOI or URL lands on the correct page
4. separate those findings from style-only issues such as APA or GB/T 7714 formatting

The scripts in `scripts/` are optional helpers. They are there to accelerate extraction, normalization, and evidence gathering when useful. They are not meant to be a required checklist that every user must run manually.

## Default Usage

Recommended usage:

- give the draft, references, or exported metadata to the agent
- ask the agent to audit references using this skill
- let the agent decide whether helper scripts are worth using

Most users should start with a prompt like:

```text
Audit the references in this paper using the reference-chain-audit skill.
Focus on existence, local claim relevance, and landing correctness.
Treat APA or GB/T issues as style follow-up only.
Use any helper scripts only if they actually save time.
```

## Core Audit Logic

A reference passes only if all three checks are satisfied:

- `existence`
- `local claim relevance`
- `landing correctness`

Examples of failure:

- the DOI resolves to a different paper
- the URL is a CNKI tokenized session link
- the cited sentence overclaims what the source actually studies
- the entry looks correct in APA or GB/T 7714, but points to the wrong item

## Skill-First Workflow

### 1. Gather local citation evidence

The agent finds where each reference is cited and what the surrounding sentence is actually claiming.

### 2. Normalize metadata when needed

If the available references are messy, the agent may normalize them into BibTeX or another structured form.

### 3. Audit the evidence chain

The agent checks:

- existence
- relevance to the local claim
- landing correctness

### 4. Handle style separately

APA, GB/T 7714, Chicago, and similar formats are a follow-up layer.

### 5. Produce a report

The agent should output clear decisions such as:

- keep as is
- revise prose
- replace DOI or URL
- remove DOI or URL
- replace citation

## Optional Helper Scripts

Use these only when they reduce work.

- `scripts/run_reference_chain_audit.py`
  - wrapper for the packaged extraction and matrix workflow
- `scripts/extract_citation_contexts.py`
  - TeX citation-context extraction
- `scripts/subset_cited_bib.py`
  - cited-only BibTeX subset generation
- `scripts/import_csl_json.py`
  - CSL JSON to BibTeX plus citekey mapping and contexts skeleton
- `scripts/extract_pdf_links.py`
  - compiled PDF hyperlink extraction
- `scripts/link_browser_probe.py`
  - optional browser landing-page probe
- `scripts/build_reference_audit_matrix.py`
  - review-matrix generation

## Non-TeX Workflows

Non-TeX workflows are supported in an agent-first way.

The agent can work from:

- `citation_contexts.json`
- BibTeX or equivalent metadata
- CSL JSON exports from Zotero or similar tools
- compiled PDFs with embedded links

If CSL JSON is available, the agent may optionally call `scripts/import_csl_json.py` to generate:

- BibTeX
- a citekey mapping
- a `citation_contexts.json` skeleton

## Repository Layout

```text
reference-chain-audit/
├── SKILL.md
├── LICENSE
├── README.md
├── README_zh.md
├── agents/
├── references/
├── scripts/
└── examples/
```

## What To Read

- `SKILL.md`
  - the main skill behavior
- `references/decision-rules.md`
  - keep, replace, or remove DOI/URL decisions
- `references/style-scope.md`
  - APA and GB/T as style-only follow-up
- `references/report-template.md`
  - structured reporting template

## Boundaries

This is not a general-purpose citation formatter.

It is a reference evidence audit skill.

The packaged automation is strongest for:

- LaTeX citation extraction
- BibTeX metadata handling
- CSL JSON import
- PDF hyperlink extraction

But the audit logic itself is broader than those formats.

## For GitHub Promotion

The most accurate short description is:

- reference evidence audit skill
- agent-first workflow
- LaTeX/BibTeX-first helper tooling
- practical CSL JSON bridge for non-TeX workflows
