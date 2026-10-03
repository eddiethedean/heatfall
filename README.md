<img src="https://raw.githubusercontent.com/eddiethedean/heatfall/main/docs/heatfall_logo.png" alt="Heatfall logo: a hexagonal flame in ember, orange, and amber" width="100" align="right">

# Heatfall

**Turn latitude and longitude lists into static maps colored by point count.**

[![PyPI](https://img.shields.io/pypi/v/heatfall.svg)](https://pypi.org/project/heatfall/)
[![Tests](https://github.com/eddiethedean/heatfall/actions/workflows/tests.yml/badge.svg)](https://github.com/eddiethedean/heatfall/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/python-3.8%E2%80%933.13-blue)](https://github.com/eddiethedean/heatfall/blob/main/pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](https://github.com/eddiethedean/heatfall/blob/main/LICENSE)

Heatfall groups geographic observations into geohash rectangles or H3 cells,
counts the points in each cell, and draws the occupied cells over a basemap.
Save the result as a Pillow image, or combine a heat layer with points, routes,
and service areas through [Landfall](https://landfall.readthedocs.io/en/latest/).

![H3 cells over downtown Tampa, rendered by Heatfall](https://raw.githubusercontent.com/eddiethedean/heatfall/main/docs/images/h3.png)

*Synthetic observations around downtown Tampa. Each occupied cell is colored by
its point count; the map tiles and attribution come from OpenStreetMap.*

[Install](#install) · [Quick start](#quick-start) · [Choose a grid](#choose-a-grid)
· [Add other layers](#add-other-layers) · [API](#api) · [Troubleshooting](#troubleshooting)
· [Documentation source](https://github.com/eddiethedean/heatfall/blob/main/docs/index.md)

## Install

Python **3.8–3.13** is supported. Install the latest published release with:

```sh
python -m pip install heatfall
```

To install the latest code from `main`, including fixes that may not yet be on PyPI:

```sh
python -m pip install "git+https://github.com/eddiethedean/heatfall.git@main"
```

The examples below require **1.1.0 or newer** for opacity controls and H3 fixes.
Check your version with `python -m pip show heatfall`. See the
[changelog](https://github.com/eddiethedean/heatfall/blob/main/CHANGELOG.md) for
release details.

The default OpenStreetMap basemap needs network access when tiles are not cached.
No API key is required for that default provider.

## Quick start

Create an H3 map from 15 synthetic observations. Repeated coordinates deliberately
produce cells with different counts.

```python
import heatfall

lats = [27.9470] * 8 + [27.9515] * 4 + [27.9430] * 2 + [27.9475]
lons = [-82.4580] * 8 + [-82.4500] * 4 + [-82.4475] * 2 + [-82.4400]

image = heatfall.plot_heat_h3s(
    lats,
    lons,
    precision=8,
    color_scheme="wheel",
    size=(800, 500),
)
image.save("h3-heatmap.png")
```

Both plotting functions return a `PIL.Image.Image`. Heatfall fits the map to the
added cells automatically. `size` is the output width and height in pixels.

For dataframe columns, pass lists such as `df["latitude"].tolist()` and
`df["longitude"].tolist()`.

## Choose a grid

| | Geohash | H3 |
| --- | --- | --- |
| Function | `plot_heat_hashes()` | `plot_heat_h3s()` |
| Cell shape | Latitude/longitude rectangles | Mostly hexagons, with pentagons in the global grid |
| `precision` range | 1–12 | 0–15; H3 calls this resolution |
| Choose it when | Your data or downstream tools already use geohashes | You want hexagonal aggregation or already use H3 |
| City-scale starting point | Try `precision=6` | Try `precision=8` |

Higher precision means smaller cells. If most occupied cells contain only one
point, reduce precision to aggregate more observations. Start with a coarser grid
for data spread over a large region. The two precision scales are independent:
geohash precision 8 and H3 resolution 8 do not imply the same cell size.

| Geohash, precision 6 | H3, resolution 8 |
| --- | --- |
| ![Geohash rectangles over downtown Tampa](https://raw.githubusercontent.com/eddiethedean/heatfall/main/docs/images/geohash.png) | ![H3 cells over downtown Tampa](https://raw.githubusercontent.com/eddiethedean/heatfall/main/docs/images/h3.png) |

*The same observations, aggregated into different grids. Each map fits its own
cell boundaries, so the basemap extent can differ.*

Create the same map using geohash cells:

```python
import heatfall

lats = [27.9470] * 8 + [27.9515] * 4 + [27.9430] * 2 + [27.9475]
lons = [-82.4580] * 8 + [-82.4500] * 4 + [-82.4475] * 2 + [-82.4400]

image = heatfall.plot_heat_hashes(
    lats, lons, precision=6, color_scheme="wheel", size=(800, 500)
)
image.save("geohash-heatmap.png")
```

## Understand the colors

Each observation contributes **one count** to its cell. Only occupied cells are
drawn. Within a heat layer, cells with the same count share a color; different
count levels receive different palette colors.

Heat fills default to **60% opacity (40% transparent)**, keeping streets and
labels visible beneath the cells. Set `opacity` on either plotting function or
heat layer method to control the fill: `0.4` is lighter, `1.0` is solid, and `0.0`
is invisible. Opacity applies uniformly to the layer; counts still determine
the palette colors.

| `color_scheme` | Behavior |
| --- | --- |
| `"distinct"` — default | Generates visually distinct colors for the count levels |
| `"wheel"` | Selects colors from an HSV color wheel |
| `"random"` | Generates random colors for the count levels |

These palettes distinguish count levels; they do **not** guarantee a sequential
light-to-dark or cool-to-hot scale. A red cell does not inherently mean a higher
count. Colors are assigned separately for each layer, and `"distinct"` and
`"random"` may change between calls. Avoid comparing counts across separate maps
by color alone.

The result shows raw counts per cell, not counts normalized by cell area. It does
not apply smoothing, accept observation weights, or add a numeric legend.

## Add other layers

`heatfall.Context` extends `landfall.Context`, so heat cells can share a map with
ordinary geographic objects. Add the heat layer first, then add the overlays.

Landfall's [Context API](https://landfall.readthedocs.io/en/latest/api/#context)
documents the inherited methods; its
[shapes and styling guide](https://landfall.readthedocs.io/en/latest/shapes-and-styling/)
explains point sizes, line widths, circle radii, and overlay colors.

```python
import heatfall

lats = [27.9470] * 8 + [27.9515] * 4 + [27.9430] * 2 + [27.9475]
lons = [-82.4580] * 8 + [-82.4500] * 4 + [-82.4475] * 2 + [-82.4400]

context = heatfall.Context()
context.add_heat_h3s(lats, lons, precision=8, color_scheme="wheel")

# A reference location.
context.add_points([27.9470], [-82.4580], colors=["black"], point_size=10)

# A route in (latitude, longitude) order.
context.add_line(
    [(27.9430, -82.4475), (27.9475, -82.4400)], color="black", width=3
)

# One circle per center, with radii in meters.
context.add_circles(
    [27.9515], [-82.4500], [300],
    color="blue", fill_color="transparent", width=2,
)

context.render_pillow(800, 500).save("layered-heatmap.png")
```

![A Heatfall H3 layer with a point, route, and circle](https://raw.githubusercontent.com/eddiethedean/heatfall/main/docs/images/layers.png)

Landfall also supplies polygons, GeoJSON support, styling, and SVG rendering.
See its [documentation](https://github.com/eddiethedean/landfall#readme) for the
inherited methods. For Heatfall's own layer methods, see the API below.

## API

The public package exports two plotting functions and `Context`:

| Entry point | Result |
| --- | --- |
| `heatfall.plot_heat_hashes()` | A Pillow image containing a geohash heat layer |
| `heatfall.plot_heat_h3s()` | A Pillow image containing an H3 heat layer |
| `heatfall.Context()` | A map context for composing layers |

Both plotting functions accept the same arguments:

| Argument | Default | Meaning |
| --- | --- | --- |
| `lats` | Required | List of latitudes in decimal degrees, from −90 to 90 |
| `lons` | Required | Matching list of longitudes in decimal degrees, from −180 to 180 |
| `precision` | Required | Geohash length 1–12, or H3 resolution 0–15 |
| `color_scheme` | `"distinct"` | `"distinct"`, `"random"`, or `"wheel"` |
| `tileprovider` | OpenStreetMap | A `staticmaps.TileProvider` for the basemap |
| `size` | `(800, 500)` | Output `(width, height)` in pixels |
| `opacity` | `0.6` | Keyword-only fill opacity from `0.0` to `1.0` |

The heat layer methods mutate the context and return `None`:

```python
context.add_heat_hashes(lats, lons, precision, color_scheme="distinct", opacity=0.6)
context.add_heat_h3s(lats, lons, precision, color_scheme="distinct", opacity=0.6)
```

The default provider is `staticmaps.tile_provider_OSM`.
Configure a context's basemap with `context.set_tile_provider(provider)` and
render it with `context.render_pillow(width, height)`. The standalone plotting
keyword is spelled **`tileprovider`**, without an underscore.
See Landfall's [custom tile service guide](https://landfall.readthedocs.io/en/latest/custom-tile-service/)
for basemap configuration and its
[SVG example](https://landfall.readthedocs.io/en/latest/shapes-and-styling/#combine-shapes-and-export-svg)
for exporting a composed map.

### Input rules

- Supply parallel coordinate lists in **latitude, longitude** order, using
  decimal degrees. GeoJSON positions commonly use the reverse order.
- Lists must have matching lengths. Out-of-range coordinates and non-finite
  values such as `NaN` and infinity raise `ValueError`.
- Use an integer precision in the supported range and one of the named palettes.
- Opacity must be finite and between `0.0` and `1.0`, inclusive.
- Standalone plotting functions reject empty lists. Adding an empty heat layer
  to a `Context` is a no-op; add some content before rendering.
- Repeated coordinates count as repeated observations. Deduplicate your input
  first if your analysis should count unique locations instead.

### Crossing the antimeridian

H3 maps can contain points on both sides of ±180° longitude:

```python
import heatfall

image = heatfall.plot_heat_h3s(
    lats=[10.0, 10.0, 10.0],
    lons=[179.5, -179.5, 179.5],
    precision=3,
)
image.save("antimeridian.png")
```

Heatfall splits crossing H3 cell boundaries into closed polygons at the
antimeridian, with intersections calculated along spherical edges. Both pieces
keep the original cell's observation count and color, and the automatic map
extent follows the short span across the seam. Exact `180` and `-180` longitude
are accepted. These fixes require Heatfall 1.1.0 or newer.

This handling applies to rendered H3 cells. Polygon-to-cell filling of external
GeoJSON is outside Heatfall's point API. For polar cells, H3 rendering is clipped
to the Web Mercator tile latitude limit of approximately ±85.0511°; these maps
do not display the poles.

## Documentation

The documentation includes a visual example gallery, a heat-colored light/dark
theme, searchable guides, and an API reference generated from the package.
Browse the source guides below, or [build the site locally](#build-the-documentation).

| Guide | What you will find |
| --- | --- |
| [Getting started](https://github.com/eddiethedean/heatfall/blob/main/docs/installation.md) | Installation, coordinates, and your first image |
| [Usage and styling](https://github.com/eddiethedean/heatfall/blob/main/docs/usage.md) | Grid choices, palettes, transparency, and layers |
| [Point data](https://github.com/eddiethedean/heatfall/blob/main/docs/data.md) | CSV input, coordinate pairs, and count semantics |
| [Basemaps and output](https://github.com/eddiethedean/heatfall/blob/main/docs/basemaps.md) | Providers, fixed views, rendering without tiles, and SVG |
| [Geography](https://github.com/eddiethedean/heatfall/blob/main/docs/geography.md) | Antimeridian handling and polar limits |
| [Troubleshooting](https://github.com/eddiethedean/heatfall/blob/main/docs/troubleshooting.md) | Common errors and reproducible bug reports |

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Every cell has the same color | Counts may all be equal. Use a coarser precision if you want more aggregation. |
| Cells appear in the wrong place | Check latitude/longitude order and decimal-degree units. For H3, use Heatfall 1.1.0 or newer. |
| Cells are larger or smaller than expected | Geohash and H3 use different precision scales. Adjust within the range for your chosen grid. |
| Basemap tiles are missing or rendering stalls | Check network access and tile-provider availability. Cached tiles can avoid later requests. |
| Colors differ between runs or maps | Palettes are generated per layer. Distinct and random colors can vary, and the number of count levels changes the palette. |
| `add_circles()` raises `TypeError` | Pass latitude, longitude, and radii sequences; use `[1000] * len(lats)` for equal one-kilometer radii. |

Keep the provider attribution visible when sharing map images. Heatfall's MIT
license covers the package; basemap imagery has its own provider terms.

## Develop and contribute

Create a virtual environment, then install the package with its development tools:

```sh
git clone https://github.com/eddiethedean/heatfall.git
cd heatfall
python -m venv .venv
```

Activate it with `source .venv/bin/activate` on macOS/Linux, or
`.venv\Scripts\Activate.ps1` in Windows PowerShell. Then run:

```sh
python -m pip install -e ".[dev]"
python -m pytest
python -m tox -e ruff,mypy
```

`pytest` generates coverage reports. Ordinary rendering tests use mock tiles;
tests explicitly marked `integration` may make real tile requests.

To run the complete Python version matrix, install the matching interpreters and
run `python -m tox`. For a single installed version, use `python -m tox -e py311`.
CI runs tests on Python 3.8–3.13 on Linux, Python 3.13 on macOS and Windows, and
checks formatting, linting, types, and package builds.

### Build the documentation

Use Python 3.12 or newer for Sphinx and the documentation dependencies:

```sh
python -m pip install -e ".[docs]"
python -m sphinx -b html -W --keep-going docs docs/_build/html
```

Open `docs/_build/html/index.html` to view the site. With Python 3.13 available,
`python -m tox -e docs` builds it in an isolated environment. CI also builds the
documentation and fails on warnings.

The repository is configured for Read the Docs through `.readthedocs.yaml`.
See the [documentation setup guide](https://github.com/eddiethedean/heatfall/blob/main/docs/development.md#connect-read-the-docs)
for importing the GitHub repository into a Read the Docs account.

The README images are actual package output. Reproduce them with:

```sh
python examples/generate_doc_maps.py
```

The generator uses synthetic data and real OpenStreetMap tiles. It needs network
access when those tiles are not already cached.

For changes, include a runnable example or a regression test where appropriate,
run the checks above, and open a pull request. For bug reports, include your Python
and Heatfall versions, a small coordinate sample, the precision, and the traceback.

Maintainers can follow the [release guide](https://github.com/eddiethedean/heatfall/blob/main/docs/releasing.md)
for compatibility notes, distribution validation, and publishing steps. Pushing
a matching `vX.Y.Z` tag runs the release checks and publishes to PyPI through
trusted publishing.

## Dependencies and license

Heatfall uses [Landfall ≥0.4.2](https://github.com/eddiethedean/landfall) for map
composition and colors, [Geodude ≥0.1.1](https://github.com/eddiethedean/geodude)
and [PyGeodesy](https://github.com/mrJean1/PyGeodesy) for geohashes, and
[H3 ≥4.0.0](https://github.com/uber/h3-py) for H3 cells. Landfall provides the
underlying py-staticmaps and Pillow rendering dependencies.

Released under the [MIT license](https://github.com/eddiethedean/heatfall/blob/main/LICENSE).
Report bugs and request features in
[GitHub Issues](https://github.com/eddiethedean/heatfall/issues).
