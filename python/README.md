# padillasplats

Load a small, hand-made collection of objects as 3D Gaussian splats, in one line.

```bash
pip install padillasplats
```

```python
import padillasplats as ps

print(ps.summary())           # what is in the collection, and under what terms
s = ps.load("plant")          # downloads once, caches, verifies, decodes
s.positions                   # (113648, 3) float32
s.colors                      # (113648, 4) uint8 RGBA
```

You never need a URL. Describe what you want and it is fetched, checksum-verified
and decoded:

```python
ps.load_random(source_method="capture")            # any real scan
ps.load("lucy", lod="10k")                         # one object, small tier
ps.find(source_method="mesh2splat", lod="10k")     # every 10k-gaussian mesh object
```

Everything here was made, cleaned and labelled by one person, so expect a handful
of objects rather than thousands, each with its quirks and its provenance written
down next to it.

## Selecting objects

Filtering runs against an inventory bundled in the package, so it is offline and
instant. Nothing downloads until you load.

```python
ps.find(category="object", min_splats=100_000)
ps.find(source_method="capture")   # real scans only, not generated
ps.find(open_license=True)         # only the freely-licensed objects
ps.find(license="CC-BY-4.0")
ps.find(source_method=["capture", "synthetic-render"])
ps.find(tags=["plant"])
ps.find(has_quality=True)          # only objects carrying PSNR and SSIM
ps.tags(); ps.categories(); ps.source_methods(); ps.licenses(); ps.lods()
```

Every object carries a `category` (`object` or `scene`, what it is) and a
`source_method` (how it was made). `ps.source_methods()` lists them:

| `source_method` | meaning | license |
|---|---|---|
| `capture` | real photogrammetry: a phone video reconstructed with COLMAP + Brush | CC-BY-4.0 |
| `mesh2splat` | converted directly from a known 3D mesh, no photography | that mesh's license |
| `synthetic-render` | trained from renders of a known 3D asset | that asset's license |
| `image-to-3d-generation` | a generative model invented it from a single image | as-is, no warranty |

`category`, `source_method` and `license` each take one value or a list of
allowed values. `ps.find(open_license=True)` (or `s.open_license` on a loaded
object) keeps only the objects with no strings attached; the ones it drops are
still usable, they just carry a condition, spelled out in `license_note`.
`ps.is_open_license(id)` checks a single object.

## Levels of detail

The mesh-derived objects ship at four resolutions: **10k, 100k, 500k and 1M**
gaussians. `ps.lods()` lists them, `ps.lods_of(id)` says which an object has
(empty for a capture, which is a single file), and every download path takes a
`lod=`:

```python
ps.load("lucy", lod="1m")            # the finest tier
ps.load("lucy", lod="min")           # whichever is smallest, for any object
ps.path("armadillo", lod="100k")     # just the local file path
ps.download("./small", lod="10k")    # every 10k tier, ~320 kB each
```

`ps.find(lod=...)` keeps only objects that ship that tier, and returns each one
already resolved to it, so `file`, `splats`, `bytes` and `sha256` describe the
tier you asked for:

```python
ps.find(lod="10k")                                # everything that has a 10k tier
ps.find(source_method="mesh2splat", lod="100k")   # the mesh objects at 100k
ps.find(lod="min", max_bytes=1_000_000)           # anything under a megabyte
```

`"min"` and `"max"` mean the smallest and largest each object has, so they work
on single-file objects too. A named tier an object does not have raises, rather
than quietly handing back a different resolution.

## Picking objects at random

```python
ps.random()                                    # one record, no download
ps.random(source_method="capture", seed=0)     # reproducible
ps.sample(3, category="object")                # three distinct records
s = ps.load_random(source_method="mesh2splat", lod="10k")   # picked and loaded
```

Filters are the same ones `find()` takes. An impossible filter raises
`LookupError` rather than returning nothing, so a typo fails where you made it.

## Loading in bulk

```python
for s in ps.load_all(category="object"):       # one at a time, never all in RAM
    print(s.id, len(s), s.meta["license"])

for s in ps.load_all(source_method="mesh2splat", lod="10k"):
    print(s.id, len(s))                        # ~3 MB for the whole set
```

Or take local copies. With a `lod=`, files are named `<id>_<lod>.splat`, so two
resolutions can share a folder:

```python
ps.download("./splats")                        # everything
ps.download("./big", min_splats=100_000)       # a subset
ps.download("./safe", open_license=True)       # no licence conditions
```

Objects added after this release show up with `ps.refresh_inventory()`, which
pulls the live inventory without upgrading the package.

## From the command line

```bash
python -m padillasplats                                  # what is in here
python -m padillasplats list --source mesh2splat --lod 10k
python -m padillasplats info lucy
python -m padillasplats get lucy --lod 1m                # prints the local path
python -m padillasplats get --source capture --out ./scans
python -m padillasplats random --open-license --get
```

## What you get back

`ps.load()` returns a `Splat`:

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
print(ps.citation())          # BibTeX
print(ps.citation("text"))    # one-line plain text
```

## Caching and safety

Downloads land in a per-user cache: `%LOCALAPPDATA%` on Windows,
`~/Library/Caches` on macOS, `$XDG_CACHE_HOME` or `~/.cache` on Linux. Override
with the `PADILLASPLATS_CACHE` environment variable, or wipe it with
`ps.clear_cache()`. Each level of detail is cached as its own file.

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

`ps.find(open_license=True)` keeps only the first group plus the CC0 and
public-domain meshes, i.e. everything with no condition attached.

## Links

- Repository and data: https://github.com/marcelpadilla/splats
- Browse in the browser: https://marcelpadilla.github.io/Projects/Gaussian_Splat_Object_Dataset/
