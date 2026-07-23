"""The ``.splat`` container and its decoder.

The format is the antimatter15 packing: a header-less array of 32-byte records,
so the splat count is exactly ``filesize // 32``. One record is

===========  ======  ==================================================
byte range   type    meaning
===========  ======  ==================================================
``0:12``     3x f32  position x, y, z
``12:24``    3x f32  scale x, y, z (linear, already exponentiated)
``24:28``    4x u8   colour R, G, B, A (A is the opacity, not a mask)
``28:32``    4x u8   rotation quaternion w, x, y, z, as ``q * 128 + 128``
===========  ======  ==================================================

There is no room in the format for metadata: it has no header and no trailer,
and anything appended would break the ``filesize // 32`` invariant every other
reader relies on. Per-object metadata therefore lives in the inventory and in
each object's ``meta.json``, never inside the ``.splat``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict

import numpy as np

RECORD_BYTES = 32


@dataclass
class Splat:
    """One decoded Gaussian splat object.

    All arrays share the same first dimension, one row per Gaussian.
    """

    id: str
    positions: np.ndarray   # (N, 3) float32
    scales: np.ndarray      # (N, 3) float32, linear
    colors: np.ndarray      # (N, 4) uint8, RGBA
    rotations: np.ndarray   # (N, 4) float32, unit quaternion (w, x, y, z)
    meta: Dict[str, Any] = field(default_factory=dict)
    path: Path | None = None

    def __len__(self) -> int:
        return int(self.positions.shape[0])

    def __repr__(self) -> str:
        title = self.meta.get("title", self.id)
        return f"<Splat {self.id!r} ({title}) {len(self):,} gaussians>"

    @property
    def rgb(self) -> np.ndarray:
        """Colour only, as (N, 3) uint8."""
        return self.colors[:, :3]

    @property
    def opacity(self) -> np.ndarray:
        """Alpha as (N,) float32 in 0..1."""
        return self.colors[:, 3].astype(np.float32) / 255.0

    def bounds(self) -> "tuple[np.ndarray, np.ndarray]":
        """Axis-aligned (min, max) corners of the positions."""
        return self.positions.min(axis=0), self.positions.max(axis=0)


def decode(buf: bytes, obj_id: str = "", meta: Dict[str, Any] | None = None,
           path: Path | None = None) -> Splat:
    """Decode raw ``.splat`` bytes into a :class:`Splat`."""
    a = np.frombuffer(buf, dtype=np.uint8)
    if a.size == 0 or a.size % RECORD_BYTES:
        raise ValueError(
            f"not a .splat: {a.size} bytes is not a positive multiple of {RECORD_BYTES}"
        )
    a = a.reshape(-1, RECORD_BYTES)

    # .copy() before .view: the slices are strided views of the original buffer
    # and numpy will not reinterpret those as float32 without a contiguous copy.
    positions = a[:, 0:12].copy().view(np.float32)
    scales = a[:, 12:24].copy().view(np.float32)
    colors = a[:, 24:28].copy()

    q = (a[:, 28:32].astype(np.float32) - 128.0) / 128.0
    norm = np.linalg.norm(q, axis=1, keepdims=True)
    rotations = q / np.where(norm == 0.0, 1.0, norm)

    return Splat(
        id=obj_id,
        positions=positions,
        scales=scales,
        colors=colors,
        rotations=rotations.astype(np.float32),
        meta=dict(meta or {}),
        path=path,
    )


def load_file(path: "str | Path", obj_id: str = "",
              meta: Dict[str, Any] | None = None) -> Splat:
    """Decode a ``.splat`` from disk."""
    p = Path(path)
    return decode(p.read_bytes(), obj_id or p.stem, meta, p)
