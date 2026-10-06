# Roadmap

Heatfall **1.3.0** requires Landfall 0.5.0 or newer and adds palette seeds,
tile API-key forwarding, and optional GIS and Cairo installation extras.
It retains the default-on count legends, ordered palettes, shared count colors,
and immutable heat-layer metadata introduced in 1.2.0.
See the [changelog](changelog.md) for release history and compatibility notes.

Beyond 1.3.0, there is no committed feature schedule. Proposed work and
bug reports are tracked in [GitHub Issues](https://github.com/eddiethedean/heatfall/issues);
an issue is not a delivery commitment. The
[development guide](development.md) explains how to run checks and contribute.

## Current scope

Heatfall counts unweighted point observations in geohash or H3 cells. It does
not currently provide weighted input, spatial smoothing, count normalization by
cell area, polygon-to-cell filling, or interactive map controls. See
[point-data semantics](data.md#understand-the-counts) before interpreting a map
as a density surface.
