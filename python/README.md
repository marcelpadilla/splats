# splatset

Load a free collection of objects as 3D Gaussian splats, in one line.

```bash
pip install splatset
```

```python
import splatset

print(splatset.summary())   # what is in the collection, and under what terms
s = splatset.load("plant")  # downloads once, caches, verifies, decodes
s.positions                 # (113648, 3) float32
s.colors                    # (113648, 4) uint8 RGBA
```

You never need a URL. Describe what you want and it is fetched, checksum-verified
and decoded:

```python
splatset.load_random(source_method="capture")            # any real scan
splatset.load("lucy", lod="10k")                         # one object, small tier
splatset.find(source_method="mesh2splat", lod="10k")     # every 10k-gaussian mesh object
```

Everything here was made and labelled by one person, so expect a hundred objects
rather than a hundred thousand, each with its quirks and its provenance written
down next to it.

## Selecting objects

Filtering runs against an inventory bundled in the package, so it is offline and
instant. Nothing downloads until you load.

```python
splatset.find(category="object", min_splats=100_000)
splatset.find(source_method="capture")   # real scans only, not generated
splatset.find(open_license=True)         # only the freely-licensed objects
splatset.find(license="CC-BY-4.0")
splatset.find(source_method=["capture", "synthetic-render"])
splatset.find(tags=["plant"])
splatset.find(has_quality=True)          # only objects carrying PSNR and SSIM
splatset.tags(); splatset.categories(); splatset.source_methods()
splatset.licenses(); splatset.lods()
```

Every object carries a `category` (`object` or `scene`, what it is) and a
`source_method` (how it was made). `splatset.source_methods()` lists them:

| `source_method` | meaning | license |
|---|---|---|
| `capture` | real photogrammetry: a phone video reconstructed with COLMAP + Brush | CC-BY-4.0 |
| `mesh2splat` | converted directly from a known 3D mesh, no photography | that mesh's license |
| `synthetic-render` | trained from renders of a known 3D asset | that asset's license |
| `image-to-3d-generation` | a generative model invented it from a single image | as-is, no warranty |

`category`, `source_method` and `license` each take one value or a list of
allowed values. `splatset.find(open_license=True)` (or `s.open_license` on a loaded
object) keeps only the objects with no strings attached; the ones it drops are
still usable, they just carry a condition, spelled out in `license_note`.
`splatset.is_open_license(id)` checks a single object.

## Levels of detail

The mesh-derived objects ship at four resolutions: **10k, 100k, 500k and 1M**
gaussians. `splatset.lods()` lists them, `splatset.lods_of(id)` says which an object has
(empty for a capture, which is a single file), and every download path takes a
`lod=`:

```python
splatset.load("lucy", lod="1m")            # the finest tier
splatset.load("lucy", lod="min")           # whichever is smallest, for any object
splatset.path("armadillo", lod="100k")     # just the local file path
splatset.download("./small", lod="10k")    # every 10k tier, ~320 kB each
```

`splatset.find(lod=...)` keeps only objects that ship that tier, and returns each one
already resolved to it, so `file`, `splats`, `bytes` and `sha256` describe the
tier you asked for:

```python
splatset.find(lod="10k")                                # everything that has a 10k tier
splatset.find(source_method="mesh2splat", lod="100k")   # the mesh objects at 100k
splatset.find(lod="min", max_bytes=1_000_000)           # anything under a megabyte
```

`"min"` and `"max"` mean the smallest and largest each object has, so they work
on single-file objects too. A named tier an object does not have raises, rather
than quietly handing back a different resolution.

## Picking objects at random

```python
splatset.random()                                                # one record, no download
splatset.random(source_method="capture", seed=0)                 # reproducible
splatset.sample(3, category="object")                            # three distinct records
s = splatset.load_random(source_method="mesh2splat", lod="10k")  # picked and loaded
```

Filters are the same ones `find()` takes. An impossible filter raises
`LookupError` rather than returning nothing, so a typo fails where you made it.

## Loading in bulk

```python
for s in splatset.load_all(category="object"):       # one at a time, never all in RAM
    print(s.id, len(s), s.meta["license"])

for s in splatset.load_all(source_method="mesh2splat", lod="10k"):
    print(s.id, len(s))                        # ~3 MB for the whole set
```

Or take local copies. With a `lod=`, files are named `<id>_<lod>.splat`, so two
resolutions can share a folder:

```python
splatset.download("./splats")                        # everything
splatset.download("./big", min_splats=100_000)       # a subset
splatset.download("./safe", open_license=True)       # no licence conditions
```

Objects added after this release show up with `splatset.refresh_inventory()`, which
pulls the live inventory without upgrading the package.

## From the command line

```bash
python -m splatset                                  # what is in here
python -m splatset list --source mesh2splat --lod 10k
python -m splatset info lucy
python -m splatset get lucy --lod 1m                # prints the local path
python -m splatset get --source capture --out ./scans
python -m splatset random --open-license --get
```

## What you get back

`splatset.load()` returns a `Splat`:

| Attribute | Shape | Meaning |
|---|---|---|
| `positions` | (N, 3) float32 | x, y, z |
| `scales` | (N, 3) float32 | linear, already exponentiated |
| `colors` | (N, 4) uint8 | R, G, B, A where A is opacity |
| `rotations` | (N, 4) float32 | unit quaternion, w, x, y, z |
| `meta` | dict | that object's inventory record, resolved to the tier you loaded |

Plus `len(s)`, `s.rgb`, `s.opacity`, `s.bounds()`, and the provenance shortcuts
`s.license`, `s.source_method`, `s.category`, `s.lod`, and `s.open_license`.

Up is `-y`, following the Inria and Brush convention. Scale is not metric.
Spherical harmonics are dropped, so there is no view-dependent shading.

## Citing

```python
print(splatset.citation())          # BibTeX
print(splatset.citation("text"))    # one-line plain text
```

## Caching and safety

Downloads land in a per-user cache: `%LOCALAPPDATA%` on Windows,
`~/Library/Caches` on macOS, `$XDG_CACHE_HOME` or `~/.cache` on Linux. Override
with the `SPLATSET_CACHE` environment variable, or wipe it with
`splatset.clear_cache()`. Each level of detail is cached as its own file.

Every download is checked against the SHA-256 recorded in the inventory and
rejected on mismatch, so a compromise of the hosting side cannot hand you
altered bytes. Transfers are HTTPS only. The loader never unpickles or evaluates
anything it downloads: `.splat` bytes go straight into a numpy array. numpy is
the only dependency.

## Licensing

The data license depends on how each object was made. It is on every record as
`license`, with the terms in `license_note`, and `s.open_license` is the quick
boolean:

- **Scanned objects are CC-BY-4.0.** Use them anywhere, including commercially,
  but credit Marcel Padilla.
- **Mesh-derived and rendered objects inherit the license of the mesh they came
  from.** Most are CC0 or public domain and need nothing. The Stanford 3D
  Scanning Repository objects (`stanford_bunny`, `armadillo`, `dragon`, `happy`,
  `lucy`, `xyzrgb_dragon`) are free to use, including commercially, but are
  **not** Creative Commons: acknowledge Stanford and do not misrepresent the
  data. The rendered bunny is CC-BY-3.0; credit Makerbot.
- **Generated objects are as-is, with no warranty of rights.** An AI model
  invented them from an image and its training data is undisclosed, so they are
  not under CC-BY; you clear any rights for your use.
- **This package's code is 0BSD.** No attribution required for the code itself.

`splatset.find(open_license=True)` keeps only the first group plus the CC0 and
public-domain meshes, i.e. everything with no condition attached.

## Links

- Repository and data: https://github.com/marcelpadilla/splats
- Browse in the browser: https://marcelpadilla.github.io/Projects/Gaussian_Splat_Object_Dataset/
