# Changelog

## [Unreleased]

## [1.2.0] - Unreleased

### Added
- Add `LegendOptions.background_opacity` (0–1) for translucent legend panels
  in Pillow, SVG, and Cairo without changing text or swatch opacity.
- Enable a discrete count legend by default for Pillow, SVG, and Cairo maps;
  allow disabling it or configuring position, anchor, units, offset, clipping,
  labels, columns, typography, panel colors, and spacing.
- Retain immutable per-layer metadata, including grid, precision, observation
  and cell totals, count levels, and the final count-to-RGBA mapping.
- Add a light-to-dark blue sequential palette and explicit shared
  `count_colors` mappings for comparable maps.
- Add visual examples for the default legend and shared H3/geohash colors.

### Changed
- Wrap legend titles by default to reduce unused panel width; expose
  `title_wrap`, `title_max_width`, and `title_line_spacing` controls and preserve
  explicit title line breaks across Pillow, SVG, and Cairo.
- Refine legend typography, spacing, swatch size, and panel styling; bundle
  scalable regular and bold fonts for consistent Pillow output.
- Align text and swatches across renderers, remove trailing row whitespace,
  and blend Pillow swatches over the legend panel rather than map content.
- Add visual previews of all nine legend positions at three sizes and a
  composed map with separately styled layer headings.
- Set the package version to 1.2.0 for the prepared release candidate.
- Document the legend's default-on behavior and the `legend=False` opt-out.
- Use concise numeric count labels by default; the legend title states the unit.

## [1.1.0] - 2026-10-03

Published to [PyPI](https://pypi.org/project/heatfall/1.1.0/) from
[tag `v1.1.0`](https://github.com/eddiethedean/heatfall/tree/v1.1.0).
All 14 jobs in the [release workflow](https://github.com/eddiethedean/heatfall/actions/runs/37095082186)
passed, including trusted publishing of the wheel and source archive.

### Changed
- Default geohash and H3 heat fills to 60% opacity so basemap details remain
  visible. Regenerate the README images with the new default.
- Require landfall>=0.4.2 and geodude>=0.1.1.
- Expand the README with rendered examples, API details, and troubleshooting.

### Added
- Add a keyword-only `opacity` option (0–1) to both plotting functions and
  Context heat layer methods; use `opacity=1` for solid fills.
- Add GitHub Actions checks for supported Python versions, macOS and Windows,
  code quality, and package builds.
- Add a Read the Docs configuration and a Sphinx documentation site with usage
  guides, geographic considerations, and an API reference generated from code.
- Link the README guides and package documentation metadata to the published
  Read the Docs site, and add a documentation build-status badge.
- Add pinned documentation dependencies, an isolated tox build, and a strict
  documentation check in GitHub Actions.
- Add a heat-colored documentation theme with light/dark modes, a visual
  landing page, copyable examples, and focused data, basemap, and troubleshooting
  guides.
- Replace the original illustration with a transparent hexagonal flame logo used in
  the README, documentation navigation, and browser icon.
- Add release instructions and CI validation of the installed wheel, dependency
  consistency, and downloadable distribution artifacts.
- Publish validated distributions to PyPI through trusted publishing when a
  matching `vX.Y.Z` tag is pushed; run the full CI suite before publishing.

### Fixed
- Composite antimeridian pieces together so translucent H3 cells do not acquire
  a darker seam where their pieces meet.
- Split H3 cell boundaries at the antimeridian using spherical intersections,
  preserving cell counts and colors across the resulting polygons.
- Keep automatic H3 map extents centered across ±180° longitude and remove
  artificial outlines between split pieces in all rendering backends.
- Close pole-containing H3 cells through their pole and limit their rendering
  to the Web Mercator latitude range.
- Preserve latitude/longitude order when rendering H3 cell boundaries.
- Validate coordinates in Context heatmap methods, including non-finite values.
- Use license metadata compatible with Python 3.8 build tools.
- Discover Python interpreters portably in tox.
- Use mock map tiles automatically in tests unless marked as integration tests.
- Include shared test fixtures and development configuration in source archives.
- Correct the Landfall circle examples to pass a sequence of radii.

## [1.0.0] - 2025-10-28

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
