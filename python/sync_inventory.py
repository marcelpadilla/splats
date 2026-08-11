#!/usr/bin/env python3
"""Propagate data/inventory.json to everywhere else that repeats it.

data/inventory.json is the single source of truth. Three places repeat it and
all are generated from it here, so none can drift:

  1. src/splatset/inventory.json, the copy shipped in the wheel, which is
     what makes ids() and find() work offline.
  2. the gallery table in the root README, between the inventory markers.
  3. the BibTeX block in the root README, between the citation markers.

Run after adding or changing an object:

    python python/sync_inventory.py

tests/test_splatset.py fails if the packaged copy is stale, so step 1 can
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
PKG_COPY = HERE / "src" / "splatset" / "inventory.json"
README = REPO / "README.md"

INV_START = "<!-- inventory:start -->"
INV_END = "<!-- inventory:end -->"
CITE_START = "<!-- citation:start -->"
CITE_END = "<!-- citation:end -->"

RAW = "https://raw.githubusercontent.com/marcelpadilla/splats/main/data/"

# How each source_method reads in the human-facing "Type" column, combined with
# category so a reader sees both what it is and how it was made in one phrase.
METHOD_WORD = {
    "capture": "Scanned",
    "image-to-3d-generation": "Generated",
    "synthetic-render": "Rendered",
    "mesh2splat": "Geometry",
}


def human_size(n: int) -> str:
    return f"{n / 1e6:.1f} MB" if n >= 1e6 else f"{n / 1e3:.0f} kB"


def approx_count(n: int) -> str:
    """Gaussian count, shown approximately (an exact count is noise to a reader)."""
    if n >= 1_000_000:
        return f"~{n / 1e6:.1f}M".replace(".0M", "M")
    return f"~{n // 1000}k" if n >= 1000 else str(n)


def object_bytes(o: dict) -> int:
    """Every byte an object ships, which for a multi-tier object is all its tiers.

    The footer used to sum only the default tier, which understated the download
    by more than half once the mesh objects arrived at four resolutions each.
    """
    return sum(l["bytes"] for l in o["lods"]) if o.get("lods") else o["bytes"]


def object_gaussians(o: dict) -> int:
    """Gaussians in an object's default tier: the total across tiers would just
    count the same surface four times over."""
    return o["splats"]


def source_word(o: dict) -> str:
    """How the object was made: Scanned / Generated / Rendered."""
    return METHOD_WORD.get(o.get("source_method", ""), o.get("source_method", "?"))


def kind_word(o: dict) -> str:
    """Object or Scene (everything is an object for now)."""
    return (o.get("category", "") or "").capitalize()


def newest_first(objects: list) -> list:
    """Reading order for the gallery: most recently added object at the top.

    Marcel, while the collection is still growing: "always sort them newest
    first so that I can easily find them, and then later we do alphabetical
    sorting." `added` is a DATE, not a timestamp, and a whole batch shares one,
    so ties fall back on promotion order reversed, which within a batch is the
    order the objects were staged in.

    data/inventory.json itself keeps promotion order: that is a record of what
    happened and reordering it would churn the file on every batch. Only the
    views sort. The website page carries the same comparator.
    """
    return sorted(enumerate(objects),
                  key=lambda t: (t[1].get("added", ""), t[0]), reverse=True)


def gallery(doc: dict) -> str:
    # Two dedicated columns: Source (how it was made) and Kind (object/scene).
    rows = [
        "| | Object | Source | Kind | Size | Download |",
        "|---|---|---|---|--:|:--:|",
    ]
    for _, o in newest_first(doc["objects"]):
        name = (
            f"**{o['title']}**<br><sub>`{o['id']}`</sub>"
            f"<br><sub>{', '.join(o.get('tags', []))}</sub>"
        )
        # License sits under the source word, so how it was made and what you may
        # do with it read together. Generated objects flag their as-is notice here.
        source = f"{source_word(o)}<br><sub>{o.get('license', '')}</sub>"
        # A multi-LOD object lists every tier (count + size) and a download link per
        # level; a single-file object keeps the one size and one link.
        if o.get("lods"):
            size = "<br>".join(
                f"{approx_count(l['splats'])} · {human_size(l['bytes'])}" for l in o["lods"])
            links = " · ".join(f"[{l['lod']}]({RAW}{l['file']})" for l in o["lods"])
            download = f"{links}<br><sub>[meta](data/{o['meta']})</sub>"
        else:
            size = f"{approx_count(o['splats'])} · {human_size(o['bytes'])}"
            download = f"[.splat]({RAW}{o['file']}) · [meta](data/{o['meta']})"
        rows.append(
            f"| <img src=\"data/{o['thumbnail']}\" width=\"220\"> | {name} | "
            f"{source} | {kind_word(o)} | {size} | {download} |"
        )
    n = len(doc["objects"])
    total_g = sum(object_gaussians(o) for o in doc["objects"])
    total_b = sum(object_bytes(o) for o in doc["objects"])
    tiered = sum(1 for o in doc["objects"] if o.get("lods"))
    licenses = sorted({o.get("license", "CC-BY-4.0") for o in doc["objects"]})
    lic = licenses[0] if len(licenses) == 1 else "licenses per object (see Source)"
    tiers = (f" · {tiered} of them at four levels of detail" if tiered else "")
    rows.append("")
    rows.append(
        f"<sub>{n} object{'s' if n != 1 else ''} · {approx_count(total_g)} gaussians "
        f"at the default level{tiers} · {human_size(total_b)} for every file · "
        f"{lic}</sub>"
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


def stamp_updated(doc: dict) -> bool:
    """Set the collection's `updated` date from the objects themselves.

    It was hand-written, so it rotted: it still said 2026-07-28 after two batches
    and a normalization pass, which is exactly the kind of wrong that a reader
    trusts. Deriving it from the newest `added` cannot drift, and unlike stamping
    today's date it does not churn the file on every unrelated run.
    """
    newest = max((o.get("added") or "" for o in doc["objects"]), default="")
    if not newest or doc.get("updated") == newest:
        return False
    doc["updated"] = newest
    return True


def stamp_citation(doc: dict) -> bool:
    """Put the snapshot and the object count into the citation.

    The same URL served 2 objects on 2026-07-23, 19 on 2026-07-28 and 109 with
    every coordinate rescaled on 2026-08-06. Without a snapshot in the entry, two
    papers cite datasets that differ by 50x in size with identical BibTeX. Both
    strings are regenerated from the inventory here, for the same reason
    `updated` is: a hand-maintained copy of a number is a number that goes stale.
    """
    n = len(doc["objects"])
    ref = doc.get("data_ref") or doc.get("updated", "")
    note = f"Snapshot {ref}, {n} objects"
    bib = ("@misc{padilla_splats,\n"
           "  author       = {Marcel Padilla},\n"
           "  title        = {splats: a small collection of Gaussian splat objects},\n"
           "  year         = {2026},\n"
           f"  note         = {{{note}}},\n"
           f"  howpublished = {{\\url{{{doc['homepage']}}}}}\n"
           "}")
    text = (f"Marcel Padilla. splats: a small collection of Gaussian splat objects. "
            f"2026. {note}. {doc['homepage']}")
    before = doc.get("citation")
    doc["citation"] = {"bibtex": bib, "text": text}
    return doc["citation"] != before


def main() -> int:
    if not SRC.is_file():
        print(f"source inventory not found: {SRC}", file=sys.stderr)
        return 1
    doc = json.loads(SRC.read_text(encoding="utf-8"))

    if stamp_updated(doc) | stamp_citation(doc):
        SRC.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        print(f"updated    {SRC}  (updated -> {doc['updated']}, citation restamped)")

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
