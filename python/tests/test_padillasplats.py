"""Tests that do not touch the network.

Everything here runs against the bundled inventory and against the .splat files
in ../data, so the suite is fast, offline and works the same on every platform.
The one network path (fetch) is exercised by pointing the cache at a temporary
directory and copying from data/ instead, which keeps CI honest without making
it depend on GitHub being up.
"""

import json
import os
import sys
from pathlib import Path

import numpy as np
import pytest

import padillasplats as ps
from padillasplats import _paths

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "data"
has_data = DATA.is_dir()
needs_data = pytest.mark.skipif(not has_data, reason="running outside the repo checkout")


# --- inventory --------------------------------------------------------------

def test_ids_nonempty():
    assert ps.ids(), "the inventory should not be empty"
    assert len(set(ps.ids())) == len(ps.ids()), "ids must be unique"


def test_every_record_has_required_fields():
    for r in ps.inventory():
        for key in ("id", "title", "category", "file", "sha256", "splats", "bytes", "license"):
            assert key in r, f"{r.get('id')} is missing {key!r}"
        assert r["category"] in ps.categories()
        assert len(r["sha256"]) == 64
        assert r["splats"] * 32 == r["bytes"], "a .splat is exactly 32 bytes per gaussian"


def test_get_and_missing():
    first = ps.ids()[0]
    assert ps.get(first)["id"] == first
    with pytest.raises(KeyError):
        ps.get("no-such-object")


def test_find_filters():
    everything = ps.inventory()
    assert ps.find() == everything
    assert ps.find(category="object") == [r for r in everything if r["category"] == "object"]

    biggest = max(r["splats"] for r in everything)
    assert ps.find(min_splats=biggest + 1) == []
    assert len(ps.find(max_splats=biggest)) == len(everything)

    scored = ps.find(has_quality=True)
    assert all(r["psnr"] is not None and r["ssim"] is not None for r in scored)
    unscored = ps.find(has_quality=False)
    assert len(scored) + len(unscored) == len(everything)


def test_find_tags_all_vs_any():
    tags = ps.tags()
    assert tags, "expected at least one tag"
    a = tags[0]
    assert all(a in r["tags"] for r in ps.find(tags=[a]))
    # An impossible AND is empty; the same pair as an OR is not.
    pair = ps.find(tags=tags, match_any_tag=False)
    assert pair == [] or len(pair) == 1
    assert ps.find(tags=tags, match_any_tag=True)


def test_find_by_ids():
    first = ps.ids()[0]
    got = ps.find(ids=[first])
    assert [r["id"] for r in got] == [first]


# --- identifier safety ------------------------------------------------------

@pytest.mark.parametrize("bad", [
    "../evil", "..", "a/b", "a\\b", "/abs", "", ".hidden/../x", "x/../../y",
])
def test_unsafe_ids_rejected(bad):
    with pytest.raises(ValueError):
        _paths.check_id(bad)


@pytest.mark.parametrize("bad", ["/abs/path", "../escape/x.splat", "a/../../b"])
def test_unsafe_relpaths_rejected(bad):
    with pytest.raises(ValueError):
        _paths.check_relpath(bad)


def test_good_relpath_normalises_separators():
    assert _paths.check_relpath("plant\\plant.splat") == "plant/plant.splat"


def test_load_rejects_unsafe_id():
    with pytest.raises(ValueError):
        ps.load("../../etc/passwd")


# --- cache location ---------------------------------------------------------

def test_cache_dir_respects_env(monkeypatch, tmp_path):
    monkeypatch.setenv(_paths.ENV_CACHE, str(tmp_path / "somewhere"))
    assert _paths.cache_dir() == tmp_path / "somewhere"


def test_cache_dir_is_absolute_and_platform_appropriate(monkeypatch):
    monkeypatch.delenv(_paths.ENV_CACHE, raising=False)
    d = _paths.cache_dir()
    assert d.is_absolute()
    assert "padillasplats" in str(d)


# --- decoding ---------------------------------------------------------------

def _synthetic(n=5):
    a = np.zeros((n, 32), dtype=np.uint8)
    pos = np.arange(n * 3, dtype=np.float32).reshape(n, 3)
    a[:, 0:12] = pos.view(np.uint8).reshape(n, 12)
    scl = np.full((n, 3), 0.25, dtype=np.float32)
    a[:, 12:24] = scl.view(np.uint8).reshape(n, 12)
    a[:, 24:28] = 200
    a[:, 28:32] = [255, 128, 128, 128]      # -> quaternion (1, 0, 0, 0) after decode
    return a.tobytes()


def test_decode_shapes_and_values():
    s = ps.decode(_synthetic(5), "synthetic")
    assert len(s) == 5
    assert s.positions.shape == (5, 3) and s.positions.dtype == np.float32
    assert s.scales.shape == (5, 3)
    assert s.colors.shape == (5, 4) and s.colors.dtype == np.uint8
    assert s.rotations.shape == (5, 4)
    np.testing.assert_allclose(s.positions[1], [3, 4, 5], atol=1e-6)
    np.testing.assert_allclose(s.scales[0], [0.25, 0.25, 0.25], atol=1e-6)
    np.testing.assert_allclose(np.linalg.norm(s.rotations, axis=1), 1.0, atol=1e-6)
    np.testing.assert_allclose(s.rotations[0], [1, 0, 0, 0], atol=1e-6)


def test_decode_rejects_bad_length():
    with pytest.raises(ValueError):
        ps.decode(b"\x00" * 33)
    with pytest.raises(ValueError):
        ps.decode(b"")


def test_helpers():
    s = ps.decode(_synthetic(4), "synthetic")
    assert s.rgb.shape == (4, 3)
    np.testing.assert_allclose(s.opacity, 200 / 255, atol=1e-6)
    lo, hi = s.bounds()
    assert lo.shape == (3,) and np.all(hi >= lo)
    assert "synthetic" in repr(s)


# --- against the real data --------------------------------------------------

@needs_data
def test_bundled_inventory_matches_data_dir():
    packaged = json.loads(
        (Path(ps.__file__).with_name("inventory.json")).read_text(encoding="utf-8"))
    source = json.loads((DATA / "inventory.json").read_text(encoding="utf-8"))
    assert packaged == source, "run python/sync_inventory.py"


@needs_data
@pytest.mark.parametrize("record", ps.inventory(), ids=lambda r: r["id"])
def test_files_match_their_checksums_and_counts(record):
    from padillasplats._fetch import sha256_file
    p = DATA / record["file"]
    assert p.is_file(), f"missing {p}"
    assert p.stat().st_size == record["bytes"]
    assert sha256_file(p) == record["sha256"]
    s = ps.load_file(p, record["id"], record)
    assert len(s) == record["splats"]


@needs_data
@pytest.mark.parametrize("record", ps.inventory(), ids=lambda r: r["id"])
def test_thumbnail_and_meta_exist(record):
    assert (DATA / record["thumbnail"]).is_file()
    meta = json.loads((DATA / record["meta"]).read_text(encoding="utf-8"))
    assert meta["id"] == record["id"]
    assert meta["sha256"] == record["sha256"]
    assert meta["license"] == record["license"]


@needs_data
def test_fetch_verifies_checksum(monkeypatch, tmp_path):
    """A cached file whose bytes do not match the inventory must be rejected."""
    from padillasplats import _fetch
    monkeypatch.setenv(_paths.ENV_CACHE, str(tmp_path))
    record = ps.inventory()[0]

    # Pre-seed the cache with the right file: fetch should accept it untouched.
    dest = tmp_path / record["id"] / Path(record["file"]).name
    dest.parent.mkdir(parents=True)
    dest.write_bytes((DATA / record["file"]).read_bytes())
    got = _fetch.fetch(record, "https://example.invalid/", verify=True)
    assert got == dest

    # Corrupt it: fetch must not return the bad bytes. With an unreachable base
    # URL the refetch fails, which proves it did not simply trust the cache.
    dest.write_bytes(b"\x00" * 32)
    with pytest.raises(Exception):
        _fetch.fetch(record, "https://example.invalid/", verify=True)


def test_non_https_is_refused():
    from padillasplats import _fetch
    with pytest.raises(ValueError):
        _fetch.read_url("http://example.com/x.json")
