# splatset

A free collection of 109 objects as 3D Gaussian splats, one line to load any of
them.

```bash
pip install splatset
```

```python
import splatset

print(splatset.summary())    # what is in the collection
s = splatset.load("plant")   # downloads once, caches, checks, decodes
s.positions                  # (113648, 3) float32
s.colors                     # (113648, 4) uint8 RGBA
```

## Finding objects

You never write a URL. Filtering runs offline against an inventory bundled in the
package, and nothing downloads until you load.

```python
splatset.find(source_method="capture")           # real scans only
splatset.find(open_license=True)                 # freely licensed only
splatset.find(category="object", min_splats=100_000)
splatset.find(tags=["plant"])
splatset.random(seed=0)                          # one record, no download
splatset.load_random(source_method="capture")    # or just give me one
```

`splatset.tags()`, `categories()`, `source_methods()`, `licenses()` and `lods()`
list what you can filter on. An impossible filter raises `LookupError` instead of
returning nothing, so a typo fails where you made it.

Every object has a `category` (`object` or `scene`) and a `source_method`:

| `source_method` | meaning | license |
|---|---|---|
| `capture` | a phone video reconstructed with COLMAP and Brush | CC-BY-4.0 |
| `mesh2splat` | converted from a known mesh, no photography | that mesh's license |
| `synthetic-render` | trained from renders of a known asset | that asset's license |
| `image-to-3d-generation` | a model invented it from one image | as-is, no warranty |

## Levels of detail

Mesh objects come at **10k, 100k, 500k and 1M** gaussians. Every call takes a
`lod=`, and `"min"` or `"max"` work on single-file objects too.

```python
splatset.load("lucy", lod="1m")
splatset.find(lod="10k")                  # only objects that have a 10k tier
splatset.download("./small", lod="min")   # local copies, smallest of each
```

`find(lod=...)` hands back each record already resolved to that tier, so `file`,
`splats`, `bytes` and `sha256` describe what you asked for. A tier an object does
not have raises, rather than quietly giving you a different resolution.

## Loading in bulk

```python
for s in splatset.load_all(category="object"):   # one at a time, never all in RAM
    print(s.id, len(s), s.license)

splatset.download("./splats")                    # or take local copies
```

Objects added after this release appear with `splatset.refresh_inventory()`,
which pulls the live inventory without upgrading the package.

## From the command line

```bash
python -m splatset                     # what is in here
python -m splatset list --source mesh2splat --lod 10k
python -m splatset get lucy --lod 1m   # prints the local path
```

## What you get back

`splatset.load()` returns a `Splat`:

| Attribute | Shape | Meaning |
|---|---|---|
| `positions` | (N, 3) float32 | x, y, z |
| `scales` | (N, 3) float32 | linear, already exponentiated |
| `colors` | (N, 4) uint8 | R, G, B, A where A is opacity |
| `rotations` | (N, 4) float32 | unit quaternion, w, x, y, z |
| `meta` | dict | that object's inventory record |

Plus `len(s)`, `s.rgb`, `s.opacity`, `s.bounds()` and the shortcuts `s.license`,
`s.source_method`, `s.category`, `s.lod` and `s.open_license`.

Up is `-y`. Spherical harmonics are dropped, so there is no view-dependent
shading. Every object sits on the origin and is scaled so its longest side is 1,
so any two of them load at the same size and switching `lod=` never makes an
object jump. That is a relative scale, not metres.

## Cache

Downloads land in a per-user cache. `SPLATSET_CACHE` overrides where,
`splatset.clear_cache()` wipes it. Every file is checked against the SHA-256 in
the inventory and rejected on mismatch. Transfers are HTTPS only, nothing is ever
unpickled or evaluated, and numpy is the only dependency.

## License

Every object carries its own license as `license`, with the terms in
`license_note` and `s.open_license` as the quick boolean.

- **Scanned** objects are CC-BY-4.0. Use them anywhere, credit Marcel Padilla.
- **Mesh and rendered** objects keep the license of the source mesh. Most are
  CC-BY or CC0, eight are NonCommercial, and six come from the Stanford 3D
  Scanning Repository. Credit the mesh author, not me.
- **Generated** objects are as-is, with no warranty of rights.
- **This package's code** is 0BSD. No attribution required.

`find(open_license=True)` keeps the 32 objects under a Creative Commons or public
domain license. That is not the same as asking nothing, because CC-BY still
requires attribution, which each record's `attribution` field spells out. For the
objects that ask nothing at all, filter `license=["CC0-1.0", "Public Domain"]`.

## Citing

```python
print(splatset.citation())        # BibTeX
print(splatset.citation("text"))  # one line
```

## Links

- Repository and data: https://github.com/marcelpadilla/splats
- Browse in the browser: https://marcelpadilla.github.io/Projects/Gaussian_Splat_Object_Dataset/
