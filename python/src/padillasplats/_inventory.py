"""The inventory: what is in the collection, and how to filter it.

A copy of ``data/inventory.json`` ships inside the wheel, so listing and
filtering work offline and instantly. Only the splat bytes need the network.
``refresh()`` pulls the live inventory for anyone who wants objects added after
this release without upgrading the package.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

_BUNDLED = Path(__file__).with_name("inventory.json")

Record = Dict[str, Any]

_cache: Optional[Dict[str, Any]] = None


def _bundled() -> Dict[str, Any]:
    global _cache
    if _cache is None:
        _cache = json.loads(_BUNDLED.read_text(encoding="utf-8"))
    return _cache


def raw() -> Dict[str, Any]:
    """The whole inventory document, including dataset-level fields."""
    return _bundled()


def refresh(url: Optional[str] = None, timeout: float = 30.0) -> Dict[str, Any]:
    """Replace the in-memory inventory with the live one from the repository.

    Use this to see objects added since this package was released. It affects
    only the current process; nothing is written to disk.
    """
    from ._fetch import read_url

    doc = _bundled()
    url = url or (doc["base_url"].rstrip("/") + "/inventory.json")
    fresh = json.loads(read_url(url, timeout=timeout).decode("utf-8"))
    if "objects" not in fresh:
        raise ValueError("refreshed inventory has no 'objects' key")
    global _cache
    _cache = fresh
    return fresh


def objects() -> List[Record]:
    """Every object record, in inventory order."""
    return list(_bundled()["objects"])


def ids() -> List[str]:
    """Just the object ids."""
    return [o["id"] for o in _bundled()["objects"]]


def get(obj_id: str) -> Record:
    """The record for one object, by id."""
    for o in _bundled()["objects"]:
        if o["id"] == obj_id:
            return o
    known = ", ".join(ids())
    raise KeyError(f"no object {obj_id!r} in the inventory. Available: {known}")


def find(
    *,
    category: Optional[str] = None,
    source_method: Optional[str] = None,
    tags: Optional[Sequence[str]] = None,
    match_any_tag: bool = False,
    min_splats: Optional[int] = None,
    max_splats: Optional[int] = None,
    max_bytes: Optional[int] = None,
    has_quality: Optional[bool] = None,
    ids_: Optional[Iterable[str]] = None,
) -> List[Record]:
    """Select objects by inventory conditions. Every argument is optional.

    ``category`` is ``"object"`` or ``"scene"`` (what the thing is).
    ``source_method`` is how the splat was made, one of ``"capture"`` (real
    photogrammetry from a video), ``"image-to-3d-generation"`` (a generative
    model invented it from an image) or ``"synthetic-render"`` (trained from
    renders of a known 3D asset). Filter on it to keep real scans apart from
    generated ones, which usually matters for how you may use them.
    ``tags`` requires all of the given tags by default, or any of them with
    ``match_any_tag=True``. ``has_quality=True`` keeps only objects that carry
    PSNR and SSIM numbers, which is what you want when the metrics are part of
    your experiment.
    """
    out = objects()
    if ids_ is not None:
        want = set(ids_)
        out = [o for o in out if o["id"] in want]
    if category is not None:
        out = [o for o in out if o.get("category") == category]
    if source_method is not None:
        out = [o for o in out if o.get("source_method") == source_method]
    if tags:
        want = set(tags)
        if match_any_tag:
            out = [o for o in out if want & set(o.get("tags", ()))]
        else:
            out = [o for o in out if want <= set(o.get("tags", ()))]
    if min_splats is not None:
        out = [o for o in out if o.get("splats", 0) >= min_splats]
    if max_splats is not None:
        out = [o for o in out if o.get("splats", 0) <= max_splats]
    if max_bytes is not None:
        out = [o for o in out if o.get("bytes", 0) <= max_bytes]
    if has_quality is not None:
        def scored(o: Record) -> bool:
            return o.get("psnr") is not None and o.get("ssim") is not None
        out = [o for o in out if scored(o) is has_quality]
    return out


def tags() -> List[str]:
    """Every tag used in the collection, sorted."""
    seen = set()
    for o in objects():
        seen.update(o.get("tags", ()))
    return sorted(seen)


def categories() -> List[str]:
    """Every category the collection declares."""
    return list(_bundled().get("categories", []))


def source_methods() -> List[str]:
    """Every way a splat here was made, e.g. ``capture``, ``synthetic-render``."""
    doc = _bundled()
    declared = doc.get("source_methods")
    if declared:
        return list(declared)
    # Older inventory without the field: read the values actually in use.
    return sorted({o["source_method"] for o in doc["objects"] if o.get("source_method")})


def citation(fmt: str = "bibtex") -> str:
    """How to cite the collection. ``fmt`` is ``"bibtex"`` or ``"text"``."""
    c = _bundled().get("citation") or {}
    if fmt not in ("bibtex", "text"):
        raise ValueError("fmt must be 'bibtex' or 'text'")
    value = c.get(fmt)
    if value:
        return value
    # No citation block: fall back to a plain line built from dataset fields.
    doc = _bundled()
    return f"{doc.get('attribution', '')}. {doc.get('name', 'splats')}. {doc.get('homepage', '')}".strip()
