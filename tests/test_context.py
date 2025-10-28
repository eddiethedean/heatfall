"""Tests for Context class functionality."""

from PIL import Image
import staticmaps

from heatfall.heat import Context


class TestContext:
    """Test Context class methods."""

    def test_context_creation(self):
        """Test basic context creation."""
        context = Context()
        assert isinstance(context, staticmaps.Context)

    def test_add_heat_hashes_with_context(self, sample_coordinates):
        """Test adding heatmap to existing context."""
        context = Context()
        context.add_heat_hashes(
            sample_coordinates["lats"],
            sample_coordinates["lons"],
            precision=4,
            color_scheme="distinct",
        )
        # Should not raise exceptions
        assert True

    def test_add_heat_h3s_with_context(self, sample_coordinates):
        """Test adding H3 heatmap to existing context."""
        context = Context()
        context.add_heat_h3s(
            sample_coordinates["lats"],
            sample_coordinates["lons"],
            precision=8,
            color_scheme="wheel",
        )
        # Should not raise exceptions
        assert True

    def test_add_heat_hashes_color_schemes(self, sample_coordinates):
        """Test different color schemes with heat hashes."""
        context = Context()
        for scheme in ["distinct", "random", "wheel"]:
            context.add_heat_hashes(
                sample_coordinates["lats"],
                sample_coordinates["lons"],
                precision=4,
                color_scheme=scheme,
            )
        # Should not raise exceptions
        assert True

    def test_add_heat_h3s_color_schemes(self, sample_coordinates):
        """Test different color schemes with H3 heatmaps."""
        context = Context()
        for scheme in ["distinct", "random", "wheel"]:
            context.add_heat_h3s(
                sample_coordinates["lats"],
                sample_coordinates["lons"],
                precision=8,
                color_scheme=scheme,
            )
        # Should not raise exceptions
        assert True

    def test_render_pillow(self):
        """Test rendering to PIL Image."""
        context = Context()
        # Add some content so we can render
        context.add_heat_hashes([27.88], [-82.49], precision=4)
        img = context.render_pillow(800, 500)
        assert isinstance(img, Image.Image)
        assert img.size == (800, 500)

    def test_render_pillow_custom_size(self):
        """Test rendering with custom size."""
        context = Context()
        # Add some content so we can render
        context.add_heat_hashes([27.88], [-82.49], precision=4)
        img = context.render_pillow(1024, 768)
        assert isinstance(img, Image.Image)
        assert img.size == (1024, 768)
