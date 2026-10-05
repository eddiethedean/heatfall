# Usage and styling

## Create an H3 heatmap

This example contains 15 synthetic observations around downtown Tampa. Repeated
coordinates deliberately produce cells with different counts.

```python
import heatfall

lats = [27.9470] * 8 + [27.9515] * 4 + [27.9430] * 2 + [27.9475]
lons = [-82.4580] * 8 + [-82.4500] * 4 + [-82.4475] * 2 + [-82.4400]

image = heatfall.plot_heat_h3s(
    lats, lons, precision=8, color_scheme="wheel", size=(800, 500)
)
image.save("h3-heatmap.png")
```

The plotting functions return a `PIL.Image.Image`, automatically fitting the map
to the occupied cells. `size` is `(width, height)` in pixels.

## Choose a grid

| | Geohash | H3 |
| --- | --- | --- |
| Function | `plot_heat_hashes()` | `plot_heat_h3s()` |
| Cell shape | Latitude/longitude rectangles | Mostly hexagons, plus pentagons |
| Precision range | 1–12 | 0–15, called resolution in H3 |
| City-scale starting point | `precision=6` | `precision=8` |

Higher precision means smaller cells. Lower it when most cells contain a single
observation. The two grids' precision scales differ: level 8 in one grid does not
imply the same cell size as level 8 in the other.

Create a geohash map from the same observations:

```python
image = heatfall.plot_heat_hashes(
    lats, lons, precision=6, color_scheme="wheel", size=(800, 500)
)
image.save("geohash-heatmap.png")
```

![Geohash rectangles over downtown Tampa](images/geohash.png)

## Colors and opacity

Each observation contributes one count to its cell. Only occupied cells are
drawn. Within a layer, cells with the same count share a color; different count
levels receive different palette colors.

| `color_scheme` | Behavior |
| --- | --- |
| `"distinct"` (default) | Generates distinct colors for the count levels |
| `"wheel"` | Selects colors from an HSV color wheel |
| `"random"` | Generates random colors for the count levels |
| `"sequential"` | Uses a fixed light-to-dark blue scale by numeric count |

The palettes do not guarantee a sequential light-to-dark or cool-to-hot scale.
A red cell does not inherently indicate a higher count. Palettes are assigned
per layer, and distinct/random colors may vary between calls.

Use `count_colors` to fix colors to specific count values across maps or grids.
Provide every count present in the data; extra entries are allowed. Colors accept
hex strings, `staticmaps.Color` values, or RGB/RGBA tuples. Opacity is applied
once to the supplied alpha. When `count_colors` is supplied, it takes precedence
over `color_scheme`.

```python
shared_colors = {1: "#deebf7", 4: "#9ecae1", 8: "#3182bd"}
image = heatfall.plot_heat_h3s(
    lats, lons, precision=8, count_colors=shared_colors
)
```

Sequential colors interpolate from light blue (`#deebf7`) to dark blue
(`#08519c`) using the observed numeric count range; a layer with one count
level uses the midpoint. Each layer scales to its own range. Use a shared
`count_colors` mapping when equal counts should have equal colors across maps.
Both palettes receive a discrete legend with one entry per exact count.

### Legends

Plotting functions and new contexts show a legend by default. It uses the
layer's exact final colors and alpha and labels the raw observation count per
occupied cell. Hide it with `legend=False`, or toggle a context legend with
`context.set_legend(False)`. Empty heat additions have no legend entries.

```python
image = heatfall.plot_heat_h3s(lats, lons, precision=8, legend=False)

image = heatfall.plot_heat_h3s(
    lats, lons, precision=8,
    legend=heatfall.LegendOptions(
        position=(0.95, 0.08),
        units="fraction",
        anchor="top-right",
        offset=(-8, 0),
        title="Observations per cell",
        columns=2,
        label_format="{count} points",
    ),
)
```

`position` accepts the nine named anchors (`top-left`, `top-center`,
`top-right`, `center-left`, `center`, `center-right`, `bottom-left`,
`bottom-center`, `bottom-right`) or any `(x, y)` coordinate. Named positions
are inset by `margin` pixels, which defaults to 12. Coordinates use pixels by
default; `units="fraction"` scales them by output width and height. `anchor`
chooses the legend point aligned to that position, and signed `offset` values
fine-tune placement in pixels. Custom coordinates default to the top-left anchor.

The legend is measured against the final image dimensions and raises
`ValueError` if it does not fit. Add `allow_clipping=True` to deliberately let
it extend beyond the canvas. `LegendOptions` also configures title, labels,
font size, colors, border, corner radius, shadow, padding, swatches, row
spacing, and columns. The default panel uses a bold heading, a subtle divider
and shadow, rounded corners, and larger color chips for quicker scanning.

Every visual part can be styled independently. Set a role-specific font size,
weight, or color for the title, layer headings, and count labels; omitted role
colors inherit `text_color`, and omitted role font sizes inherit `font_size`.
`font_family` accepts a system family name or a TrueType/OpenType font file;
Pillow falls back to DejaVu Sans if it cannot load the requested font.
Panel, shadow, divider, swatch, row, and column dimensions and colors are also
independent options:

| Part | `LegendOptions` parameters |
| --- | --- |
| Placement | `position`, `units`, `anchor`, `offset`, `margin`, `allow_clipping` |
| Title and labels | `title`, `label_format`, `font_family`, `font_size`, `title_font_size`, `section_font_size`, `label_font_size`, `title_weight`, `section_weight`, `label_weight`, `title_align` |
| Text colors | `text_color`, `title_color`, `section_color`, `label_color` |
| Panel | `background_color`, `border_color`, `border_width`, `corner_radius`, `padding` |
| Shadow | `shadow`, `shadow_color`, `shadow_opacity`, `shadow_offset` |
| Divider | `divider_color`, `divider_width`, `title_spacing` |
| Rows and swatches | `swatch_size`, `swatch_radius`, `label_gap`, `row_spacing`, `section_spacing`, `columns`, `column_spacing` |

Colors accept names, hexadecimal strings, `staticmaps.Color` values, and
RGB/RGBA tuples. Shadow opacity ranges from 0 (transparent) to 1 (full color).
Weights accept `"normal"` or `"bold"`; title alignment accepts `"left"`,
`"center"`, or `"right"`.

Each heat layer uses its own palette. A composed map displays separately titled
sections in layer order; set `legend_label` on a heat method to name a section.
Read the immutable `context.heat_layers` sequence for each layer's grid,
precision, observation total, occupied cell total, distinct counts, and exact
count-to-RGBA mapping. The legend is drawn over map content in image coordinates.
Keep tile attribution visible when choosing a custom location.

Fills default to **60% opacity (40% transparent)**. Both plotting functions and
`Context` heat methods accept the keyword-only `opacity` option:

```python
# Softer cells, showing more of the basemap.
image = heatfall.plot_heat_h3s(lats, lons, precision=8, opacity=0.4)

# Restore solid fills.
image = heatfall.plot_heat_hashes(lats, lons, precision=6, opacity=1.0)
```

Opacity must be between 0 and 1 inclusive; 0 makes the fill invisible. It applies
uniformly to the layer and does not encode the observation count.

The result shows raw counts per cell. It does not normalize by cell area, smooth
counts, or accept observation weights.

## Compose other layers

`heatfall.Context` extends `landfall.Context`. Add heat cells first, then points,
routes, and circles to draw those objects above the heat layer:

```python
context = heatfall.Context()
context.add_heat_h3s(lats, lons, precision=8, color_scheme="wheel")
context.add_points([27.9470], [-82.4580], colors=["black"], point_size=10)
context.add_line([(27.9430, -82.4475), (27.9475, -82.4400)], color="black", width=3)
context.add_circles(
    [27.9515], [-82.4500], [300], color="blue", fill_color="transparent", width=2
)
context.render_pillow(800, 500).save("layered-heatmap.png")
```

![An H3 heat layer with a point, route, and circle](images/layers.png)

See Landfall's [Context API](https://landfall.readthedocs.io/en/latest/api/#context)
for inherited layer methods, and its
[shapes and styling guide](https://landfall.readthedocs.io/en/latest/shapes-and-styling/)
for point sizes, line widths, circle radii, and overlay colors.

Configure the basemap with `context.set_tile_provider(provider)`. For standalone
functions, the argument is spelled `tileprovider`, without an underscore.
`Context` also inherits py-staticmaps' SVG and optional Cairo rendering methods.
Landfall documents [custom tile services](https://landfall.readthedocs.io/en/latest/custom-tile-service/)
and [combining shapes and exporting SVG](https://landfall.readthedocs.io/en/latest/shapes-and-styling/#combine-shapes-and-export-svg).

## Next steps

- [Prepare point data](data.md) from a CSV or coordinate pairs.
- [Choose a basemap or export SVG](basemaps.md), including rendering without tiles.
- [Check geographic boundaries](geography.md) for antimeridian and polar behavior.
- [Look up exact signatures](api.rst) or [troubleshoot a map](troubleshooting.md).
