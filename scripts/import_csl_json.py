from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


STOPWORDS = {
    "a",
    "an",
    "and",
    "for",
    "in",
    "of",
    "on",
    "the",
    "to",
    "with",
    "using",
}

TYPE_MAP = {
    "article-journal": "article",
    "article-magazine": "article",
    "article-newspaper": "article",
    "paper-conference": "inproceedings",
    "chapter": "incollection",
    "book": "book",
    "thesis": "phdthesis",
    "report": "techreport",
    "webpage": "misc",
    "post-weblog": "misc",
    "post": "misc",
    "dataset": "misc",
    "software": "misc",
}

DATE_FIELDS = ["issued", "published-print", "published-online", "created"]


def coerce_text(value: object) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        return " ".join(str(part).strip() for part in value if str(part).strip()).strip()
    return ""


def coerce_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(part).strip() for part in value if str(part).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def pick_field(item: dict, *names: str) -> str:
    for name in names:
        value = item.get(name)
        text = coerce_text(value)
        if text:
            return text
    return ""


def extract_year(item: dict) -> str:
    for field in DATE_FIELDS:
        payload = item.get(field)
        if not isinstance(payload, dict):
            continue
        date_parts = payload.get("date-parts")
        if isinstance(date_parts, list) and date_parts and date_parts[0]:
            year = str(date_parts[0][0]).strip()
            if year:
                return year
        raw = str(payload.get("raw", "")).strip()
        match = re.search(r"(19|20)\d{2}", raw)
        if match:
            return match.group(0)
    return ""


def format_person(person: dict) -> str:
    literal = str(person.get("literal", "")).strip()
    if literal:
        return literal
    family = str(person.get("family", "")).strip()
    given = str(person.get("given", "")).strip()
    if family and given:
        return f"{family}, {given}"
    return family or given


def format_people(people: object) -> str:
    if not isinstance(people, list):
        return ""
    parts = [format_person(person) for person in people if isinstance(person, dict)]
    return " and ".join(part for part in parts if part)


def pick_container_title(item: dict) -> str:
    return pick_field(item, "container-title", "collection-title")


def normalize_doi(value: str) -> str:
    text = value.strip()
    if not text:
        return ""
    text = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", text, flags=re.I)
    text = re.sub(r"^doi:\s*", "", text, flags=re.I)
    return text.strip()


def sanitize_token(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def title_token(title: str) -> str:
    words = [word for word in re.findall(r"[A-Za-z0-9]+", title.lower()) if word not in STOPWORDS]
    if not words:
        return "ref"
    return "".join(words[:2])[:20]


def author_token(item: dict) -> str:
    people = item.get("author") or item.get("editor") or []
    if isinstance(people, list) and people:
        person = people[0]
        if isinstance(person, dict):
            raw = person.get("family") or person.get("literal") or person.get("given") or ""
            token = sanitize_token(str(raw))
            if token:
                return token[:16]
    title = pick_field(item, "title")
    token = sanitize_token(title)
    return token[:16] or "ref"


def generated_citekey(item: dict) -> str:
    year = extract_year(item) or "nd"
    title = title_token(pick_field(item, "title"))
    return f"{author_token(item)}{year}{title}"[:48]


def sanitize_id(raw: str) -> str:
    token = re.sub(r"[^A-Za-z0-9:_-]+", "", raw.strip())
    if token and token[0].isdigit():
        token = f"ref{token}"
    return token


def choose_citekey(item: dict, mode: str, seen: set[str]) -> str:
    candidate = ""
    if mode == "id":
        candidate = sanitize_id(str(item.get("id", "")))
    if not candidate:
        candidate = generated_citekey(item)
    if not candidate:
        candidate = f"ref{len(seen) + 1}"

    base = candidate
    suffix = 2
    while candidate in seen:
        candidate = f"{base}_{suffix}"
        suffix += 1
    seen.add(candidate)
    return candidate


def entry_type_for(item: dict) -> str:
    csl_type = str(item.get("type", "")).strip().lower()
    return TYPE_MAP.get(csl_type, "misc")


def build_entry(item: dict, citekey: str) -> dict:
    entry_type = entry_type_for(item)
    entry = {"ID": citekey, "ENTRYTYPE": entry_type}

    author = format_people(item.get("author"))
    editor = format_people(item.get("editor"))
    title = pick_field(item, "title")
    container = pick_container_title(item)
    year = extract_year(item)
    publisher = pick_field(item, "publisher")
    doi = normalize_doi(pick_field(item, "DOI", "doi"))
    url = pick_field(item, "URL", "url")
    language = pick_field(item, "language")
    abstract = pick_field(item, "abstract")
    volume = pick_field(item, "volume")
    issue = pick_field(item, "issue")
    pages = pick_field(item, "page")
    number = issue
    keywords = ", ".join(coerce_list(item.get("keyword")))
    note = ""
    original_id = str(item.get("id", "")).strip()
    if original_id:
        note = f"Original CSL id: {original_id}"

    if author:
        entry["author"] = author
    elif editor:
        entry["editor"] = editor

    if title:
        entry["title"] = title
    if year:
        entry["year"] = year
    if doi:
        entry["doi"] = doi
    if url:
        entry["url"] = url
    if language:
        entry["language"] = language
    if abstract:
        entry["abstract"] = abstract
    if volume:
        entry["volume"] = volume
    if number:
        entry["number"] = number
    if pages:
        entry["pages"] = pages
    if keywords:
        entry["keywords"] = keywords
    if note:
        entry["note"] = note

    isbn = pick_field(item, "ISBN", "isbn")
    issn = pick_field(item, "ISSN", "issn")
    if isbn:
        entry["isbn"] = isbn
    if issn:
        entry["issn"] = issn

    if entry_type == "article":
        if container:
            entry["journal"] = container
    elif entry_type == "inproceedings":
        booktitle = container or pick_field(item, "event-title")
        if booktitle:
            entry["booktitle"] = booktitle
        event_place = pick_field(item, "event-place")
        if event_place:
            entry["address"] = event_place
        if publisher:
            entry["publisher"] = publisher
    elif entry_type == "incollection":
        if container:
            entry["booktitle"] = container
        if publisher:
            entry["publisher"] = publisher
    elif entry_type == "book":
        if publisher:
            entry["publisher"] = publisher
    elif entry_type == "phdthesis":
        if publisher:
            entry["school"] = publisher
        thesis_type = pick_field(item, "genre")
        if thesis_type:
            entry["type"] = thesis_type
    elif entry_type == "techreport":
        if publisher:
            entry["institution"] = publisher
        report_number = pick_field(item, "number")
        if report_number:
            entry["number"] = report_number
    else:
        if publisher:
            entry["publisher"] = publisher
        howpublished = pick_field(item, "medium")
        if howpublished:
            entry["howpublished"] = howpublished

    return entry


def load_items(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        items = payload.get("items")
        if isinstance(items, list):
            return [item for item in items if isinstance(item, dict)]
    raise SystemExit("CSL JSON must be a list of items or an object with an `items` list.")


def write_bib(entries: list[dict], out_path: Path) -> None:
    try:
        import bibtexparser
        from bibtexparser.bwriter import BibTexWriter
    except Exception as exc:
        raise SystemExit("bibtexparser is required for CSL JSON import. Install dependencies with `pip install -r requirements.txt`.") from exc

    db = bibtexparser.bibdatabase.BibDatabase()
    db.entries = entries
    writer = BibTexWriter()
    writer.indent = "  "
    writer.order_entries_by = ("ID",)
    writer.display_order = (
        "author",
        "editor",
        "title",
        "journal",
        "booktitle",
        "publisher",
        "institution",
        "school",
        "year",
        "volume",
        "number",
        "pages",
        "doi",
        "url",
        "language",
        "keywords",
        "abstract",
        "note",
    )
    out_path.write_text(writer.write(db), encoding="utf-8")


def write_contexts_skeleton(records: list[dict], out_path: Path) -> None:
    payload = {
        "main_text_source": "fill in your non-TeX source document here",
        "instructions": [
            "Replace the empty context arrays with real local citation snippets from Word, Markdown, notes, or another writing source.",
            "Keep citekeys aligned with the generated BibTeX before running the audit wrapper.",
        ],
        "citekeys": [record["citekey"] for record in records],
        "contexts": {record["citekey"]: [] for record in records},
        "items": [
            {
                "citekey": record["citekey"],
                "original_id": record["original_id"],
                "type": record["type"],
                "title": record["title"],
                "year": record["year"],
            }
            for record in records
        ],
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_mapping(records: list[dict], out_path: Path) -> None:
    payload = {
        "source": "csl-json-import",
        "items": records,
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import CSL JSON items into BibTeX and helper files for the reference-chain audit workflow."
    )
    parser.add_argument("--csl-json", required=True, help="Path to a CSL JSON export, for example from Zotero.")
    parser.add_argument("--out-bib", required=True, help="Output BibTeX path.")
    parser.add_argument(
        "--out-mapping",
        default="",
        help="Optional JSON mapping from original CSL ids to generated citekeys.",
    )
    parser.add_argument(
        "--out-contexts-skeleton",
        default="",
        help="Optional citation_contexts.json skeleton for non-TeX workflows.",
    )
    parser.add_argument(
        "--citekey-source",
        choices=["generated", "id"],
        default="generated",
        help="Use generated citekeys by default, or sanitize the CSL `id` field when possible.",
    )
    args = parser.parse_args()

    csl_path = Path(args.csl_json).resolve()
    out_bib = Path(args.out_bib).resolve()
    out_bib.parent.mkdir(parents=True, exist_ok=True)

    items = load_items(csl_path)
    seen: set[str] = set()
    entries = []
    records = []
    for item in items:
        citekey = choose_citekey(item, args.citekey_source, seen)
        entry = build_entry(item, citekey)
        entries.append(entry)
        records.append(
            {
                "citekey": citekey,
                "original_id": str(item.get("id", "")).strip(),
                "type": str(item.get("type", "")).strip(),
                "title": pick_field(item, "title"),
                "year": extract_year(item),
            }
        )

    write_bib(entries, out_bib)

    if args.out_mapping:
        out_mapping = Path(args.out_mapping).resolve()
        out_mapping.parent.mkdir(parents=True, exist_ok=True)
        write_mapping(records, out_mapping)

    if args.out_contexts_skeleton:
        out_contexts = Path(args.out_contexts_skeleton).resolve()
        out_contexts.parent.mkdir(parents=True, exist_ok=True)
        write_contexts_skeleton(records, out_contexts)

    print(f"Imported {len(entries)} CSL JSON items into {out_bib}")


if __name__ == "__main__":
    main()
