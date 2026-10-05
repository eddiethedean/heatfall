"""Regression tests for H3 boundaries and map extents at ±180° longitude."""

import math
import re
import xml.etree.ElementTree as ET

import h3
import pytest
import s2sphere
import staticmaps

from heatfall import Context, plot_heat_h3s
from heatfall.heat import _clip_longitude, _make_h3_polygons


def spherical_area(points):
    """Sum signed spherical triangles, including concave polar-cap pieces."""
    vertices = [point.to_point() for point in points]
    return abs(
        sum(
            math.copysign(
                s2sphere.area(vertices[0], a, b),
                vertices[0].dot_prod(a.cross_prod(b)),
            )
            for a, b in zip(vertices[1:-1], vertices[2:])
        )
    )


@pytest.mark.parametrize("latitude", [0, 45, -45, 80])
@pytest.mark.parametrize("longitude", [-180, 180])
@pytest.mark.parametrize("resolution", [0, 1, 3, 8, 15])
def test_split_preserves_cell_area(latitude, longitude, resolution):
    cell = h3.latlng_to_cell(latitude, longitude, resolution)
    original = [staticmaps.create_latlng(*p) for p in h3.cell_to_boundary(cell)]
    pieces = _make_h3_polygons(cell)
    assert len(pieces) == 2
    for piece in pieces:
        assert piece[0] == piece[-1]
        assert len(set((p.lat().degrees, p.lng().degrees) for p in piece)) >= 3
        longitudes = [p.lng().degrees for p in piece]
        assert all(-180 <= lon <= 180 for lon in longitudes)
        assert max(longitudes) - min(longitudes) < 180
    assert sum(spherical_area(p) for p in pieces) == pytest.approx(
        spherical_area(original), rel=1e-6, abs=1e-22
    )


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("rotation", range(4))
def test_splitting_includes_closing_edge(monkeypatch, reverse, rotation):
    ring = [(10, 179), (11, 179), (11, -179), (10, -179)]
    ring = ring[rotation:] + ring[:rotation]
    if reverse:
        ring.reverse()
    monkeypatch.setattr(h3, "cell_to_boundary", lambda _: ring)
    pieces = _make_h3_polygons("synthetic")
    assert len(pieces) == 2
    assert all(piece[0] == piece[-1] for piece in pieces)
    assert sum(spherical_area(p) for p in pieces) == pytest.approx(
        spherical_area([staticmaps.create_latlng(*p) for p in ring]), rel=1e-10
    )


@pytest.mark.parametrize("sign", [-1, 1])
def test_ring_touching_seam_has_no_degenerate_fragment(monkeypatch, sign):
    ring = [(0, sign * 179), (1, sign * 179), (1, sign * 180), (0, sign * 180)]
    monkeypatch.setattr(h3, "cell_to_boundary", lambda _: ring)
    pieces = _make_h3_polygons("synthetic")
    assert len(pieces) == 1
    assert pieces[0][0] == pieces[0][-1]
    assert spherical_area(pieces[0]) > 0


def test_intersection_follows_great_circle():
    # At high latitudes the true edge crosses north of a straight lon/lat edge.
    clipped = _clip_longitude([(70, 170), (70, 190), (60, 190), (60, 170)], 180, True)
    expected = math.degrees(
        math.atan(math.tan(math.radians(70)) / math.cos(math.radians(10)))
    )
    crossings = [lat for lat, lon in clipped if lon == 180]
    assert max(crossings) == pytest.approx(expected)
    assert max(crossings) > 70


def red_context(monkeypatch):
    monkeypatch.setattr(
        "heatfall.heat.process_colors", lambda scheme, n: [staticmaps.RED] * n
    )
    context = Context()
    context.set_tile_provider(staticmaps.tile_provider_None)
    context.set_background_color(staticmaps.BLACK)
    return context


def test_split_pieces_keep_original_observation_count(monkeypatch):
    monkeypatch.setattr(
        "heatfall.heat.process_colors",
        lambda scheme, n: [staticmaps.BLUE, staticmaps.RED],
    )
    context = Context()
    context.add_heat_h3s(
        [0, 0, 35.68], [180, -180, 139.69], precision=5, color_scheme="distinct"
    )
    assert len(context._objects) == 2
    assert len(context._objects[0]._parts) == 2
    assert [obj.fill_color().int_rgba() for obj in context._objects] == [
        (255, 0, 0, 153),
        (0, 0, 255, 153),
    ]


@pytest.mark.parametrize("longitudes", [[179.999, -179.999], [179.5, -179.5]])
@pytest.mark.parametrize("size", [(200, 200), (800, 500), (1200, 400)])
@pytest.mark.parametrize("resolution", [0, 5, 8])
def test_automatic_center_stays_at_dateline(monkeypatch, size, resolution, longitudes):
    context = red_context(monkeypatch)
    context.add_heat_h3s([0, 0], longitudes, resolution, color_scheme="distinct")
    center, zoom = context.determine_center_zoom(*size)
    assert abs(center.lng().degrees) > 170
    assert zoom >= 3
    assert context.render_pillow(*size).size == size


def test_seam_has_no_gap_or_world_spanning_fill(monkeypatch):
    context = red_context(monkeypatch)
    context.add_heat_h3s(
        [0, 0], [180, -180], precision=5, color_scheme="distinct", opacity=1
    )
    image = context.render_pillow(800, 500)
    filled = [
        (x, y)
        for y in range(500)
        for x in range(800)
        if image.getpixel((x, y))[:3] == (255, 0, 0)
    ]
    assert 10000 < len(filled) < 800 * 500 * 0.8
    assert min(x for x, _ in filled) > 0
    assert max(x for x, _ in filled) < 799
    row = [x for x in range(800) if image.getpixel((x, 250))[:3] == (255, 0, 0)]
    assert row == list(range(min(row), max(row) + 1))


def test_fixed_world_view_fills_only_dateline_edges(monkeypatch):
    context = red_context(monkeypatch)
    context.add_heat_h3s([0], [180], precision=2, color_scheme="distinct", opacity=1)
    context.set_center(staticmaps.create_latlng(0, 0))
    context.set_zoom(2)
    image = context.render_pillow(1024, 300)
    row = [x for x in range(1024) if image.getpixel((x, 150))[:3] == (255, 0, 0)]
    assert 0 in row and 1023 in row
    assert all(x < 100 or x > 924 for x in row)


def test_svg_pieces_do_not_span_the_world(monkeypatch):
    context = red_context(monkeypatch)
    context.add_heat_h3s([0], [180], precision=5, color_scheme="distinct")
    center, zoom = context.determine_center_zoom(800, 500)
    world_width = 256 * 2**zoom
    svg = ET.fromstring(context.render_svg(800, 500).tostring())
    paths = svg.findall(".//{http://www.w3.org/2000/svg}path")
    assert len(paths) == 3  # One compound path in each world copy.
    for path in paths:
        assert path.attrib["d"].count("M") == 2
        xs = [
            float(pair.split(",")[0])
            for pair in re.findall(r"[-\d.e]+,[-\d.e]+", path.attrib["d"])
        ]
        assert max(xs) - min(xs) < world_width / 100
    assert abs(center.lng().degrees) > 179


@pytest.mark.parametrize("latitude", [-90, 90])
@pytest.mark.parametrize("resolution", [0, 1, 3, 8, 15])
def test_polar_cells_render_without_invalid_mercator_coordinates(latitude, resolution):
    cell = h3.latlng_to_cell(latitude, 180, resolution)
    original = [staticmaps.create_latlng(*p) for p in h3.cell_to_boundary(cell)]
    assert sum(spherical_area(p) for p in _make_h3_polygons(cell)) == pytest.approx(
        spherical_area(original), rel=1e-6, abs=1e-22
    )
    context = Context()
    context.set_tile_provider(staticmaps.tile_provider_None)
    context.add_heat_h3s([latitude], [180], resolution, color_scheme="distinct")
    for obj in context._objects:
        for part in obj._parts:
            assert all(
                abs(point.lat().degrees) <= 85.051129 for point in part.interpolate()
            )
    assert context.render_pillow(400, 300).size == (400, 300)


def test_all_base_cells_preserve_area():
    """Include pentagons, face-crossing cells, and both polar caps."""
    for cell in h3.get_res0_cells():
        original = [staticmaps.create_latlng(*p) for p in h3.cell_to_boundary(cell)]
        assert sum(spherical_area(p) for p in _make_h3_polygons(cell)) == pytest.approx(
            spherical_area(original), rel=1e-10
        ), cell


def test_public_plot_accepts_points_on_both_sides():
    image = plot_heat_h3s(
        [10, 10],
        [179.5, -179.5],
        precision=3,
        tileprovider=staticmaps.tile_provider_None,
    )
    assert image.size == (800, 500)
