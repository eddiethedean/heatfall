# py-staticmaps interoperability

Use native `staticmaps` objects and context controls alongside Heatfall's heat
layers. [py-staticmaps](https://github.com/flopp/py-staticmaps) supplies the map
engine and is installed through Landfall; its Python import is `staticmaps`.
Native markers, lines, areas, and circles work with the standard Heatfall
installation. GeoPandas and Shapely extras are only needed for GIS overlays.

## Use one context for heat and native objects

The inheritance chain is:

```text
heatfall.Context → landfall.Context → staticmaps.Context
```

Create a `heatfall.Context` and pass it to helpers that accept a
`staticmaps.Context`. Add native objects with the public `add_object()` method.
The example below writes PNG and SVG files without downloading map tiles:

```python
import heatfall
import staticmaps


def add_route(map_context: staticmaps.Context) -> None:
    stops = [
        staticmaps.create_latlng(27.9470, -82.4580),
        staticmaps.create_latlng(27.9515, -82.4500),
    ]
    map_context.add_object(
        staticmaps.Line(stops, color=staticmaps.BLACK, width=3)
    )
    for stop in stops:
        map_context.add_object(
            staticmaps.Marker(stop, color=staticmaps.BLACK, size=10)
        )


context = heatfall.Context()
context.set_tile_provider(staticmaps.tile_provider_None)
context.add_heat_h3s(
    [27.9470, 27.9470, 27.9515, 27.9430],
    [-82.4580, -82.4580, -82.4500, -82.4475],
    precision=8,
)
add_route(context)

context.render_pillow(800, 500).save("heat-native.png")
context.render_svg(800, 500).saveas("heat-native.svg")
```

An existing helper such as `add_route()` can retain its native Context type
annotation. A plain `staticmaps.Context` has no `add_heat_h3s()` or
`add_heat_hashes()` method; start with `heatfall.Context` when you need both
native objects and heat aggregation. Heatfall's standalone `plot_heat_*()`
functions return images and do not accept an existing context.

## Coordinates, colors, and units

Native object constructors take `s2sphere.LatLng` objects. Create them with
`staticmaps.create_latlng(latitude, longitude)` in decimal degrees. Latitude
comes first, as in Heatfall's heat inputs. GeoJSON uses the opposite order;
see [GIS composition](usage.md#geojson-overlays) when mixing formats.

Use `staticmaps.Color`, constants such as `staticmaps.BLUE`, or
`staticmaps.parse_color("#335577")` for native object colors. Heatfall's heat
`opacity` setting applies to heat cells; native fills use their own color's
alpha channel, from 0 to 255.

| Native object | Input and styling |
| --- | --- |
| `staticmaps.Marker` | One `LatLng`; `size` is in pixels. |
| `staticmaps.Line` | At least two `LatLng` values; `width` is in pixels. |
| `staticmaps.Area` | A boundary of `LatLng` values, with separate fill and outline colors. |
| `staticmaps.Circle` | One `LatLng` center and a radius in **kilometres**. |
| `staticmaps.ImageMarker` | One `LatLng`, a PNG filename, and pixel offsets for its anchor. |

### Native circle radii are kilometres

Continue with the context from the first example to add a 300-metre circle:

```python
context.add_object(
    staticmaps.Circle(
        staticmaps.create_latlng(27.9470, -82.4580),
        radius_km=0.3,
        fill_color=staticmaps.TRANSPARENT,
        color=staticmaps.BLUE,
        width=2,
    )
)
context.render_pillow(800, 500).save("heat-native-circle.png")
```

Heatfall's inherited Landfall helper `context.add_circle()` defaults to
**metres**. Its equivalent radius argument is `300`, optionally with
`radius_unit="meters"`. Keep the unit distinction when translating existing
code between the helper and the native constructor.

### Native areas

This example continues with the same context. Repeat the first point to close
the boundary explicitly:

```python
ring = [
    (27.9440, -82.4620),
    (27.9440, -82.4460),
    (27.9540, -82.4460),
    (27.9540, -82.4620),
    (27.9440, -82.4620),
]
context.add_object(
    staticmaps.Area(
        [staticmaps.create_latlng(lat, lon) for lat, lon in ring],
        fill_color=staticmaps.Color(255, 210, 90, 60),
        color=staticmaps.BLACK,
        width=2,
    )
)
context.render_pillow(800, 500).save("heat-native-area.png")
```

Objects draw in addition order. To put this fill underneath the route and
markers, insert it before `add_route(context)` in the first example. For
polygons with interior holes, use Landfall's inherited
[`context.add_polygon(..., holes=...)`](usage.md#polygons-with-holes) helper.

## Control framing and tile caching

Automatic framing fits the heat cells and native objects together. The heat
legend uses image coordinates and does not change geographic bounds. Set a
fixed view when comparing maps:

```python
context.set_center(staticmaps.create_latlng(27.9470, -82.4500))
context.set_zoom(13)
context.render_pillow(800, 500).save("heat-native-fixed-view.png")
```

To include an empty part of a study area in automatic framing, use native
`add_bounds()`. Start a fresh context so no fixed center or zoom overrides the
automatic view:

```python
import heatfall
import s2sphere
import staticmaps

context = heatfall.Context()
context.set_tile_provider(staticmaps.tile_provider_None)
context.add_heat_h3s([27.9470], [-82.4580], precision=8)
study_area = s2sphere.LatLngRect.from_point_pair(
    staticmaps.create_latlng(27.9350, -82.4700),
    staticmaps.create_latlng(27.9650, -82.4400),
)
context.add_bounds(study_area)
context.render_pillow(800, 500).save("heat-study-area.png")
```

py-staticmaps handles tile downloads and disk caching. Set a cache directory
before rendering with a tile provider:

```python
context.set_cache_dir("map-tile-cache")
```

Choose `staticmaps.tile_provider_OSM` to add an OpenStreetMap basemap, or
`staticmaps.tile_provider_None` to retain the offline behavior shown here.
Set the provider with `context.set_tile_provider(provider)`; Heatfall's plotting
functions spell their argument `tileprovider`. For keyed services, use
`context.set_tile_provider(provider, api_key=...)`. See
[basemaps and API keys](basemaps.md#tile-services-with-api-keys) for provider
setup, network behavior, and attribution.

## Render through the Heatfall instance

Call `context.render_*()` so Heatfall's legend hooks run after the native map
layers. Calling a base renderer directly, such as
`staticmaps.Context.render_pillow(context, 800, 500)`, bypasses those hooks.

| Method | Return value | Save a file |
| --- | --- | --- |
| `context.render_pillow(width, height)` | Pillow image | `image.save("map.png")` |
| `context.render_svg(width, height)` | `svgwrite.Drawing` | `drawing.saveas("map.svg")` |
| `context.render_cairo(width, height)` | `cairo.ImageSurface` | `surface.write_to_png("map.png")` |

Pillow and SVG work with the standard installation. For Cairo, install
`heatfall[cairo]` and the required native libraries as described in
[Cairo setup](basemaps.md#optional-cairo-rendering). Then, with a context from
the examples above:

```python
surface = context.render_cairo(800, 500)
surface.write_to_png("heat-native-cairo.png")
```

Native objects do not contribute observations or entries to the heat legend.
`context.heat_layers` continues to describe the heat layers added through
`add_heat_hashes()` and `add_heat_h3s()`. Configure that legend with
`context.set_legend(...)`; see [legend styling](usage.md#legends).

## Further reading and credits

- [Upstream py-staticmaps examples](https://github.com/flopp/py-staticmaps/tree/master/examples)
  for native objects, including image markers.
- [Landfall's py-staticmaps API guide](https://landfall.readthedocs.io/en/latest/py-staticmaps/)
  for additional context and renderer controls.
- [Heatfall architecture](architecture.md#rendering-boundaries) for the roles of
  Heatfall, Landfall, and py-staticmaps.

Credit for the underlying map engine belongs to
[Florian Pigorsch (`flopp`)](https://github.com/flopp) and the
[py-staticmaps contributors](https://github.com/flopp/py-staticmaps).
