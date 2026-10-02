"""Shared pytest fixtures and configuration for heatfall tests."""

import pytest
import staticmaps

from heatfall.heat import Context
from tests.mock_tile_downloader import MockTileDownloader


@pytest.fixture(autouse=True)
def offline_tiles(monkeypatch, request):
    """Use mock tiles for ordinary tests; integration tests may use real tiles."""
    if request.node.get_closest_marker("integration") is None:
        monkeypatch.setattr("staticmaps.context.TileDownloader", MockTileDownloader)


@pytest.fixture
def mock_context():
    """Create a heatfall context with mock tile downloader."""
    context = Context()
    context.set_tile_downloader(MockTileDownloader())
    return context


@pytest.fixture
def mock_staticmaps_context():
    """Create a staticmaps context with mock tile downloader."""
    context = staticmaps.Context()
    context.set_tile_downloader(MockTileDownloader())
    return context


@pytest.fixture
def sample_coordinates():
    """Sample coordinate data for testing."""
    return {
        "lats": [27.88, 27.92, 27.94],
        "lons": [-82.49, -82.49, -82.46],
        "points": [(27.88, -82.49), (27.92, -82.49), (27.94, -82.46)],
    }


@pytest.fixture
def single_coordinate():
    """Single coordinate for testing."""
    return {"lats": [27.88], "lons": [-82.49]}


@pytest.fixture
def many_coordinates():
    """Many coordinates for stress testing."""
    return {
        "lats": [27.88 + i * 0.01 for i in range(100)],
        "lons": [-82.49 + i * 0.01 for i in range(100)],
    }


@pytest.fixture
def sample_polygons():
    """Sample polygon data for testing."""
    return [
        [(27.88, -82.49), (27.92, -82.49), (27.94, -82.46), (27.88, -82.49)],
        [(28.0, -82.5), (28.1, -82.5), (28.1, -82.4), (28.0, -82.4)],
    ]
