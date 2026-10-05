# Performance and scale

Heatfall takes all observations as in-memory latitude and longitude lists. It
does not stream input or accept pre-aggregated weights. Work therefore depends
on both the number of input rows and the number of occupied cells:

- Each input observation must be converted to a grid cell and counted.
- Each occupied cell becomes map geometry. Legend size depends on distinct
  count levels: the default `"heatmap"` palette uses at most five ranges per
  layer, while other palettes can show one entry per distinct count.
- Tile requests depend on output size, zoom, rendered view, and provider. The
  plotting functions fit the view to their cells automatically, so the input's
  spatial extent can affect which tiles are requested. With a fixed view, tile
  requests do not grow with the number of observations.

These are scaling relationships, not runtime guarantees. Measure with your
data, grid, Python version, and tile provider before setting a production
capacity target.

## Reduce work safely

1. Filter to the analysis period and geographic area before passing points.
2. Deduplicate only if the intended observation is a unique coordinate. If
   repeated rows represent separate events, keep them; Heatfall counts each row.
3. Choose a coarser precision when the map has more occupied cells than needed.
   This reduces geometry work; it may also reduce legend entries if it reduces
   the number of distinct count levels. Heatfall still processes every input
   observation.
4. Use `staticmaps.tile_provider_None` while measuring aggregation and drawing
   without tile downloads. Use the same tile provider and cache state when
   measuring real map output.
5. Keep output dimensions and map view fixed when comparing performance
   between runs.

If the input no longer fits comfortably in memory, Heatfall does not currently
provide a streaming or weighted-count interface. An upstream aggregation is
only equivalent if it preserves the observation counts and can be represented
by the coordinate rows Heatfall accepts; there is no public API for passing a
precomputed count directly.

## Benchmark reproducibly

Record the number of input rows, unique occupied cells, grid and precision,
output dimensions, tile provider, Python version, and Heatfall/dependency
versions. Run several trials after separating cold tile downloads from cached
rendering. Use `time.perf_counter()` around both the heat-layer addition and the
render call if you need to identify which stage dominates.

Heatfall does not publish a universal point-count threshold or benchmark
because hardware, spatial distribution, tile access, and occupied-cell count
change the result. For a reproducible performance report, open a
[GitHub issue](https://github.com/eddiethedean/heatfall/issues) with a small
synthetic workload and the details above.
