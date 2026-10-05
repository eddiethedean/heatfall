# Roadmap

Heatfall **1.2.0** is the current stable release. It adds default-on count
legends, a five-step ordered heatmap palette, sequential colors, explicit
count-to-color mappings, and immutable metadata for composed heat layers.
See the [changelog](changelog.md) for release history and compatibility notes.

There is no committed feature schedule for a later release. Proposed work and
bug reports are tracked in [GitHub Issues](https://github.com/eddiethedean/heatfall/issues);
an issue is not a delivery commitment. The
[development guide](development.md) explains how to run checks and contribute.

## Current scope

Heatfall counts unweighted point observations in geohash or H3 cells. It does
not currently provide weighted input, spatial smoothing, count normalization by
cell area, polygon-to-cell filling, or interactive map controls. See
[point-data semantics](data.md#understand-the-counts) before interpreting a map
as a density surface.
