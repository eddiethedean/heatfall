# Installation

Heatfall supports **Python 3.8–3.13**. Install the latest published release:

```sh
python -m pip install heatfall
```

These docs describe the version shown on the documentation home page. Features added in
1.1.0 include configurable opacity, translucent defaults, and antimeridian-safe
H3 rendering. If that version is not yet on PyPI, install the current source:

```sh
python -m pip install "git+https://github.com/eddiethedean/heatfall.git@main"
```

Check your installed version:

```python
import heatfall

print(heatfall.__version__)
```

The default OpenStreetMap basemap requires network access when tiles are not
already cached. It needs no API key. Preserve provider attribution when sharing
images; basemap imagery has its own provider terms.

## Make your first map

Save a small H3 example with the default translucent fill:

```python
import heatfall

lats = [27.9470, 27.9470, 27.9515, 27.9430]
lons = [-82.4580, -82.4580, -82.4500, -82.4475]

image = heatfall.plot_heat_h3s(lats, lons, precision=8)
image.save("first-heatmap.png")
```

`image` is a Pillow image. In a notebook, put `image` on its own as the last
expression in a cell to display it. Coordinates are latitude first, longitude
second, in decimal degrees; repeated locations count as separate observations.

Continue with [usage and styling](usage.md) for the illustrated example,
[prepare your point data](data.md) to load a CSV, or
[basemaps and output](basemaps.md) to configure a view and export SVG.

## Dependencies

Installation brings in [Landfall](https://github.com/eddiethedean/landfall) for map
composition and colors, [Geodude](https://github.com/eddiethedean/geodude) and
[PyGeodesy](https://github.com/mrJean1/PyGeodesy) for geohashes, and
[H3](https://github.com/uber/h3-py) for H3 cells. Landfall supplies py-staticmaps and
Pillow for rendering. Landfall's
[getting started guide](https://landfall.readthedocs.io/en/latest/getting-started/)
covers ordinary map layers and image output, and its
[troubleshooting guide](https://landfall.readthedocs.io/en/latest/troubleshooting/)
covers tile access and optional dependencies.
