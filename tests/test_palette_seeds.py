"""Heatfall forwards reproducible palette seeds to Landfall."""

from inspect import Parameter, signature
import random

import pytest
import staticmaps
from landfall.color import process_colors

import heatfall


LATS = [27.9470] * 4 + [27.9515] * 2 + [27.9430]
LONS = [-82.4580] * 4 + [-82.4500] * 2 + [-82.4475]


def test_palette_seed_is_optional_and_keyword_only():
    for function in (
        heatfall.Context.add_heat_hashes,
        heatfall.Context.add_heat_h3s,
        heatfall.plot_heat_hashes,
        heatfall.plot_heat_h3s,
    ):
        parameter = signature(function).parameters["rng"]
        assert parameter.default is None
        assert parameter.kind is Parameter.KEYWORD_ONLY


def test_tile_api_key_is_optional_and_keyword_only():
    for function in (heatfall.plot_heat_hashes, heatfall.plot_heat_h3s):
        parameter = signature(function).parameters["api_key"]
        assert parameter.default is None
        assert parameter.kind is Parameter.KEYWORD_ONLY


@pytest.mark.parametrize("method", ["add_heat_hashes", "add_heat_h3s"])
@pytest.mark.parametrize("scheme", ["random", "distinct"])
@pytest.mark.parametrize("seed", [0, 42, -42])
def test_seeded_palettes_match_landfall_and_preserve_global_random_state(
    method, scheme, seed
):
    state = random.getstate()
    first = heatfall.Context()
    second = heatfall.Context()
    getattr(first, method)(LATS, LONS, 8, color_scheme=scheme, rng=seed)
    getattr(second, method)(LATS[::-1], LONS[::-1], 8, color_scheme=scheme, rng=seed)

    assert first.heat_layers[0].counts == (1, 2, 4)
    assert first.heat_layers[0].count_colors == second.heat_layers[0].count_colors
    expected = tuple(
        (count, (*color.int_rgba()[:3], 153))
        for count, color in zip((1, 2, 4), process_colors(scheme, 3, rng=seed))
    )
    assert first.heat_layers[0].count_colors == expected
    assert random.getstate() == state


@pytest.mark.parametrize("method", ["add_heat_hashes", "add_heat_h3s"])
def test_different_random_seeds_produce_different_colors(method):
    first = heatfall.Context()
    second = heatfall.Context()
    getattr(first, method)(LATS, LONS, 8, color_scheme="random", rng=42)
    getattr(second, method)(LATS, LONS, 8, color_scheme="random", rng=43)
    assert first.heat_layers[0].count_colors != second.heat_layers[0].count_colors


@pytest.mark.parametrize(
    "plot,method",
    [
        (heatfall.plot_heat_hashes, "add_heat_hashes"),
        (heatfall.plot_heat_h3s, "add_heat_h3s"),
    ],
)
def test_plotting_wrappers_forward_the_seed(plot, method):
    context = heatfall.Context()
    context.set_tile_provider(staticmaps.tile_provider_None)
    getattr(context, method)(LATS, LONS, 8, color_scheme="random", rng=42)
    expected = context.render_pillow(800, 500)
    actual = plot(
        LATS,
        LONS,
        8,
        color_scheme="random",
        rng=42,
        tileprovider=staticmaps.tile_provider_None,
    )
    assert actual.tobytes() == expected.tobytes()


@pytest.mark.parametrize("method", ["add_heat_hashes", "add_heat_h3s"])
@pytest.mark.parametrize("scheme", ["heatmap", "sequential", "wheel"])
def test_seed_does_not_change_ordered_or_fixed_palettes(method, scheme):
    first = heatfall.Context()
    second = heatfall.Context()
    getattr(first, method)(LATS, LONS, 8, color_scheme=scheme, rng=42)
    getattr(second, method)(LATS, LONS, 8, color_scheme=scheme, rng=43)
    assert first.heat_layers[0].count_colors == second.heat_layers[0].count_colors

    fixed = {1: "blue", 2: "orange", 4: "red"}
    third = heatfall.Context()
    fourth = heatfall.Context()
    getattr(third, method)(LATS, LONS, 8, count_colors=fixed, rng=42)
    getattr(fourth, method)(LATS, LONS, 8, count_colors=fixed, rng=43)
    assert third.heat_layers[0].count_colors == fourth.heat_layers[0].count_colors


@pytest.mark.parametrize("method", ["add_heat_hashes", "add_heat_h3s"])
@pytest.mark.parametrize("seed", [True, False, 1.5, "42", [], float("nan")])
def test_invalid_seeds_are_rejected_before_context_mutation(method, seed):
    context = heatfall.Context()
    with pytest.raises(ValueError, match="rng must be an integer seed or None"):
        getattr(context, method)(LATS, LONS, 8, rng=seed)
    assert context._objects == []
    assert context.heat_layers == ()


@pytest.mark.parametrize("plot", [heatfall.plot_heat_hashes, heatfall.plot_heat_h3s])
def test_plotting_wrappers_reject_invalid_seeds(plot):
    with pytest.raises(ValueError, match="rng must be an integer seed or None"):
        plot(LATS, LONS, 8, rng=True)
