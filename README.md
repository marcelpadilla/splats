# splats

A small, hand-cleaned collection of everyday objects scanned as 3D Gaussian splats, free to use.

Every object here was captured, trained and cleaned by one person, so expect a
handful of them rather than thousands. Each is a real capture with its real
quirks, and each ships with its capture conditions, pipeline settings and known
caveats written down next to it.

**[Download everything](https://github.com/marcelpadilla/splats/archive/refs/heads/main.zip)**
&nbsp;·&nbsp;
[Browse in your browser](https://marcelpadilla.github.io/Projects/Gaussian_Splat_Object_Dataset/)
&nbsp;·&nbsp;
`pip install padillasplats`

## The collection

<!-- inventory:start -->
| | Object | Category | Gaussians | Size | PSNR / SSIM | Download |
|---|---|---|--:|--:|:--:|:--:|
| <img src="data/plant/thumb.jpg" width="220"> | **Houseplant**<br><sub>`plant`</sub><br><sub>plant, houseplant, foliage, organic, indoor, glossy</sub> | object | 113,648 | 3.6 MB | not measured | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/plant/plant.splat) · [meta](data/plant/meta.json) |
| <img src="data/academic_tarot_cards/thumb.jpg" width="220"> | **Academic Tarot Cards box**<br><sub>`academic_tarot_cards`</sub><br><sub>box, packaging, cardboard, print, indoor, boxy</sub> | object | 114,865 | 3.7 MB | 25.97 / 0.906 | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/academic_tarot_cards/academic_tarot_cards.splat) · [meta](data/academic_tarot_cards/meta.json) |

<sub>2 objects · 228,513 gaussians · 7.3 MB total</sub>
<!-- inventory:end -->

## Use it from Python

```bash
pip install padillasplats
```

```python
import padillasplats as ps

s = ps.load("plant")     # downloads once, caches, verifies the checksum, decodes
s.positions              # (113648, 3) float32
s.colors                 # (113648, 4) uint8 RGBA
```

Pick objects by inventory conditions without downloading anything:

```python
ps.find(category="object", min_splats=100_000)
ps.find(tags=["plant"])
ps.find(has_quality=True)              # only objects carrying PSNR and SSIM

for s in ps.load_all(category="object"):
    print(s.id, len(s))

ps.download("./splats")                # local copies of everything
```

Full package documentation: [python/README.md](python/README.md).

## Format

One `.splat` per object, the antimatter15 packing: a header-less array of
32-byte records, so the gaussian count is exactly `filesize // 32`.

| bytes | type | meaning |
|---|---|---|
| `0:12` | 3x float32 | position x, y, z |
| `12:24` | 3x float32 | scale x, y, z, linear and already exponentiated |
| `24:28` | 4x uint8 | colour R, G, B, A, where A is opacity |
| `28:32` | 4x uint8 | rotation quaternion w, x, y, z, as `q * 128 + 128` |

Up is `-y`, following the Inria and Brush convention. Scale is the COLMAP
reconstruction scale and is **not metric**. Spherical harmonics are dropped
(SH degree 0), so there is no view-dependent shading, but the files stay small
and every browser viewer reads them.

The format has no header and no trailer, so there is nowhere inside a `.splat`
to put metadata without breaking the `filesize // 32` invariant that every other
reader depends on. Metadata therefore lives in `data/inventory.json` and in each
object's `meta.json`, never in the splat itself.

## Licensing

Two licenses, on purpose:

- **The data in `data/` is [CC-BY-4.0](LICENSE).** Use it for anything,
  including commercially. You must credit the author.
- **The code in `python/` is [0BSD](python/LICENSE).** No attribution required.

Credit line you can paste:

> Gaussian splat by Marcel Padilla, from https://github.com/marcelpadilla/splats, licensed CC-BY-4.0.

Every object is the author's own capture of a generic or self-made object. The
license covers the capture and reconstruction, not the industrial design of any
object depicted.

## Layout

```
data/
  inventory.json          the machine-readable index, and the source of truth
  <id>/
    <id>.splat            the gaussians
    meta.json             capture, pipeline, quality, caveats
    thumb.jpg             the gallery image above
python/                   the padillasplats package
LICENSE                   CC-BY-4.0, for the data
```

## Adding an object

1. Put `data/<id>/<id>.splat`, its `meta.json` and a `thumb.jpg` in place.
2. Add an entry to `data/inventory.json`, including its SHA-256.
3. Run `python python/sync_inventory.py`, which refreshes the copy bundled in
   the package and regenerates the gallery table above.
4. Run `python -m pytest python/tests` to confirm the checksums and counts agree.

Existing installs pick up new objects with `ps.refresh_inventory()`, without a
package upgrade.
