"""Cache location and identifier safety.

Kept in one place because these are the two things that decide where bytes from
the network land on disk, which is the only part of a downloader with real
security consequences.
"""

from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path

#: An object id may only ever be a plain name. Ids reach this module from the
#: inventory, which can be refreshed over the network, so they are treated as
#: untrusted input and never interpolated into a path unchecked. Without this a
#: crafted id such as ``../../.bashrc`` would escape the cache directory.
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

ENV_CACHE = "SPLATSET_CACHE"


def check_id(obj_id: str) -> str:
    """Return ``obj_id`` if it is safe to use as a single path component."""
    if not isinstance(obj_id, str) or not _SAFE_ID.match(obj_id) or ".." in obj_id:
        raise ValueError(f"unsafe object id: {obj_id!r}")
    return obj_id


def check_relpath(rel: str) -> str:
    """Return ``rel`` if it is a safe repo-relative path (``a/b.splat``)."""
    if not isinstance(rel, str) or not rel or rel.startswith(("/", "\\")):
        raise ValueError(f"unsafe path: {rel!r}")
    parts = rel.replace("\\", "/").split("/")
    for p in parts:
        check_id(p)
    return "/".join(parts)


def cache_dir() -> Path:
    """Where downloaded splats are cached.

    Follows each platform's own convention rather than dropping files in the
    working directory, so a loop over the dataset costs one download per file
    for the life of the machine.
    """
    override = os.environ.get(ENV_CACHE)
    if override:
        return Path(override).expanduser()
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or (Path.home() / "AppData" / "Local")
        return Path(base) / "splatset" / "Cache"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Caches" / "splatset"
    base = os.environ.get("XDG_CACHE_HOME") or (Path.home() / ".cache")
    return Path(base) / "splatset"


def clear_cache() -> None:
    """Delete every cached file. The next load re-downloads."""
    d = cache_dir()
    if d.is_dir():
        shutil.rmtree(d)
