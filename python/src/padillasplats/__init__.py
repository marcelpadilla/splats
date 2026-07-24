"""padillasplats: load Marcel Padilla's Gaussian splat collection in one line.

    >>> import padillasplats as ps
    >>> ps.ids()
    ['plant', 'academic_tarot_cards']
    >>> s = ps.load("plant")
    >>> s.positions.shape
    (113648, 3)

Filtering happens on a copy of the inventory bundled in this package, so it is
offline and instant. Only the splat bytes are downloaded, once, into a per-user
cache directory, and every download is verified against the SHA-256 recorded in
the inventory.

The data is CC-BY-4.0 (credit Marcel Padilla). This package's code is 0BSD, so
the code itself needs no attribution.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence

from . import _inventory
from ._fetch import fetch as _fetch_file
from ._paths import cache_dir, check_id, clear_cache
from ._splat import RECORD_BYTES, Splat, decode, load_file

__version__ = "0.2.0"

__all__ = [
    "Splat",
    "cache_dir",
    "categories",
    "citation",
    "clear_cache",
    "decode",
    "download",
    "find",
    "get",
    "ids",
    "inventory",
    "load",
    "load_all",
    "load_file",
    "path",
    "refresh_inventory",
    "source_methods",
    "tags",
    "__version__",
]

Record = Dict[str, Any]


# --- what is in the collection ---------------------------------------------

def inventory() -> List[Record]:
    """Every object record. See :func:`find` to select a subset."""
    return _inventory.objects()


def ids() -> List[str]:
    """The ids of every object, in inventory order."""
    return _inventory.ids()


def get(obj_id: str) -> Record:
    """The inventory record for one object."""
    return _inventory.get(obj_id)


def tags() -> List[str]:
    """Every tag in use, sorted."""
    return _inventory.tags()


def categories() -> List[str]:
    """The categories the collection declares, such as ``object``, ``scene``."""
    return _inventory.categories()


def source_methods() -> List[str]:
    """How the splats here were made: ``capture``, ``image-to-3d-generation``,
    ``synthetic-render``. Filter on it with ``find(source_method=...)``."""
    return _inventory.source_methods()


def citation(fmt: str = "bibtex") -> str:
    """How to cite the collection, as ``"bibtex"`` (default) or ``"text"``.

        >>> print(ps.citation())
        >>> print(ps.citation("text"))
    """
    return _inventory.citation(fmt)


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
    ids: Optional[Iterable[str]] = None,
) -> List[Record]:
    """Select objects by inventory conditions. Nothing is downloaded.

        >>> ps.find(category="object", min_splats=100_000)
        >>> ps.find(source_method="capture")   # real scans only, not generated
        >>> ps.find(tags=["plant"])
        >>> ps.find(has_quality=True)          # only objects with PSNR and SSIM
    """
    return _inventory.find(
        category=category,
        source_method=source_method,
        tags=tags,
        match_any_tag=match_any_tag,
        min_splats=min_splats,
        max_splats=max_splats,
        max_bytes=max_bytes,
        has_quality=has_quality,
        ids_=ids,
    )


def refresh_inventory(url: Optional[str] = None) -> List[Record]:
    """Pull the live inventory, to see objects added since this release.

    Affects this process only. Nothing is written to disk.
    """
    return list(_inventory.refresh(url)["objects"])


# --- getting the data -------------------------------------------------------

def path(obj_id: str, *, verify: bool = True, force: bool = False) -> Path:
    """Local path to an object's ``.splat``, downloading and caching if needed."""
    record = _inventory.get(check_id(obj_id))
    return _fetch_file(record, _inventory.raw()["base_url"], verify=verify, force=force)


def load(obj_id: str, *, verify: bool = True, force: bool = False) -> Splat:
    """Download if needed, then decode. This is the one-liner.

        >>> s = ps.load("plant")
    """
    record = _inventory.get(check_id(obj_id))
    p = _fetch_file(record, _inventory.raw()["base_url"], verify=verify, force=force)
    return load_file(p, record["id"], record)


def load_all(**filters: Any) -> Iterator[Splat]:
    """Iterate over the objects matching :func:`find`, decoding each in turn.

    Lazy on purpose: it downloads and decodes one object at a time, so looping
    over the whole collection does not need it all in memory at once.

        >>> for s in ps.load_all(category="object"):
        ...     print(s.id, len(s))
    """
    for record in find(**filters):
        yield load(record["id"])


def download(dest: "str | Path", *, verify: bool = True, **filters: Any) -> List[Path]:
    """Copy the matching objects into ``dest`` as ``<dest>/<id>.splat``.

    Use this for a local working copy. Omit the filters to take everything.

        >>> ps.download("./splats")                      # all of them
        >>> ps.download("./big", min_splats=100_000)
    """
    out_dir = Path(dest).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    written: List[Path] = []
    for record in find(**filters):
        src = _fetch_file(record, _inventory.raw()["base_url"], verify=verify)
        target = out_dir / f"{check_id(record['id'])}.splat"
        shutil.copyfile(src, target)
        written.append(target)
    return written
