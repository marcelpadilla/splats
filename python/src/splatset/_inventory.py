"""The inventory: what is in the collection, and how to filter it.

A copy of ``data/inventory.json`` ships inside the wheel, so listing and
filtering work offline and instantly. Only the splat bytes need the network.
``refresh()`` pulls the live inventory for anyone who wants objects added after
this release without upgrading the package.

Some objects ship at several **levels of detail** -- the mesh-derived ones come
at 10k / 100k / 500k / 1M gaussians. A record names one tier in its top-level
``file``/``splats``/``bytes``/``sha256`` (the one ``default_lod`` picks) and
lists them all under ``lods``. :func:`resolve` swaps a record onto a different
tier, which is what lets every download path -- ``path``, ``load``, ``download``
-- take a ``lod=`` argument without any of them knowing about tiers.
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
    # NOT derived from base_url: that is pinned to an immutable tag so a released
    # version's checksums can never go stale, and deriving from it would make
    # this function re-read the very snapshot the caller is trying to look past.
    url = url or doc.get("live_inventory_url") or (
        doc["base_url"].rstrip("/") + "/inventory.json")
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


# --- levels of detail -------------------------------------------------------

#: Names that mean "work it out from what this object actually has", so a call
#: can ask for the smallest or largest tier without knowing the tier names, and
#: still work on an object that has only one file.
LOD_ALIASES = ("min", "smallest", "max", "largest", "default")


def lods_of(record: Record) -> List[str]:
    """The tier names this object ships, smallest first. Empty if it has one file."""
    return [str(l["lod"]) for l in record.get("lods", [])]


def lods() -> List[str]:
    """Every tier name in the collection, smallest first.

    Sorted by the gaussian count the tier actually holds rather than by name, so
    the order is meaningful ("100k" before "1m") without parsing the labels.
    """
    sizes: Dict[str, int] = {}
    for o in objects():
        for l in o.get("lods", []):
            sizes.setdefault(str(l["lod"]), int(l.get("splats", 0)))
    return [name for name, _ in sorted(sizes.items(), key=lambda kv: kv[1])]


def resolve(record: Record, lod: Optional[str]) -> Record:
    """A copy of ``record`` pointing at tier ``lod``, or the record unchanged.

    The returned record keeps every descriptive field (title, tags, license) and
    swaps only the four that identify the bytes -- ``file``, ``splats``,
    ``bytes``, ``sha256`` -- plus a ``lod`` key naming the tier. Because it is
    still an ordinary record, the downloader verifies the checksum of the tier
    that was actually asked for, with no special case anywhere.

    ``lod=None`` returns the record as-is. ``"min"``/``"max"``/``"default"``
    always work, including on a single-file object, where they all mean its one
    file. An explicit tier name the object does not have is an error, since
    silently handing back a different resolution would be worse than failing.
    """
    if lod is None:
        return record
    tiers = record.get("lods") or []
    if not tiers:
        if lod in LOD_ALIASES:
            return record
        raise KeyError(
            f"{record['id']!r} ships a single file, not levels of detail; "
            f"asked for {lod!r}. Use lod=None, or 'min'/'max'/'default'.")

    if lod in ("min", "smallest"):
        tier = min(tiers, key=lambda t: t.get("splats", 0))
    elif lod in ("max", "largest"):
        tier = max(tiers, key=lambda t: t.get("splats", 0))
    elif lod == "default":
        want = record.get("default_lod")
        tier = next((t for t in tiers if str(t["lod"]) == str(want)), tiers[-1])
    else:
        tier = next((t for t in tiers if str(t["lod"]) == str(lod)), None)
        if tier is None:
            have = ", ".join(lods_of(record))
            raise KeyError(f"{record['id']!r} has no {lod!r} level of detail. Has: {have}")

    out = dict(record)
    out["lod"] = str(tier["lod"])
    for key in ("file", "splats", "bytes", "sha256"):
        if key in tier:
            out[key] = tier[key]
    return out


def has_lod(record: Record, lod: str) -> bool:
    """Whether ``resolve(record, lod)`` would succeed."""
    if lod in LOD_ALIASES:
        return True
    return str(lod) in lods_of(record)


# --- licensing --------------------------------------------------------------

#: Licence-id fragments that mean "there is a string attached". NonCommercial
#: forbids a whole class of use; ShareAlike forces your own work open. Both are
#: Creative Commons, so a plain "starts with CC" test would wave them through --
#: which is the one mistake in this file that would actually mislead someone
#: about what they are allowed to do.
_CONDITIONAL = ("-NC", "-SA", "NONCOMMERCIAL", "SHAREALIKE")


def is_open(record: Record) -> bool:
    """Whether an object is free to use for anything, with at most attribution.

    True for CC0, public domain and plain CC-BY. False for everything that
    carries a condition beyond credit, which in this collection means three
    things: the as-is generated objects, whose provenance is unsettled; the
    Stanford-repository objects, which are free to use but not Creative Commons;
    and the NonCommercial or ShareAlike meshes, which restrict commercial use or
    force a licence onto your derivative.

    An explicit ``license_open`` flag in the record always wins -- that is what
    marks the public-domain objects, whose licence ids do not spell "CC".
    """
    if "license_open" in record:
        return bool(record["license_open"])
    lic = str(record.get("license", "")).upper()
    if any(flag in lic for flag in _CONDITIONAL):
        return False
    return lic.startswith("CC") or lic == "PUBLIC DOMAIN"


def _matches(value: Any, wanted: Any) -> bool:
    """``value == wanted``, or ``value in wanted`` when ``wanted`` is a list,
    tuple or set of options (a string is treated as a single option)."""
    if isinstance(wanted, (list, tuple, set, frozenset)):
        return value in set(wanted)
    return value == wanted


def find(
    *,
    category: Optional[Any] = None,
    source_method: Optional[Any] = None,
    license: Optional[Any] = None,
    open_license: Optional[bool] = None,
    lod: Optional[str] = None,
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
    photogrammetry from a video), ``"mesh2splat"`` (converted directly from a
    known mesh), ``"synthetic-render"`` (trained from renders of a known 3D
    asset) or ``"image-to-3d-generation"`` (a generative model invented it from
    an image). Filter on it to keep real scans apart from the rest, which
    usually matters for how you may use them.
    ``category``, ``source_method`` and ``license`` each accept a single value
    or a list of values to allow, so ``source_method=["capture",
    "synthetic-render"]`` keeps everything except generated and mesh-derived.
    ``open_license=True`` keeps only the openly-licensed objects (Creative
    Commons or public domain); the rest are usable but carry a condition.
    ``lod`` keeps only objects that ship that level of detail and returns each
    already resolved to it, so ``lod="10k"`` answers "the 10k version of
    everything that has one". ``"min"``/``"max"`` mean the smallest/largest each
    object has and therefore keep single-file objects too.
    ``tags`` requires all of the given tags by default, or any of them with
    ``match_any_tag=True``. ``has_quality=True`` keeps only objects that carry
    PSNR and SSIM numbers, which is what you want when the metrics are part of
    your experiment.

    Size limits are applied *after* the level of detail, so
    ``find(lod="10k", max_bytes=500_000)`` measures the 10k files, not the
    default ones.
    """
    out = objects()
    if ids_ is not None:
        want = set(ids_)
        out = [o for o in out if o["id"] in want]
    if category is not None:
        out = [o for o in out if _matches(o.get("category"), category)]
    if source_method is not None:
        out = [o for o in out if _matches(o.get("source_method"), source_method)]
    if license is not None:
        out = [o for o in out if _matches(o.get("license"), license)]
    if open_license is not None:
        out = [o for o in out if is_open(o) is open_license]
    if tags:
        want = set(tags)
        if match_any_tag:
            out = [o for o in out if want & set(o.get("tags", ()))]
        else:
            out = [o for o in out if want <= set(o.get("tags", ()))]
    if lod is not None:
        out = [resolve(o, lod) for o in out if has_lod(o, lod)]
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
    """Every way a splat here was made, e.g. ``capture``, ``mesh2splat``."""
    doc = _bundled()
    declared = doc.get("source_methods")
    if declared:
        return list(declared)
    # Older inventory without the field: read the values actually in use.
    return sorted({o["source_method"] for o in doc["objects"] if o.get("source_method")})


def licenses() -> List[str]:
    """Every license id in use, sorted."""
    return sorted({o.get("license", "") for o in objects() if o.get("license")})


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


# --- a readable overview ----------------------------------------------------

#: How each source method reads in prose. Anything not listed prints its raw id,
#: so an inventory refreshed from a newer repository still renders.
SOURCE_WORD = {
    "capture": "Scanned",
    "mesh2splat": "From geometry",
    "synthetic-render": "Rendered",
    "image-to-3d-generation": "Generated",
}


def summary() -> str:
    """A short plain-text overview of the collection: what is here, and its terms.

    Exists so that the first thing anyone types after installing can be
    ``print(splatset.summary())`` and get the shape of the dataset -- how many objects,
    made which ways, under which licenses -- rather than a wall of JSON.
    """
    objs = objects()
    doc = _bundled()
    lines = [f"{doc.get('name', 'splats')}: {len(objs)} objects"
             f" (inventory updated {doc.get('updated', '?')})"]
    for sm in source_methods():
        group = [o for o in objs if o.get("source_method") == sm]
        if not group:
            continue
        lic = sorted({o.get("license", "?") for o in group})
        gauss = sum(o.get("splats", 0) for o in group)
        lines.append(
            f"  {SOURCE_WORD.get(sm, sm):<14} {len(group):>3} object"
            f"{' ' if len(group) == 1 else 's'}  "
            f"{gauss / 1e6:>5.1f}M gaussians   {', '.join(lic)}")
    tiered = [o for o in objs if o.get("lods")]
    if tiered:
        lines.append(f"  levels of detail: {', '.join(lods())}"
                     f"  (on {len(tiered)} of {len(objs)} objects)")
    closed = [o for o in objs if not is_open(o)]
    if closed:
        lines.append(f"  {len(closed)} object{'' if len(closed) == 1 else 's'} carry a "
                     "licence condition; find(open_license=True) drops them")
    return "\n".join(lines)
