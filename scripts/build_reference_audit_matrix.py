from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import bibtexparser
from bibtexparser.bparser import BibTexParser


def normalize_url(value: str) -> str:
    return value.strip().rstrip("/").lower()


def detect_language(entry: dict) -> str:
    lang = (entry.get("language") or entry.get("langid") or "").lower()
    if "chinese" in lang:
        return "chinese"
    text = " ".join([entry.get("author", ""), entry.get("title", ""), entry.get("journal", "")])
    return "chinese" if re.search(r"[\u4e00-\u9fff]", text) else "non_chinese"


def recommended_policy(language: str) -> str:
    if language == "chinese":
        return "Prefer official journal abstract pages or stable DOI; avoid CNKI tokenized links."
    return "Prefer DOI canonical links or official publisher/proceedings pages."


def match_pdf_links(entry: dict, pdf_links: list[dict]) -> list[dict]:
    hits = []
    doi = (entry.get("doi") or "").strip().lower()
    url = (entry.get("url") or "").strip().lower()
    for row in pdf_links:
        uri = row["uri"].strip().lower()
        if doi and doi in uri:
            hits.append(row)
            continue
        if url and normalize_url(url) == normalize_url(uri):
            hits.append(row)
    return hits


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge bib entries, citation contexts, and PDF link evidence into one audit matrix.")
    parser.add_argument("--bib", required=True)
    parser.add_argument("--contexts", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--pdf-links", default="")
    args = parser.parse_args()

    bib_path = Path(args.bib).resolve()
    contexts_path = Path(args.contexts).resolve()
    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    parser_obj = BibTexParser(common_strings=True)
    with bib_path.open(encoding="utf-8") as fh:
        db = bibtexparser.load(fh, parser=parser_obj)

    contexts_payload = json.loads(contexts_path.read_text(encoding="utf-8"))
    contexts = contexts_payload["contexts"]
    ordered_keys = contexts_payload["citekeys"]

    pdf_links = []
    if args.pdf_links:
        pdf_path = Path(args.pdf_links).resolve()
        if pdf_path.exists():
            pdf_links = json.loads(pdf_path.read_text(encoding="utf-8"))

    entry_map = {entry["ID"]: entry for entry in db.entries}
    matrix = []
    for key in ordered_keys:
        entry = entry_map.get(key, {})
        language = detect_language(entry) if entry else "unknown"
        matched_links = match_pdf_links(entry, pdf_links) if entry else []
        matrix.append(
            {
                "key": key,
                "title": entry.get("title", ""),
                "language": language,
                "entry_type": entry.get("ENTRYTYPE", ""),
                "author": entry.get("author", ""),
                "year": entry.get("year", ""),
                "journal_or_booktitle": entry.get("journal") or entry.get("booktitle") or entry.get("publisher") or "",
                "doi": entry.get("doi", ""),
                "url": entry.get("url", ""),
                "contexts": contexts.get(key, []),
                "pdf_link_candidates": matched_links,
                "existence_status": "pending",
                "abstract_relation_status": "pending",
                "landing_status": "pending",
                "recommended_action": "pending",
                "policy_note": recommended_policy(language),
            }
        )

    out_path.write_text(json.dumps(matrix, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(matrix)} audit rows to {out_path}")


if __name__ == "__main__":
    main()
