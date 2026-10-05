"""Legends, layer metadata, and reproducible count colors."""

from dataclasses import FrozenInstanceError
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock
import sys
import xml.etree.ElementTree as ET

import pytest
import staticmaps

import heatfall
from heatfall.heat import _draw_pillow_legend
from heatfall.legend import (
    _font,
    draw_cairo_legend,
    draw_svg_legend,
    legend_colors,
    layout_legend,
    validate_legend_options,
)


@pytest.mark.parametrize(
    "method,grid,precision",
    [("add_heat_hashes", "geohash", 5), ("add_heat_h3s", "h3", 8)],
)
def test_layer_metadata_is_immutable_and_matches_fills(method, grid, precision):
    context = heatfall.Context()
    getattr(context, method)(
        [27.947, 27.947, 27.951],
        [-82.458, -82.458, -82.450],
        precision,
        legend_label="Morning",
    )
    info = context.heat_layers[0]
    assert info.grid == grid
    assert info.precision == precision
    assert info.label == "Morning"
    assert info.observation_count == 3
    assert info.cell_count == 2
    assert info.counts == (1, 2)
    assert tuple(count for count, _ in info.count_colors) == info.counts
    assert {color for _, color in info.count_colors} == {
        obj.fill_color().int_rgba() for obj in context._objects
    }
    with pytest.raises(FrozenInstanceError):
        info.label = "changed"
    assert isinstance(context.heat_layers, tuple)


@pytest.mark.parametrize("method", ["add_heat_hashes", "add_heat_h3s"])
def test_empty_layers_are_noops_and_plain_objects_have_no_metadata(method):
    context = heatfall.Context()
    getattr(context, method)([], [], 6)
    context.add_object(
        staticmaps.Area(
            [
                staticmaps.create_latlng(0, 0),
                staticmaps.create_latlng(1, 1),
                staticmaps.create_latlng(1, 0),
            ]
        )
    )
    assert context.heat_layers == ()
    assert context.render_pillow(200, 200).size == (200, 200)


@pytest.mark.parametrize("method", ["add_heat_hashes", "add_heat_h3s"])
def test_invalid_legend_label_does_not_mutate_context(method):
    context = heatfall.Context()
    with pytest.raises(ValueError, match="legend_label"):
        getattr(context, method)([27.947], [-82.458], 6, legend_label=" ")
    assert not context._objects
    assert context.heat_layers == ()


@pytest.mark.parametrize("plot", [heatfall.plot_heat_hashes, heatfall.plot_heat_h3s])
def test_plot_legend_defaults_to_enabled_and_false_disables(monkeypatch, plot):
    monkeypatch.setattr(
        "heatfall.heat.process_colors", lambda scheme, n: [staticmaps.RED] * n
    )
    args = ([27.947, 27.947], [-82.458, -82.458], 6)
    enabled = plot(*args, tileprovider=staticmaps.tile_provider_None, size=(300, 240))
    explicit = plot(
        *args, tileprovider=staticmaps.tile_provider_None, size=(300, 240), legend=True
    )
    hidden = plot(
        *args, tileprovider=staticmaps.tile_provider_None, size=(300, 240), legend=False
    )
    assert list(enabled.getdata()) == list(explicit.getdata())
    assert list(enabled.getdata()) != list(hidden.getdata())


def test_context_legend_can_change_between_renders():
    context = heatfall.Context()
    context.set_tile_provider(staticmaps.tile_provider_None)
    context.add_heat_h3s([27.947, 27.947], [-82.458, -82.458], 8)
    enabled = context.render_pillow(300, 240)
    context.set_legend(False)
    hidden = context.render_pillow(300, 240)
    context.set_legend(True)
    enabled_again = context.render_pillow(300, 240)
    assert list(enabled.getdata()) == list(enabled_again.getdata())
    assert list(enabled.getdata()) != list(hidden.getdata())


@pytest.mark.parametrize(
    "position",
    [
        "top-left",
        "top-center",
        "top-right",
        "center-left",
        "center",
        "center-right",
        "bottom-left",
        "bottom-center",
        "bottom-right",
    ],
)
def test_all_preset_legend_positions_fit(position):
    context = heatfall.Context()
    context.set_tile_provider(staticmaps.tile_provider_None)
    context.add_heat_hashes([27.947, 27.947], [-82.458, -82.458], 6)
    context.set_legend(heatfall.LegendOptions(position=position))
    assert context.render_pillow(400, 300).size == (400, 300)


@pytest.mark.parametrize(
    "anchor",
    [
        "top-left",
        "top-center",
        "top-right",
        "center-left",
        "center",
        "center-right",
        "bottom-left",
        "bottom-center",
        "bottom-right",
    ],
)
def test_custom_coordinate_anchors_and_fraction_units(anchor):
    layer = heatfall.HeatLayerInfo("h3", 8, None, 1, 1, (1,), ((1, (20, 40, 60, 153)),))
    options = heatfall.LegendOptions(
        position=(0.5, 0.5),
        units="fraction",
        anchor=anchor,
        offset=(-1, 2),
        title=None,
        allow_clipping=True,
    )
    layout = layout_legend((layer,), options, 300, 200)
    assert layout is not None
    ax = 0 if anchor.endswith("left") else 1 if anchor.endswith("right") else 0.5
    ay = 0 if anchor.startswith("top") else 1 if anchor.startswith("bottom") else 0.5
    assert layout.x == pytest.approx(150 - ax * layout.width - 1)
    assert layout.y == pytest.approx(100 - ay * layout.height + 2)


def test_legend_clipping_overflow_and_invalid_options():
    layer = heatfall.HeatLayerInfo("h3", 8, None, 1, 1, (1,), ((1, (20, 40, 60, 153)),))
    with pytest.raises(ValueError, match="allow_clipping=True"):
        layout_legend((layer,), heatfall.LegendOptions(position=(500, 500)), 300, 200)
    clipped = layout_legend(
        (layer,),
        heatfall.LegendOptions(position=(500, 500), allow_clipping=True),
        300,
        200,
    )
    assert clipped is not None and clipped.x == 500
    for options in (
        heatfall.LegendOptions(position="middle"),
        heatfall.LegendOptions(units="meters"),
        heatfall.LegendOptions(anchor="middle"),
        heatfall.LegendOptions(position=(float("nan"), 2)),
        heatfall.LegendOptions(offset=(0, float("inf"))),
        heatfall.LegendOptions(columns=0),
        heatfall.LegendOptions(font_size=0),
        heatfall.LegendOptions(margin=-1),
        heatfall.LegendOptions(padding=float("nan")),
        heatfall.LegendOptions(corner_radius=-1),
        heatfall.LegendOptions(allow_clipping="yes"),
        heatfall.LegendOptions(shadow="yes"),
        heatfall.LegendOptions(title=1),
        heatfall.LegendOptions(title_font_size=0),
        heatfall.LegendOptions(section_font_size=-1),
        heatfall.LegendOptions(label_font_size=True),
        heatfall.LegendOptions(title_weight="heavy"),
        heatfall.LegendOptions(title_align="justify"),
        heatfall.LegendOptions(title_wrap="yes"),
        heatfall.LegendOptions(title_max_width=0),
        heatfall.LegendOptions(title_max_width=True),
        heatfall.LegendOptions(title_max_width=80.5),
        heatfall.LegendOptions(title_line_spacing=-1),
        heatfall.LegendOptions(font_family=" "),
        heatfall.LegendOptions(shadow_opacity=1.1),
        heatfall.LegendOptions(shadow_offset=(0, float("inf"))),
        heatfall.LegendOptions(title_color="#not-a-color"),
        heatfall.LegendOptions(label_format=1),
        heatfall.LegendOptions(label_format="{unknown}"),
        heatfall.LegendOptions(label_format="count"),
        heatfall.LegendOptions(count_order="sideways"),
        heatfall.LegendOptions(text_color="#zzzzzz"),
        heatfall.LegendOptions(position=[1, 2]),
    ):
        with pytest.raises(ValueError):
            validate_legend_options(options)
    with pytest.raises(TypeError):
        validate_legend_options(True)
    with pytest.raises(TypeError):
        heatfall.Context().set_legend("yes")


def test_exact_count_legend_defaults_high_to_low_and_supports_low_to_high():
    layer = heatfall.HeatLayerInfo(
        "h3",
        8,
        None,
        6,
        3,
        (1, 2, 3),
        (
            (1, (30, 136, 229, 255)),
            (2, (253, 216, 53, 255)),
            (3, (229, 57, 53, 255)),
        ),
    )

    def labels(count_order):
        layout = layout_legend(
            (layer,), heatfall.LegendOptions(count_order=count_order), 300, 240
        )
        return [row.label for rows in layout.sections[0][1] for row in rows]

    assert labels("descending") == ["3", "2", "1"]
    assert labels("ascending") == ["1", "2", "3"]


def test_named_preset_accepts_an_explicit_alignment_anchor():
    layer = heatfall.HeatLayerInfo("h3", 8, None, 1, 1, (1,), ((1, (20, 40, 60, 153)),))
    options = heatfall.LegendOptions(
        position="top-center", anchor="top-right", margin=0, allow_clipping=True
    )
    layout = layout_legend((layer,), options, 300, 200)
    assert layout is not None
    assert layout.x == pytest.approx(150 - layout.width)
    assert layout.y == 0


def test_svg_renders_panel_text_and_opacity():
    context = heatfall.Context()
    context.set_tile_provider(staticmaps.tile_provider_None)
    context.add_heat_h3s([27.947, 27.947], [-82.458, -82.458], 8, opacity=0.5)
    context.set_legend(heatfall.LegendOptions(title="Counts", position="bottom-left"))
    svg = ET.fromstring(context.render_svg(400, 300).tostring())
    ns = {"svg": "http://www.w3.org/2000/svg"}
    assert "Counts" in [node.text for node in svg.findall(".//svg:text", ns)]
    swatches = svg.findall('.//svg:rect[@width="16"]', ns)
    assert swatches[0].attrib.get("fill-opacity") == str(128 / 255)


def test_legend_default_style_uses_card_and_swatch_corners():
    context = heatfall.Context()
    context.set_tile_provider(staticmaps.tile_provider_None)
    context.add_heat_h3s([27.947, 27.947, 27.951], [-82.458, -82.458, -82.450], 8)
    image = context.render_pillow(400, 300).convert("RGBA")
    svg = context.render_svg(400, 300).tostring()
    assert image.size == (400, 300)
    assert 'rx="12"' in svg
    assert 'font-weight="bold"' in svg
    root = ET.fromstring(svg)
    ns = {"svg": "http://www.w3.org/2000/svg"}
    labels = [node.text for node in root.findall(".//svg:text", ns)]
    assert labels == ["Observations", "per cell", "2", "1"]


@pytest.mark.parametrize("align", ["left", "center", "right"])
@pytest.mark.parametrize("shadow", [True, False])
def test_legend_visual_parameters_are_applied(align, shadow):
    context = heatfall.Context()
    context.set_tile_provider(staticmaps.tile_provider_None)
    context.add_heat_h3s([27.947, 27.951], [-82.458, -82.450], 8)
    context.add_heat_hashes([27.947, 27.951], [-82.458, -82.450], 6)
    context.set_legend(
        heatfall.LegendOptions(
            title_font_size=16,
            section_font_size=12,
            label_font_size=11,
            font_family="DejaVu Sans",
            title_weight="bold",
            section_weight="normal",
            label_weight="bold",
            title_align=align,
            text_color="#102030",
            title_color="#203040",
            section_color="#304050",
            label_color="#405060",
            corner_radius=13,
            shadow=shadow,
            shadow_color="#112233",
            shadow_opacity=0.3,
            shadow_offset=(4, 5),
            divider_color="#506070",
            divider_width=2,
            title_spacing=14,
            section_spacing=4,
            padding=13,
            swatch_size=16,
            swatch_radius=2,
            label_gap=6,
            row_spacing=3,
            columns=2,
            column_spacing=20,
        )
    )
    assert context.render_pillow(500, 300).size == (500, 300)
    svg = ET.fromstring(context.render_svg(500, 300).tostring())
    ns = {"svg": "http://www.w3.org/2000/svg"}
    assert len(svg.findall('.//svg:rect[@width="16"]', ns)) == 2
    assert len(svg.findall('.//svg:rect[@fill="#112233"]', ns)) == int(shadow)
    assert any(
        node.attrib.get("font-size") == "11"
        and node.attrib.get("font-weight") == "bold"
        for node in svg.findall(".//svg:text", ns)
    )
    assert any(
        node.attrib.get("font-size") == "16" and node.attrib.get("fill") == "#203040"
        for node in svg.findall(".//svg:text", ns)
    )


def test_svg_preserves_text_and_border_alpha():
    context = heatfall.Context()
    context.set_tile_provider(staticmaps.tile_provider_None)
    context.add_heat_h3s([27.947], [-82.458], 8)
    context.set_legend(
        heatfall.LegendOptions(
            text_color=(10, 20, 30, 64), border_color=(40, 50, 60, 128)
        )
    )
    svg = ET.fromstring(context.render_svg(400, 300).tostring())
    ns = {"svg": "http://www.w3.org/2000/svg"}
    panel = svg.find('.//svg:rect[@stroke="#28323c"]', ns)
    assert panel is not None
    assert panel.attrib["stroke-opacity"] == str(128 / 255)
    for text in svg.findall(".//svg:text", ns):
        assert text.attrib["fill-opacity"] == str(64 / 255)


def test_multiple_layers_have_separate_labelled_sections():
    context = heatfall.Context()
    context.set_tile_provider(staticmaps.tile_provider_None)
    context.add_heat_h3s([27.947], [-82.458], 8, legend_label="Morning")
    context.add_heat_hashes([27.947], [-82.458], 6)
    context.set_legend(
        heatfall.LegendOptions(
            position=(0.5, 0.5), units="fraction", anchor="center", columns=2
        )
    )
    svg = context.render_svg(400, 300).tostring()
    assert "Morning" in svg
    assert "GEOHASH layer 2" in svg

    image = context.render_pillow(400, 300)
    assert image.size == (400, 300)


def test_empty_legend_drawing_helpers_are_noops():
    from PIL import Image

    source = Image.new("RGBA", (100, 100), "black")
    assert _draw_pillow_legend(source, (), heatfall.LegendOptions()) is source
    drawing = MagicMock()
    draw_svg_legend(drawing, (), heatfall.LegendOptions(), 100, 100)
    drawing.add.assert_not_called()
    cairo = SimpleNamespace(Context=MagicMock())
    original = sys.modules.get("cairo")
    sys.modules["cairo"] = cairo
    try:
        draw_cairo_legend(object(), (), heatfall.LegendOptions(), 100, 100)
        cairo.Context.assert_not_called()
    finally:
        if original is None:
            sys.modules.pop("cairo", None)
        else:
            sys.modules["cairo"] = original


def test_custom_label_format_and_single_count_sequential_color():
    context = heatfall.Context()
    context.set_tile_provider(staticmaps.tile_provider_None)
    context.add_heat_h3s([27.947], [-82.458], 8, color_scheme="sequential")
    assert context.heat_layers[0].count_colors[0][1][:3] == (115, 158, 202)
    context.set_legend(
        heatfall.LegendOptions(
            title=None,
            label_format="{count} points",
            background_color=(255, 255, 255, 220),
            border_color=staticmaps.Color(0, 0, 0),
            text_color=(20, 20, 20),
            border_width=2,
            padding=3,
            swatch_size=8,
            row_spacing=2,
        )
    )
    image = context.render_pillow(300, 240)
    assert image.mode == "RGBA"


@pytest.mark.parametrize("title_align", ["left", "center", "right"])
def test_cairo_legend_draws_when_backend_is_available(monkeypatch, title_align):
    cairo = SimpleNamespace(
        FONT_SLANT_NORMAL=0,
        FONT_WEIGHT_NORMAL=0,
        FONT_WEIGHT_BOLD=1,
        Context=lambda surface: canvas,
    )
    canvas = MagicMock()
    canvas.font_extents.return_value = (0, 0, 12, 0, 0)
    canvas.text_extents.return_value = (0, 0, 10, 12, 10, 0)
    monkeypatch.setitem(sys.modules, "cairo", cairo)
    context = heatfall.Context()
    context.set_tile_provider(staticmaps.tile_provider_None)
    context.add_heat_h3s([27.947], [-82.458], 8, legend_label="Morning")
    context.add_heat_hashes([27.947], [-82.458], 6)
    context.set_legend(
        heatfall.LegendOptions(
            title_align=title_align,
            title_font_size=16,
            section_font_size=12,
            label_font_size=10,
            title_color="#203040",
            shadow_offset=(4, 5),
        )
    )
    monkeypatch.setattr(
        landfall_context_base(), "render_cairo", lambda self, w, h: object()
    )
    result = context.render_cairo(300, 240)
    assert result is not None
    canvas.show_text.assert_called()


@pytest.mark.parametrize("family", ["custom-font.ttf", "Unavailable Family"])
def test_font_family_accepts_font_files_and_system_family_names(family):
    assert _font(12, bold=True, family=family) is not None


@pytest.mark.parametrize("bold", [False, True])
def test_bundled_font_and_missing_family_preserve_requested_size_and_weight(bold):
    small = _font(11, bold=bold, family="Missing Heatfall Font")
    large = _font(24, bold=bold)
    assert small.size == 11
    assert large.size == 24
    assert large.getlength("1-38") > small.getlength("1-38") * 2
    assert Path(large.path).name == (
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    )
    custom = _font(19, bold=bold, family=str(Path(_font(13).path)))
    assert custom.size == 19
    assert Path(custom.path).name == Path(large.path).name
    assert _font(13, True).getlength("Observations") > _font(13).getlength(
        "Observations"
    )


@pytest.mark.parametrize(
    "position",
    [
        "top-left",
        "top-center",
        "top-right",
        "center-left",
        "center",
        "center-right",
        "bottom-left",
        "bottom-center",
        "bottom-right",
    ],
)
@pytest.mark.parametrize(
    "size,font_size,columns",
    [((320, 240), 11, 1), ((440, 300), 14, 2), ((640, 400), 20, 3)],
)
def test_range_legend_text_stays_inside_card_at_all_positions_and_sizes(
    monkeypatch, position, size, font_size, columns
):
    from PIL import Image, ImageDraw

    layer = heatfall.HeatLayerInfo(
        "h3",
        9,
        None,
        100,
        5,
        (1, 8, 18, 28, 38),
        (),
        tuple(
            (low, high, (30, 136, 229, 153))
            for low, high in ((1, 5), (6, 14), (15, 24), (25, 33), (34, 38))
        ),
    )
    options = heatfall.LegendOptions(
        position=position,
        font_size=font_size,
        columns=columns,
        swatch_size=font_size + 3,
        label_format="gyp {count}",
    )
    layout = layout_legend((layer,), options, *size)
    assert layout is not None
    bounds = []
    original = ImageDraw.ImageDraw.text

    def record_text(draw, xy, text, **kwargs):
        bounds.append(draw.textbbox(xy, text, font=kwargs["font"]))
        return original(draw, xy, text, **kwargs)

    monkeypatch.setattr(ImageDraw.ImageDraw, "text", record_text)
    _draw_pillow_legend(Image.new("RGBA", size, "black"), (layer,), options)
    title_line_count = len(layout.title_lines)
    assert len(bounds) == 5 + title_line_count
    for left, top, right, bottom in bounds:
        assert left >= layout.x + options.padding
        assert top >= layout.y + options.padding
        assert right <= layout.x + layout.width - options.padding
        assert bottom <= layout.y + layout.height - options.padding
    # The title's ink must end above the divider and first row's text.
    assert max(box[3] for box in bounds[:title_line_count]) < min(
        box[1] for box in bounds[title_line_count:]
    )


def test_translucent_swatches_blend_over_the_panel_instead_of_the_map():
    from PIL import Image

    color = (229, 57, 53, 153)
    layer = heatfall.HeatLayerInfo("h3", 9, None, 1, 1, (1,), ((1, color),))
    options = heatfall.LegendOptions(
        title=None,
        position="top-left",
        background_color="white",
        shadow=False,
        swatch_size=30,
    )
    layout = layout_legend((layer,), options, 300, 240)
    image = _draw_pillow_legend(
        Image.new("RGBA", (300, 240), "black"), (layer,), options
    )
    center = (
        int(layout.x + options.padding + 15),
        int(layout.y + options.padding + 15),
    )
    expected = Image.alpha_composite(
        Image.new("RGBA", (1, 1), "white"), Image.new("RGBA", (1, 1), color)
    ).getpixel((0, 0))
    assert image.getpixel(center) == expected


@pytest.mark.parametrize("opacity", [0, 0.5, 1])
@pytest.mark.parametrize("color_alpha", [128, 255])
def test_background_opacity_preserves_content_and_matches_all_renderers(
    monkeypatch, opacity, color_alpha
):
    from PIL import Image
    import svgwrite

    options = heatfall.LegendOptions(
        position="top-left",
        background_color=(255, 255, 255, color_alpha),
        background_opacity=opacity,
        corner_radius=0,
        shadow=False,
    )
    validate_legend_options(options)
    layer = heatfall.HeatLayerInfo(
        "h3", 9, None, 1, 1, (1,), ((1, (30, 136, 229, 153)),)
    )
    effective_alpha = round(color_alpha * opacity)
    colors = legend_colors(options)
    assert colors["background"] == (255, 255, 255, effective_alpha)
    assert colors["title"] == legend_colors(heatfall.LegendOptions())["title"]
    assert colors["label"] == legend_colors(heatfall.LegendOptions())["label"]

    image = _draw_pillow_legend(
        Image.new("RGBA", (300, 240), "black"), (layer,), options
    )
    layout = layout_legend((layer,), options, 300, 240)
    blank_panel_pixel = (
        int(layout.x + options.padding),
        int(layout.y + options.padding / 2),
    )
    assert image.getpixel(blank_panel_pixel) == (effective_alpha,) * 3 + (255,)

    drawing = svgwrite.Drawing(size=(300, 240))
    draw_svg_legend(drawing, (layer,), options, 300, 240)
    root = ET.fromstring(drawing.tostring())
    ns = {"svg": "http://www.w3.org/2000/svg"}
    panel = root.find('.//svg:rect[@fill="#ffffff"]', ns)
    assert float(panel.attrib["fill-opacity"]) == effective_alpha / 255
    swatch = root.find('.//svg:rect[@fill="#1e88e5"]', ns)
    assert float(swatch.attrib["fill-opacity"]) == 153 / 255

    canvas = MagicMock()
    canvas.font_extents.return_value = (13, 4, 17, 0, 0)
    canvas.text_extents.return_value = (0, 0, 10, 12, 10, 0)
    cairo = SimpleNamespace(
        FONT_SLANT_NORMAL=0,
        FONT_WEIGHT_NORMAL=0,
        FONT_WEIGHT_BOLD=1,
        Context=lambda surface: canvas,
    )
    monkeypatch.setitem(sys.modules, "cairo", cairo)
    draw_cairo_legend(object(), (layer,), options, 300, 240)
    canvas.set_source_rgba.assert_any_call(1, 1, 1, effective_alpha / 255)


@pytest.mark.parametrize(
    "opacity", [-0.1, 1.1, float("nan"), float("inf"), True, "0.5", None]
)
def test_background_opacity_rejects_invalid_values(opacity):
    with pytest.raises(ValueError, match="background_opacity must be between 0 and 1"):
        heatfall.Context().set_legend(
            heatfall.LegendOptions(background_opacity=opacity)
        )


def test_title_wrap_compacts_the_card_and_preserves_explicit_newlines():
    layer = heatfall.HeatLayerInfo(
        "h3", 9, None, 1, 1, (1,), ((1, (30, 136, 229, 153)),)
    )
    wrapped = layout_legend((layer,), heatfall.LegendOptions(), 300, 240)
    unwrapped = layout_legend(
        (layer,), heatfall.LegendOptions(title_wrap=False), 300, 240
    )
    assert wrapped.title_lines == ("Observations", "per cell")
    assert unwrapped.title_lines == ("Observations per cell",)
    assert wrapped.width < unwrapped.width
    assert wrapped.height > unwrapped.height
    assert wrapped.sections == unwrapped.sections
    manual = layout_legend(
        (layer,),
        heatfall.LegendOptions(title="Counts\n\nper cell", title_wrap=False),
        300,
        240,
    )
    assert manual.title_lines == ("Counts", "", "per cell")


@pytest.mark.parametrize("align", ["left", "center", "right"])
def test_wrapped_titles_draw_every_line_before_rows_in_all_renderers(
    monkeypatch, align
):
    from PIL import Image, ImageDraw
    import svgwrite

    layer = heatfall.HeatLayerInfo(
        "h3", 9, None, 1, 1, (1,), ((1, (30, 136, 229, 153)),)
    )
    title = "Supercalifragilistic activity\n\nper cell"
    options = heatfall.LegendOptions(
        title=title,
        title_max_width=90,
        title_line_spacing=5,
        title_align=align,
    )
    layout = layout_legend((layer,), options, 400, 400)
    assert len(layout.title_lines) > 3
    assert "" in layout.title_lines
    assert "".join(layout.title_lines).replace(" ", "") == title.replace(
        "\n", ""
    ).replace(" ", "")
    assert all(_font(13, True).getlength(line) <= 90 for line in layout.title_lines)

    recorded = []
    original = ImageDraw.ImageDraw.text

    def record_text(draw, xy, text, **kwargs):
        recorded.append(text)
        return original(draw, xy, text, **kwargs)

    monkeypatch.setattr(ImageDraw.ImageDraw, "text", record_text)
    _draw_pillow_legend(Image.new("RGBA", (400, 400), "black"), (layer,), options)
    assert recorded == list(layout.title_lines) + ["1"]

    drawing = svgwrite.Drawing(size=(400, 400))
    draw_svg_legend(drawing, (layer,), options, 400, 400)
    root = ET.fromstring(drawing.tostring())
    texts = root.findall(".//{http://www.w3.org/2000/svg}text")
    assert [node.text or "" for node in texts] == list(layout.title_lines) + ["1"]
    assert (
        float(texts[-1].attrib["y"])
        > float(texts[-2].attrib["y"]) + options.title_line_spacing
    )

    canvas = MagicMock()
    canvas.font_extents.return_value = (13, 4, 17, 0, 0)
    canvas.text_extents.return_value = (0, 0, 10, 12, 10, 0)
    monkeypatch.setitem(
        sys.modules,
        "cairo",
        SimpleNamespace(
            FONT_SLANT_NORMAL=0,
            FONT_WEIGHT_NORMAL=0,
            FONT_WEIGHT_BOLD=1,
            Context=lambda surface: canvas,
        ),
    )
    draw_cairo_legend(object(), (layer,), options, 400, 400)
    assert [call.args[0] for call in canvas.show_text.call_args_list] == list(
        layout.title_lines
    ) + ["1"]


def landfall_context_base():
    return __import__("landfall").Context
