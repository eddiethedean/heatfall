"""
Heatmap visualization functions for geographic data.

This module provides functions for creating heatmaps of geographic points
using either geohash binning or H3 hexagonal binning.
"""

from typing import List, Tuple, Any, Optional, cast
from collections import Counter
import math
from PIL import Image, ImageDraw

import staticmaps
import pygeodesy
import h3
from geodude import calculate_geohashes

# Import from landfall
import landfall
from landfall.color import process_colors


_MERCATOR_MAX_LAT = math.degrees(math.atan(math.sinh(math.pi)))


def _clip_longitude(
    ring: List[Tuple[float, float]], longitude: float, keep_east: bool
) -> List[Tuple[float, float]]:
    """Clip an unwrapped H3 ring along a meridian on the sphere."""
    clipped = []
    previous = ring[-1]
    previous_inside = (previous[1] >= longitude) == keep_east
    for current in ring:
        inside = (current[1] >= longitude) == keep_east
        if inside != previous_inside:
            lat1, lon1 = previous
            lat2, lon2 = current
            if abs(lat1) == 90 and lat1 == lat2:
                latitude = lat1  # The artificial closing edge of a polar cap.
            else:
                a = math.radians(lon1 - longitude)
                b = math.radians(lon2 - longitude)
                latitude = math.degrees(
                    math.atan(
                        (
                            math.tan(math.radians(lat1)) * math.sin(b)
                            - math.tan(math.radians(lat2)) * math.sin(a)
                        )
                        / math.sin(b - a)
                    )
                )
            clipped.append((latitude, longitude))
        if inside:
            clipped.append(current)
        previous, previous_inside = current, inside
    return clipped


def _make_h3_polygons(h: str) -> List[List[Any]]:
    """Return closed cell pieces confined to [-180, 180] longitude.

    Unwrap successive vertices before clipping, so the closing edge also takes
    the short path. Intersections follow H3's spherical great-circle edges.
    Cells containing a pole close through that pole rather than across the map.
    """
    boundary = list(h3.cell_to_boundary(h))
    ring = [boundary[0]]
    for lat, lon in boundary[1:] + boundary[:1]:
        previous_lon = ring[-1][1]
        ring.append((lat, previous_lon + (lon - previous_lon + 180) % 360 - 180))
    if abs(ring[-1][1] - ring[0][1]) > 180:
        pole = 90.0 if h3.cell_to_latlng(h)[0] > 0 else -90.0
        ring.extend([(pole, ring[-1][1]), (pole, ring[0][1])])
    else:
        ring.pop()  # Clipping treats the ring as implicitly closed.

    polygons = []
    first = math.floor((min(lon for _, lon in ring) + 180) / 360)
    last = math.floor((max(lon for _, lon in ring) + 180) / 360)
    for world in range(first, last + 1):
        piece = _clip_longitude(ring, -180 + world * 360, True)
        piece = _clip_longitude(piece, 180 + world * 360, False)
        # A ring that merely touches the seam can leave a zero-width fragment.
        if len({lon for _, lon in piece}) < 2:
            continue
        points = [
            staticmaps.create_latlng(lat, lon - world * 360) for lat, lon in piece
        ]
        points.append(points[0])
        polygons.append(points)
    return polygons


class _H3Area(staticmaps.Area):
    """A seam-safe area for every staticmaps rendering backend."""

    _interpolation_cache: Optional[List[Any]]

    def interpolate(self) -> List[Any]:
        # Interpolation can overshoot a meridian by floating-point roundoff.
        # Limit polar caps to the latitude covered by Web Mercator map tiles.
        if self._interpolation_cache is None:
            points = super().interpolate()
            self._interpolation_cache = [
                staticmaps.create_latlng(
                    max(
                        -_MERCATOR_MAX_LAT, min(_MERCATOR_MAX_LAT, point.lat().degrees)
                    ),
                    max(-180.0, min(180.0, point.lng().degrees)),
                )
                for point in points
            ]
        return self._interpolation_cache


class _H3Cell(staticmaps.Object):
    """Render split pieces as one fill so opacity is applied once per cell."""

    def __init__(
        self, polygons: List[List[Any]], fill_color: Any, longitude: float
    ) -> None:
        super().__init__()
        self._parts = [_H3Area(polygon, width=0) for polygon in polygons]
        self._fill_color = fill_color
        self._longitude = longitude

    def fill_color(self) -> Any:
        return self._fill_color

    def bounds(self) -> Any:
        bounds = self._parts[0].bounds()
        for part in self._parts[1:]:
            bounds = bounds.union(part.bounds())
        return bounds

    def extra_pixel_bounds(self) -> Tuple[int, int, int, int]:
        return (0, 0, 0, 0)

    def _project(self, trans: Any) -> List[List[Tuple[float, float]]]:
        # Align both seam pieces with the cell's longitude before rendering.
        # Otherwise world repetition can composite the shared edge twice.
        reference_x, _ = trans.ll2pixel(staticmaps.create_latlng(0, self._longitude))
        polygons = []
        for part in self._parts:
            pixels = [trans.ll2pixel(point) for point in part.interpolate()]
            midpoint = (min(x for x, _ in pixels) + max(x for x, _ in pixels)) / 2
            shift = (
                round((reference_x - midpoint) / trans.world_width())
                * trans.world_width()
            )
            polygons.append([(x + shift, y) for x, y in pixels])
        return polygons

    def pixel_rect(self, trans: Any) -> Tuple[float, float, float, float]:
        # S2 normalizes -180 to +180 in bounds. Use projected vertices and the
        # nearest world copy when staticmaps adjusts the map center.
        pixels = [pixel for polygon in self._project(trans) for pixel in polygon]
        left = min(x for x, _ in pixels)
        right = max(x for x, _ in pixels)
        shift = (
            round((trans.image_width() / 2 - (left + right) / 2) / trans.world_width())
            * trans.world_width()
        )
        return (
            left + shift,
            min(y for _, y in pixels),
            right + shift,
            max(y for _, y in pixels),
        )

    def render_pillow(self, renderer: Any) -> None:
        # staticmaps calls objects for several world offsets. Draw all copies
        # into one overlay on the zero-offset call, including shared cap edges.
        if renderer.offset_x() != 0:
            return
        trans = renderer.transformer()
        world_width = trans.world_width()
        copies = math.ceil(trans.image_width() / (2 * world_width))
        overlay = Image.new("RGBA", renderer.image().size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        for polygon in self._project(trans):
            # Drawing into one overlay replaces shared pixels rather than
            # blending them repeatedly; composite the entire cell once.
            for copy in range(-copies, copies + 1):
                draw.polygon(
                    [(x + copy * world_width, y) for x, y in polygon],
                    fill=self._fill_color.int_rgba(),
                )
        renderer.alpha_compose(overlay)

    def render_svg(self, renderer: Any) -> None:
        contours = [
            "M " + " L ".join(f"{x},{y}" for x, y in polygon) + " Z"
            for polygon in self._project(renderer.transformer())
        ]
        renderer.group().add(
            renderer.drawing().path(
                d=" ".join(contours),
                fill=self._fill_color.hex_rgb(),
                opacity=self._fill_color.float_a(),
            )
        )

    def render_cairo(self, renderer: Any) -> None:
        context = renderer.context()
        context.new_path()
        for polygon in self._project(renderer.transformer()):
            context.move_to(*polygon[0])
            for x, y in polygon[1:]:
                context.line_to(x, y)
            context.close_path()
        context.set_source_rgba(*self._fill_color.float_rgba())
        context.fill()


def _validate_opacity(opacity: float) -> None:
    if not 0 <= opacity <= 1:
        raise ValueError("opacity must be between 0 and 1")


def _with_opacity(color: Any, opacity: float) -> Any:
    """Copy a palette color, preserving any existing transparency."""
    red, green, blue, alpha = color.int_rgba()
    return staticmaps.Color(red, green, blue, round(alpha * opacity))


def _validate_coordinates(lats: List[float], lons: List[float]) -> None:
    """Reject mismatched lists and coordinates outside geographic bounds."""
    if len(lats) != len(lons):
        raise ValueError(
            f"lats and lons must have same length (got {len(lats)} and {len(lons)})"
        )
    if not all(-90 <= lat <= 90 for lat in lats):
        raise ValueError("All latitudes must be between -90 and 90")
    if not all(-180 <= lon <= 180 for lon in lons):
        raise ValueError("All longitudes must be between -180 and 180")


class Context(landfall.Context):
    """Extended Context with heatmap-specific methods."""

    def add_heat_hashes(
        self,
        lats: List[float],
        lons: List[float],
        precision: int,
        color_scheme: str = "distinct",
        *,
        opacity: float = 0.6,
    ) -> None:
        """
        Add geohash-based heatmap to the map.

        Args:
            lats: List of latitude values
            lons: List of longitude values
            precision: Geohash precision (1-12)
            color_scheme: Color scheme ("distinct", "random", "wheel")
            opacity: Fill opacity from 0 (invisible) to 1 (solid), default 0.6
        """
        _validate_coordinates(lats, lons)
        _validate_opacity(opacity)
        hashes = calculate_geohashes(lats, lons, precision)
        counts = Counter(hashes)

        # Use landfall's color system instead of custom density_colors
        unique_counts = sorted(set(counts.values()))
        colors_list = process_colors(color_scheme, len(unique_counts))

        # Map counts to colors
        count_to_color = {
            count: _with_opacity(color, opacity)
            for count, color in zip(unique_counts, colors_list)
        }

        for h, count in counts.items():
            color = count_to_color[count]
            self.add_object(
                staticmaps.Area(
                    make_hash_poly_points(h),
                    fill_color=color,
                    width=0,
                    color=staticmaps.TRANSPARENT,
                )
            )

    def add_heat_h3s(
        self,
        lats: List[float],
        lons: List[float],
        precision: int,
        color_scheme: str = "distinct",
        *,
        opacity: float = 0.6,
    ) -> None:
        """
        Add H3-based heatmap to the map.

        Args:
            lats: List of latitude values
            lons: List of longitude values
            precision: H3 resolution (0-15)
            color_scheme: Color scheme ("distinct", "random", "wheel")
            opacity: Fill opacity from 0 (invisible) to 1 (solid), default 0.6
        """
        _validate_opacity(opacity)
        hashes = calculate_h3_hashes(lats, lons, precision)
        counts = Counter(hashes)

        # Use landfall's color system
        unique_counts = sorted(set(counts.values()))
        colors_list = process_colors(color_scheme, len(unique_counts))

        # Map counts to colors
        count_to_color = {
            count: _with_opacity(color, opacity)
            for count, color in zip(unique_counts, colors_list)
        }

        for h, count in counts.items():
            self.add_object(
                _H3Cell(
                    _make_h3_polygons(h),
                    count_to_color[count],
                    h3.cell_to_latlng(h)[1],
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
    *,
    opacity: float = 0.6,
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
        opacity: Fill opacity from 0 (invisible) to 1 (solid), default 0.6

    Returns:
        PIL Image object containing the rendered heatmap

    Raises:
        ValueError: If coordinates, precision, or opacity are invalid

    Example:
        >>> import heatfall
        >>> lats = [27.88, 27.92, 27.94]
        >>> lons = [-82.49, -82.49, -82.46]
        >>> img = heatfall.plot_heat_hashes(lats, lons, precision=4)
        >>> img.save("heatmap.png")
    """
    # Validate inputs
    _validate_coordinates(lats, lons)

    if len(lats) == 0:
        raise ValueError("lats and lons cannot be empty")

    if not (1 <= precision <= 12):
        raise ValueError(f"Geohash precision must be 1-12 (got {precision})")

    # Create context and add heatmap
    context = Context()
    context.set_tile_provider(tileprovider)
    context.add_heat_hashes(lats, lons, precision, color_scheme, opacity=opacity)
    return cast(Image.Image, context.render_pillow(*size))


def plot_heat_h3s(
    lats: List[float],
    lons: List[float],
    precision: int,
    color_scheme: str = "distinct",
    tileprovider: staticmaps.TileProvider = tp,
    size: Tuple[int, int] = (800, 500),
    *,
    opacity: float = 0.6,
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
        opacity: Fill opacity from 0 (invisible) to 1 (solid), default 0.6

    Returns:
        PIL Image object containing the rendered heatmap

    Raises:
        ValueError: If coordinates, precision, or opacity are invalid

    Example:
        >>> import heatfall
        >>> lats = [27.88, 27.92, 27.94]
        >>> lons = [-82.49, -82.49, -82.46]
        >>> img = heatfall.plot_heat_h3s(lats, lons, precision=8)
        >>> img.save("h3_heatmap.png")
    """
    # Validate inputs
    _validate_coordinates(lats, lons)

    if len(lats) == 0:
        raise ValueError("lats and lons cannot be empty")

    if not (0 <= precision <= 15):
        raise ValueError(f"H3 precision must be 0-15 (got {precision})")

    # Create context and add heatmap
    context = Context()
    context.set_tile_provider(tileprovider)
    context.add_heat_h3s(lats, lons, precision, color_scheme, opacity=opacity)
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
    return [staticmaps.create_latlng(lat, lon) for lat, lon in points]


def calculate_h3_hashes(
    latitudes: List[float], longitudes: List[float], precision: int
) -> List[str]:
    """Calculate H3 cell identifiers for given coordinates."""
    _validate_coordinates(latitudes, longitudes)
    if not (0 <= precision <= 15):
        raise ValueError(f"H3 precision must be 0-15 (got {precision})")

    return [
        h3.latlng_to_cell(lat, lon, precision)
        for lat, lon in zip(latitudes, longitudes)
    ]
