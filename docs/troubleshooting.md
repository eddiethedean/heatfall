# Troubleshooting

Start with coordinate order, grid precision, and tile access. The table below
connects common symptoms to a concrete next step.

| Symptom | Next check |
| --- | --- |
| Every cell has the same color | All cells may have the same count. Lower precision to group more observations. |
| A cell appears in the wrong place | Confirm latitude first, longitude second, and decimal-degree units. Both swapped numbers can still pass bounds validation. |
| Cells look too large or small | Geohash precision and H3 resolution use different scales. See [grid choices](usage.md#choose-a-grid). |
| The basemap is missing or slow | Check network connectivity, provider availability, and usage limits. Try [rendering without tiles](basemaps.md#render-without-a-basemap) to inspect the heat layer. |
| Colors differ between maps | Colors are assigned per layer. Distinct and random palettes may vary; color alone cannot establish equal counts across maps. |
| Red cells do not correspond to the largest count | Palettes are categorical, not sequential. See [colors and opacity](usage.md#colors-and-opacity). |
| The map spans the world near ±180° | Use Heatfall 1.1.0 or newer for H3 splitting and extent fixes. See [antimeridian behavior](geography.md#crossing-the-antimeridian). |
| Cells are invisible | Check whether `opacity=0` was supplied. The default is `0.6`; use `1.0` for solid fills. |
| The poles are missing | Web Mercator basemaps end at approximately ±85.0511°. See [polar limits](geography.md#polar-limits). |
| `add_circles()` raises `TypeError` | Supply latitude, longitude, and radii sequences; for one circle use `[latitude]`, `[longitude]`, and `[radius]`. |
| `tile_provider` raises an unexpected keyword error | Heatfall's plotting argument is `tileprovider`; a context uses `set_tile_provider()`. |
| `opacity` raises an unexpected keyword error | Check the installed version and interpreter; this option requires Heatfall 1.1.0 or newer. |
| A legend does not fit | Add columns, reduce font size or padding, enlarge the image, or set `allow_clipping=True` when partial placement is intentional. |
| A legend covers tile attribution | Choose another `LegendOptions.position` and keep the provider attribution visible. |
| Equal counts have different colors across maps | Supply the same `count_colors` mapping to both maps. Automatic palettes are assigned per layer. |

## Check the running version

```sh
python -m pip show heatfall
python -c "import sys, heatfall; print(sys.executable); print(heatfall.__version__)"
```

Run installation commands with the same interpreter that runs your script or
notebook. Heatfall 1.1.0 is available on PyPI; upgrade an older installation with:

```sh
python -m pip install --upgrade heatfall
```

See the [installation guide](installation.md) to pin the release or install
development changes from source.

## Resolve input errors

- Keep latitude and longitude lists the same length and preserve their pairing.
- Use finite numeric values: latitude −90…90, longitude −180…180.
- Use an integer precision: geohash 1–12, H3 0–15.
- Use one of `"distinct"`, `"random"`, `"wheel"`, or `"sequential"` for `color_scheme`.
- Pass `opacity` as a keyword, between 0 and 1 inclusive.
- Give plotting functions at least one observation. An empty context heat layer
  is a no-op; the context still needs content before rendering.

See [preparing point data](data.md) for CSV parsing and coordinate conversion.
Landfall's [troubleshooting guide](https://landfall.readthedocs.io/en/latest/troubleshooting/)
covers ordinary layer errors and optional rendering dependencies.

## Report a reproducible problem

Open a [GitHub issue](https://github.com/eddiethedean/heatfall/issues) with:

1. Python and Heatfall versions, operating system, and the full traceback.
2. A minimal runnable coordinate sample, precision, palette, and opacity.
3. Expected output and a screenshot of the actual result.
4. Whether rendering without tiles reproduces it.

Use synthetic coordinates when your original data is private. A small sample
near the same boundary or latitude is often sufficient to explain the problem.
