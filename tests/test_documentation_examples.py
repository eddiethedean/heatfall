"""Smoke tests for public examples; all renders explicitly avoid tile access."""

import staticmaps

import heatfall


def test_installation_first_map_example(tmp_path):
    lats = [27.9470, 27.9470, 27.9515, 27.9430]
    lons = [-82.4580, -82.4580, -82.4500, -82.4475]

    image = heatfall.plot_heat_h3s(
        lats, lons, precision=8, tileprovider=staticmaps.tile_provider_None
    )
    output = tmp_path / "first-heatmap.png"
    image.save(output)

    assert image.size == (800, 500)
    assert output.is_file()


def test_fixed_color_period_comparison_example(tmp_path):
    morning_lats = [27.9470, 27.9470, 27.9515]
    morning_lons = [-82.4580, -82.4580, -82.4500]
    afternoon_lats = [27.9470, 27.9515, 27.9515]
    afternoon_lons = [-82.4580, -82.4500, -82.4500]
    colors = {1: "#deebf7", 2: "#3182bd"}

    for name, lats, lons in (
        ("morning", morning_lats, morning_lons),
        ("afternoon", afternoon_lats, afternoon_lons),
    ):
        context = heatfall.Context()
        context.set_tile_provider(staticmaps.tile_provider_None)
        context.set_center(staticmaps.create_latlng(27.9470, -82.4540))
        context.set_zoom(13)
        context.add_heat_h3s(lats, lons, precision=8, count_colors=colors)
        context.render_pillow(600, 400).save(tmp_path / f"{name}.png")

        layer = context.heat_layers[0]
        assert layer.counts == (1, 2)
        assert {count for count, _ in layer.count_colors} == set(colors)
        assert (tmp_path / f"{name}.png").is_file()


def test_composed_map_example(tmp_path):
    lats = [27.9470, 27.9470, 27.9515, 27.9430]
    lons = [-82.4580, -82.4580, -82.4500, -82.4475]
    context = heatfall.Context()
    context.set_tile_provider(staticmaps.tile_provider_None)
    context.add_heat_h3s(lats, lons, precision=8)
    context.add_points([27.9470], [-82.4580], colors=["black"], point_size=10)

    output = tmp_path / "layered-map.png"
    context.render_pillow(800, 500).save(output)

    assert output.is_file()
    assert context.heat_layers[0].observation_count == len(lats)
