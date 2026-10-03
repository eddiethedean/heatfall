# Geographic considerations

## Coordinate rules

- Supply parallel latitude and longitude lists in **latitude, longitude** order.
  GeoJSON positions commonly use the reverse order.
- Latitude must be between −90 and 90; longitude between −180 and 180, inclusive.
- Lists must have matching lengths. Non-finite values such as `NaN` and infinity
  raise `ValueError`.
- Precision must be an integer in the grid's supported range; opacity must be
  finite and between 0 and 1 inclusive.
- Standalone plotting functions reject empty lists. Adding an empty heat layer
  to a context is a no-op; add content before rendering it.
- Repeated coordinates count as repeated observations. Deduplicate first when
  your analysis should count unique locations.

## Crossing the antimeridian

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

Heatfall splits crossing H3 boundaries into closed polygons at the antimeridian,
using spherical intersections. The pieces share the original cell's count and
color and are composited together to avoid a darker transparency seam. Automatic
map extents follow the short span across the seam. Exact 180 and −180 longitude
are accepted.

This behavior applies to rendered H3 cells. Polygon-to-cell filling of external
GeoJSON is outside Heatfall's point API.

## Polar limits

H3 rendering is clipped to the Web Mercator tile latitude limit of approximately
±85.0511°. Pole-containing cells close through their pole before clipping, but
these maps do not display the poles themselves.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Every cell has the same color | Counts may all be equal. Try a coarser precision. |
| Cells appear in the wrong place | Check coordinate order, decimal-degree units, and use Heatfall 1.1.0 or newer for the H3 fixes. |
| Cells have an unexpected size | Geohash and H3 use different precision scales. |
| Basemap tiles are missing or rendering stalls | Check network access and tile-provider availability. Cached tiles can avoid later requests. |
| Colors differ between maps | Palettes are generated per layer; avoid comparing counts across maps by color alone. |
| `add_circles()` raises `TypeError` | Pass latitude, longitude, and radii sequences, such as `[1000] * len(lats)` for one-kilometer radii. |
