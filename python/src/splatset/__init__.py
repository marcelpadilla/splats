"""splatset: load a free collection of Gaussian splat objects in one line.

    >>> import splatset
    >>> splatset.ids()
    ['plant', 'academic_tarot_cards', ...]
    >>> s = splatset.load("plant")
    >>> s.positions.shape
    (113648, 3)

You never need a URL. Say what you want and it is fetched, checksum-verified and
decoded:

    >>> splatset.load_random(source_method="capture")          # any real scan
    >>> splatset.find(source_method="mesh2splat", lod="10k")   # every 10k-gaussian mesh object
    >>> splatset.load("lucy", lod="1m")                        # one object at a chosen resolution

Filtering happens on a copy of the inventory bundled in this package, so it is
offline and instant. Only the splat bytes are downloaded, once, into a per-user
cache directory, and every download is verified against the SHA-256 recorded in
the inventory.

The data's license is per object -- see ``splatset.summary()`` and each record's
``license``. This package's code is 0BSD, so the code itself needs no
attribution.
"""

from __future__ import annotations

import random as _random
import shutil
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence

from . import _inventory
from ._fetch import fetch as _fetch_file
from ._paths import cache_dir, check_id, clear_cache
from ._splat import RECORD_BYTES, Splat, decode, load_file

__version__ = "0.4.0"

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
    "is_open_license",
    "licenses",
    "load",
    "load_all",
    "load_file",
    "load_random",
    "lods",
    "lods_of",
    "path",
    "random",
    "refresh_inventory",
    "sample",
    "source_methods",
    "summary",
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


def get(obj_id: str, *, lod: Optional[str] = None) -> Record:
    """The inventory record for one object, optionally at a chosen resolution.

        >>> splatset.get("lucy")["splats"]
        500000
        >>> splatset.get("lucy", lod="10k")["splats"]
        10000
    """
    return _inventory.resolve(_inventory.get(obj_id), lod)


def tags() -> List[str]:
    """Every tag in use, sorted."""
    return _inventory.tags()


def categories() -> List[str]:
    """The categories the collection declares, such as ``object``, ``scene``."""
    return _inventory.categories()


def source_methods() -> List[str]:
    """How the splats here were made: ``capture``, ``mesh2splat``,
    ``synthetic-render``, ``image-to-3d-generation``. Filter on it with
    ``find(source_method=...)``."""
    return _inventory.source_methods()


def lods() -> List[str]:
    """Every level of detail in the collection, smallest first.

        >>> splatset.lods()
        ['10k', '100k', '500k', '1m']

    Objects derived from a mesh ship all of these; a capture ships one file and
    has none. ``lods_of(id)`` says which an individual object has.
    """
    return _inventory.lods()


def lods_of(obj: "str | Record") -> List[str]:
    """The levels of detail one object ships, smallest first ([] if it has one file)."""
    record = _inventory.get(obj) if isinstance(obj, str) else obj
    return _inventory.lods_of(record)


def licenses() -> List[str]:
    """Every license id in the collection, sorted."""
    return _inventory.licenses()


def is_open_license(obj: "str | Record") -> bool:
    """Whether an object is under an open license: Creative Commons or public domain.

    Pass an id or a record. Objects that come with a condition return ``False``:
    the as-is generated ones, whose provenance is unsettled, and the
    mesh-derived ones whose source asks for attribution instead of releasing
    under CC. Use ``find(open_license=True)`` to select only the open ones.
    """
    record = _inventory.get(obj) if isinstance(obj, str) else obj
    return _inventory.is_open(record)


def summary() -> str:
    """A short plain-text overview: how many objects, made how, under what terms.

        >>> print(splatset.summary())
    """
    return _inventory.summary()


def citation(fmt: str = "bibtex") -> str:
    """How to cite the collection, as ``"bibtex"`` (default) or ``"text"``.

        >>> print(splatset.citation())
        >>> print(splatset.citation("text"))
    """
    return _inventory.citation(fmt)


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
    ids: Optional[Iterable[str]] = None,
) -> List[Record]:
    """Select objects by inventory conditions. Nothing is downloaded.

        >>> splatset.find(category="object", min_splats=100_000)
        >>> splatset.find(source_method="capture")    # real scans only, not generated
        >>> splatset.find(open_license=True)          # only the freely-licensed ones
        >>> splatset.find(license="CC-BY-4.0")
        >>> splatset.find(source_method=["capture", "synthetic-render"])
        >>> splatset.find(source_method="mesh2splat", lod="10k")   # the small ones
        >>> splatset.find(lod="min", max_bytes=1_000_000)          # anything under a megabyte
        >>> splatset.find(tags=["plant"])
        >>> splatset.find(has_quality=True)           # only objects with PSNR and SSIM

    ``category``, ``source_method`` and ``license`` accept either one value or a
    list of allowed values. ``open_license=True`` keeps only objects under an
    open license (Creative Commons or public domain), which is the quick way to
    stay on the safe side of the licensing; the ones it drops are usable too,
    but each carries a condition spelled out in its ``license_note``.

    ``lod`` keeps only objects that ship that level of detail, each already
    resolved to it -- so the returned records' ``file``, ``splats``, ``bytes``
    and ``sha256`` describe that tier, and a later ``load(r["id"], lod=...)``
    fetches exactly what the record says. ``"min"`` and ``"max"`` mean the
    smallest and largest each object has, and keep single-file objects too.
    Size limits are applied after the tier is chosen.
    """
    return _inventory.find(
        category=category,
        source_method=source_method,
        license=license,
        open_license=open_license,
        lod=lod,
        tags=tags,
        match_any_tag=match_any_tag,
        min_splats=min_splats,
        max_splats=max_splats,
        max_bytes=max_bytes,
        has_quality=has_quality,
        ids_=ids,
    )


def random(*, seed: Optional[int] = None, **filters: Any) -> Record:
    """One record at random, from the objects matching :func:`find`.

        >>> splatset.random()                              # anything
        >>> splatset.random(source_method="capture")       # a real scan
        >>> splatset.random(lod="10k", seed=0)             # reproducible

    Returns the record, not the data, so it costs nothing; :func:`load_random`
    is the same choice already downloaded and decoded. Raises ``LookupError``
    rather than returning ``None`` when the filters match nothing, so a typo in
    a filter fails loudly instead of an object appearing later in the script.
    """
    return sample(1, seed=seed, **filters)[0]


def sample(n: int = 1, *, seed: Optional[int] = None, **filters: Any) -> List[Record]:
    """``n`` distinct records at random from the objects matching :func:`find`.

        >>> splatset.sample(3, category="object")
        >>> splatset.sample(5, source_method="mesh2splat", lod="100k", seed=0)

    Asking for more than exist returns all of them, shuffled, rather than
    failing: for "give me a handful to test with", a short list is the useful
    answer.
    """
    pool = find(**filters)
    if not pool:
        raise LookupError(
            f"nothing in the collection matches {filters!r}. "
            f"Try splatset.summary() to see what is there.")
    rng = _random.Random(seed)
    return rng.sample(pool, min(int(n), len(pool)))


def load_random(*, seed: Optional[int] = None, verify: bool = True,
                **filters: Any) -> Splat:
    """Pick one object at random, download it if needed, and decode it.

        >>> s = splatset.load_random()
        >>> s = splatset.load_random(source_method="mesh2splat", lod="10k")
    """
    record = random(seed=seed, **filters)
    return load(record["id"], lod=record.get("lod"), verify=verify)


def refresh_inventory(url: Optional[str] = None) -> List[Record]:
    """Pull the live inventory, to see objects added since this release.

    Affects this process only. Nothing is written to disk.
    """
    return list(_inventory.refresh(url)["objects"])


# --- getting the data -------------------------------------------------------

def path(obj_id: str, *, lod: Optional[str] = None, verify: bool = True,
         force: bool = False) -> Path:
    """Local path to an object's ``.splat``, downloading and caching if needed.

        >>> splatset.path("plant")
        >>> splatset.path("lucy", lod="10k")
    """
    record = _inventory.resolve(_inventory.get(check_id(obj_id)), lod)
    return _fetch_file(record, _inventory.raw()["base_url"], verify=verify, force=force)


def load(obj_id: str, *, lod: Optional[str] = None, verify: bool = True,
         force: bool = False) -> Splat:
    """Download if needed, then decode. This is the one-liner.

        >>> s = splatset.load("plant")
        >>> s = splatset.load("lucy", lod="1m")     # a chosen level of detail
        >>> s = splatset.load("lucy", lod="min")    # whichever is smallest

    ``lod`` is only meaningful for the mesh-derived objects; ``splatset.lods_of(id)``
    says which levels an object has. Asking a single-file object for a named
    tier is an error rather than a silent fallback to a different resolution.
    """
    record = _inventory.resolve(_inventory.get(check_id(obj_id)), lod)
    p = _fetch_file(record, _inventory.raw()["base_url"], verify=verify, force=force)
    return load_file(p, record["id"], record)


def load_all(**filters: Any) -> Iterator[Splat]:
    """Iterate over the objects matching :func:`find`, decoding each in turn.

    Lazy on purpose: it downloads and decodes one object at a time, so looping
    over the whole collection does not need it all in memory at once.

        >>> for s in splatset.load_all(category="object"):
        ...     print(s.id, len(s))
        >>> for s in splatset.load_all(source_method="mesh2splat", lod="10k"):
        ...     print(s.id, len(s))          # 10k each, ~3 MB for the whole set
    """
    lod = filters.get("lod")
    for record in find(**filters):
        yield load(record["id"], lod=record.get("lod", lod))


def download(dest: "str | Path", *, verify: bool = True, **filters: Any) -> List[Path]:
    """Copy the matching objects into ``dest``. Use this for a local working copy.

        >>> splatset.download("./splats")                          # all of them
        >>> splatset.download("./big", min_splats=100_000)
        >>> splatset.download("./small", lod="10k")                # every 10k tier
        >>> splatset.download("./safe", open_license=True)         # CC-licensed only

    Files are named ``<id>.splat``, or ``<id>_<lod>.splat`` when a level of
    detail was chosen, so two resolutions of the same object can sit in one
    folder without one overwriting the other.
    """
    out_dir = Path(dest).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    written: List[Path] = []
    for record in find(**filters):
        # find() has already resolved the tier, so the record's own `lod` is the
        # concrete tier name -- never the "min"/"max" the caller may have asked
        # for, which would make a misleading filename.
        tier = record.get("lod")
        src = _fetch_file(record, _inventory.raw()["base_url"], verify=verify)
        name = check_id(record["id"]) + (f"_{tier}" if tier else "") + ".splat"
        target = out_dir / name
        shutil.copyfile(src, target)
        written.append(target)
    return written
