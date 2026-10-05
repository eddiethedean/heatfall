"""Sequential heat colors and fixed count-to-color mappings."""

import pytest

import heatfall


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
