![Heatfall Logo](https://raw.githubusercontent.com/eddiethedean/heatfall/main/docs/heatfall_logo.png)
-----------------

# Heatfall: Easy to use functions for plotting heat maps of geographic data on static maps
[![PyPI Latest Release](https://img.shields.io/pypi/v/heatfall.svg)](https://pypi.org/project/heatfall/)
![Tests](https://github.com/eddiethedean/heatfall/actions/workflows/tests.yml/badge.svg)

## What is it?

**Heatfall** is a Python package with easy to use functions for plotting heat maps of geographic data on a static map.

## Where to get it
The source code is currently hosted on GitHub at:
https://github.com/eddiethedean/heatfall

```sh
# PyPI
pip install heatfall
```

## Dependencies
- [py-staticmaps - A python module to create static map images (PNG, SVG) with markers, geodesic lines, etc.](https://github.com/flopp/py-staticmaps)
- [PyGeodesy - A pure Python implementation of geodesy tools for various ellipsoidal and spherical earth models using precision trigonometric, vector-based, exact, elliptic, iterative and approximate methods for geodetic (lat-/longitude), geocentric (ECEF cartesian) and certain triaxial ellipsoidal coordinates.] (https://github.com/mrJean1/PyGeodesy)

## Example
```sh
import heatfall


lats = [27.88, 27.92, 27.94]
lons = [-82.49, -82.49, -82.46]

heatfall.plot_heat(lats, lons)
```
![](https://raw.githubusercontent.com/eddiethedean/heatfall/main/docs/example_map.png)