"""Downloading, with checksum verification.

The checksum is the part that matters. Every object in the inventory carries a
SHA-256, and a downloaded file is only accepted if it matches. That makes a
compromise of the hosting side non-exploitable: wrong bytes are refused rather
than handed to the caller.
"""

from __future__ import annotations

import hashlib
import os
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

from ._paths import cache_dir, check_id, check_relpath

_USER_AGENT = "splatset (+https://github.com/marcelpadilla/splats)"
_CHUNK = 1 << 20


def _check_https(url: str) -> str:
    if not url.lower().startswith("https://"):
        raise ValueError(f"refusing a non-HTTPS URL: {url!r}")
    return url


def read_url(url: str, timeout: float = 30.0) -> bytes:
    """Fetch a small resource into memory over HTTPS."""
    req = urllib.request.Request(_check_https(url), headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 (scheme checked)
        return r.read()


def _download_to(url: str, dest: Path, timeout: float) -> "tuple[str, Path]":
    """Stream ``url`` next to ``dest``, returning (SHA-256, temporary path).

    Writes to a sibling temporary file and renames only after the caller has
    accepted the digest, so an interrupted or corrupt download can never be
    mistaken for a complete cached file.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + f".part{os.getpid()}")
    h = hashlib.sha256()
    req = urllib.request.Request(_check_https(url), headers={"User-Agent": _USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r, open(tmp, "wb") as f:  # noqa: S310
            while True:
                chunk = r.read(_CHUNK)
                if not chunk:
                    break
                h.update(chunk)
                f.write(chunk)
        return h.hexdigest(), tmp
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(_CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(
    record: Dict[str, Any],
    base_url: str,
    *,
    verify: bool = True,
    force: bool = False,
    timeout: float = 60.0,
) -> Path:
    """Return a local path to the object's ``.splat``, downloading if needed.

    A cached file is re-verified against its expected digest, so a truncated or
    tampered cache entry is replaced rather than trusted.
    """
    obj_id = check_id(record["id"])
    rel = check_relpath(record["file"])
    expected: Optional[str] = record.get("sha256") if verify else None

    dest = cache_dir() / obj_id / Path(rel).name
    if dest.is_file() and not force:
        if expected is None or sha256_file(dest) == expected:
            return dest
        dest.unlink()  # cache entry does not match the inventory: refetch

    url = base_url.rstrip("/") + "/" + rel
    got, tmp = _download_to(url, dest, timeout)
    if expected is not None and got != expected:
        tmp.unlink(missing_ok=True)
        raise OSError(
            f"checksum mismatch for {obj_id!r}\n"
            f"  expected {expected}\n  got      {got}\n"
            f"  from     {url}\n"
            "The file was NOT saved. Re-running cannot help: this means the bytes\n"
            "on the server are not the bytes this release was built against. Try\n"
            "splatset.refresh_inventory(), or upgrade the package."
        )
    os.replace(tmp, dest)
    return dest
