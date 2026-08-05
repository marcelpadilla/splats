# splats

A small, hand-made collection of objects as 3D Gaussian splats, free to use.

Three ways of making one, in one place: everyday things **scanned** from a phone
video, classic meshes converted straight **from geometry** at four resolutions,
and a couple **generated** by an AI model from a single image. Everything here
was made, cleaned and labelled by one person, so expect a handful of objects
rather than thousands. Each ships with how it was made, its pipeline settings,
its license and its known caveats written down next to it.

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
ps.find(open_license=True)           # only the freely-licensed objects
ps.find(tags=["plant"])
ps.download("./scans", open_license=True)   # local copies, safe licenses only
```

The mesh-derived objects ship at **10k / 100k / 500k / 1M** gaussians, and every
download path takes the tier you want, so you never assemble a URL:

```python
ps.load("lucy", lod="10k")                        # one object, small tier
ps.find(source_method="mesh2splat", lod="10k")    # everything that has a 10k tier
ps.download("./small", lod="min")                 # the smallest of each object
ps.load_random(source_method="capture")           # or just give me one
```

Every object also carries its license, so you can stay on the safe side of the
rights in one line: `open_license=True` keeps only what has no condition
attached, and `ps.is_open_license("<id>")` checks a single one.
`print(ps.summary())` prints the whole picture.

There is a command line too:

```bash
python -m padillasplats list --source mesh2splat --lod 10k
python -m padillasplats get lucy --lod 1m
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

Every object carries a **Kind** (`object` or `scene`, what it is) and a
**Source** (how it was made): `capture` (Scanned) is real photogrammetry from a
phone video, `mesh2splat` (Geometry) is converted directly from a known mesh with
no photography and no training, `synthetic-render` (Rendered) is trained from
renders of a known 3D asset, and `image-to-3d-generation` (Generated) is invented
by a model from a single image. The license sits under each Source, because it
depends on how the object was made (see [Licensing](#licensing)).

Geometry objects list four levels of detail with a download link each; the colour
of a mesh2splat object encodes its tier (10k red, 100k yellow, 500k green, 1M
blue), so you can see at a glance which resolution you are looking at.

<!-- inventory:start -->
| | Object | Source | Kind | Size | Download |
|---|---|---|---|--:|:--:|
| <img src="data/plant/thumb.png" width="220"> | **Houseplant**<br><sub>`plant`</sub><br><sub>plant, houseplant, foliage, organic, indoor, glossy</sub> | Scanned<br><sub>CC-BY-4.0</sub> | Object | ~113k · 3.6 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/plant/plant.splat) · [meta](data/plant/meta.json) |
| <img src="data/academic_tarot_cards/thumb.png" width="220"> | **Academic Tarot Cards box**<br><sub>`academic_tarot_cards`</sub><br><sub>box, packaging, cardboard, print, indoor, boxy</sub> | Scanned<br><sub>CC-BY-4.0</sub> | Object | ~114k · 3.7 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/academic_tarot_cards/academic_tarot_cards.splat) · [meta](data/academic_tarot_cards/meta.json) |
| <img src="data/textile_ball/thumb.png" width="220"> | **Textile ball**<br><sub>`textile_ball`</sub><br><sub>ball, textile, fabric, sphere, decor, bumpy</sub> | Scanned<br><sub>CC-BY-4.0</sub> | Object | ~384k · 12.3 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/textile_ball/textile_ball.splat) · [meta](data/textile_ball/meta.json) |
| <img src="data/plant_generated/thumb.png" width="220"> | **Houseplant (generated)**<br><sub>`plant_generated`</sub><br><sub>plant, houseplant, foliage, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/plant_generated/plant_generated.splat) · [meta](data/plant_generated/meta.json) |
| <img src="data/bunny_render/thumb.png" width="220"> | **Stanford bunny (rendered)**<br><sub>`bunny_render`</sub><br><sub>bunny, stanford-bunny, rendered, synthetic, test-model</sub> | Rendered<br><sub>CC-BY-3.0</sub> | Object | ~188k · 6.0 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/bunny_render/bunny_render.splat) · [meta](data/bunny_render/meta.json) |
| <img src="data/bunny_generated/thumb.png" width="220"> | **Stanford bunny (generated)**<br><sub>`bunny_generated`</sub><br><sub>bunny, stanford-bunny, generated, ai, test-model, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/bunny_generated/bunny_generated.splat) · [meta](data/bunny_generated/meta.json) |
| <img src="data/spot/thumb.png" width="220"> | **Spot**<br><sub>`spot`</sub><br><sub>cow, keenan-crane, classic, test-model, cute</sub> | Geometry<br><sub>CC0-1.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/spot/spot_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/spot/spot_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/spot/spot_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/spot/spot_1m.splat)<br><sub>[meta](data/spot/meta.json)</sub> |
| <img src="data/bob/thumb.png" width="220"> | **Bob**<br><sub>`bob`</sub><br><sub>blob, keenan-crane, classic, test-model</sub> | Geometry<br><sub>CC0-1.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/bob/bob_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/bob/bob_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/bob/bob_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/bob/bob_1m.splat)<br><sub>[meta](data/bob/meta.json)</sub> |
| <img src="data/teapot/thumb.png" width="220"> | **Utah Teapot**<br><sub>`teapot`</sub><br><sub>teapot, utah, classic, newell</sub> | Geometry<br><sub>Public Domain</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/teapot/teapot_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/teapot/teapot_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/teapot/teapot_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/teapot/teapot_1m.splat)<br><sub>[meta](data/teapot/meta.json)</sub> |
| <img src="data/cylinder/thumb.png" width="220"> | **Cylinder**<br><sub>`cylinder`</sub><br><sub>primitive, cylinder</sub> | Geometry<br><sub>CC0-1.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/cylinder/cylinder_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/cylinder/cylinder_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/cylinder/cylinder_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/cylinder/cylinder_1m.splat)<br><sub>[meta](data/cylinder/meta.json)</sub> |
| <img src="data/torus/thumb.png" width="220"> | **Torus**<br><sub>`torus`</sub><br><sub>primitive, torus, donut</sub> | Geometry<br><sub>CC0-1.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/torus/torus_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/torus/torus_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/torus/torus_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/torus/torus_1m.splat)<br><sub>[meta](data/torus/meta.json)</sub> |
| <img src="data/ring/thumb.png" width="220"> | **Ring**<br><sub>`ring`</sub><br><sub>primitive, ring, torus</sub> | Geometry<br><sub>CC0-1.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/ring/ring_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/ring/ring_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/ring/ring_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/ring/ring_1m.splat)<br><sub>[meta](data/ring/meta.json)</sub> |
| <img src="data/stanford_bunny/thumb.png" width="220"> | **Stanford Bunny**<br><sub>`stanford_bunny`</sub><br><sub>bunny, stanford-bunny, classic, test-model</sub> | Geometry<br><sub>Stanford 3DSR (attribution)</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/stanford_bunny/stanford_bunny_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/stanford_bunny/stanford_bunny_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/stanford_bunny/stanford_bunny_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/stanford_bunny/stanford_bunny_1m.splat)<br><sub>[meta](data/stanford_bunny/meta.json)</sub> |
| <img src="data/armadillo/thumb.png" width="220"> | **Armadillo**<br><sub>`armadillo`</sub><br><sub>armadillo, stanford, classic, test-model, organic</sub> | Geometry<br><sub>Stanford 3DSR (attribution)</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/armadillo/armadillo_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/armadillo/armadillo_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/armadillo/armadillo_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/armadillo/armadillo_1m.splat)<br><sub>[meta](data/armadillo/meta.json)</sub> |
| <img src="data/dragon/thumb.png" width="220"> | **Stanford Dragon**<br><sub>`dragon`</sub><br><sub>dragon, stanford, classic, test-model, detailed</sub> | Geometry<br><sub>Stanford 3DSR (attribution)</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/dragon/dragon_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/dragon/dragon_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/dragon/dragon_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/dragon/dragon_1m.splat)<br><sub>[meta](data/dragon/meta.json)</sub> |
| <img src="data/happy/thumb.png" width="220"> | **Happy Buddha**<br><sub>`happy`</sub><br><sub>buddha, happy-buddha, stanford, classic, test-model, detailed</sub> | Geometry<br><sub>Stanford 3DSR (attribution)</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/happy/happy_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/happy/happy_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/happy/happy_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/happy/happy_1m.splat)<br><sub>[meta](data/happy/meta.json)</sub> |
| <img src="data/lucy/thumb.png" width="220"> | **Lucy**<br><sub>`lucy`</sub><br><sub>lucy, angel, statue, stanford, classic, test-model</sub> | Geometry<br><sub>Stanford 3DSR (attribution)</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/lucy/lucy_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/lucy/lucy_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/lucy/lucy_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/lucy/lucy_1m.splat)<br><sub>[meta](data/lucy/meta.json)</sub> |
| <img src="data/xyzrgb_dragon/thumb.png" width="220"> | **XYZ RGB Dragon**<br><sub>`xyzrgb_dragon`</sub><br><sub>dragon, stanford, xyz-rgb, test-model, detailed, high-poly</sub> | Geometry<br><sub>Stanford 3DSR (attribution)</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/xyzrgb_dragon/xyzrgb_dragon_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/xyzrgb_dragon/xyzrgb_dragon_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/xyzrgb_dragon/xyzrgb_dragon_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/xyzrgb_dragon/xyzrgb_dragon_1m.splat)<br><sub>[meta](data/xyzrgb_dragon/meta.json)</sub> |
| <img src="data/shell/thumb.png" width="220"> | **Abalone shell**<br><sub>`shell`</sub><br><sub>shell, abalone, nacre, mother-of-pearl, iridescent, organic, natural</sub> | Scanned<br><sub>CC-BY-4.0</sub> | Object | ~187k · 6.0 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/shell/shell.splat) · [meta](data/shell/meta.json) |
| <img src="data/boat/thumb.png" width="220"> | **Boat**<br><sub>`boat`</sub><br><sub>boat, ship, vehicle, hull</sub> | Geometry<br><sub>CC-BY-4.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/boat/boat_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/boat/boat_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/boat/boat_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/boat/boat_1m.splat)<br><sub>[meta](data/boat/meta.json)</sub> |
| <img src="data/boot/thumb.png" width="220"> | **Boot**<br><sub>`boot`</sub><br><sub>boot, shoe, footwear, leather</sub> | Geometry<br><sub>CC-BY-4.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/boot/boot_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/boot/boot_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/boot/boot_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/boot/boot_1m.splat)<br><sub>[meta](data/boot/meta.json)</sub> |
| <img src="data/cat/thumb.png" width="220"> | **Cat**<br><sub>`cat`</sub><br><sub>cat, animal, pet, stretching</sub> | Geometry<br><sub>CC-BY-4.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/cat/cat_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/cat/cat_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/cat/cat_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/cat/cat_1m.splat)<br><sub>[meta](data/cat/meta.json)</sub> |
| <img src="data/cheese/thumb.png" width="220"> | **Cheese**<br><sub>`cheese`</sub><br><sub>cheese, food, wedge</sub> | Geometry<br><sub>CC-BY-4.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/cheese/cheese_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/cheese/cheese_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/cheese/cheese_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/cheese/cheese_1m.splat)<br><sub>[meta](data/cheese/meta.json)</sub> |
| <img src="data/cube/thumb.png" width="220"> | **Cube**<br><sub>`cube`</sub><br><sub>cube, primitive, box</sub> | Geometry<br><sub>CC-BY-4.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/cube/cube_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/cube/cube_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/cube/cube_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/cube/cube_1m.splat)<br><sub>[meta](data/cube/meta.json)</sub> |
| <img src="data/demosthenes/thumb.png" width="220"> | **Demosthenes**<br><sub>`demosthenes`</sub><br><sub>bust, statue, sculpture, portrait, classical</sub> | Geometry<br><sub>CC-BY-4.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/demosthenes/demosthenes_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/demosthenes/demosthenes_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/demosthenes/demosthenes_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/demosthenes/demosthenes_1m.splat)<br><sub>[meta](data/demosthenes/meta.json)</sub> |
| <img src="data/goathead/thumb.png" width="220"> | **Goat head**<br><sub>`goathead`</sub><br><sub>goat, head, animal, horns</sub> | Geometry<br><sub>CC-BY-3.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/goathead/goathead_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/goathead/goathead_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/goathead/goathead_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/goathead/goathead_1m.splat)<br><sub>[meta](data/goathead/meta.json)</sub> |
| <img src="data/hammer/thumb.png" width="220"> | **Hammer**<br><sub>`hammer`</sub><br><sub>hammer, tool, hardware</sub> | Geometry<br><sub>CC-BY-4.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/hammer/hammer_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/hammer/hammer_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/hammer/hammer_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/hammer/hammer_1m.splat)<br><sub>[meta](data/hammer/meta.json)</sub> |
| <img src="data/koala/thumb.png" width="220"> | **Koala**<br><sub>`koala`</sub><br><sub>koala, animal, bear</sub> | Geometry<br><sub>CC-BY-3.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/koala/koala_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/koala/koala_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/koala/koala_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/koala/koala_1m.splat)<br><sub>[meta](data/koala/meta.json)</sub> |
| <img src="data/mountain/thumb.png" width="220"> | **Mountain**<br><sub>`mountain`</sub><br><sub>mountain, terrain, landscape, peak</sub> | Geometry<br><sub>CC-BY-4.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/mountain/mountain_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/mountain/mountain_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/mountain/mountain_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/mountain/mountain_1m.splat)<br><sub>[meta](data/mountain/meta.json)</sub> |
| <img src="data/parsnip/thumb.png" width="220"> | **Parsnip**<br><sub>`parsnip`</sub><br><sub>parsnip, vegetable, food, root</sub> | Geometry<br><sub>CC-BY-4.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/parsnip/parsnip_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/parsnip/parsnip_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/parsnip/parsnip_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/parsnip/parsnip_1m.splat)<br><sub>[meta](data/parsnip/meta.json)</sub> |
| <img src="data/penguin/thumb.png" width="220"> | **Penguin**<br><sub>`penguin`</sub><br><sub>penguin, animal, bird, cartoon</sub> | Geometry<br><sub>CC-BY-4.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/penguin/penguin_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/penguin/penguin_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/penguin/penguin_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/penguin/penguin_1m.splat)<br><sub>[meta](data/penguin/meta.json)</sub> |
| <img src="data/pizza/thumb.png" width="220"> | **Pizza**<br><sub>`pizza`</sub><br><sub>pizza, food, flat</sub> | Geometry<br><sub>CC-BY-4.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/pizza/pizza_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/pizza/pizza_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/pizza/pizza_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/pizza/pizza_1m.splat)<br><sub>[meta](data/pizza/meta.json)</sub> |
| <img src="data/plane/thumb.png" width="220"> | **Plane**<br><sub>`plane`</sub><br><sub>plane, aircraft, airplane, vehicle</sub> | Geometry<br><sub>CC-BY-3.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/plane/plane_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/plane/plane_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/plane/plane_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/plane/plane_1m.splat)<br><sub>[meta](data/plane/meta.json)</sub> |
| <img src="data/scorpion/thumb.png" width="220"> | **Scorpion**<br><sub>`scorpion`</sub><br><sub>scorpion, animal, arachnid, detailed</sub> | Geometry<br><sub>CC-BY-3.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/scorpion/scorpion_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/scorpion/scorpion_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/scorpion/scorpion_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/scorpion/scorpion_1m.splat)<br><sub>[meta](data/scorpion/meta.json)</sub> |
| <img src="data/skull/thumb.png" width="220"> | **Skull**<br><sub>`skull`</sub><br><sub>skull, anatomy, bone, head</sub> | Geometry<br><sub>CC-BY-3.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/skull/skull_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/skull/skull_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/skull/skull_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/skull/skull_1m.splat)<br><sub>[meta](data/skull/meta.json)</sub> |
| <img src="data/sword/thumb.png" width="220"> | **Sword**<br><sub>`sword`</sub><br><sub>sword, weapon, blade, historical</sub> | Geometry<br><sub>CC-BY-4.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/sword/sword_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/sword/sword_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/sword/sword_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/sword/sword_1m.splat)<br><sub>[meta](data/sword/meta.json)</sub> |
| <img src="data/tree/thumb.png" width="220"> | **Tree**<br><sub>`tree`</sub><br><sub>tree, plant, nature, branches</sub> | Geometry<br><sub>CC-BY-4.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/tree/tree_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/tree/tree_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/tree/tree_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/tree/tree_1m.splat)<br><sub>[meta](data/tree/meta.json)</sub> |
| <img src="data/wingnut/thumb.png" width="220"> | **Wing nut**<br><sub>`wingnut`</sub><br><sub>wingnut, hardware, cad, nut</sub> | Geometry<br><sub>CC-BY-4.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/wingnut/wingnut_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/wingnut/wingnut_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/wingnut/wingnut_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/wingnut/wingnut_1m.splat)<br><sub>[meta](data/wingnut/meta.json)</sub> |
| <img src="data/fish/thumb.png" width="220"> | **Fish**<br><sub>`fish`</sub><br><sub>fish, animal, sea</sub> | Geometry<br><sub>Public Domain</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/fish/fish_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/fish/fish_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/fish/fish_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/fish/fish_1m.splat)<br><sub>[meta](data/fish/meta.json)</sub> |
| <img src="data/violin/thumb.png" width="220"> | **Violin**<br><sub>`violin`</sub><br><sub>violin, instrument, music, scan</sub> | Geometry<br><sub>CC0-1.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/violin/violin_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/violin/violin_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/violin/violin_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/violin/violin_1m.splat)<br><sub>[meta](data/violin/meta.json)</sub> |
| <img src="data/brucewick/thumb.png" width="220"> | **Brucewick**<br><sub>`brucewick`</sub><br><sub>bust, head, portrait, character</sub> | Geometry<br><sub>CC-BY-NC-4.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/brucewick/brucewick_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/brucewick/brucewick_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/brucewick/brucewick_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/brucewick/brucewick_1m.splat)<br><sub>[meta](data/brucewick/meta.json)</sub> |
| <img src="data/cow/thumb.png" width="220"> | **Cow**<br><sub>`cow`</sub><br><sub>cow, animal, farm, cattle</sub> | Geometry<br><sub>CC-BY-NC-4.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/cow/cow_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/cow/cow_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/cow/cow_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/cow/cow_1m.splat)<br><sub>[meta](data/cow/meta.json)</sub> |
| <img src="data/falconstatue/thumb.png" width="220"> | **Falcon statue**<br><sub>`falconstatue`</sub><br><sub>falcon, bird, statue, sculpture</sub> | Geometry<br><sub>CC-BY-NC-SA-4.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/falconstatue/falconstatue_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/falconstatue/falconstatue_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/falconstatue/falconstatue_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/falconstatue/falconstatue_1m.splat)<br><sub>[meta](data/falconstatue/meta.json)</sub> |
| <img src="data/house/thumb.png" width="220"> | **House**<br><sub>`house`</sub><br><sub>house, building, architecture, cottage</sub> | Geometry<br><sub>CC-BY-NC-4.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/house/house_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/house/house_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/house/house_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/house/house_1m.splat)<br><sub>[meta](data/house/meta.json)</sub> |
| <img src="data/mushroom/thumb.png" width="220"> | **Mushroom**<br><sub>`mushroom`</sub><br><sub>mushroom, fungus, nature, plant</sub> | Geometry<br><sub>CC-BY-NC-4.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/mushroom/mushroom_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/mushroom/mushroom_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/mushroom/mushroom_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/mushroom/mushroom_1m.splat)<br><sub>[meta](data/mushroom/meta.json)</sub> |
| <img src="data/strawberry/thumb.png" width="220"> | **Strawberry**<br><sub>`strawberry`</sub><br><sub>strawberry, fruit, food</sub> | Geometry<br><sub>CC-BY-NC-4.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/strawberry/strawberry_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/strawberry/strawberry_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/strawberry/strawberry_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/strawberry/strawberry_1m.splat)<br><sub>[meta](data/strawberry/meta.json)</sub> |
| <img src="data/tower/thumb.png" width="220"> | **Tower**<br><sub>`tower`</sub><br><sub>tower, building, architecture, lighthouse</sub> | Geometry<br><sub>CC-BY-NC-3.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/tower/tower_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/tower/tower_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/tower/tower_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/tower/tower_1m.splat)<br><sub>[meta](data/tower/meta.json)</sub> |
| <img src="data/well/thumb.png" width="220"> | **Well**<br><sub>`well`</sub><br><sub>well, building, architecture, medieval</sub> | Geometry<br><sub>CC-BY-NC-4.0</sub> | Object | ~10k · 320 kB<br>~100k · 3.2 MB<br>~500k · 16.0 MB<br>~1M · 32.0 MB | [10k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/well/well_10k.splat) · [100k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/well/well_100k.splat) · [500k](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/well/well_500k.splat) · [1m](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/well/well_1m.splat)<br><sub>[meta](data/well/meta.json)</sub> |
| <img src="data/eiffel_generated/thumb.png" width="220"> | **Eiffel Tower (generated)**<br><sub>`eiffel_generated`</sub><br><sub>eiffel-tower, tower, landmark, architecture, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/eiffel_generated/eiffel_generated.splat) · [meta](data/eiffel_generated/meta.json) |
| <img src="data/big_ben_generated/thumb.png" width="220"> | **Big Ben (generated)**<br><sub>`big_ben_generated`</sub><br><sub>big-ben, elizabeth-tower, london, clock-tower, landmark, architecture, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/big_ben_generated/big_ben_generated.splat) · [meta](data/big_ben_generated/meta.json) |
| <img src="data/taipei_101_generated/thumb.png" width="220"> | **Taipei 101 (generated)**<br><sub>`taipei_101_generated`</sub><br><sub>taipei-101, taipei, skyscraper, tower, landmark, architecture, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/taipei_101_generated/taipei_101_generated.splat) · [meta](data/taipei_101_generated/meta.json) |
| <img src="data/pisa_tower_generated/thumb.png" width="220"> | **Leaning Tower of Pisa (generated)**<br><sub>`pisa_tower_generated`</sub><br><sub>leaning-tower-of-pisa, pisa, tower, campanile, landmark, architecture, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/pisa_tower_generated/pisa_tower_generated.splat) · [meta](data/pisa_tower_generated/meta.json) |
| <img src="data/tortoise_generated/thumb.png" width="220"> | **Galapagos tortoise (generated)**<br><sub>`tortoise_generated`</sub><br><sub>tortoise, animal, reptile, nature, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/tortoise_generated/tortoise_generated.splat) · [meta](data/tortoise_generated/meta.json) |
| <img src="data/cactus_generated/thumb.png" width="220"> | **Cactus (generated)**<br><sub>`cactus_generated`</sub><br><sub>cactus, plant, succulent, nature, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/cactus_generated/cactus_generated.splat) · [meta](data/cactus_generated/meta.json) |
| <img src="data/toy_accordion_generated/thumb.png" width="220"> | **Toy accordion (generated)**<br><sub>`toy_accordion_generated`</sub><br><sub>accordion, instrument, toy, music, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/toy_accordion_generated/toy_accordion_generated.splat) · [meta](data/toy_accordion_generated/meta.json) |
| <img src="data/typewriter_generated/thumb.png" width="220"> | **Manual typewriter (generated)**<br><sub>`typewriter_generated`</sub><br><sub>typewriter, machine, vintage, office, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/typewriter_generated/typewriter_generated.splat) · [meta](data/typewriter_generated/meta.json) |
| <img src="data/tractor_generated/thumb.png" width="220"> | **Fordson tractor (generated)**<br><sub>`tractor_generated`</sub><br><sub>tractor, vehicle, farm, machine, vintage, fordson, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/tractor_generated/tractor_generated.splat) · [meta](data/tractor_generated/meta.json) |
| <img src="data/ford_model_t_generated/thumb.png" width="220"> | **Ford Model T (generated)**<br><sub>`ford_model_t_generated`</sub><br><sub>car, automobile, vintage, vehicle, ford, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/ford_model_t_generated/ford_model_t_generated.splat) · [meta](data/ford_model_t_generated/meta.json) |
| <img src="data/bentwood_chair_generated/thumb.png" width="220"> | **Bentwood chair (generated)**<br><sub>`bentwood_chair_generated`</sub><br><sub>chair, furniture, bentwood, vintage, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/bentwood_chair_generated/bentwood_chair_generated.splat) · [meta](data/bentwood_chair_generated/meta.json) |
| <img src="data/log_cabin_generated/thumb.png" width="220"> | **Log cabin (generated)**<br><sub>`log_cabin_generated`</sub><br><sub>cabin, house, building, wood, vernacular, architecture, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/log_cabin_generated/log_cabin_generated.splat) · [meta](data/log_cabin_generated/meta.json) |
| <img src="data/teacup_generated/thumb.png" width="220"> | **Teacup (generated)**<br><sub>`teacup_generated`</sub><br><sub>cup, teacup, ceramic, tableware, kitchen, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/teacup_generated/teacup_generated.splat) · [meta](data/teacup_generated/meta.json) |
| <img src="data/vintage_motorcycle_generated/thumb.png" width="220"> | **Vintage motorcycle (generated)**<br><sub>`vintage_motorcycle_generated`</sub><br><sub>motorcycle, vehicle, vintage, machine, bmw, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/vintage_motorcycle_generated/vintage_motorcycle_generated.splat) · [meta](data/vintage_motorcycle_generated/meta.json) |
| <img src="data/tiffany_lamp_generated/thumb.png" width="220"> | **Tiffany table lamp (generated)**<br><sub>`tiffany_lamp_generated`</sub><br><sub>lamp, lampshade, tiffany, glass, lighting, furniture, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/tiffany_lamp_generated/tiffany_lamp_generated.splat) · [meta](data/tiffany_lamp_generated/meta.json) |
| <img src="data/dolls_bed_generated/thumb.png" width="220"> | **Doll's bed (generated)**<br><sub>`dolls_bed_generated`</sub><br><sub>bed, furniture, toy, dolls-house, miniature, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/dolls_bed_generated/dolls_bed_generated.splat) · [meta](data/dolls_bed_generated/meta.json) |
| <img src="data/kilim_rug_generated/thumb.png" width="220"> | **Kilim rug (generated)**<br><sub>`kilim_rug_generated`</sub><br><sub>rug, carpet, kilim, textile, weaving, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~261k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/kilim_rug_generated/kilim_rug_generated.splat) · [meta](data/kilim_rug_generated/meta.json) |
| <img src="data/cat_generated/thumb.png" width="220"> | **Cat (generated)**<br><sub>`cat_generated`</sub><br><sub>cat, animal, pet, mammal, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/cat_generated/cat_generated.splat) · [meta](data/cat_generated/meta.json) |
| <img src="data/dog_generated/thumb.png" width="220"> | **Dog (generated)**<br><sub>`dog_generated`</sub><br><sub>dog, animal, pet, mammal, ridgeback, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/dog_generated/dog_generated.splat) · [meta](data/dog_generated/meta.json) |
| <img src="data/bonsai_generated/thumb.png" width="220"> | **Bonsai tree (generated)**<br><sub>`bonsai_generated`</sub><br><sub>tree, bonsai, plant, nature, pot, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/bonsai_generated/bonsai_generated.splat) · [meta](data/bonsai_generated/meta.json) |
| <img src="data/morpho_butterfly_generated/thumb.png" width="220"> | **Blue morpho butterfly (generated)**<br><sub>`morpho_butterfly_generated`</sub><br><sub>butterfly, morpho, insect, animal, nature, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/morpho_butterfly_generated/morpho_butterfly_generated.splat) · [meta](data/morpho_butterfly_generated/meta.json) |
| <img src="data/blackbird_generated/thumb.png" width="220"> | **Blackbird (generated)**<br><sub>`blackbird_generated`</sub><br><sub>blackbird, bird, animal, turdus-merula, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/blackbird_generated/blackbird_generated.splat) · [meta](data/blackbird_generated/meta.json) |
| <img src="data/goldfinch_generated/thumb.png" width="220"> | **Goldfinch (generated)**<br><sub>`goldfinch_generated`</sub><br><sub>goldfinch, bird, animal, nature, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/goldfinch_generated/goldfinch_generated.splat) · [meta](data/goldfinch_generated/meta.json) |
| <img src="data/kiwi_generated/thumb.png" width="220"> | **Kiwi (generated)**<br><sub>`kiwi_generated`</sub><br><sub>kiwi, bird, animal, nature, new-zealand, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/kiwi_generated/kiwi_generated.splat) · [meta](data/kiwi_generated/meta.json) |
| <img src="data/horse_generated/thumb.png" width="220"> | **Horse (generated)**<br><sub>`horse_generated`</sub><br><sub>horse, animal, mammal, nature, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/horse_generated/horse_generated.splat) · [meta](data/horse_generated/meta.json) |
| <img src="data/elephant_generated/thumb.png" width="220"> | **Elephant (generated)**<br><sub>`elephant_generated`</sub><br><sub>elephant, animal, mammal, nature, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/elephant_generated/elephant_generated.splat) · [meta](data/elephant_generated/meta.json) |
| <img src="data/snail_generated/thumb.png" width="220"> | **Snail (generated)**<br><sub>`snail_generated`</sub><br><sub>snail, shell, animal, mollusc, nature, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/snail_generated/snail_generated.splat) · [meta](data/snail_generated/meta.json) |
| <img src="data/fly_agaric_generated/thumb.png" width="220"> | **Fly agaric mushroom (generated)**<br><sub>`fly_agaric_generated`</sub><br><sub>mushroom, fungus, fly-agaric, amanita, nature, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/fly_agaric_generated/fly_agaric_generated.splat) · [meta](data/fly_agaric_generated/meta.json) |
| <img src="data/pineapple_generated/thumb.png" width="220"> | **Pineapple (generated)**<br><sub>`pineapple_generated`</sub><br><sub>pineapple, fruit, food, plant, nature, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/pineapple_generated/pineapple_generated.splat) · [meta](data/pineapple_generated/meta.json) |
| <img src="data/wedgwood_teapot_generated/thumb.png" width="220"> | **Jasperware teapot (generated)**<br><sub>`wedgwood_teapot_generated`</sub><br><sub>teapot, ceramic, wedgwood, jasperware, tableware, kitchen, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/wedgwood_teapot_generated/wedgwood_teapot_generated.splat) · [meta](data/wedgwood_teapot_generated/meta.json) |
| <img src="data/folding_camera_generated/thumb.png" width="220"> | **Folding camera (generated)**<br><sub>`folding_camera_generated`</sub><br><sub>camera, photography, vintage, folding-camera, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/folding_camera_generated/folding_camera_generated.splat) · [meta](data/folding_camera_generated/meta.json) |
| <img src="data/sewing_machine_generated/thumb.png" width="220"> | **Sewing machine (generated)**<br><sub>`sewing_machine_generated`</sub><br><sub>sewing-machine, singer, machine, vintage, tool, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/sewing_machine_generated/sewing_machine_generated.splat) · [meta](data/sewing_machine_generated/meta.json) |
| <img src="data/gramophone_generated/thumb.png" width="220"> | **Gramophone (generated)**<br><sub>`gramophone_generated`</sub><br><sub>gramophone, phonograph, music, vintage, machine, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/gramophone_generated/gramophone_generated.splat) · [meta](data/gramophone_generated/meta.json) |
| <img src="data/brass_horn_generated/thumb.png" width="220"> | **Double-belled euphonium (generated)**<br><sub>`brass_horn_generated`</sub><br><sub>euphonium, horn, brass, instrument, music, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/brass_horn_generated/brass_horn_generated.splat) · [meta](data/brass_horn_generated/meta.json) |
| <img src="data/watering_can_generated/thumb.png" width="220"> | **Watering can (generated)**<br><sub>`watering_can_generated`</sub><br><sub>watering-can, garden, metal, tool, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/watering_can_generated/watering_can_generated.splat) · [meta](data/watering_can_generated/meta.json) |
| <img src="data/smartphone_generated/thumb.png" width="220"> | **Smartphone (generated)**<br><sub>`smartphone_generated`</sub><br><sub>smartphone, phone, mobile, electronics, device, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/smartphone_generated/smartphone_generated.splat) · [meta](data/smartphone_generated/meta.json) |
| <img src="data/fire_hydrant_generated/thumb.png" width="220"> | **Fire hydrant (generated)**<br><sub>`fire_hydrant_generated`</sub><br><sub>hydrant, fire-hydrant, street-furniture, cast-iron, utility, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/fire_hydrant_generated/fire_hydrant_generated.splat) · [meta](data/fire_hydrant_generated/meta.json) |
| <img src="data/hand_bell_generated/thumb.png" width="220"> | **Ritual hand bell (generated)**<br><sub>`hand_bell_generated`</sub><br><sub>bell, hand-bell, dril-bu, bronze, ritual, instrument, generated, ai, single-image</sub> | Generated<br><sub>As-is (no warranty)</sub> | Object | ~262k · 8.4 MB | [.splat](https://raw.githubusercontent.com/marcelpadilla/splats/main/data/hand_bell_generated/hand_bell_generated.splat) · [meta](data/hand_bell_generated/meta.json) |

<sub>86 objects · ~32M gaussians at the default level · 41 of them at four levels of detail · 2479.5 MB for every file · licenses per object (see Source)</sub>
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

The data license depends on how each object was made (shown under its **Source**
in the table above, and in each object's `meta.json`):

- **Scanned objects are [CC-BY-4.0](LICENSE).** Use them for anything, including
  commercially. You must credit the author.
- **Geometry and rendered objects inherit the license of the mesh they came
  from.** Converting a mesh to splats does not launder its license. Most are CC0
  or public domain and ask for nothing (Spot and Bob by Keenan Crane, the Utah
  teapot, the primitives). The rendered bunny is CC-BY-3.0 (Stanford Bunny STL by
  Makerbot, via Wikimedia Commons); credit that author as well.
- **The Stanford subset is free to use but is not Creative Commons.**
  `stanford_bunny`, `armadillo`, `dragon`, `happy`, `lucy` and `xyzrgb_dragon`
  come from the [Stanford 3D Scanning
  Repository](http://graphics.stanford.edu/data/3Dscanrep/), which permits use
  including in derivative and commercial work, but asks that you acknowledge the
  source and do not misrepresent the data. Credit *Stanford University Computer
  Graphics Laboratory* (and *XYZ RGB Inc.* for `xyzrgb_dragon`).
- **Generated objects are provided as-is, with no warranty of rights.** They were
  invented by an AI image-to-3D model whose training data is undisclosed, so their
  copyright status cannot be warranted and they are **not under CC-BY**. You are
  responsible for clearing any rights for your use.

`ps.find(open_license=True)` keeps only what has no condition attached: the
CC-licensed and public-domain objects, dropping the Stanford subset and the
generated ones.

- **The code in `python/` is [0BSD](python/LICENSE).** No attribution required.

Credit line you can paste for a CC-BY object:

> Gaussian splat by Marcel Padilla, from https://github.com/marcelpadilla/splats, licensed CC-BY-4.0.

The license covers the capture, render or generation and the reconstruction, not
the industrial design of any object depicted.

## Layout

```
data/
  inventory.json          the machine-readable index, and the source of truth
  <id>/
    <id>.splat            the gaussians (a single-file object)
    <id>_<lod>.splat      or one file per level of detail (10k/100k/500k/1m)
    meta.json             provenance, pipeline, quality, caveats, every tier
    thumb.jpg             the gallery image above
python/                   the padillasplats package
LICENSE                   CC-BY-4.0, the license of the scanned objects
```

## Adding an object

1. Put `data/<id>/<id>.splat` (or one file per tier), its `meta.json` and a
   `thumb.jpg` in place.
2. Add an entry to `data/inventory.json`, including its SHA-256, `category`,
   `source_method` and `license`. A multi-resolution object also lists every
   tier under `lods` and names one in `default_lod`; the top-level
   `file`/`splats`/`bytes`/`sha256` must be that tier's, not a fifth file.
3. Run `python python/sync_inventory.py`, which refreshes the copy bundled in
   the package and regenerates the gallery and citation blocks above.
4. Run `python -m pytest python/tests` to confirm the checksums and counts agree,
   for every tier.

The website reads `data/inventory.json` straight from this repository, and
existing package installs pick up new objects with `ps.refresh_inventory()`, so
neither needs a separate update.
