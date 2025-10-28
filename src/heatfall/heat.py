"""
Heatmap visualization functions for geographic data.

This module provides functions for creating heatmaps of geographic points
using either geohash binning or H3 hexagonal binning.
"""

from typing import List, Tuple, Any, cast
from collections import Counter
from PIL import Image

import staticmaps
import pygeodesy
import h3
from geodude import calculate_geohashes

# Import from landfall
import landfall
from landfall.color import process_colors


class Context(landfall.Context):
    """Extended Context with heatmap-specific methods."""

    def add_heat_hashes(
        self,
        lats: List[float],
        lons: List[float],
        precision: int,
        color_scheme: str = "distinct",
    ) -> None:
        """
        Add geohash-based heatmap to the map.

        Args:
            lats: List of latitude values
            lons: List of longitude values
            precision: Geohash precision (1-12)
            color_scheme: Color scheme ("distinct", "random", "wheel")
        """
        hashes = calculate_geohashes(lats, lons, precision)
        counts = Counter(hashes)

        # Use landfall's color system instead of custom density_colors
        unique_counts = sorted(set(counts.values()))
        colors_list = process_colors(color_scheme, len(unique_counts))

        # Map counts to colors
        count_to_color = dict(zip(unique_counts, colors_list))

        for h, count in counts.items():
            color = count_to_color[count]
            self.add_object(
                staticmaps.Area(
                    make_hash_poly_points(h),
                    fill_color=color,
                    width=1,
                    color=staticmaps.TRANSPARENT,
                )
            )

    def add_heat_h3s(
        self,
        lats: List[float],
        lons: List[float],
        precision: int,
        color_scheme: str = "distinct",
    ) -> None:
        """
        Add H3-based heatmap to the map.

        Args:
            lats: List of latitude values
            lons: List of longitude values
            precision: H3 resolution (0-15)
            color_scheme: Color scheme ("distinct", "random", "wheel")
        """
        hashes = calculate_h3_hashes(lats, lons, precision)
        counts = Counter(hashes)

        # Use landfall's color system
        unique_counts = sorted(set(counts.values()))
        colors_list = process_colors(color_scheme, len(unique_counts))

        # Map counts to colors
        count_to_color = dict(zip(unique_counts, colors_list))

        for h, count in counts.items():
            color = count_to_color[count]
            self.add_object(
                staticmaps.Area(
                    make_h3_poly_points(h),
                    fill_color=color,
                    width=1,
                    color=staticmaps.TRANSPARENT,
                )
            )


tp = staticmaps.tile_provider_OSM


def plot_heat_hashes(
    lats: List[float],
    lons: List[float],
    precision: int,
    color_scheme: str = "distinct",
    tileprovider: staticmaps.TileProvider = tp,
    size: Tuple[int, int] = (800, 500),
) -> Image.Image:
    """
    Plot a heatmap of geographic points using geohash binning.

    Creates a static map with colored polygons representing point density
    in each geohash cell.

    Args:
        lats: List of latitude values (decimal degrees, -90 to 90)
        lons: List of longitude values (decimal degrees, -180 to 180)
        precision: Geohash precision level (1-12, higher = smaller cells)
        color_scheme: Color scheme - "distinct" (default), "random", or "wheel"
        tileprovider: Tile provider for the base map (default: OpenStreetMap)
        size: Output image size in pixels as (width, height)

    Returns:
        PIL Image object containing the rendered heatmap

    Raises:
        ValueError: If lats/lons lengths don't match or precision is invalid

    Example:
        >>> import heatfall
        >>> lats = [27.88, 27.92, 27.94]
        >>> lons = [-82.49, -82.49, -82.46]
        >>> img = heatfall.plot_heat_hashes(lats, lons, precision=4)
        >>> img.save("heatmap.png")
    """
    # Validate inputs
    if len(lats) != len(lons):
        raise ValueError(
            f"lats and lons must have same length (got {len(lats)} and {len(lons)})"
        )

    if len(lats) == 0:
        raise ValueError("lats and lons cannot be empty")

    if not (1 <= precision <= 12):
        raise ValueError(f"Geohash precision must be 1-12 (got {precision})")

    if not all(-90 <= lat <= 90 for lat in lats):
        raise ValueError("All latitudes must be between -90 and 90")

    if not all(-180 <= lon <= 180 for lon in lons):
        raise ValueError("All longitudes must be between -180 and 180")

    # Create context and add heatmap
    context = Context()
    context.set_tile_provider(tileprovider)
    context.add_heat_hashes(lats, lons, precision, color_scheme)
    return cast(Image.Image, context.render_pillow(*size))


def plot_heat_h3s(
    lats: List[float],
    lons: List[float],
    precision: int,
    color_scheme: str = "distinct",
    tileprovider: staticmaps.TileProvider = tp,
    size: Tuple[int, int] = (800, 500),
) -> Image.Image:
    """
    Plot a heatmap of geographic points using H3 hexagonal binning.

    Creates a static map with colored hexagonal polygons representing
    point density in each H3 cell.

    Args:
        lats: List of latitude values (decimal degrees, -90 to 90)
        lons: List of longitude values (decimal degrees, -180 to 180)
        precision: H3 resolution level (0-15, higher = smaller cells)
        color_scheme: Color scheme - "distinct" (default), "random", or "wheel"
        tileprovider: Tile provider for the base map (default: OpenStreetMap)
        size: Output image size in pixels as (width, height)

    Returns:
        PIL Image object containing the rendered heatmap

    Raises:
        ValueError: If lats/lons lengths don't match or precision is invalid

    Example:
        >>> import heatfall
        >>> lats = [27.88, 27.92, 27.94]
        >>> lons = [-82.49, -82.49, -82.46]
        >>> img = heatfall.plot_heat_h3s(lats, lons, precision=8)
        >>> img.save("h3_heatmap.png")
    """
    # Validate inputs
    if len(lats) != len(lons):
        raise ValueError(
            f"lats and lons must have same length (got {len(lats)} and {len(lons)})"
        )

    if len(lats) == 0:
        raise ValueError("lats and lons cannot be empty")

    if not (0 <= precision <= 15):
        raise ValueError(f"H3 precision must be 0-15 (got {precision})")

    if not all(-90 <= lat <= 90 for lat in lats):
        raise ValueError("All latitudes must be between -90 and 90")

    if not all(-180 <= lon <= 180 for lon in lons):
        raise ValueError("All longitudes must be between -180 and 180")

    # Create context and add heatmap
    context = Context()
    context.set_tile_provider(tileprovider)
    context.add_heat_h3s(lats, lons, precision, color_scheme)
    return cast(Image.Image, context.render_pillow(*size))


# Keep helper functions for geohash/H3 polygon generation
def make_hash_poly_points(h: str) -> List[Any]:
    """Convert geohash string to polygon points for rendering."""
    b = pygeodesy.geohash.bounds(h)
    sw = b.latS, b.lonW
    nw = b.latN, b.lonW
    ne = b.latN, b.lonE
    se = b.latS, b.lonE
    polygon = [sw, nw, ne, se, sw]
    return [staticmaps.create_latlng(lat, lon) for lat, lon in polygon]


def make_h3_poly_points(h: str) -> List[Any]:
    """Convert H3 cell string to polygon points for rendering."""
    points = list(h3.cell_to_boundary(h))
    return [staticmaps.create_latlng(lat, lon) for lon, lat in points]


def calculate_h3_hashes(
    latitudes: List[float], longitudes: List[float], precision: int
) -> List[str]:
    """Calculate H3 cell identifiers for given coordinates."""
    if len(latitudes) != len(longitudes):
        raise ValueError(
            f"latitudes and longitudes must have same length "
            f"(got {len(latitudes)} and {len(longitudes)})"
        )

    return [
        h3.latlng_to_cell(lat, lon, precision)
        for lat, lon in zip(latitudes, longitudes)
    ]
