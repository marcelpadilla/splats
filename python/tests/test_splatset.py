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

import splatset
from splatset import _paths

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "data"
has_data = DATA.is_dir()
needs_data = pytest.mark.skipif(not has_data, reason="running outside the repo checkout")


# --- inventory --------------------------------------------------------------

def test_ids_nonempty():
    assert splatset.ids(), "the inventory should not be empty"
    assert len(set(splatset.ids())) == len(splatset.ids()), "ids must be unique"


def test_every_record_has_required_fields():
    for r in splatset.inventory():
        for key in ("id", "title", "category", "source_method", "file", "sha256",
                    "splats", "bytes", "license", "extent"):
            assert key in r, f"{r.get('id')} is missing {key!r}"
        assert r["category"] in splatset.categories()
        assert r["source_method"] in splatset.source_methods()
        assert len(r["sha256"]) == 64
        assert r["splats"] * 32 == r["bytes"], "a .splat is exactly 32 bytes per gaussian"


@needs_data
@pytest.mark.parametrize("record", splatset.inventory(), ids=lambda r: r["id"])
def test_default_tier_is_normalized(record):
    """Every object is centred on the origin with its longest side 1.

    This is the property the whole 2026-08-06 pass was for, and nothing guarded
    it: promote_to_dataset.py measures extent *from the file* and never asserts
    it, so an unnormalized object would promote with a perfectly self-consistent
    checksum and sail through the rest of this suite.
    """
    a = np.fromfile(DATA / record["file"], dtype=np.uint8).reshape(-1, 32)
    pos = a[:, 0:12].copy().view(np.float32).reshape(-1, 3)
    lo, hi = pos.min(axis=0), pos.max(axis=0)
    side = float((hi - lo).max())
    centre = np.abs((hi + lo) / 2).max()
    assert side == pytest.approx(1.0, abs=2e-3), f"longest side {side}"
    assert centre < 2e-3, f"not centred on the origin: {centre}"
    assert np.allclose(record["extent"], hi - lo, atol=1e-3),         "the inventory's extent disagrees with the file"


@needs_data
@pytest.mark.parametrize("record", [r for r in splatset.inventory() if r.get("lods")],
                         ids=lambda r: r["id"])
def test_lod_tiers_share_one_scale(record):
    """Coarser tiers inherit the object's scale rather than being renormalized.

    Renormalizing each tier to its own box would make a viewer switching level of
    detail see the object jump, so decimation is allowed to shrink the box a
    little. It is 1% on the worst tier in the collection (dragon_10k), never
    more.
    """
    for tier in record["lods"]:
        a = np.fromfile(DATA / tier["file"], dtype=np.uint8).reshape(-1, 32)
        pos = a[:, 0:12].copy().view(np.float32).reshape(-1, 3)
        side = float((pos.max(axis=0) - pos.min(axis=0)).max())
        assert 0.98 <= side <= 1.01, f"{tier['file']} longest side {side}"


def test_source_method_filter():
    everything = splatset.inventory()
    methods = splatset.source_methods()
    assert methods, "expected at least one source method"
    covered = 0
    for m in methods:
        got = splatset.find(source_method=m)
        assert all(r["source_method"] == m for r in got)
        covered += len(got)
    assert covered == len([r for r in everything if r.get("source_method")])
    assert splatset.find(source_method="no-such-method") == []


def test_license_filters_and_open_license():
    everything = splatset.inventory()

    # Exact license match, single value and list of allowed values.
    for lic in splatset.licenses():
        got = splatset.find(license=lic)
        assert got and all(r["license"] == lic for r in got)
    all_lics = splatset.licenses()
    assert splatset.find(license=all_lics) == everything

    # open_license partitions the collection into freely-licensed and conditional.
    openish = splatset.find(open_license=True)
    closed = splatset.find(open_license=False)
    assert len(openish) + len(closed) == len(everything)
    assert all(splatset.is_open_license(r) for r in openish)
    assert not any(splatset.is_open_license(r) for r in closed)

    # Generated objects are the as-is, not-open ones.
    gen = splatset.find(source_method="image-to-3d-generation")
    if gen:
        assert all(not splatset.is_open_license(r["id"]) for r in gen)
        assert all(r["license"] == "As-is (no warranty)" for r in gen)
        assert set(r["id"] for r in gen) <= set(r["id"] for r in closed)

    # A list-valued source_method excludes generated in one call.
    non_generated = splatset.find(source_method=[m for m in splatset.source_methods()
                                           if m != "image-to-3d-generation"])
    assert all(r["source_method"] != "image-to-3d-generation" for r in non_generated)
    assert len(non_generated) + len(gen) == len(everything)


def test_non_cc_objects_explain_themselves():
    """Anything not openly licensed must say why, or a user cannot comply."""
    for r in splatset.find(open_license=False):
        assert r.get("license"), f"{r['id']} has no license id"
        assert r.get("license_note") or r.get("attribution"), \
            f"{r['id']} is not openly licensed but carries no note or attribution"


# --- levels of detail -------------------------------------------------------

def test_lods_listed_smallest_first():
    tiers = splatset.lods()
    if not tiers:
        pytest.skip("no multi-resolution objects in this inventory")
    sizes = []
    for name in tiers:
        r = next(r for r in splatset.inventory() if name in splatset.lods_of(r["id"]))
        sizes.append(next(l["splats"] for l in r["lods"] if l["lod"] == name))
    assert sizes == sorted(sizes), "lods() must be ordered by gaussian count"


def test_resolve_swaps_only_the_identity_of_the_bytes():
    multi = [r for r in splatset.inventory() if r.get("lods")]
    if not multi:
        pytest.skip("no multi-resolution objects in this inventory")
    base = multi[0]
    for tier in base["lods"]:
        got = splatset.get(base["id"], lod=tier["lod"])
        assert got["lod"] == tier["lod"]
        for key in ("file", "splats", "bytes", "sha256"):
            assert got[key] == tier[key]
        # Descriptive fields must survive: the licence of a 10k tier is the
        # licence of the object, and a caller reads it off the resolved record.
        for key in ("id", "title", "license", "source_method", "tags"):
            assert got[key] == base[key]
        assert got["splats"] * 32 == got["bytes"]


def test_lod_aliases_work_everywhere_including_single_file_objects():
    for r in splatset.inventory():
        smallest = splatset.get(r["id"], lod="min")
        largest = splatset.get(r["id"], lod="max")
        default = splatset.get(r["id"], lod="default")
        assert smallest["splats"] <= largest["splats"]
        if r.get("lods"):
            assert smallest["splats"] == min(l["splats"] for l in r["lods"])
            assert largest["splats"] == max(l["splats"] for l in r["lods"])
            assert default["lod"] == r["default_lod"]
            assert default["sha256"] == r["sha256"], "default tier must be the record's own"
        else:
            # A single-file object has one resolution; the aliases all mean it.
            assert smallest["sha256"] == largest["sha256"] == r["sha256"]


def test_unknown_lod_is_an_error_not_a_silent_fallback():
    multi = [r for r in splatset.inventory() if r.get("lods")]
    single = [r for r in splatset.inventory() if not r.get("lods")]
    if multi:
        with pytest.raises(KeyError):
            splatset.get(multi[0]["id"], lod="7k")
    if single:
        with pytest.raises(KeyError):
            splatset.get(single[0]["id"], lod="10k")


def test_find_by_lod_selects_and_resolves():
    tiers = splatset.lods()
    if not tiers:
        pytest.skip("no multi-resolution objects in this inventory")
    tier = tiers[0]
    got = splatset.find(lod=tier)
    assert got, f"expected objects at {tier}"
    assert all(r["lod"] == tier for r in got)
    assert all(tier in splatset.lods_of(r["id"]) for r in got)
    # Only objects that actually have the tier; single-file ones are dropped.
    assert len(got) == len([r for r in splatset.inventory() if tier in splatset.lods_of(r["id"])])

    # min/max keep everything, since every object has a smallest and a largest.
    assert len(splatset.find(lod="min")) == len(splatset.inventory())
    assert len(splatset.find(lod="max")) == len(splatset.inventory())


def test_size_filters_apply_after_the_lod_is_chosen():
    tiers = splatset.lods()
    if not tiers:
        pytest.skip("no multi-resolution objects in this inventory")
    small, big = tiers[0], tiers[-1]
    at_small = splatset.find(lod=small)
    cap = max(r["bytes"] for r in at_small)
    # Every small tier fits under the cap; the same objects at their big tier
    # do not. That only holds if the filter runs on the resolved record.
    assert len(splatset.find(lod=small, max_bytes=cap)) == len(at_small)
    assert splatset.find(lod=big, max_bytes=cap) == []


# --- picking at random ------------------------------------------------------

def test_random_and_sample_are_seeded_filtered_and_distinct():
    assert splatset.random(seed=7)["id"] == splatset.random(seed=7)["id"], "seeding must be stable"
    assert splatset.random(seed=7) in splatset.inventory()

    picked = splatset.sample(3, seed=1)
    assert len(picked) == 3
    assert len({r["id"] for r in picked}) == 3, "sample must not repeat an object"

    # Filters reach find() unchanged.
    for r in splatset.sample(2, source_method="capture", seed=0):
        assert r["source_method"] == "capture"
    if splatset.lods():
        assert splatset.random(lod=splatset.lods()[0], seed=0)["lod"] == splatset.lods()[0]

    # Asking for more than exist yields all of them rather than failing.
    everything = splatset.sample(len(splatset.inventory()) + 50, seed=0)
    assert len(everything) == len(splatset.inventory())

    # An impossible filter is loud, so a typo cannot look like an empty dataset.
    with pytest.raises(LookupError):
        splatset.random(source_method="no-such-method")


def test_summary_mentions_every_source_method():
    text = splatset.summary()
    assert str(len(splatset.inventory())) in text
    for m in splatset.source_methods():
        if splatset.find(source_method=m):
            word = splatset._inventory.SOURCE_WORD.get(m, m)
            assert word in text


@needs_data
def test_loaded_splat_exposes_license_and_provenance():
    for record in splatset.inventory():
        s = splatset.load_file(DATA / record["file"], record["id"], record)
        assert s.license == record["license"]
        assert s.source_method == record["source_method"]
        assert s.category == record["category"]
        assert s.open_license == splatset.is_open_license(record)


def test_citation():
    bib = splatset.citation()
    assert "@" in bib and "padilla" in bib.lower()
    assert splatset.citation("text")
    with pytest.raises(ValueError):
        splatset.citation("markdown")


def test_get_and_missing():
    first = splatset.ids()[0]
    assert splatset.get(first)["id"] == first
    with pytest.raises(KeyError):
        splatset.get("no-such-object")


def test_find_filters():
    everything = splatset.inventory()
    assert splatset.find() == everything
    assert splatset.find(category="object") == [r for r in everything if r["category"] == "object"]

    biggest = max(r["splats"] for r in everything)
    assert splatset.find(min_splats=biggest + 1) == []
    assert len(splatset.find(max_splats=biggest)) == len(everything)

    scored = splatset.find(has_quality=True)
    assert all(r["psnr"] is not None and r["ssim"] is not None for r in scored)
    unscored = splatset.find(has_quality=False)
    assert len(scored) + len(unscored) == len(everything)


def test_find_tags_all_vs_any():
    tags = splatset.tags()
    assert tags, "expected at least one tag"
    a = tags[0]
    assert all(a in r["tags"] for r in splatset.find(tags=[a]))
    # An impossible AND is empty; the same pair as an OR is not.
    pair = splatset.find(tags=tags, match_any_tag=False)
    assert pair == [] or len(pair) == 1
    assert splatset.find(tags=tags, match_any_tag=True)


def test_find_by_ids():
    first = splatset.ids()[0]
    got = splatset.find(ids=[first])
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
        splatset.load("../../etc/passwd")


# --- cache location ---------------------------------------------------------

def test_cache_dir_respects_env(monkeypatch, tmp_path):
    monkeypatch.setenv(_paths.ENV_CACHE, str(tmp_path / "somewhere"))
    assert _paths.cache_dir() == tmp_path / "somewhere"


def test_cache_dir_is_absolute_and_platform_appropriate(monkeypatch):
    monkeypatch.delenv(_paths.ENV_CACHE, raising=False)
    d = _paths.cache_dir()
    assert d.is_absolute()
    assert "splatset" in str(d)


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
    s = splatset.decode(_synthetic(5), "synthetic")
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
        splatset.decode(b"\x00" * 33)
    with pytest.raises(ValueError):
        splatset.decode(b"")


def test_helpers():
    s = splatset.decode(_synthetic(4), "synthetic")
    assert s.rgb.shape == (4, 3)
    np.testing.assert_allclose(s.opacity, 200 / 255, atol=1e-6)
    lo, hi = s.bounds()
    assert lo.shape == (3,) and np.all(hi >= lo)
    assert "synthetic" in repr(s)


# --- against the real data --------------------------------------------------

@needs_data
def test_bundled_inventory_matches_data_dir():
    packaged = json.loads(
        (Path(splatset.__file__).with_name("inventory.json")).read_text(encoding="utf-8"))
    source = json.loads((DATA / "inventory.json").read_text(encoding="utf-8"))
    assert packaged == source, "run python/sync_inventory.py"


@needs_data
@pytest.mark.parametrize("record", splatset.inventory(), ids=lambda r: r["id"])
def test_files_match_their_checksums_and_counts(record):
    from splatset._fetch import sha256_file
    p = DATA / record["file"]
    assert p.is_file(), f"missing {p}"
    assert p.stat().st_size == record["bytes"]
    assert sha256_file(p) == record["sha256"]
    s = splatset.load_file(p, record["id"], record)
    assert len(s) == record["splats"]


@needs_data
@pytest.mark.parametrize("record", [r for r in splatset.inventory() if r.get("lods")],
                         ids=lambda r: r["id"])
def test_every_lod_file_matches_its_checksum(record):
    """Not just the default tier: a wrong hash on any tier breaks that download."""
    from splatset._fetch import sha256_file
    seen = set()
    for tier in record["lods"]:
        p = DATA / tier["file"]
        assert p.is_file(), f"missing {p}"
        assert p.stat().st_size == tier["bytes"]
        assert tier["splats"] * 32 == tier["bytes"]
        assert sha256_file(p) == tier["sha256"]
        seen.add(tier["lod"])
    assert record["default_lod"] in seen
    # The record's own top-level bytes must BE one of the tiers, not a fifth file.
    assert record["sha256"] in {t["sha256"] for t in record["lods"]}


@needs_data
@pytest.mark.parametrize("record", splatset.inventory(), ids=lambda r: r["id"])
def test_thumbnail_and_meta_exist(record):
    assert (DATA / record["thumbnail"]).is_file()
    meta = json.loads((DATA / record["meta"]).read_text(encoding="utf-8"))
    assert meta["id"] == record["id"]
    assert meta["sha256"] == record["sha256"]
    assert meta["license"] == record["license"]


@needs_data
def test_fetch_verifies_checksum(monkeypatch, tmp_path):
    """A cached file whose bytes do not match the inventory must be rejected."""
    from splatset import _fetch
    monkeypatch.setenv(_paths.ENV_CACHE, str(tmp_path))
    record = splatset.inventory()[0]

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
    from splatset import _fetch
    with pytest.raises(ValueError):
        _fetch.read_url("http://example.com/x.json")


# --- the command line -------------------------------------------------------

def run_cli(capsys, *argv):
    from splatset.__main__ import main
    assert main(list(argv)) == 0
    return capsys.readouterr().out


def test_cli_lists_and_filters_without_the_network(capsys):
    assert str(len(splatset.inventory())) in run_cli(capsys, "summary")

    out = run_cli(capsys, "list")
    for oid in splatset.ids():
        assert oid in out

    only = run_cli(capsys, "list", "--source", "capture")
    for r in splatset.find(source_method="capture"):
        assert r["id"] in only
    for r in splatset.find(source_method="image-to-3d-generation"):
        assert r["id"] not in only

    if splatset.lods():
        tier = splatset.lods()[0]
        tiered = run_cli(capsys, "list", "--lod", tier)
        assert f"@{tier}" in tiered

    assert "@" in run_cli(capsys, "cite")
    assert splatset.ids()[0] in run_cli(capsys, "info", splatset.ids()[0])


def test_cli_get_refuses_to_pull_everything_by_accident():
    from splatset.__main__ import main
    assert main(["get"]) == 2
