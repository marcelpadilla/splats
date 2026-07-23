#!/usr/bin/env python3
"""Propagate data/inventory.json to everywhere else that repeats it.

data/inventory.json is the single source of truth. Two places repeat it and both
are generated from it here, so neither can drift:

  1. src/padillasplats/inventory.json, the copy shipped in the wheel, which is
     what makes ids() and find() work offline.
  2. the gallery table in the root README, between the inventory markers.

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

START = "<!-- inventory:start -->"
END = "<!-- inventory:end -->"

RAW = "https://raw.githubusercontent.com/marcelpadilla/splats/main/data/"


def human_size(n: int) -> str:
    return f"{n / 1e6:.1f} MB" if n >= 1e6 else f"{n / 1e3:.0f} kB"


def gallery(doc: dict) -> str:
    rows = [
        "| | Object | Category | Gaussians | Size | PSNR / SSIM | Download |",
        "|---|---|---|--:|--:|:--:|:--:|",
    ]
    for o in doc["objects"]:
        quality = (
            f"{o['psnr']:.2f} / {o['ssim']:.3f}"
            if o.get("psnr") is not None and o.get("ssim") is not None
            else "not measured"
        )
        name = (
            f"**{o['title']}**<br><sub>`{o['id']}`</sub>"
            f"<br><sub>{', '.join(o.get('tags', []))}</sub>"
        )
        rows.append(
            f"| <img src=\"data/{o['thumbnail']}\" width=\"220\"> | {name} | "
            f"{o['category']} | {o['splats']:,} | {human_size(o['bytes'])} | {quality} | "
            f"[.splat]({RAW}{o['file']}) · [meta](data/{o['meta']}) |"
        )
    n = len(doc["objects"])
    total_g = sum(o["splats"] for o in doc["objects"])
    total_b = sum(o["bytes"] for o in doc["objects"])
    rows.append("")
    rows.append(
        f"<sub>{n} object{'s' if n != 1 else ''} · {total_g:,} gaussians · "
        f"{human_size(total_b)} total</sub>"
    )
    return "\n".join(rows)


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
    if START not in text or END not in text:
        print(f"markers {START} / {END} not found in {README}", file=sys.stderr)
        return 1
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    new = f"{head}{START}\n{gallery(doc)}\n{END}{tail}"
    changed = new != text
    README.write_text(new, encoding="utf-8")
    print(f"{'updated  ' if changed else 'unchanged'}  {README}  "
          f"({len(doc['objects'])} object(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
