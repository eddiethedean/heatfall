"""Render the README maps from synthetic downtown Tampa observations.

Run from an editable checkout with:
    python examples/generate_doc_maps.py

The default OpenStreetMap basemap requires network access on a cold tile cache.
"""

from pathlib import Path
import random
from typing import List, Tuple

import heatfall
from PIL import Image


def synthetic_tampa_observations() -> Tuple[List[float], List[float]]:
    """Return seeded clusters and background points around downtown Tampa."""
    rng = random.Random(1208)
    clusters = (
        # latitude, longitude, size, latitude spread, longitude spread
        (27.9506, -82.4590, 220, 0.0025, 0.0030),  # downtown
        (27.9418, -82.4515, 160, 0.0022, 0.0030),  # Water Street
        (27.9377, -82.4720, 150, 0.0025, 0.0032),  # Hyde Park
        (27.9607, -82.4380, 130, 0.0025, 0.0030),  # Ybor City
        (27.9600, -82.4590, 120, 0.0028, 0.0032),  # Tampa Heights
    )
    points: List[Tuple[float, float]] = []
    for center_lat, center_lon, size, lat_spread, lon_spread in clusters:
        points.extend(
            (
                rng.gauss(center_lat, lat_spread),
                rng.gauss(center_lon, lon_spread),
            )
            for _ in range(size)
        )

    # Sparse background activity keeps the map from looking like isolated blobs.
    points.extend(
        (rng.uniform(27.927, 27.970), rng.uniform(-82.490, -82.423)) for _ in range(260)
    )
    return [lat for lat, _ in points], [lon for _, lon in points]


def main() -> None:
    output = Path(__file__).resolve().parents[1] / "docs" / "images"
    output.mkdir(parents=True, exist_ok=True)

    lats, lons = synthetic_tampa_observations()

    heatfall.plot_heat_h3s(
        lats, lons, precision=9, color_scheme="wheel", size=(800, 500), legend=False
    ).save(output / "h3.png")

    heatfall.plot_heat_hashes(
        lats, lons, precision=7, color_scheme="wheel", size=(800, 500), legend=False
    ).save(output / "geohash.png")

    heatfall.plot_heat_h3s(
        lats,
        lons,
        precision=9,
        color_scheme="heatmap",
        legend=heatfall.LegendOptions(columns=3),
        size=(800, 500),
    ).save(output / "h3-legend.png")

    # Keep this compact fixed-count example predictable across grid systems.
    comparison_lats = [27.9470] * 8 + [27.9515] * 4 + [27.9430] * 2 + [27.9475]
    comparison_lons = [-82.4580] * 8 + [-82.4500] * 4 + [-82.4475] * 2 + [-82.4400]
    shared_colors = {
        1: "#deebf7",
        2: "#9ecae1",
        4: "#4292c6",
        8: "#08519c",
    }
    h3_image = heatfall.plot_heat_h3s(
        comparison_lats,
        comparison_lons,
        precision=8,
        count_colors=shared_colors,
        size=(800, 500),
    )
    geohash_image = heatfall.plot_heat_hashes(
        comparison_lats,
        comparison_lons,
        precision=6,
        count_colors=shared_colors,
        size=(800, 500),
    )
    comparison = Image.new("RGBA", (1600, 500), "white")
    comparison.paste(h3_image, (0, 0))
    comparison.paste(geohash_image, (800, 0))
    comparison.save(output / "shared-counts.png")

    context = heatfall.Context()
    context.add_heat_h3s(lats, lons, precision=9, color_scheme="wheel")
    context.set_legend(False)
    context.add_points([27.9470], [-82.4580], colors=["black"], point_size=10)
    context.add_line([(27.9430, -82.4475), (27.9475, -82.4400)], color="black", width=3)
    context.add_circles(
        [27.9515], [-82.4500], [300], color="blue", fill_color="transparent", width=2
    )
    context.render_pillow(800, 500).save(output / "layers.png")
    print("Rendered documentation maps to {}".format(output))


if __name__ == "__main__":
    main()
