from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Optional Playwright landing-page probe for reference links.")
    parser.add_argument("--input", required=True, help="JSON list of rows containing at least a `uri` field.")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        raise SystemExit(
            "Playwright is not installed in the current environment. "
            "Install it before using this script."
        ) from exc

    rows = json.loads(Path(args.input).read_text(encoding="utf-8"))
    out = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for row in rows:
            uri = row["uri"]
            item = {"uri": uri, "status": "unknown", "final_url": "", "title": ""}
            try:
                page.goto(uri, wait_until="domcontentloaded", timeout=45000)
                page.wait_for_timeout(1200)
                item["status"] = "ok"
                item["final_url"] = page.url
                item["title"] = page.title()
            except Exception as exc:
                item["status"] = f"error:{type(exc).__name__}"
                item["final_url"] = page.url
                item["title"] = page.title()
            out.append(item)
        browser.close()

    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(out)} browser probe rows to {args.out}")


if __name__ == "__main__":
    main()
