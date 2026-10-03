# Prepare your point data

Heatfall accepts two parallel lists of decimal-degree coordinates: latitudes
first, then longitudes. Each row is one observation. Start with the
[usage guide](usage.md) if you want to try a map before loading a file.

## Load a CSV

Save this small example as `observations.csv`:

```text
latitude,longitude
27.9470,-82.4580
27.9470,-82.4580
27.9515,-82.4500
27.9430,-82.4475
```

Use Python's standard library to read it; no dataframe dependency is needed:

```python
import csv
import heatfall

with open("observations.csv", newline="", encoding="utf-8") as source:
    rows = list(csv.DictReader(source))

lats = [float(row["latitude"]) for row in rows]
lons = [float(row["longitude"]) for row in rows]

heatfall.plot_heat_h3s(lats, lons, precision=8).save("observations.png")
```

Convert numeric strings before plotting. Empty fields and non-numeric values
will fail at `float()`; handle those rows according to your data's meaning
before creating the map. Keep each latitude paired with its original longitude.

## Convert coordinate pairs

For native `(latitude, longitude)` pairs:

```python
points = [(27.9470, -82.4580), (27.9515, -82.4500)]
lats = [latitude for latitude, longitude in points]
lons = [longitude for latitude, longitude in points]
```

For GeoJSON point positions, the order is **longitude, latitude**:

```python
positions = [[-82.4580, 27.9470], [-82.4500, 27.9515]]
lats = [position[1] for position in positions]
lons = [position[0] for position in positions]
```

```{warning} Coordinate systems matter
Heatfall expects geographic coordinates in decimal degrees. Reproject projected
coordinates into WGS84 before passing them in. Heatfall does not read GeoJSON
files or GeoDataFrames, infer a CRS, or fill polygons with cells.
```

For ordinary GIS shapes and file plotting, see Landfall's
[GeoJSON and GeoPandas guide](https://landfall.readthedocs.io/en/latest/geospatial-data/).
To make a heat layer from those datasets, extract the point coordinates into
lists after confirming their coordinate system.

## Understand the counts

Every observation increments one cell's count. Repeated rows are counted again,
and only occupied cells are drawn. For example, ten observations at one location
contribute ten counts even though they occupy a single cell.

Choose the counting unit before plotting:

| Your question | Prepare the rows this way |
| --- | --- |
| Where did events happen most often? | Keep one row per event, including repeated locations. |
| Where are unique locations concentrated? | Deduplicate coordinate pairs first. |
| Where did events occur in one time period? | Filter the rows to that period first. |
| How do two periods compare? | Use the same precision and view, and inspect counts separately; palette colors are assigned independently per layer. |

Heatfall does not accept observation weights, normalize counts by area, smooth
neighboring cells, or add a numeric legend. Geohash cells vary in physical area
with latitude, and H3 cells also vary in area. Interpret the result as **counts
per cell**, rather than a calibrated density surface.

## Choose precision deliberately

Begin with geohash `precision=6` or H3 `precision=8` for a city example, then
adjust to your observation spacing and map extent. Higher precision gives
smaller cells. If every cell has one observation, lower the precision to group
nearby observations. Larger study areas usually need coarser cells.

The grids use different scales; equal precision values do not imply equal cell
sizes. Compare the two outputs in the [grid guide](usage.md#choose-a-grid).

## Validate before rendering

Check matching list lengths, finite values, and geographic bounds before
plotting a large dataset. Heatfall raises `ValueError` for mismatched lengths,
latitudes outside −90…90, or longitudes outside −180…180. Values can be within
those ranges and still describe the wrong location if the order is swapped.

See [coordinate rules](geography.md#coordinate-rules) and
[troubleshooting](troubleshooting.md) for the full input checklist.
