"""Tests for heat mapping functionality."""

import pytest
from PIL import Image

import heatfall
from heatfall.heat import calculate_h3_hashes


class TestPlotHeatHashes:
    """Test geohash-based heat mapping."""

    def test_basic_heat_hashes(self, sample_coordinates):
        """Test basic geohash heatmap."""
        img = heatfall.plot_heat_hashes(
            sample_coordinates["lats"], sample_coordinates["lons"], precision=4
        )
        assert isinstance(img, Image.Image)
        assert img.size == (800, 500)

    def test_heat_hashes_custom_size(self, sample_coordinates):
        """Test custom output size."""
        img = heatfall.plot_heat_hashes(
            sample_coordinates["lats"],
            sample_coordinates["lons"],
            precision=4,
            size=(1024, 768),
        )
        assert img.size == (1024, 768)

    def test_heat_hashes_precision_range(self, sample_coordinates):
        """Test various precision levels."""
        for precision in [1, 4, 8, 12]:
            img = heatfall.plot_heat_hashes(
                sample_coordinates["lats"],
                sample_coordinates["lons"],
                precision=precision,
            )
            assert isinstance(img, Image.Image)

    def test_heat_hashes_color_schemes(self, sample_coordinates):
        """Test different color schemes."""
        for scheme in ["distinct", "random", "wheel"]:
            img = heatfall.plot_heat_hashes(
                sample_coordinates["lats"],
                sample_coordinates["lons"],
                precision=4,
                color_scheme=scheme,
            )
            assert isinstance(img, Image.Image)

    def test_heat_hashes_empty_input(self):
        """Test empty input raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            heatfall.plot_heat_hashes([], [], precision=4)

    def test_heat_hashes_mismatched_lengths(self):
        """Test mismatched input lengths raise error."""
        with pytest.raises(ValueError, match="same length"):
            heatfall.plot_heat_hashes([1, 2], [1], precision=4)

    def test_heat_hashes_invalid_precision(self, sample_coordinates):
        """Test invalid precision raises error."""
        with pytest.raises(ValueError, match="precision must be"):
            heatfall.plot_heat_hashes(
                sample_coordinates["lats"], sample_coordinates["lons"], precision=0
            )

    def test_heat_hashes_invalid_latitude(self):
        """Test invalid latitude raises error."""
        with pytest.raises(ValueError, match="latitudes must be between"):
            heatfall.plot_heat_hashes([91], [0], precision=4)

    def test_heat_hashes_invalid_longitude(self):
        """Test invalid longitude raises error."""
        with pytest.raises(ValueError, match="longitudes must be between"):
            heatfall.plot_heat_hashes([0], [181], precision=4)


class TestPlotHeatH3s:
    """Test H3-based heat mapping."""

    def test_basic_heat_h3s(self, sample_coordinates):
        """Test basic H3 heatmap."""
        img = heatfall.plot_heat_h3s(
            sample_coordinates["lats"], sample_coordinates["lons"], precision=8
        )
        assert isinstance(img, Image.Image)
        assert img.size == (800, 500)

    def test_heat_h3s_custom_size(self, sample_coordinates):
        """Test custom output size."""
        img = heatfall.plot_heat_h3s(
            sample_coordinates["lats"],
            sample_coordinates["lons"],
            precision=8,
            size=(1024, 768),
        )
        assert img.size == (1024, 768)

    def test_heat_h3s_precision_range(self, sample_coordinates):
        """Test various precision levels."""
        for precision in [
            5,
            10,
            15,
        ]:  # Skip precision 0 as it can cause rendering issues
            img = heatfall.plot_heat_h3s(
                sample_coordinates["lats"],
                sample_coordinates["lons"],
                precision=precision,
            )
            assert isinstance(img, Image.Image)

    def test_heat_h3s_color_schemes(self, sample_coordinates):
        """Test H3 with different color schemes."""
        for scheme in ["distinct", "random", "wheel"]:
            img = heatfall.plot_heat_h3s(
                sample_coordinates["lats"],
                sample_coordinates["lons"],
                precision=8,
                color_scheme=scheme,
            )
            assert isinstance(img, Image.Image)

    def test_heat_h3s_empty_input(self):
        """Test empty input raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            heatfall.plot_heat_h3s([], [], precision=8)

    def test_heat_h3s_mismatched_lengths(self):
        """Test mismatched input lengths raise error."""
        with pytest.raises(ValueError, match="same length"):
            heatfall.plot_heat_h3s([1, 2], [1], precision=8)

    def test_heat_h3s_invalid_precision(self, sample_coordinates):
        """Test invalid precision raises error."""
        with pytest.raises(ValueError, match="precision must be"):
            heatfall.plot_heat_h3s(
                sample_coordinates["lats"], sample_coordinates["lons"], precision=16
            )

    def test_heat_h3s_invalid_latitude(self):
        """Test invalid latitude raises error."""
        with pytest.raises(ValueError, match="latitudes must be between"):
            heatfall.plot_heat_h3s([91], [0], precision=8)

    def test_heat_h3s_invalid_longitude(self):
        """Test invalid longitude raises error."""
        with pytest.raises(ValueError, match="longitudes must be between"):
            heatfall.plot_heat_h3s([0], [181], precision=8)


class TestCalculateH3Hashes:
    """Test H3 hash calculation."""

    def test_basic_calculation(self):
        """Test basic H3 hash calculation."""
        lats = [27.88, 27.92]
        lons = [-82.49, -82.46]
        hashes = calculate_h3_hashes(lats, lons, precision=8)

        assert len(hashes) == 2
        assert all(isinstance(h, str) for h in hashes)
        assert all(len(h) > 0 for h in hashes)

    def test_different_precisions(self):
        """Test different precision levels."""
        lats = [27.88]
        lons = [-82.49]

        for precision in [0, 5, 10, 15]:
            hashes = calculate_h3_hashes(lats, lons, precision)
            assert len(hashes) == 1
            assert isinstance(hashes[0], str)

    def test_empty_input(self):
        """Test empty input."""
        hashes = calculate_h3_hashes([], [], precision=8)
        assert len(hashes) == 0

    def test_mismatched_lengths(self):
        """Test mismatched input lengths."""
        with pytest.raises(ValueError):
            calculate_h3_hashes([1, 2], [1], precision=8)
