# Changelog

## [1.0.1] - 2026-10-02

### Fixed
- Preserve latitude/longitude order when rendering H3 cell boundaries.
- Validate coordinates in Context heatmap methods, including non-finite values.
- Use license metadata compatible with Python 3.8 build tools.
- Discover Python interpreters portably in tox.
- Use mock map tiles automatically in tests unless marked as integration tests.
- Include shared test fixtures and development configuration in source archives.
- Correct the Landfall circle examples to pass a sequence of radii.

### Changed
- Require landfall>=0.4.2 and geodude>=0.1.1.
- Add GitHub Actions checks for supported Python versions, macOS and Windows,
  code quality, and package builds.

## [1.0.0] - 2025-01-XX

### 🎉 Major Release - Complete Modernization

This is a major release representing a complete modernization of the heatfall package with significant improvements in reliability, functionality, and maintainability.

### Added
- **Multiple color schemes**: Choose from "distinct", "random", or "wheel" color palettes
- **Enhanced Context class**: Now extends landfall.Context for advanced map composition
- **Comprehensive type annotations**: Full type safety with mypy support
- **Input validation**: Robust validation on all public functions
- **Modern packaging**: Complete migration to `pyproject.toml` build system
- **Development infrastructure**: Full linting, formatting, and testing setup

### Changed
- **BREAKING**: Now built on top of landfall for improved infrastructure
- **BREAKING**: Removed custom `density_colors()` in favor of landfall's color system
- **BREAKING**: Simplified Context class by extending landfall.Context
- **BREAKING**: Removed unused plotting functions (plot_cluster, plot_super_cluster, etc.)
- Added `color_scheme` parameter to heatmap functions ("distinct", "random", "wheel")
- Updated Python version support to 3.8-3.13
- Modernized all dependencies to latest secure versions

### Improved
- **100% test coverage**: Comprehensive test suite ensuring reliability
- **Better color generation**: Using landfall's proven algorithms
- **Reduced code duplication**: ~160 lines removed, leveraging shared infrastructure
- **More consistent API**: Aligned with landfall sister package
- **Better error messages**: Clear, descriptive validation errors
- **Enhanced documentation**: Comprehensive examples and API reference

### Dependencies
- **Added**: landfall>=0.4.0 (core infrastructure)
- **Removed**: range_key_dict, more_itertools (now via landfall)
- **Kept**: pygeodesy, geodude, h3 (heatfall-specific)
- **Updated**: All dependencies to latest secure versions

### Migration Guide
- **Install landfall**: `pip install landfall>=0.4.0`
- **Replace custom colors**: Use `color_scheme="distinct"` (or "random"/"wheel")
- **Context usage**: Note that Context now extends landfall.Context
- **Backward compatibility**: Basic function calls remain the same

## [0.3.0] - 2025-01-XX

### Changed
- **BREAKING**: Now built on top of landfall for improved infrastructure
- **BREAKING**: Removed custom `density_colors()` in favor of landfall's color system
- Added `color_scheme` parameter to heatmap functions ("distinct", "random", "wheel")
- Simplified Context class by extending landfall.Context
- Removed unused plotting functions (plot_cluster, plot_super_cluster, etc.)

### Improved
- Better color generation using landfall's proven algorithms
- Reduced code duplication and maintenance burden
- More consistent API with landfall sister package
- Better test coverage leveraging landfall's infrastructure

### Dependencies
- Added: landfall>=0.4.0
- Removed: range_key_dict, more_itertools (now via landfall)
- Kept: pygeodesy, geodude, h3 (heatfall-specific)

### Migration Guide
- Replace calls with default colors to use `color_scheme="distinct"`
- If using Context directly, note it now extends landfall.Context
- Custom color schemes are no longer supported, use "distinct", "random", or "wheel"

## [0.2.0] - 2025-01-XX

### Fixed
- Fixed typo: `percision` → `precision` in function parameter
- Updated deprecated H3 API calls:
  - `h3.geo_to_h3()` → `h3.latlng_to_cell()`
  - `h3.h3_to_geo_boundary()` → `h3.cell_to_boundary()`

### Changed
- Migrated to modern `pyproject.toml` build system
- Updated Python version support to 3.8-3.13
- Updated all dependencies to latest secure versions
- Added comprehensive type annotations
- Added input validation to all public functions
- Added comprehensive test suite with 80%+ coverage

### Improved
- Complete type safety with mypy support
- Comprehensive docstrings for all public functions
- Modern packaging standards
- Better error messages and validation

## [0.1.0] - 2024-XX-XX

### Added
- Initial release
- Geohash-based heatmap plotting
- H3 hexagonal heatmap plotting
- Basic Context class for map composition
