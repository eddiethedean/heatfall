# Roadmap

## Phase 1.2 — Map legends and meaningful colors

**Status:** Implemented. **Target release:** 1.2.0.

Make each heat color understandable directly on an exported map, with legends
enabled by default and precise placement controls. Add complementary color and
metadata features so users can build readable, reproducible comparisons.

This phase describes the APIs introduced for 1.2.0. All feature tasks and
acceptance criteria are complete. Version 1.2.0 is prepared but not published.

### Scope and compatibility

- Support both geohash and H3 heat layers.
- Enable legends by default (`legend=True`) on both plotting functions and new
  contexts. Users can opt out with `legend=False` or `context.set_legend(False)`.
- Document the default visual change from 1.1.0; disabling the legend restores
  the previous appearance. Preserve existing plotting arguments, return types,
  default palettes, opacity, and map fitting.
- Support Pillow, SVG, and optional Cairo rendering with shared layout rules.
- Retain Python 3.8–3.13 support and avoid adding a plotting-library dependency.
- Colors and legend labels continue to represent raw observations per cell.

### HF12-01 — Retain heat layer metadata

- [x] Store one immutable metadata record per nonempty heat layer, including
  grid type, precision, optional label, observation total, occupied cell total,
  sorted distinct counts, and the exact final count-to-RGBA mapping.
- [x] Expose records through `context.heat_layers` as a read-only sequence of
  public `HeatLayerInfo` objects. Use immutable nested values rather than
  exposing internal color objects or mutable dictionaries.
- [x] Add keyword-only `legend_label=None` to both context heat methods.
- [x] Generate a palette once per layer. Rendering, repeated rendering, and
  metadata inspection must not regenerate colors or aggregate input again.
- [x] Validate new options before mutating map objects or layer metadata.
  Empty heat additions remain no-ops and produce no metadata or legend section.

**Acceptance:** Metadata matches rendered cells exactly, including opacity and
H3 cells split across the antimeridian. Each split cell counts as one cell.
Adding ordinary map objects does not create heat layer records.

### HF12-02 — Default legends with complete placement controls

- [x] Export `LegendOptions` and accept keyword-only
  `legend=True` on both plotting functions, accepting `False`, `True`, or
  `LegendOptions`.
- [x] Add `context.set_legend(False | True | LegendOptions)` so users can enable,
  reposition, or disable a legend after adding layers and between renders.
  New contexts start with legends enabled; contexts without nonempty heat
  layers render no legend.
- [x] Show one swatch for every distinct occupied-cell count, in configurable
  count order (high-to-low by default),
  with numeric default labels such as "1" and "8"; the legend title supplies
  the unit once ("Observations per cell").
- [x] Use the stored colors, including fill opacity. Do not infer meaning from
  palette order, merge different count values, or substitute a gradient.
- [x] Support nine named positions: `top-left`, `top-center`, `top-right`,
  `center-left`, `center`, `center-right`, `bottom-left`, `bottom-center`, and
  `bottom-right`.
- [x] Accept arbitrary `(x, y)` positions in `units="pixels"` or
  `units="fraction"`, measured from the output image's top-left. Fractions are
  multiplied by the final output width and height.
- [x] Support the same nine `anchor` values to select which point of the legend
  aligns with the requested position, signed pixel `offset=(dx, dy)`, and a
  pixel `margin` for preset positions. Presets use the matching anchor by
  default; coordinate positions default to `top-left`.
- [x] Default to `top-right`, a 12-pixel margin, and no offset. Never silently
  move a requested position or change the geographic extent or image size.
- [x] Reject nonfinite coordinates, unsupported options, and legends extending
  beyond the canvas by default. Provide `allow_clipping=True` for deliberate
  partial placement. Validate render-dependent bounds at render time.

**Acceptance:** The same controls work for every supported output backend and
image size. Omitting `legend` produces the same output as `legend=True`;
`legend=False` restores existing output. A legend renders once, even when
geographic objects repeat across world copies.

### HF12-03 — Legend styling and composed maps

- [x] Default to an opaque white panel with dark text and a subtle border;
  preserve the swatch's actual RGBA color when compositing onto the panel.
- [x] Allow `title`, `font_size`, `text_color`, `background_color`,
  `border_color`, `border_width`, `padding`, `swatch_size`, `row_spacing`, and
  `columns` to be configured. Title defaults to "Observations per cell";
  `title=None` hides it.
- [x] Use numeric `label_format`, such as `"{count} points"`, for custom units.
  Document that changing a label does not change the underlying aggregation.
- [x] Put multiple heat layers in separate sections, in addition order, using
  `legend_label` or fallback titles such as "H3 layer 1" and "Geohash layer 2".
  Never combine independent palettes into one shared count scale.
- [x] Lay entries out across the requested columns in ascending row order,
  measure the complete panel before positioning, and display every entry.
- [x] When content cannot fit, raise an actionable error suggesting additional
  columns, smaller styling, or a larger output. Only clip on explicit request.
- [x] Compose legends in image coordinates above ordinary map objects. Keep
  default placement clear of bottom attribution and document that custom
  placement must keep attribution visible.

**Acceptance:** Single-count layers, long labels, multiple sections, and large
counts remain readable. Repeated rendering does not duplicate sections or
change palette assignments. Text metrics can differ between backends, but
entry ordering, anchor behavior, and visibility must agree.

### HF12-04 — Sequential and explicit count colors

These additions complement the legend: an ordered palette makes increasing
counts easier to see, and explicit mappings make comparisons reproducible.

- [x] Add an opt-in `color_scheme="sequential"` with a documented, fixed
  light-to-dark blue ramp. Interpolate RGB by numeric count between the layer's
  minimum and maximum; use the ramp midpoint when all counts are equal.
- [x] Keep `distinct`, `wheel`, and `random` behavior unchanged. A sequential
  palette still receives a discrete exact-count legend.
- [x] Add keyword-only `count_colors=None` to both plotting functions and both
  heat layer methods. Accept a mapping of positive integer counts to color
  specifications, normalized through the existing staticmaps color facilities.
- [x] When supplied, use this mapping instead of `color_scheme` generation.
  Require a color for every observed count; permit extra counts so one mapping
  can serve several maps. Reject missing counts and invalid colors before
  mutating the context.
- [x] Apply layer opacity once while preserving any supplied color alpha.
  Store resulting RGBA values in metadata and use them unchanged for legends.
- [x] Document that automatic sequential scales remain relative to each layer;
  use a shared explicit mapping for matching counts across maps.
- [x] Add a default heatmap scale with five fixed blue/green/yellow/orange/red
  colors and finite inclusive count ranges in its legend; retain the blue
  sequential scale as an alternative.
- [x] Order legend ranges high-to-low by default and allow low-to-high ordering
  with `LegendOptions(count_order="ascending")`.

**Acceptance:** Equal counts have identical colors under a shared mapping,
regardless of grid, input ordering, or other counts present. Sequential colors
are deterministic, increase in darkness with count, and work for a single count.

### Proposed usage

These examples use the implemented interface:

```python
import heatfall

# Legends are enabled automatically.
heatfall.plot_heat_h3s(lats, lons, precision=8).save("default-legend.png")

# Opt out to retain the previous appearance.
heatfall.plot_heat_h3s(
    lats, lons, precision=8, legend=False,
).save("heatmap-without-legend.png")

image = heatfall.plot_heat_h3s(
    lats, lons, precision=8,
    color_scheme="sequential",
    legend=heatfall.LegendOptions(
        position=(0.95, 0.10),
        units="fraction",
        anchor="top-right",
        offset=(-8, 0),
        title="Observations per cell",
        columns=1,
    ),
)
image.save("heatmap-with-legend.png")

context = heatfall.Context()
context.add_heat_h3s(
    lats, lons, precision=8,
    legend_label="Morning observations",
    count_colors={1: "#deebf7", 4: "#9ecae1", 8: "#3182bd"},
)
context.set_legend(heatfall.LegendOptions(position=(24, 24), units="pixels"))
context.render_pillow(800, 500).save("morning.png")
context.set_legend(False)
```

The explicit mapping example assumes observed counts are covered by 1, 4, and 8.

### HF12-05 — Verification, examples, and release preparation

- [x] Add focused tests for palette/legend equality, metadata immutability,
  multiple layers, empty layers, opacity, explicit mappings, and single counts.
- [x] Cover all presets, anchors, pixel/fraction coordinates, signed offsets,
  bounds errors, clipping, columns, long labels, and different canvas sizes.
- [x] Verify omitted `legend` and explicit `legend=True` produce identical
  output with deterministic colors on both plotting functions and new contexts.
  Verify `legend=False` and `context.set_legend(False)` against the existing
  behavior; retain opacity and antimeridian regression coverage.
- [x] Exercise Pillow and SVG output plus optional Cairo behavior. Verify
  inherited render signatures and return types before adding render overrides.
- [x] Add `src/heatfall/legend.py` for configuration, metadata types, and shared
  layout; integrate layer capture and rendering in `heat.py`, with public
  exports in `__init__.py`. Put new tests in `tests/test_legend.py` and
  `tests/test_colors.py`.
- [x] Update README, API reference, usage, basemap/output, and troubleshooting
  guides. Replace statements that Heatfall cannot add a numeric legend.
- [x] Extend `examples/generate_doc_maps.py` with a legend map and a comparison
  using a shared mapping. Visually inspect exports, text, and attribution.
- [x] Pass the existing test matrix and 100% statement coverage requirement,
  Ruff, mypy, strict Sphinx build, and installed-wheel/package checks.
- [x] Record completed behavior in the changelog and update both version sources
  to 1.2.0 for the prepared but unpublished release candidate.

### Execution order and completion

Phase 1.2 is complete. The 1.2.0 release candidate passes the locally available
Python-version test matrix, code quality, documentation, and package checks.

Weighted observations, count binning, density normalization, interactive map
controls, arbitrary non-heat legends, and expanded canvases for outside-map
panels belong to later phases.
