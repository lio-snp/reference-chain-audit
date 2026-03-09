from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


CITE_RE = re.compile(
    r"\\[A-Za-z]*cite[A-Za-z*]*\s*(?:\[[^\]]*\]\s*)?(?:\[[^\]]*\]\s*)?\{([^}]+)\}"
)
INPUT_RE = re.compile(r"\\(?:input|include)\{([^}]+)\}")


def strip_comments(text: str) -> str:
    lines = []
    for line in text.splitlines():
        clean = re.sub(r"(?<!\\)%.*$", "", line)
        lines.append(clean)
    return "\n".join(lines)


def resolve_tex(path: Path) -> Path:
    if path.suffix:
        return path
    return path.with_suffix(".tex")


def collect_tex_files(main_tex: Path) -> list[Path]:
    seen: set[Path] = set()
    ordered: list[Path] = []

    def visit(path: Path) -> None:
        path = path.resolve()
        if path in seen or not path.exists():
            return
        seen.add(path)
        ordered.append(path)
        text = strip_comments(path.read_text(encoding="utf-8"))
        for match in INPUT_RE.finditer(text):
            child = resolve_tex((path.parent / match.group(1)).resolve())
            visit(child)

    visit(main_tex)
    return ordered


def make_snippet(text: str, start: int, radius: int = 180) -> str:
    lo = max(0, start - radius)
    hi = min(len(text), start + radius)
    snippet = re.sub(r"\s+", " ", text[lo:hi]).strip()
    return snippet


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract citekeys and local citation contexts from a TeX tree.")
    parser.add_argument("--main-tex", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    main_tex = Path(args.main_tex).resolve()
    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    files = collect_tex_files(main_tex)
    contexts: dict[str, list[dict]] = {}
    ordered_keys: list[str] = []

    for tex_path in files:
        raw = tex_path.read_text(encoding="utf-8")
        text = strip_comments(raw)
        for match in CITE_RE.finditer(text):
            keys = [k.strip() for k in match.group(1).split(",") if k.strip()]
            line_no = text.count("\n", 0, match.start()) + 1
            snippet = make_snippet(text, match.start())
            command = match.group(0).split("{", 1)[0]
            for key in keys:
                if key not in contexts:
                    contexts[key] = []
                    ordered_keys.append(key)
                contexts[key].append(
                    {
                        "file": str(tex_path),
                        "line": line_no,
                        "command": command,
                        "snippet": snippet,
                    }
                )

    payload = {
        "main_tex": str(main_tex),
        "files": [str(p) for p in files],
        "citekeys": ordered_keys,
        "contexts": contexts,
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(ordered_keys)} citekeys to {out_path}")


if __name__ == "__main__":
    main()
