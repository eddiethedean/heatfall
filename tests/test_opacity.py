"""Heat fill defaults, overrides, and compositing across the antimeridian."""

from types import SimpleNamespace
from unittest.mock import MagicMock
import xml.etree.ElementTree as ET

import pytest
import staticmaps

import heatfall


@pytest.mark.parametrize("method", ["add_heat_hashes", "add_heat_h3s"])
@pytest.mark.parametrize("opacity,alpha", [(0, 0), (0.25, 64), (0.6, 153), (1, 255)])
def test_context_opacity_overrides(monkeypatch, method, opacity, alpha):
    source = staticmaps.Color(20, 40, 60)
    monkeypatch.setattr("heatfall.heat.process_colors", lambda scheme, n: [source] * n)
    context = heatfall.Context()
    getattr(context, method)(
        [27.947], [-82.458], precision=6, color_scheme="distinct", opacity=opacity
    )
    assert len(context._objects) == 1
    assert context._objects[0].fill_color().int_rgba() == (20, 40, 60, alpha)
    assert source.int_rgba() == (20, 40, 60, 255)


@pytest.mark.parametrize("method", ["add_heat_hashes", "add_heat_h3s"])
def test_default_is_sixty_percent_opaque(monkeypatch, method):
    monkeypatch.setattr(
        "heatfall.heat.process_colors", lambda scheme, n: [staticmaps.RED] * n
    )
    context = heatfall.Context()
    getattr(context, method)([27.947], [-82.458], precision=6, color_scheme="distinct")
    assert context._objects[0].fill_color().int_rgba() == (255, 0, 0, 153)


@pytest.mark.parametrize("method", ["add_heat_hashes", "add_heat_h3s"])
def test_existing_palette_alpha_is_preserved(monkeypatch, method):
    color = staticmaps.Color(20, 40, 60, 128)
    monkeypatch.setattr("heatfall.heat.process_colors", lambda scheme, n: [color] * n)
    context = heatfall.Context()
    getattr(context, method)(
        [27.947], [-82.458], precision=6, color_scheme="distinct", opacity=0.5
    )
    assert context._objects[0].fill_color().int_rgba() == (20, 40, 60, 64)
    assert color.int_rgba() == (20, 40, 60, 128)


@pytest.mark.parametrize("method", ["add_heat_hashes", "add_heat_h3s"])
@pytest.mark.parametrize(
    "opacity", [-0.1, 1.1, float("nan"), float("inf"), -float("inf")]
)
def test_context_rejects_invalid_opacity(method, opacity):
    context = heatfall.Context()
    with pytest.raises(ValueError, match="opacity must be between 0 and 1"):
        getattr(context, method)([27.947], [-82.458], precision=6, opacity=opacity)
    assert not context._objects


@pytest.mark.parametrize("plot", [heatfall.plot_heat_hashes, heatfall.plot_heat_h3s])
def test_plot_rejects_invalid_opacity(plot):
    with pytest.raises(ValueError, match="opacity must be between 0 and 1"):
        plot([27.947], [-82.458], precision=6, opacity=1.1)


@pytest.mark.parametrize("plot", [heatfall.plot_heat_hashes, heatfall.plot_heat_h3s])
@pytest.mark.parametrize(
    "opacity,pixel", [(0, (0, 0, 0, 0)), (0.6, (255, 0, 0, 153)), (1, (255, 0, 0, 255))]
)
def test_plot_forwards_opacity_and_keeps_positional_arguments(
    monkeypatch, plot, opacity, pixel
):
    monkeypatch.setattr(
        "heatfall.heat.process_colors", lambda scheme, n: [staticmaps.RED] * n
    )
    # The six existing positional arguments remain valid; opacity is keyword-only.
    image = plot(
        [27.947],
        [-82.458],
        6,
        "wheel",
        staticmaps.tile_provider_None,
        (200, 200),
        opacity=opacity,
        legend=False,
    )
    assert image.size == (200, 200)
    assert image.getpixel((100, 100)) == pixel


@pytest.mark.parametrize("center", [None, 0, 180, -180])
def test_transparent_cell_has_uniform_alpha_at_seam(monkeypatch, center):
    monkeypatch.setattr(
        "heatfall.heat.process_colors", lambda scheme, n: [staticmaps.RED] * n
    )
    context = heatfall.Context()
    context.set_tile_provider(staticmaps.tile_provider_None)
    context.set_background_color(staticmaps.BLACK)
    context.add_heat_h3s([0, 0], [180, -180], precision=5, color_scheme="distinct")
    context.set_legend(False)
    if center is not None:
        context.set_center(staticmaps.create_latlng(0, center))
        context.set_zoom(5)
    image = context.render_pillow(8192 if center == 0 else 800, 500)
    reds = {r for r, g, b, a in image.getdata()}
    assert reds == {0, 153}  # No seam pixels darkened by a second alpha blend.


def test_svg_uses_one_opacity_for_both_pieces(monkeypatch):
    monkeypatch.setattr(
        "heatfall.heat.process_colors", lambda scheme, n: [staticmaps.RED] * n
    )
    context = heatfall.Context()
    context.set_tile_provider(staticmaps.tile_provider_None)
    context.add_heat_h3s([0], [180], precision=5, color_scheme="distinct")
    context.set_legend(False)
    svg = ET.fromstring(context.render_svg(800, 500).tostring())
    paths = svg.findall(".//{http://www.w3.org/2000/svg}path")
    assert len(paths) == 3
    assert all(path.attrib["opacity"] == "0.6" for path in paths)
    assert all(path.attrib["d"].count("M") == 2 for path in paths)


def test_cairo_fills_both_pieces_once(monkeypatch):
    monkeypatch.setattr(
        "heatfall.heat.process_colors", lambda scheme, n: [staticmaps.RED] * n
    )
    context = heatfall.Context()
    context.add_heat_h3s([0], [180], precision=5, color_scheme="distinct")
    center, zoom = context.determine_center_zoom(800, 500)
    trans = staticmaps.Transformer(800, 500, zoom, center, 256)
    canvas = MagicMock()
    renderer = SimpleNamespace(context=lambda: canvas, transformer=lambda: trans)
    context._objects[0].render_cairo(renderer)
    canvas.new_path.assert_called_once_with()
    assert canvas.move_to.call_count == canvas.close_path.call_count == 2
    canvas.set_source_rgba.assert_called_once_with(1.0, 0.0, 0.0, 0.6)
    canvas.fill.assert_called_once_with()


@pytest.mark.parametrize("latitude", [-90, 90])
@pytest.mark.parametrize("resolution", [0, 1, 8])
def test_repeated_world_copies_do_not_darken_polar_cap_edges(
    monkeypatch, latitude, resolution
):
    monkeypatch.setattr(
        "heatfall.heat.process_colors", lambda scheme, n: [staticmaps.RED] * n
    )
    context = heatfall.Context()
    context.set_tile_provider(staticmaps.tile_provider_None)
    context.set_background_color(staticmaps.BLACK)
    context.add_heat_h3s([latitude], [180], resolution, color_scheme="distinct")
    context.set_legend(False)
    image = context.render_pillow(800, 500)
    assert {r for r, g, b, a in image.getdata()} == {0, 153}
