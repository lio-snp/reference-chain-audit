from __future__ import annotations

import argparse
import json
from pathlib import Path

import fitz


def text_near_rect(page: fitz.Page, rect: fitz.Rect) -> str:
    probe = fitz.Rect(rect.x0 - 12, rect.y0 - 6, rect.x1 + 260, rect.y1 + 12)
    text = page.get_textbox(probe)
    return " ".join(text.split())


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract external PDF hyperlinks and nearby text.")
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    pdf_path = Path(args.pdf).resolve()
    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    rows = []
    for page_index in range(len(doc)):
        page = doc[page_index]
        for link in page.get_links():
            uri = link.get("uri")
            if not uri:
                continue
            rect = fitz.Rect(link["from"])
            rows.append(
                {
                    "page": page_index + 1,
                    "uri": uri,
                    "nearby_text": text_near_rect(page, rect),
                    "rect": [rect.x0, rect.y0, rect.x1, rect.y1],
                }
            )

    out_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(rows)} PDF links to {out_path}")


if __name__ == "__main__":
    main()
