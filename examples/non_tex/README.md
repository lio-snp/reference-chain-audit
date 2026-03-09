# Non-TeX Example

Use this example when your writing stack is not LaTeX.

There are now two practical entry points.

## 1. Start from a CSL JSON export

If you exported references from Zotero or another reference manager as CSL JSON, first convert them into audit inputs:

```bash
python3 scripts/import_csl_json.py \
  --csl-json examples/non_tex/csl_items.sample.json \
  --out-bib path/to/references.bib \
  --out-mapping path/to/csl_mapping.json \
  --out-contexts-skeleton path/to/citation_contexts.json
```

This creates:

- a BibTeX file for the audit scripts
- a mapping from original CSL item ids to generated citekeys
- a `citation_contexts.json` skeleton that you can fill with real local citation snippets

## 2. Run the main audit wrapper

After you fill the citation contexts with real snippets from Word, Markdown, notes, or another writing source:

```bash
python3 scripts/run_reference_chain_audit.py \
  --contexts-json path/to/citation_contexts.json \
  --bib path/to/references.bib \
  --outdir path/to/reference_audit
```

## Minimal context format

The `citation_contexts.json` file should contain:

- `citekeys`: the ordered list of citekeys actually used in the document
- `contexts`: a mapping from citekey to one or more local citation snippets

The sample `citation_contexts.sample.json` in this folder shows the expected structure.
