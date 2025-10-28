"""Tests for helper functions."""

import pytest
from s2sphere.sphere import LatLng

from heatfall.heat import make_hash_poly_points, make_h3_poly_points


class TestMakeHashPolyPoints:
    """Test geohash polygon point generation."""

    def test_basic_geohash(self):
        """Test basic geohash polygon generation."""
        points = make_hash_poly_points("9q5yy")

        assert isinstance(points, list)
        assert len(points) == 5  # Square polygon with closing point
        assert all(isinstance(p, LatLng) for p in points)

    def test_different_precisions(self):
        """Test different geohash precisions."""
        geohashes = ["9", "9q", "9q5", "9q5y", "9q5yy"]

        for gh in geohashes:
            points = make_hash_poly_points(gh)
            assert isinstance(points, list)
            assert len(points) == 5
            assert all(isinstance(p, LatLng) for p in points)

    def test_empty_geohash(self):
        """Test empty geohash string."""
        with pytest.raises(Exception):  # Should raise some kind of error
            make_hash_poly_points("")

    def test_invalid_geohash(self):
        """Test invalid geohash string."""
        with pytest.raises(Exception):  # Should raise some kind of error
            make_hash_poly_points("invalid")


class TestMakeH3PolyPoints:
    """Test H3 polygon point generation."""

    def test_basic_h3_cell(self):
        """Test basic H3 cell polygon generation."""
        points = make_h3_poly_points("8a1fb46622dffff")

        assert isinstance(points, list)
        assert len(points) > 0  # Hexagon has 6+ points
        assert all(isinstance(p, LatLng) for p in points)

    def test_different_resolutions(self):
        """Test different H3 resolutions."""
        h3_cells = [
            "8045fffffffffff",  # Resolution 0
            "81443ffffffffff",  # Resolution 1
            "82441ffffffffff",  # Resolution 2
        ]

        for cell in h3_cells:
            points = make_h3_poly_points(cell)
            assert isinstance(points, list)
            assert len(points) > 0
            assert all(isinstance(p, LatLng) for p in points)

    def test_empty_h3_cell(self):
        """Test empty H3 cell string."""
        with pytest.raises(Exception):  # Should raise some kind of error
            make_h3_poly_points("")

    def test_invalid_h3_cell(self):
        """Test invalid H3 cell string."""
        with pytest.raises(Exception):  # Should raise some kind of error
            make_h3_poly_points("invalid")


class TestHelperFunctionIntegration:
    """Test integration of helper functions."""

    def test_geohash_polygon_coordinates(self):
        """Test that geohash polygon coordinates are reasonable."""
        points = make_hash_poly_points("9q5yy")

        # Extract lat/lon values
        lats = [p.lat().degrees for p in points]
        lngs = [p.lng().degrees for p in points]

        # Should be reasonable coordinates (Los Angeles area)
        assert all(34 <= lat <= 35 for lat in lats)
        assert all(-119 <= lng <= -118 for lng in lngs)

    def test_h3_polygon_coordinates(self):
        """Test that H3 polygon coordinates are reasonable."""
        points = make_h3_poly_points("8a1fb46622dffff")

        # Extract lat/lon values
        lats = [p.lat().degrees for p in points]
        lngs = [p.lng().degrees for p in points]

        # Should be reasonable coordinates
        assert all(-90 <= lat <= 90 for lat in lats)
        assert all(-180 <= lng <= 180 for lng in lngs)

    def test_polygon_closing(self):
        """Test that polygons are properly closed."""
        # Geohash polygons should be closed (first and last points same)
        points = make_hash_poly_points("9q5yy")
        assert points[0].lat().degrees == points[-1].lat().degrees
        assert points[0].lng().degrees == points[-1].lng().degrees
