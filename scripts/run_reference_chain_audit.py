from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent


def resolve_bibcheck_root(raw: str) -> Path:
    if raw:
        return Path(raw).expanduser().resolve()

    env_root = os.environ.get("BIBCHECK_ROOT", "").strip()
    if env_root:
        return Path(env_root).expanduser().resolve()

    return (SKILL_ROOT / "_external" / "Bib-Check").resolve()


def run(cmd: list[str], env: dict | None = None) -> None:
    print("RUN:", " ".join(cmd))
    subprocess.run(cmd, check=True, env=env)


def main() -> None:
    parser = argparse.ArgumentParser(description="Standard wrapper for the reference-chain audit workflow.")
    parser.add_argument("--main-tex", default="")
    parser.add_argument(
        "--contexts-json",
        default="",
        help="Optional precomputed citation_contexts.json for non-TeX workflows.",
    )
    parser.add_argument("--bib", required=True)
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--pdf", default="")
    parser.add_argument("--run-bibcheck", action="store_true")
    parser.add_argument("--bibcheck-online", action="store_true")
    parser.add_argument(
        "--bibcheck-root",
        default="",
        help="Optional path to a local Bib-Check clone. Defaults to $BIBCHECK_ROOT or <skill>/_external/Bib-Check.",
    )
    args = parser.parse_args()

    if not args.main_tex and not args.contexts_json:
        parser.error("Provide --main-tex or --contexts-json.")

    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    contexts_path = outdir / "citation_contexts.json"
    cited_bib_path = outdir / "cited_subset.bib"
    pdf_links_path = outdir / "pdf_reference_links.json"
    matrix_path = outdir / "reference_audit_matrix.json"

    if args.contexts_json:
        source_contexts = Path(args.contexts_json).resolve()
        if not source_contexts.exists():
            parser.error(f"contexts JSON not found: {source_contexts}")
        if source_contexts != contexts_path:
            shutil.copyfile(source_contexts, contexts_path)
        print(f"Using precomputed citation contexts from {source_contexts}")
    else:
        run([
            sys.executable,
            str(SCRIPT_DIR / "extract_citation_contexts.py"),
            "--main-tex",
            str(Path(args.main_tex).resolve()),
            "--out",
            str(contexts_path),
        ])
    run([
        sys.executable,
        str(SCRIPT_DIR / "subset_cited_bib.py"),
        "--bib",
        str(Path(args.bib).resolve()),
        "--contexts",
        str(contexts_path),
        "--out",
        str(cited_bib_path),
    ])

    if args.pdf:
        run([
            sys.executable,
            str(SCRIPT_DIR / "extract_pdf_links.py"),
            "--pdf",
            str(Path(args.pdf).resolve()),
            "--out",
            str(pdf_links_path),
        ])

    matrix_cmd = [
        sys.executable,
        str(SCRIPT_DIR / "build_reference_audit_matrix.py"),
        "--bib",
        str(Path(args.bib).resolve()),
        "--contexts",
        str(contexts_path),
        "--out",
        str(matrix_path),
    ]
    if pdf_links_path.exists():
        matrix_cmd.extend(["--pdf-links", str(pdf_links_path)])
    run(matrix_cmd)

    if args.run_bibcheck:
        bibcheck_root = resolve_bibcheck_root(args.bibcheck_root)
        if not bibcheck_root.exists():
            print("Bib-Check clone not found; skipping Bib-Check stage.")
        else:
            out = outdir / ("bibcheck_online" if args.bibcheck_online else "bibcheck_offline")
            out.mkdir(parents=True, exist_ok=True)
            env = dict(os.environ)
            env["PYTHONPATH"] = str(bibcheck_root) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
            env["BIBCHECK_CACHE_DIR"] = str((outdir / "bibcheck_cache").resolve())
            cmd = [
                sys.executable,
                "-m",
                "bibcheck",
                str(cited_bib_path),
                "--outdir",
                str(out),
            ]
            if not args.bibcheck_online:
                cmd.append("--offline")
            run(cmd, env=env)

    print(f"Done. Outputs written to {outdir}")


if __name__ == "__main__":
    main()
