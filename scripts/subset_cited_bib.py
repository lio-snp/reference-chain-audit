from __future__ import annotations

import argparse
import json
from pathlib import Path

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter


def main() -> None:
    parser = argparse.ArgumentParser(description="Write a cited-only BibTeX subset from citation contexts.")
    parser.add_argument("--bib", required=True)
    parser.add_argument("--contexts", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    bib_path = Path(args.bib).resolve()
    contexts_path = Path(args.contexts).resolve()
    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    payload = json.loads(contexts_path.read_text(encoding="utf-8"))
    citekeys = set(payload["citekeys"])

    parser_obj = BibTexParser(common_strings=True)
    with bib_path.open(encoding="utf-8") as fh:
        db = bibtexparser.load(fh, parser=parser_obj)

    filtered = [entry for entry in db.entries if entry.get("ID") in citekeys]
    out_db = bibtexparser.bibdatabase.BibDatabase()
    out_db.entries = filtered

    writer = BibTexWriter()
    writer.indent = "  "
    writer.order_entries_by = ("ID",)
    out_path.write_text(writer.write(out_db), encoding="utf-8")
    print(f"Wrote {len(filtered)} entries to {out_path}")


if __name__ == "__main__":
    main()
