"""A small command line, so the collection is usable without writing Python.

    python -m splatset                              # what is in here
    python -m splatset list --source mesh2splat --lod 10k
    python -m splatset info lucy
    python -m splatset get lucy --lod 1m            # prints the cached path
    python -m splatset get --source capture --out ./scans
    python -m splatset random --open-license

The point is the same as the Python API's: never make anyone look up a URL. Say
which objects you want and they are fetched, checksum-verified and put on disk.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List

from . import (citation, download, find, get, ids, is_open_license, lods,
               lods_of, path, random, summary)


def _filters(a: argparse.Namespace) -> Dict[str, Any]:
    """Turn the shared selection flags into keyword arguments for find()."""
    f: Dict[str, Any] = {}
    if getattr(a, "source", None):
        f["source_method"] = a.source
    if getattr(a, "category", None):
        f["category"] = a.category
    if getattr(a, "tag", None):
        f["tags"] = a.tag
    if getattr(a, "lod", None):
        f["lod"] = a.lod
    if getattr(a, "open_license", False):
        f["open_license"] = True
    if getattr(a, "min_splats", None):
        f["min_splats"] = a.min_splats
    if getattr(a, "max_splats", None):
        f["max_splats"] = a.max_splats
    if getattr(a, "id", None):
        f["ids"] = a.id
    return f


def add_selection(p: argparse.ArgumentParser) -> None:
    p.add_argument("--source", action="append", help="capture / mesh2splat / synthetic-render / image-to-3d-generation (repeatable)")
    p.add_argument("--category", help="object or scene")
    p.add_argument("--tag", action="append", help="require this tag (repeatable)")
    p.add_argument("--lod", help="level of detail: " + ", ".join(lods()) + ", or min/max")
    p.add_argument("--open-license", action="store_true", help="Creative Commons objects only")
    p.add_argument("--min-splats", type=int)
    p.add_argument("--max-splats", type=int)
    p.add_argument("--id", action="append", help="restrict to this id (repeatable)")


def table(records: List[Dict[str, Any]]) -> str:
    if not records:
        return "(nothing matches)"
    rows = []
    for r in records:
        tier = f"@{r['lod']}" if r.get("lod") else ""
        rows.append((r["id"] + tier, f"{r.get('splats', 0):,}",
                     f"{r.get('bytes', 0) / 1e6:.1f} MB",
                     r.get("source_method", ""), r.get("license", "")))
    w = [max(len(row[i]) for row in rows) for i in range(5)]
    return "\n".join(
        f"{a:<{w[0]}}  {b:>{w[1]}}  {c:>{w[2]}}  {d:<{w[3]}}  {e}"
        for a, b, c, d, e in rows)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="splatset", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd")

    p_list = sub.add_parser("list", help="list matching objects (downloads nothing)")
    add_selection(p_list)
    p_list.add_argument("--json", action="store_true", help="print the records as JSON")

    p_info = sub.add_parser("info", help="everything known about one object")
    p_info.add_argument("obj_id")
    p_info.add_argument("--lod")

    p_get = sub.add_parser("get", help="download objects; prints each local path")
    p_get.add_argument("obj_id", nargs="?", help="one id, or use the filters")
    add_selection(p_get)
    p_get.add_argument("--out", help="copy into this directory instead of the cache")

    p_rand = sub.add_parser("random", help="pick one at random")
    add_selection(p_rand)
    p_rand.add_argument("--seed", type=int)
    p_rand.add_argument("--get", action="store_true", help="download it too")

    sub.add_parser("cite", help="the BibTeX entry")
    sub.add_parser("summary", help="what is in the collection")

    a = p.parse_args(argv)

    if a.cmd in (None, "summary"):
        print(summary())
        if a.cmd is None:
            print(f"\n{len(ids())} ids: {', '.join(ids())}")
            print("\nTry: python -m splatset list --source mesh2splat --lod 10k")
        return 0

    if a.cmd == "cite":
        print(citation())
        return 0

    if a.cmd == "list":
        records = find(**_filters(a))
        print(json.dumps(records, indent=2) if a.json else table(records))
        return 0

    if a.cmd == "info":
        record = get(a.obj_id, lod=a.lod)
        record = dict(record)
        record["levels_of_detail"] = lods_of(a.obj_id) or "(single file)"
        record["creative_commons"] = is_open_license(a.obj_id)
        print(json.dumps(record, indent=2))
        return 0

    if a.cmd == "random":
        record = random(seed=a.seed, **_filters(a))
        print(table([record]))
        if a.get:
            print(path(record["id"], lod=record.get("lod")))
        return 0

    if a.cmd == "get":
        if a.obj_id:
            print(path(a.obj_id, lod=a.lod))
            return 0
        filters = _filters(a)
        if not filters:
            print("refusing to download the whole collection without a filter; "
                  "pass an id, a filter, or --id ... for each one you want",
                  file=sys.stderr)
            return 2
        if a.out:
            for q in download(a.out, **filters):
                print(q)
        else:
            for r in find(**filters):
                print(path(r["id"], lod=r.get("lod")))
        return 0

    p.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
