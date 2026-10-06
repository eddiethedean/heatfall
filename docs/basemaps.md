# Basemaps and output

Use a plotting function for a single heat layer. Use `heatfall.Context` when you
need to configure the view, combine layers, or export SVG. Heatfall's context
inherits plotting helpers from
[Landfall](https://landfall.readthedocs.io/en/latest/api/#context). The underlying
map context, tile handling, and renderers come from
[py-staticmaps](https://github.com/flopp/py-staticmaps).
Heat maps include a legend by default; legends are rendered in image coordinates
after the geographic layers and basemap attribution.

For native objects, shared contexts, radius units, and renderer return types,
see [py-staticmaps interoperability](staticmaps.md).

::::{container} hf-feature-strip
:::{container} hf-feature
**Image output**

Plotting functions return Pillow images ready for PNG or JPEG export.
:::
:::{container} hf-feature
**Vector output**

Contexts can render cell boundaries and legends as SVG.
:::
:::{container} hf-feature
**Map context**

Add markers and routes without changing the heat aggregation.
:::
::::

::::{container} hf-gallery
:::{container}
![Heatmap with a compact count legend](images/h3-legend.png)

*A standalone heat map, fitted to its occupied H3 cells.*
:::
:::{container}
![Heatmap composed with a point, route, and circle](images/layers.png)

*A context adds ordinary map layers above the heat cells.*
:::
::::

## Choose a tile provider

The default basemap is OpenStreetMap. Supply a py-staticmaps tile provider with
`tileprovider` on either plotting function:

```python
import heatfall
import staticmaps

lats = [27.9470, 27.9470, 27.9515]
lons = [-82.4580, -82.4580, -82.4500]

image = heatfall.plot_heat_h3s(
    lats, lons, precision=8,
    tileprovider=staticmaps.tile_provider_OSM,
    size=(1000, 650),
)
image.save("heatmap.png")
```

For a composed map, call `context.set_tile_provider(provider)` before rendering.
Landfall's [custom tile service guide](https://landfall.readthedocs.io/en/latest/custom-tile-service/)
explains URL templates, tile-provider settings, and API keys.

```{note} The argument spelling differs
Heatfall's plotting functions use `tileprovider`. Landfall's plotting functions
use `tile_provider`. On a context, use `set_tile_provider()`.
```

Rendering may download tiles when they are not cached. Provider availability,
usage limits, and attribution requirements depend on the service you choose.
Keep the attribution in exported maps.

### Tile services with API keys

Contexts support keyed providers through the inherited Landfall/py-staticmaps
API, including in Heatfall 1.2.0:

```python
import os

# provider is the TileProvider instance for your chosen service.
context = heatfall.Context()
context.set_tile_provider(provider, api_key=os.environ["MAP_TILE_API_KEY"])
```

In Heatfall 1.3.0, both heat plotting functions also accept a keyword-only
`api_key`:

```python
image = heatfall.plot_heat_h3s(
    lats, lons, precision=8,
    tileprovider=provider,
    api_key=os.environ["MAP_TILE_API_KEY"],
)
```

Use a provider instance configured for the service's URL template and preserve
its attribution. See [installation](installation.md) for the current source
installation command and Landfall's
[custom tile service guide](https://landfall.readthedocs.io/en/latest/custom-tile-service/)
for provider setup.

## Render without a basemap

Use the built-in provider with no tile downloads to inspect your heat cells
without network access:

```python
import heatfall
import staticmaps

context = heatfall.Context()
context.set_tile_provider(staticmaps.tile_provider_None)
context.add_heat_h3s([27.9470, 27.9515], [-82.4580, -82.4500], precision=8)
context.render_pillow(800, 500).save("cells-only.png")
```

A map without tiles supplies no street or place-name context. Use it to inspect
cell geometry or as an input to your own composition workflow.

## Control the view

Standalone plotting functions automatically fit the occupied cells. With a
context, you can set a center and zoom explicitly:

```python
import heatfall
import staticmaps

context = heatfall.Context()
context.add_heat_h3s([27.9470, 27.9515], [-82.4580, -82.4500], precision=8)
context.set_center(staticmaps.create_latlng(27.9470, -82.4500))
context.set_zoom(13)
context.render_pillow(1000, 650).save("fixed-view.png")
```

Higher zoom brings you closer to the ground. Use the same center, zoom, and
output dimensions when comparing maps. The image size is in pixels and does not
change the grid's precision or the number of observations counted.

## Export an image or SVG

`plot_heat_hashes()` and `plot_heat_h3s()` return a Pillow image. Save it as PNG,
or use it in a notebook by leaving `image` as the last expression in a cell.
For JPEG, convert away from the image's RGBA mode first:

```python
image.convert("RGB").save("heatmap.jpg", quality=95)
```

Use a context for SVG:

```python
import heatfall

context = heatfall.Context()
context.add_heat_h3s([27.9470, 27.9515], [-82.4580, -82.4500], precision=8)
context.render_svg(800, 500).saveas("heatmap.svg")
```

Heat cell boundaries are vector paths in SVG; basemap tiles remain raster
imagery. Transparency is retained, including for cells split at the
[antimeridian](geography.md#crossing-the-antimeridian).

The legend is also included in SVG output. Pillow, SVG, and Cairo use the same
measured layout, position, anchor, and clipping checks. A legend does not affect
map bounds or zoom. Its default top-right placement leaves bottom tile
attribution clear; keep attribution visible when choosing a custom location.

## Optional Cairo rendering

Cairo output is optional and is provided by py-staticmaps through Landfall.
Heatfall's Cairo extra installs the renderer dependencies through Landfall:

```sh
python -m pip install "heatfall[cairo]"
```

The `pycairo` extension may need native Cairo development libraries to build.
On Ubuntu, install `libcairo2-dev` before the Python extra. See the
[pycairo installation guide](https://pycairo.readthedocs.io/en/latest/getting_started.html)
for platform-specific requirements. Pillow and SVG rendering do not require
this extra.

The extra requires Heatfall 1.3.0 or newer. See
[installation](installation.md#optional-cairo-rendering) to install from source.

```python
import heatfall
import staticmaps

context = heatfall.Context()
context.set_tile_provider(staticmaps.tile_provider_None)
context.add_heat_h3s([27.9470, 27.9515], [-82.4580, -82.4500], precision=8)
surface = context.render_cairo(800, 500)
surface.write_to_png("heatmap-cairo.png")
```

## Tile requests and data

Heatfall processes the coordinate lists locally; it has no Heatfall-hosted
mapping service. With the default OpenStreetMap provider, the map renderer
requests tiles for the visible map area. The tile provider can infer which
geographic area is being rendered from those requests, but the observation
lists are not sent to it by Heatfall. Use `staticmaps.tile_provider_None` to
render without map-tile network requests. The resulting image has no street or
place-name basemap.

## Combine heat with other shapes

Add heat cells first, then add points, lines, or circles to draw them above the
heat fill. See the [composed map example](usage.md#compose-other-layers) for
runnable code and an actual output image. Landfall's
[shapes and styling guide](https://landfall.readthedocs.io/en/latest/shapes-and-styling/)
covers inherited layer options and additional exports.
