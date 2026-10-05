"""Heat color scales and fixed count-to-color mappings."""

from inspect import signature

import pytest

import heatfall
from heatfall.heat import _make_count_colors


def test_heatmap_gradient_uses_blue_to_red_stops_and_center_for_one_count():
    colors = _make_count_colors((1, 2, 3, 4, 5), "heatmap", None, 1)
    assert [colors[count].int_rgba()[:3] for count in range(1, 6)] == [
        (30, 136, 229),
        (67, 160, 71),
        (253, 216, 53),
        (251, 140, 0),
        (229, 57, 53),
    ]
    single = _make_count_colors((7,), "heatmap", None, 1)
    assert single[7].int_rgba()[:3] == (253, 216, 53)


def test_all_public_heat_apis_default_to_heatmap():
    for function in (
        heatfall.Context.add_heat_hashes,
        heatfall.Context.add_heat_h3s,
        heatfall.plot_heat_hashes,
        heatfall.plot_heat_h3s,
    ):
        assert signature(function).parameters["color_scheme"].default == "heatmap"


@pytest.mark.parametrize("method", ["add_heat_hashes", "add_heat_h3s"])
def test_heatmap_is_the_default_color_scheme(method):
    args = ([27.947, 27.947, 27.951], [-82.458, -82.458, -82.450], 8)
    default = heatfall.Context()
    explicit = heatfall.Context()
    getattr(default, method)(*args, opacity=1)
    getattr(explicit, method)(*args, color_scheme="heatmap", opacity=1)
    assert default.heat_layers[0].count_colors == explicit.heat_layers[0].count_colors


@pytest.mark.parametrize("method", ["add_heat_hashes", "add_heat_h3s"])
def test_sequential_and_explicit_count_colors_are_deterministic(method):
    args = ([27.947, 27.947, 27.951], [-82.458, -82.458, -82.450], 8)
    first = heatfall.Context()
    second = heatfall.Context()
    getattr(first, method)(*args, color_scheme="sequential", opacity=1)
    getattr(second, method)(*args, color_scheme="sequential", opacity=1)
    assert first.heat_layers[0].count_colors == second.heat_layers[0].count_colors
    palette = dict(first.heat_layers[0].count_colors)
    assert palette[1][:3] == (222, 235, 247)
    assert palette[2][:3] == (8, 81, 156)

    shared = {1: "#deebf7", 2: (8, 81, 156, 128), 99: "#ffffff"}
    third = heatfall.Context()
    getattr(third, method)(*args, count_colors=shared, opacity=0.5)
    assert dict(third.heat_layers[0].count_colors) == {
        1: (222, 235, 247, 128),
        2: (8, 81, 156, 64),
    }


@pytest.mark.parametrize("method", ["add_heat_hashes", "add_heat_h3s"])
@pytest.mark.parametrize(
    "mapping", [{2: "#ffffff"}, {0: "#000000"}, {1: "#zzzzzz"}, ["#ffffff"]]
)
def test_invalid_count_colors_do_not_mutate_context(method, mapping):
    context = heatfall.Context()
    with pytest.raises(ValueError):
        getattr(context, method)([27.947], [-82.458], 6, count_colors=mapping)
    assert not context._objects
    assert context.heat_layers == ()
