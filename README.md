# splats

A small, hand-cleaned collection of everyday objects scanned as 3D Gaussian splats, free to use.

Every object here was captured, trained and cleaned by one person, so expect a
handful of them rather than thousands. Each is a real capture with its real
quirks, and each ships with its capture conditions, pipeline settings and known
caveats written down next to it.

[Browse in your browser](https://marcelpadilla.github.io/Projects/Gaussian_Splat_Object_Dataset/)
&nbsp;·&nbsp;
[Cite](#citing)
&nbsp;·&nbsp;
[License](#licensing)

## Use it from Python

```bash
pip install padillasplats
```

```python
import padillasplats as ps

s = ps.load("plant")     # downloads once, caches, verifies the checksum, decodes
s.positions              # (113648, 3) float32
s.colors                 # (113648, 4) uint8 RGBA

for s in ps.load_all(category="object"):   # loop over the whole collection
    print(s.id, len(s))
```

Filtering runs against a bundled inventory, so it is offline and instant, and
nothing downloads until you load:

```python
ps.find(category="object", min_splats=100_000)
ps.find(source_method="capture")     # real scans only, not generated
ps.find(tags=["plant"])
ps.download("./splats")              # local copies of everything
```

Full package docs: [python/README.md](python/README.md).

## Download

- **Everything, as a zip:** [main.zip](https://github.com/marcelpadilla/splats/archive/refs/heads/main.zip)
  (the whole repository, `data/` included).
- **One object at a time:** the download links in the table below, or
  `data/<id>/<id>.splat` in the tree.
- **From Python:** `ps.download("./splats")`, or `ps.load("<id>")` to get it
  straight into numpy.

## The collection

Every object carries a **category** (`object` or `scene`, what it is) and a
**source method** (how it was made): `capture` is real photogrammetry from a
phone video, `image-to-3d-generation` is invented by a model from a single
image, `synthetic-render` is trained from renders of a known 3D asset. The
**Type** column below reads both at once.

<!-- inventory:start -->
| | Object | Type | Gaussians | Size | PSNR / SSIM | Download |
|---|---|---|--:|--:|:--:|:--:|
| <img src="data/plant/thumb.jpg" width="220"> | **Houseplant**<br><sub>`plant`</sub><br><sub>plant, houseplant, foliage, organic, indoor, glossy</sub> | Captured object | 113,648 | 3.6 MB | not measured | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/plant/plant.splat) · [meta](data/plant/meta.json) |
| <img src="data/academic_tarot_cards/thumb.jpg" width="220"> | **Academic Tarot Cards box**<br><sub>`academic_tarot_cards`</sub><br><sub>box, packaging, cardboard, print, indoor, boxy</sub> | Captured object | 114,865 | 3.7 MB | 25.97 / 0.906 | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/academic_tarot_cards/academic_tarot_cards.splat) · [meta](data/academic_tarot_cards/meta.json) |

<sub>2 objects · 228,513 gaussians · 7.3 MB total</sub>
<!-- inventory:end -->

The machine-readable index of all of this is
[`data/inventory.json`](data/inventory.json): one record per object with its
checksum, dimensions, tags, category and source method. It is the single source
of truth that drives the table above, the website, and the Python package.

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

There is nowhere inside a `.splat` to put metadata without breaking the
`filesize // 32` invariant every reader depends on, so metadata lives in
`data/inventory.json` and each object's `meta.json`, never in the splat itself.

## Citing

If you use these in your work, a citation is appreciated (and required by the
data license). The BibTeX is also available from Python as `ps.citation()`.

<!-- citation:start -->
```bibtex
@misc{padilla_splats,
  author       = {Marcel Padilla},
  title        = {splats: a small collection of Gaussian splat objects},
  year         = {2026},
  howpublished = {\url{https://github.com/marcelpadilla/splats}}
}
```
<!-- citation:end -->

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
2. Add an entry to `data/inventory.json`, including its SHA-256, `category` and
   `source_method`.
3. Run `python python/sync_inventory.py`, which refreshes the copy bundled in
   the package and regenerates the gallery and citation blocks above.
4. Run `python -m pytest python/tests` to confirm the checksums and counts agree.

The website reads `data/inventory.json` straight from this repository, and
existing package installs pick up new objects with `ps.refresh_inventory()`, so
neither needs a separate update.
