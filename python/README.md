# padillasplats

Load a small, hand-cleaned collection of everyday objects scanned as 3D Gaussian splats, in one line.

```bash
pip install padillasplats
```

```python
import padillasplats as ps

ps.ids()                      # ['plant', 'academic_tarot_cards']
s = ps.load("plant")          # downloads once, caches, verifies, decodes
s.positions                   # (113648, 3) float32
s.colors                      # (113648, 4) uint8 RGBA
```

Every object was captured, trained and cleaned by hand by one person. Expect a
handful of objects, not thousands, and expect each to be a real capture with its
real quirks, documented next to it.

## Selecting objects

Filtering runs against an inventory bundled in the package, so it is offline and
instant. Nothing downloads until you load.

```python
ps.find(category="object", min_splats=100_000)
ps.find(tags=["plant"])
ps.find(has_quality=True)          # only objects carrying PSNR and SSIM
ps.tags(); ps.categories()
```

Loop over a selection, downloading one at a time:

```python
for s in ps.load_all(category="object"):
    print(s.id, len(s), s.meta["license"])
```

Or take local copies:

```python
ps.download("./splats")                        # everything
ps.download("./big", min_splats=100_000)       # a subset
```

Objects added after this release show up with `ps.refresh_inventory()`, which
pulls the live inventory without upgrading the package.

## What you get back

`ps.load()` returns a `Splat`:

| Attribute | Shape | Meaning |
|---|---|---|
| `positions` | (N, 3) float32 | x, y, z |
| `scales` | (N, 3) float32 | linear, already exponentiated |
| `colors` | (N, 4) uint8 | R, G, B, A where A is opacity |
| `rotations` | (N, 4) float32 | unit quaternion, w, x, y, z |
| `meta` | dict | that object's inventory record |

Plus `len(s)`, `s.rgb`, `s.opacity`, `s.bounds()`.

Up is `-y`, following the Inria and Brush convention. Scale is the COLMAP
reconstruction scale and is not metric. Spherical harmonics are dropped, so
there is no view-dependent shading.

## Caching and safety

Downloads land in a per-user cache: `%LOCALAPPDATA%` on Windows,
`~/Library/Caches` on macOS, `$XDG_CACHE_HOME` or `~/.cache` on Linux. Override
with the `PADILLASPLATS_CACHE` environment variable, or wipe it with
`ps.clear_cache()`.

Every download is checked against the SHA-256 recorded in the inventory and
rejected on mismatch, so a compromise of the hosting side cannot hand you
altered bytes. Transfers are HTTPS only. The loader never unpickles or evaluates
anything it downloads: `.splat` bytes go straight into a numpy array. numpy is
the only dependency.

## Licensing

Two different licenses, on purpose:

- **The splat data is CC-BY-4.0.** Use it anywhere, including commercially, but
  credit Marcel Padilla.
- **This package's code is 0BSD.** No attribution required for the code itself.

## Links

- Repository and data: https://github.com/marcelpadilla/splats
- Browse in the browser: https://marcelpadilla.github.io/Projects/Gaussian_Splat_Object_Dataset/
