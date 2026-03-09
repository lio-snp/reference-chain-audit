# Non-TeX Example

Use this example when your writing stack is not LaTeX.

The minimal requirement is a `citation_contexts.json` file that contains:

- `citekeys`: the ordered list of citekeys actually used in the document
- `contexts`: a mapping from citekey to one or more local citation snippets

The wrapper can then reuse the same audit logic:

```bash
python3 scripts/run_reference_chain_audit.py \
  --contexts-json examples/non_tex/citation_contexts.sample.json \
  --bib path/to/references.bib \
  --outdir path/to/reference_audit
```

If your source references come from Zotero, EndNote, CSL JSON, RIS, or Word, export or convert them into BibTeX first when possible.
