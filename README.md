![Heatfall Logo](https://raw.githubusercontent.com/eddiethedean/heatfall/main/docs/heatfall_logo.png)
-----------------

# Heatfall: Easy to use functions for plotting heat maps of geographic data on static maps
[![PyPI Latest Release](https://img.shields.io/pypi/v/heatfall.svg)](https://pypi.org/project/heatfall/)
![Tests](https://github.com/eddiethedean/heatfall/actions/workflows/tests.yml/badge.svg)
[![Python Support](https://img.shields.io/pypi/pyversions/heatfall.svg)](https://pypi.org/project/heatfall/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎉 Version 1.0.0 - Major Release!

**Heatfall** has reached a major milestone! Version 1.0.0 represents a complete modernization of the package with significant improvements in reliability, functionality, and maintainability.

## What is it?

**Heatfall** is a modern, production-ready Python package with easy to use functions for plotting heat maps of geographic data on static maps. Built with type safety, comprehensive testing, and cross-platform compatibility in mind.

## ✨ Features

- 🗺️ **Easy heatmap plotting** - Plot heatmaps using geohash or H3 hexagonal binning
- 🎨 **Multiple color schemes** - Choose from distinct, random, or wheel color schemes
- 📍 **Geohash support** - Plot using geohash rectangular cells
- 🔷 **H3 hexagonal support** - Plot using H3 hexagonal cells for better coverage
- 🔧 **Built on landfall** - Leverages proven geospatial plotting infrastructure
- 🔧 **Type-safe** - Full type annotations with mypy support
- 🧪 **Well-tested** - Comprehensive test suite with 100% coverage across Python 3.8-3.13
- 🚀 **Modern packaging** - Built with modern `pyproject.toml` standards
- 🔄 **Cross-platform** - Works on Windows, macOS, and Linux
- 📦 **Minimal dependencies** - Only essential packages required

## 🆕 What's New in 1.0.0

### Major Improvements
- **Complete rewrite** with landfall integration for robust infrastructure
- **Enhanced color system** with three distinct color schemes
- **100% test coverage** ensuring reliability and stability
- **Modern Python packaging** with `pyproject.toml` and proper dependency management
- **Comprehensive type safety** with full type annotations
- **Input validation** on all public functions
- **Better error handling** with clear, descriptive error messages

### New Features
- **Color schemes**: Choose from "distinct", "random", or "wheel" color palettes
- **Enhanced Context class**: Extends landfall.Context for advanced map composition
- **Improved documentation**: Comprehensive examples and API reference
- **Development tools**: Full linting, formatting, and testing infrastructure

### Breaking Changes
- **API modernization**: Some internal functions removed (not part of public API)
- **Dependency changes**: Now requires landfall>=0.4.0
- **Color system**: Custom color schemes replaced with standardized options

## Requirements

- **Python 3.8-3.13** (comprehensive version support)
- **landfall>=0.4.0** (core geospatial plotting infrastructure)
- **pygeodesy** (geohash calculations)
- **geodude** (geohash utilities)
- **h3>=4.0.0** (H3 hexagonal indexing)

## Installation

### From PyPI
```sh
pip install heatfall
```

### Development Installation
```sh
pip install -e .[dev]
```

This installs the package in editable mode with development dependencies including:
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `mypy` - Type checking
- `ruff` - Linting and formatting
- `tox` - Multi-environment testing

## Quick Start

### Basic Geohash Heatmap
```python
import heatfall

# Plot heatmap using geohash binning
lats = [27.88, 27.92, 27.94]
lons = [-82.49, -82.49, -82.46]

# Default distinct colors
img = heatfall.plot_heat_hashes(lats, lons, precision=4)
img.save("heatmap.png")
```

### H3 Hexagonal Heatmap with Color Schemes
```python
import heatfall

# Plot heatmap using H3 hexagonal binning
lats = [27.88, 27.92, 27.94, 27.96, 27.98]
lons = [-82.49, -82.49, -82.46, -82.44, -82.42]

# Try different color schemes
img1 = heatfall.plot_heat_h3s(lats, lons, precision=8, color_scheme="distinct")
img2 = heatfall.plot_heat_h3s(lats, lons, precision=8, color_scheme="wheel")
img3 = heatfall.plot_heat_h3s(lats, lons, precision=8, color_scheme="random")
```

### Custom Map Size
```python
import heatfall

# Plot with custom output size
lats = [27.88, 27.92, 27.94]
lons = [-82.49, -82.49, -82.46]

img = heatfall.plot_heat_hashes(
    lats, lons, 
    precision=4, 
    size=(1024, 768)
)
img.save("large_heatmap.png")
```

### Advanced: Using Context with Landfall Integration
```python
import heatfall

# Create a context that extends landfall.Context
context = heatfall.Context()

# Add heatmap
context.add_heat_hashes(lats, lons, precision=4, color_scheme="distinct")

# Add regular points from landfall
context.add_points([27.9], [-82.5], colors=["red"], point_size=15)

# Add lines
context.add_line([(27.88, -82.49), (27.92, -82.49)], color="blue", width=3)

# Add polygons
context.add_polygons([
    [(27.85, -82.52), (27.95, -82.52), (27.95, -82.42), (27.85, -82.42)]
], color="green", width=2)

# Add circles
context.add_circles([27.9], [-82.5], radius_meters=1000, 
                   color="yellow", fill_transparency=50)

# Render everything together
image = context.render_pillow(800, 600)
image.save("combined_map.png")
```

### Real-World Example: Urban Planning Dashboard
```python
import heatfall

# Create comprehensive map with multiple data layers
context = heatfall.Context()

# Population density heatmap
context.add_heat_h3s(population_lats, population_lons, 
                    precision=7, color_scheme="distinct")

# Infrastructure points
context.add_points(hospital_lats, hospital_lons, 
                  colors=["red"], point_size=12)
context.add_points(school_lats, school_lons, 
                  colors=["blue"], point_size=10)

# Service area circles
context.add_circles(hospital_lats, hospital_lons, 
                   radius_meters=2000, color="red", fill_transparency=80)

# Road network
for road_segment in road_segments:
    context.add_line(road_segment, color="gray", width=2)

# City boundaries
context.add_polygons(city_boundaries, color="black", width=3)

# Render the complete dashboard
dashboard = context.render_pillow(1200, 800)
dashboard.save("urban_planning_dashboard.png")
```

### Delivery Route Optimization
```python
import heatfall

# Delivery optimization visualization
context = heatfall.Context()

# Delivery density heatmap
context.add_heat_hashes(delivery_lats, delivery_lons, 
                       precision=5, color_scheme="wheel")

# Optimal routes
for route in optimal_routes:
    context.add_line(route, color="blue", width=4)

# Depot locations
context.add_points(depot_lats, depot_lons, 
                  colors=["green"], point_size=15)

# Delivery zones
context.add_polygons(delivery_zones, color="orange", 
                    width=2, fill_transparency=60)

# Render optimization map
optimization_map = context.render_pillow(1024, 768)
optimization_map.save("delivery_optimization.png")
```

## API Reference

### Core Functions

- `plot_heat_hashes(lats, lons, precision, **kwargs)` - Plot geohash-based heatmap
- `plot_heat_h3s(lats, lons, precision, **kwargs)` - Plot H3-based heatmap
- `Context()` - Context class for complex map composition

### Parameters

- `lats`: List of latitude values (decimal degrees, -90 to 90)
- `lons`: List of longitude values (decimal degrees, -180 to 180)
- `precision`: 
  - For geohash: 1-12 (higher = smaller cells)
  - For H3: 0-15 (higher = smaller cells)
- `color_scheme`: Color scheme - "distinct" (default), "random", or "wheel"
- `size`: Output image size as (width, height) tuple
- `tileprovider`: Map tile provider (default: OpenStreetMap)

## Color Schemes

- **`distinct`** (default) - Visually distinct colors optimized for differentiation
- **`random`** - Random colors for each density level
- **`wheel`** - Colors from HSV color wheel for smooth gradients

## Development

### Setup Development Environment
```sh
git clone https://github.com/eddiethedean/heatfall.git
cd heatfall
pip install -e .[dev]
```

### Running Tests
```sh
# Run all tests
pytest

# Run with coverage
pytest --cov=heatfall

# Run specific test categories
pytest tests/test_heat.py      # Heat mapping tests
pytest tests/test_context.py   # Context tests
pytest tests/test_helpers.py   # Helper function tests

# Run tests across all Python versions
tox
```

### Code Quality
```sh
# Linting
ruff check src tests

# Type checking
mypy src

# Formatting
ruff format src tests

# All quality checks
tox -e ruff,mypy
```

### Multi-Version Testing
```sh
# Test across all supported Python versions (3.8-3.13)
tox

# Test specific Python versions
tox -e py38,py311,py313
```

## Dependencies

- **[landfall](https://github.com/eddiethedean/landfall)** - Core geospatial plotting infrastructure
- **[pygeodesy](https://github.com/mrJean1/PyGeodesy)** - Geohash calculations and geodesy tools
- **[geodude](https://github.com/eddiethedean/geodude)** - Geohash utilities
- **[h3](https://github.com/uber/h3-py)** - H3 hexagonal indexing system

## 🔗 Landfall Integration

Heatfall is built on top of **[landfall](https://github.com/eddiethedean/landfall)** for robust geospatial plotting infrastructure. This means you get the best of both worlds:

### Seamless Integration
```python
import heatfall

# heatfall.Context IS landfall.Context with extra heatmap methods
context = heatfall.Context()

# All landfall methods work perfectly
context.add_points(lats, lons, colors=["red"], point_size=10)
context.add_lines(route_coords, color="blue", width=3)
context.add_polygons(boundaries, color="green", width=2)
context.add_circles(centers, radius_meters=1000, color="yellow")

# Plus heatmap-specific methods
context.add_heat_hashes(lats, lons, precision=4, color_scheme="distinct")
context.add_heat_h3s(lats, lons, precision=8, color_scheme="wheel")

# Render everything together
img = context.render_pillow(800, 600)
```

### Why This Integration Matters
- **Single Context**: One context handles both heatmaps and regular plotting
- **Consistent API**: Same parameter patterns and styling across both packages
- **Shared Infrastructure**: Same tile providers, rendering engine, and color systems
- **Performance**: Single rendering pass for all elements
- **No Conflicts**: Automatic compatibility and version management

### Available Landfall Features
- **Points**: `add_points()` with custom colors and sizes
- **Lines**: `add_line()` and `add_lines()` for routes and boundaries
- **Polygons**: `add_polygons()` for areas and zones
- **Circles**: `add_circles()` for service areas and coverage
- **GeoJSON**: `add_geojson()` for complex geometries
- **Custom Styling**: Colors, transparency, widths, and more

## Related Projects

- **[landfall](https://github.com/eddiethedean/landfall)** - Sister package for general geospatial plotting on static maps

## Contributing

We welcome contributions! Please see our development guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make your changes** with tests
4. **Run quality checks**: `tox -e ruff,mypy`
5. **Run tests**: `tox`
6. **Submit a pull request**

## Migration from Previous Versions

### From 0.2.x to 1.0.0

**Breaking Changes:**
- Now requires `landfall>=0.4.0` as a dependency
- Custom color schemes are no longer supported
- Some internal functions have been removed

**Migration Steps:**
1. Update dependencies: `pip install landfall>=0.4.0`
2. Replace custom color calls with `color_scheme="distinct"` (or "random"/"wheel")
3. Update any direct Context usage to leverage new landfall integration

**Backward Compatibility:**
- Basic function calls remain the same: `plot_heat_hashes(lats, lons, precision)`
- Default behavior uses "distinct" colors (similar to previous behavior)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 **Documentation**: [GitHub README](https://github.com/eddiethedean/heatfall#readme)
- 🐛 **Issues**: [GitHub Issues](https://github.com/eddiethedean/heatfall/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/eddiethedean/heatfall/discussions)

---

**Made with ❤️ for the geospatial Python community**

*Version 1.0.0 - A major milestone in geospatial heatmap visualization*