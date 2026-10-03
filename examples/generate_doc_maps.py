"""Render the README maps from synthetic downtown Tampa observations.

Run from an editable checkout with:
    python examples/generate_doc_maps.py

The default OpenStreetMap basemap requires network access on a cold tile cache.
"""

from pathlib import Path

import heatfall


def main() -> None:
    output = Path(__file__).resolve().parents[1] / "docs" / "images"
    output.mkdir(parents=True, exist_ok=True)

    lats = [27.9470] * 8 + [27.9515] * 4 + [27.9430] * 2 + [27.9475]
    lons = [-82.4580] * 8 + [-82.4500] * 4 + [-82.4475] * 2 + [-82.4400]

    heatfall.plot_heat_h3s(
        lats, lons, precision=8, color_scheme="wheel", size=(800, 500)
    ).save(output / "h3.png")

    heatfall.plot_heat_hashes(
        lats, lons, precision=6, color_scheme="wheel", size=(800, 500)
    ).save(output / "geohash.png")

    context = heatfall.Context()
    context.add_heat_h3s(lats, lons, precision=8, color_scheme="wheel")
    context.add_points([27.9470], [-82.4580], colors=["black"], point_size=10)
    context.add_line([(27.9430, -82.4475), (27.9475, -82.4400)], color="black", width=3)
    context.add_circles(
        [27.9515], [-82.4500], [300], color="blue", fill_color="transparent", width=2
    )
    context.render_pillow(800, 500).save(output / "layers.png")
    print("Rendered README maps to {}".format(output))


if __name__ == "__main__":
    main()
