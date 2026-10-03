# Heatfall

**Turn latitude and longitude lists into static maps colored by point count.**

Documentation for **Heatfall {{release}}**.

Heatfall groups observations into geohash rectangles or H3 cells, counts the
points in each cell, and draws the occupied cells over a basemap. Heat fills
default to 60% opacity so streets and labels remain visible.

![H3 cells over downtown Tampa](images/h3.png)

*Synthetic observations around downtown Tampa. Each occupied cell is colored by
its point count. Map tiles and attribution come from OpenStreetMap.*

Start with [installation](installation.md) and the [usage guide](usage.md).
The [API reference](api.rst) describes the plotting functions and heat layer
methods. [Geographic considerations](geography.md) covers coordinate validation,
the antimeridian, and polar limits.

```{toctree}
:maxdepth: 1
:caption: Documentation

installation
usage
api
geography
development
changelog
```

Heatfall is released under the
[MIT license](https://github.com/eddiethedean/heatfall/blob/main/LICENSE).
Find the code on [GitHub](https://github.com/eddiethedean/heatfall), or report a
problem in [GitHub Issues](https://github.com/eddiethedean/heatfall/issues).
