#!/usr/bin/env python3
"""Propagate data/inventory.json to everywhere else that repeats it.

data/inventory.json is the single source of truth. Three places repeat it and
all are generated from it here, so none can drift:

  1. src/padillasplats/inventory.json, the copy shipped in the wheel, which is
     what makes ids() and find() work offline.
  2. the gallery table in the root README, between the inventory markers.
  3. the BibTeX block in the root README, between the citation markers.

Run after adding or changing an object:

    python python/sync_inventory.py

tests/test_padillasplats.py fails if the packaged copy is stale, so step 1 can
never be forgotten silently.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SRC = REPO / "data" / "inventory.json"
PKG_COPY = HERE / "src" / "padillasplats" / "inventory.json"
README = REPO / "README.md"

INV_START = "<!-- inventory:start -->"
INV_END = "<!-- inventory:end -->"
CITE_START = "<!-- citation:start -->"
CITE_END = "<!-- citation:end -->"

RAW = "https://raw.githubusercontent.com/marcelpadilla/splats/main/data/"

# How each source_method reads in the human-facing "Type" column, combined with
# category so a reader sees both what it is and how it was made in one phrase.
METHOD_WORD = {
    "capture": "Captured",
    "image-to-3d-generation": "Generated",
    "synthetic-render": "Rendered",
}


def human_size(n: int) -> str:
    return f"{n / 1e6:.1f} MB" if n >= 1e6 else f"{n / 1e3:.0f} kB"


def approx_count(n: int) -> str:
    """Gaussian count, shown approximately in thousands (an exact count is noise)."""
    return f"~{n // 1000}k" if n >= 1000 else str(n)


def type_label(o: dict) -> str:
    """e.g. 'Captured object', 'Generated object', 'Rendered scene'."""
    word = METHOD_WORD.get(o.get("source_method", ""), o.get("source_method", "?"))
    return f"{word} {o.get('category', '')}".strip()


def gallery(doc: dict) -> str:
    rows = [
        "| | Object | Type | Size | Download |",
        "|---|---|---|--:|:--:|",
    ]
    for o in doc["objects"]:
        name = (
            f"**{o['title']}**<br><sub>`{o['id']}`</sub>"
            f"<br><sub>{', '.join(o.get('tags', []))}</sub>"
        )
        size = f"{approx_count(o['splats'])} · {human_size(o['bytes'])}"
        rows.append(
            f"| <img src=\"data/{o['thumbnail']}\" width=\"220\"> | {name} | "
            f"{type_label(o)} | {size} | "
            f"[.splat]({RAW}{o['file']}) · [meta](data/{o['meta']}) |"
        )
    n = len(doc["objects"])
    total_g = sum(o["splats"] for o in doc["objects"])
    total_b = sum(o["bytes"] for o in doc["objects"])
    rows.append("")
    rows.append(
        f"<sub>{n} object{'s' if n != 1 else ''} · {approx_count(total_g)} gaussians · "
        f"{human_size(total_b)} total · every splat CC-BY-4.0</sub>"
    )
    return "\n".join(rows)


def citation_block(doc: dict) -> str:
    bib = (doc.get("citation") or {}).get("bibtex", "")
    return "```bibtex\n" + bib + "\n```"


def splice(text: str, start: str, end: str, body: str, what: str) -> str:
    if start not in text or end not in text:
        raise SystemExit(f"markers {start} / {end} not found in {README}")
    head, rest = text.split(start, 1)
    _, tail = rest.split(end, 1)
    return f"{head}{start}\n{body}\n{end}{tail}"


def main() -> int:
    if not SRC.is_file():
        print(f"source inventory not found: {SRC}", file=sys.stderr)
        return 1
    doc = json.loads(SRC.read_text(encoding="utf-8"))

    was = PKG_COPY.read_bytes() if PKG_COPY.is_file() else None
    PKG_COPY.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SRC, PKG_COPY)
    print(f"{'unchanged' if was == SRC.read_bytes() else 'updated  '}  {PKG_COPY}")

    text = README.read_text(encoding="utf-8")
    new = splice(text, INV_START, INV_END, gallery(doc), "gallery")
    new = splice(new, CITE_START, CITE_END, citation_block(doc), "citation")
    changed = new != text
    README.write_text(new, encoding="utf-8")
    print(f"{'updated  ' if changed else 'unchanged'}  {README}  "
          f"({len(doc['objects'])} object(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
