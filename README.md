<div align="center">
  <img src="https://raw.githubusercontent.com/eddiethedean/heatfall/main/docs/heatfall_logo.png" alt="Heatfall logo" width="76">
  <h1>Heatfall</h1>
  <p><strong>Turn latitude and longitude observations into count maps.</strong></p>
  <p>Geohash rectangles or H3 cells · Discrete count legends · Pillow and SVG output</p>
  <p><a href="#quick-start">Quick start</a> · <a href="#choose-a-grid">Choose a grid</a> · <a href="#colors-and-legends">Colors and legends</a> · <a href="https://heatfall.readthedocs.io/en/latest/">Full documentation</a></p>
</div>

<p align="center">
  <a href="https://pypi.org/project/heatfall/"><img src="https://img.shields.io/pypi/v/heatfall.svg" alt="PyPI version"></a>
  <a href="https://github.com/eddiethedean/heatfall/actions/workflows/tests.yml"><img src="https://github.com/eddiethedean/heatfall/actions/workflows/tests.yml/badge.svg" alt="Test status"></a>
  <a href="https://heatfall.readthedocs.io/en/latest/index.html"><img src="https://app.readthedocs.org/projects/heatfall/badge/?version=latest" alt="Documentation status"></a>
  <a href="https://github.com/eddiethedean/heatfall/blob/main/pyproject.toml"><img src="https://img.shields.io/badge/python-3.8%E2%80%933.13-blue" alt="Python 3.8 to 3.13"></a>
  <a href="https://github.com/eddiethedean/heatfall/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="MIT license"></a>
</p>

Heatfall groups geographic observations into geohash or H3 cells, counts the
observations in each occupied cell, and draws the cells over a basemap. Use it
for a single heat layer or combine heat with points and routes through
[Landfall](https://landfall.readthedocs.io/en/latest/).

![H3 heatmap of synthetic observations across downtown Tampa, rendered by Heatfall](https://raw.githubusercontent.com/eddiethedean/heatfall/main/docs/images/first-map.png)

*Four synthetic observations, three occupied cells. The map uses the default
heatmap palette and count legend.*

## Install

Python **3.8–3.13** is supported.

```sh
python -m pip install heatfall
```

Heatfall **1.3.0** adds repeatable palette seeds, tile API keys, and optional
GIS/Cairo installation extras. The
[installation guide](https://heatfall.readthedocs.io/en/latest/installation.html)
covers these extras and source installation.

The default OpenStreetMap basemap downloads map tiles when they are not cached.
It needs network access and no API key. To render without tile requests, use
`staticmaps.tile_provider_None`; the [basemap guide](https://heatfall.readthedocs.io/en/latest/basemaps.html#render-without-a-basemap)
shows how.

## Quick start

Pass matching latitude and longitude lists in decimal degrees. Latitude comes
first; repeated rows count as repeated observations.

```python
import heatfall

lats = [27.9470, 27.9470, 27.9515, 27.9430]
lons = [-82.4580, -82.4580, -82.4500, -82.4475]

image = heatfall.plot_heat_h3s(lats, lons, precision=8)
image.save("heatmap.png")
```

Both plotting functions return a Pillow image. The default map uses a five-step
blue-to-red heatmap palette and a discrete legend. See the
[installation guide](https://heatfall.readthedocs.io/en/latest/installation.html)
for the first-map walkthrough, or the [point-data guide](https://heatfall.readthedocs.io/en/latest/data.html)
to load a CSV.

## Choose a grid

| | Geohash | H3 |
| --- | --- | --- |
| Function | `plot_heat_hashes()` | `plot_heat_h3s()` |
| Cell shape | Latitude/longitude rectangles | Mostly hexagons; pentagons also occur |
| Precision | 1–12 | 0–15 (H3 calls this resolution) |
| City-scale starting point | 6 | 8 |

Higher precision means smaller cells. The precision scales differ between grids;
geohash precision 8 and H3 resolution 8 do not imply equal cell sizes. The
[usage guide](https://heatfall.readthedocs.io/en/latest/usage.html#choose-a-grid)
compares both outputs.

## Colors and legends

`color_scheme="heatmap"` is the default. It maps low-to-high counts to up to
five ordered color steps. Its legend labels each step with an inclusive count
range; a cell still contains its raw count. The `"sequential"` palette uses a
light-to-dark blue ramp and shows one entry per observed count. `"distinct"`,
`"wheel"`, and `"random"` distinguish count levels without implying an order.

Legends are on by default, with a translucent panel. Hide one with
`legend=False`, or pass `heatfall.LegendOptions` to adjust its position, labels,
columns, colors, and typography. The [legend guide](https://heatfall.readthedocs.io/en/latest/usage.html#legends)
includes a placement gallery.

Use fixed colors when maps need to be compared by count. Supply a color for
every observed count in each map; a shared mapping can include extra counts:

```python
count_colors = {1: "#deebf7", 2: "#9ecae1", 3: "#4292c6"}
image = heatfall.plot_heat_h3s(lats, lons, precision=8, count_colors=count_colors)
```

Heatfall 1.2.0 changed the default palette from `"distinct"` to `"heatmap"` and
added a legend by default. To keep the 1.1.0 appearance, set both
`color_scheme="distinct"` and `legend=False`. See the
[release notes](https://github.com/eddiethedean/heatfall/releases/tag/v1.2.0)
for upgrade details.

## Compose other layers

Use `heatfall.Context` to add a heat layer and ordinary map shapes. Heat cells
are added first so points, routes, and circles draw above them:

```python
context = heatfall.Context()
context.add_heat_h3s(lats, lons, precision=8)
context.add_points([27.9470], [-82.4580], colors=["black"], point_size=10)
context.render_pillow(800, 500).save("layered-map.png")
```

Heatfall is built on [Landfall](https://landfall.readthedocs.io/en/latest/) for
map composition. The [basemaps and output guide](https://heatfall.readthedocs.io/en/latest/basemaps.html)
covers fixed views, offline rendering, SVG, tile providers, and attribution.

Landfall's GeoJSON, Shapely, and GeoDataFrame plotting functions also accept
`context=context` to combine GIS shapes with heat cells and keep the heat
legend. See the [GIS overlay examples](https://heatfall.readthedocs.io/en/latest/usage.html#geojson-overlays)
and [optional GIS installation](https://heatfall.readthedocs.io/en/latest/installation.html#optional-gis-dependencies).

The context also exposes the native py-staticmaps controls through Landfall.
See its [full py-staticmaps guide](https://landfall.readthedocs.io/en/latest/py-staticmaps/)
for framing, bounds padding, tile services, and optional Cairo output.

## Learn and contribute

- [Usage and styling](https://heatfall.readthedocs.io/en/latest/usage.html)
- [Geographic considerations](https://heatfall.readthedocs.io/en/latest/geography.html)
- [API reference](https://heatfall.readthedocs.io/en/latest/api.html)
- [Troubleshooting](https://heatfall.readthedocs.io/en/latest/troubleshooting.html)
- [Architecture](https://heatfall.readthedocs.io/en/latest/architecture.html)
- [Performance guidance](https://heatfall.readthedocs.io/en/latest/performance.html)
- [Contributing](https://github.com/eddiethedean/heatfall/blob/main/CONTRIBUTING.md)
- [Support](https://github.com/eddiethedean/heatfall/blob/main/SUPPORT.md)
- [Security policy](https://github.com/eddiethedean/heatfall/blob/main/SECURITY.md)

Heatfall is released under the [MIT license](https://github.com/eddiethedean/heatfall/blob/main/LICENSE). Report bugs and request
features in [GitHub Issues](https://github.com/eddiethedean/heatfall/issues).
