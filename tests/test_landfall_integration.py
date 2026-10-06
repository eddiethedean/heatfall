"""Compose real Landfall shapes with heat cells and legends, without map tiles."""

from io import BytesIO
import xml.etree.ElementTree as ET

import landfall
import pytest
import staticmaps
from geographiclib.geodesic import Geodesic
from PIL import Image

import heatfall
from tests.mock_tile_downloader import MockTileDownloader


@pytest.fixture
def heat_context():
    context = heatfall.Context()
    context.set_tile_provider(staticmaps.tile_provider_None)
    context.set_background_color(staticmaps.Color(20, 35, 50))
    context.set_center(staticmaps.create_latlng(27.9470, -82.4580))
    context.set_zoom(13)
    context.add_heat_h3s([27.9470], [-82.4580], 7)
    return context


@pytest.mark.parametrize("plot", [heatfall.plot_heat_hashes, heatfall.plot_heat_h3s])
@pytest.mark.parametrize("api_key", [None, "example-token"])
def test_plotting_wrappers_forward_tile_api_keys_without_network(
    monkeypatch, plot, api_key
):
    provider = staticmaps.TileProvider(
        "Example", "https://example.test/$z/$x/$y?key=$k", api_key="provider-default"
    )
    urls = []

    def record_tile(self, provider, cache_dir, zoom, x, y):
        urls.append(provider.url(zoom, x, y))
        return None

    monkeypatch.setattr(MockTileDownloader, "get", record_tile)
    image = plot([27.9470], [-82.4580], 8, tileprovider=provider, api_key=api_key)
    assert image.size == (800, 500)
    assert urls
    expected_key = api_key or "provider-default"
    assert all(url.endswith("?key=" + expected_key) for url in urls)


@pytest.mark.parametrize("method", ["add_heat_hashes", "add_heat_h3s"])
def test_heat_layers_use_the_public_object_hook(method):
    class TrackingContext(heatfall.Context):
        def __init__(self):
            super().__init__()
            self.added = []

        def add_object(self, obj):
            self.added.append(obj)
            super().add_object(obj)

    context = TrackingContext()
    getattr(context, method)([27.9470, 27.9515], [-82.4580, -82.4500], 8)
    assert len(context.added) == 2
    assert context.added == context._objects
    assert context.heat_layers[0].cell_count == 2


def test_inherited_shape_fixes_preserve_coordinates_and_circle_units(heat_context):
    context = heat_context
    metadata = context.heat_layers
    context.add_points([(27.9470, -82.4580), (27.9515, -82.4500)], colors=["black"])
    context.add_lines(
        [[(-82.4580, 27.9470), (-82.4500, 27.9515)]],
        colors=["blue"],
        flip_coords=True,
    )
    context.add_circle(27.9470, -82.4580, 1000, color="red", radius_unit="meters")
    assert len(context._objects) == 5
    for obj in context._objects[1:3]:
        assert obj.color().int_rgba()[:3] == (0, 0, 0)
    line = context._objects[3]
    assert line.interpolate()[0].lat().degrees == pytest.approx(27.9470)
    assert line.interpolate()[0].lng().degrees == pytest.approx(-82.4580)
    circle = context._objects[4]
    boundary = circle.interpolate()[0]
    distance = Geodesic.WGS84.Inverse(
        27.9470, -82.4580, boundary.lat().degrees, boundary.lng().degrees
    )["s12"]
    assert distance == pytest.approx(1000)
    assert context.heat_layers == metadata
    assert context.render_pillow(800, 500).size == (800, 500)


def test_polygon_hole_keeps_the_heat_underneath_and_svg_legend(heat_context):
    context = heat_context
    baseline = context.render_pillow(800, 500)
    context.add_polygon(
        [(27.91, -82.50), (27.98, -82.50), (27.98, -82.42), (27.91, -82.42)],
        holes=[[(27.94, -82.47), (27.96, -82.47), (27.96, -82.44), (27.94, -82.44)]],
        fill_color="blue",
        color="transparent",
        width=0,
    )
    image = context.render_pillow(800, 500)
    assert image.getpixel((400, 250)) == baseline.getpixel((400, 250))
    assert image.getpixel((400, 250)) != (20, 35, 50, 255)
    assert image.tobytes() != baseline.tobytes()
    svg = ET.fromstring(context.render_svg(800, 500).tostring())
    assert any(
        path.get("fill-rule") == "evenodd"
        for path in svg.iter("{http://www.w3.org/2000/svg}path")
    )
    labels = " ".join(svg.itertext())
    assert heatfall.LegendOptions().title in labels
    assert context.heat_layers[0].observation_count == 1


def test_geojson_geometry_collection_retains_all_parts_and_heat_legend(heat_context):
    data = {
        "type": "GeometryCollection",
        "geometries": [
            {
                "type": "MultiPoint",
                "coordinates": [[-82.4580, 27.9470, 12], [-82.4500, 27.9515, 18]],
            },
            {
                "type": "LineString",
                "coordinates": [[-82.4580, 27.9470], [-82.4500, 27.9515]],
            },
        ],
    }
    metadata = heat_context.heat_layers
    image = landfall.plot_geojson(
        data,
        context=heat_context,
        tile_provider=staticmaps.tile_provider_None,
        window_size=(800, 500),
    )
    assert image.size == (800, 500)
    assert len(heat_context._objects) == 4
    assert heat_context.heat_layers == metadata
    svg = ET.fromstring(heat_context.render_svg(800, 500).tostring())
    assert heatfall.LegendOptions().title in " ".join(svg.itertext())


@pytest.mark.skipif(not staticmaps.cairo_is_supported(), reason="Cairo is optional")
def test_native_cairo_preserves_polygon_holes_heat_and_legend(heat_context):
    def render():
        output = BytesIO()
        heat_context.render_cairo(800, 500).write_to_png(output)
        output.seek(0)
        with Image.open(output) as image:
            return image.convert("RGBA")

    metadata = heat_context.heat_layers
    baseline = render()
    heat_context.add_polygon(
        [(27.91, -82.50), (27.98, -82.50), (27.98, -82.42), (27.91, -82.42)],
        holes=[[(27.94, -82.47), (27.96, -82.47), (27.96, -82.44), (27.94, -82.44)]],
        fill_color="blue",
        color="transparent",
        width=0,
    )
    image = render()
    assert image.size == (800, 500)
    assert image.getpixel((400, 250)) == baseline.getpixel((400, 250))
    assert image.getpixel((400, 250)) != (20, 35, 50, 255)
    assert image.tobytes() != baseline.tobytes()
    heat_context.set_legend(False)
    plain = render()
    assert (
        image.crop((600, 0, 800, 150)).tobytes()
        != plain.crop((600, 0, 800, 150)).tobytes()
    )
    assert heat_context.heat_layers == metadata


def test_geodataframe_reprojects_nondefault_geometry_and_keeps_row_styles(heat_context):
    gpd = pytest.importorskip("geopandas")
    geometry = pytest.importorskip("shapely.geometry")
    frame = (
        gpd.GeoDataFrame(
            {"color": ["black", "red"]},
            geometry=[
                geometry.Point(-82.4580, 27.9470),
                geometry.Point(-82.4500, 27.9515),
            ],
            crs="EPSG:4326",
            index=[10, 30],
        )
        .rename_geometry("location")
        .to_crs("EPSG:3857")
    )
    metadata = heat_context.heat_layers
    image = landfall.plot_geodataframe(
        frame,
        context=heat_context,
        color_column="color",
        tile_provider=staticmaps.tile_provider_None,
        window_size=(800, 500),
    )
    assert image.size == (800, 500)
    assert len(heat_context._objects) == 3
    for point, lat, lon, color in zip(
        heat_context._objects[1:],
        [27.9470, 27.9515],
        [-82.4580, -82.4500],
        [(0, 0, 0), (255, 0, 0)],
    ):
        assert point.latlng().lat().degrees == pytest.approx(lat)
        assert point.latlng().lng().degrees == pytest.approx(lon)
        assert point.color().int_rgba()[:3] == color
    assert heat_context.heat_layers == metadata
