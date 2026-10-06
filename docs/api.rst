API reference
=============

.. container:: hf-section-intro

   Choose a plotting function for a single map, a context for composed layers,
   and legend options for the final map key. This reference follows the current
   source.

.. note::

   The ``rng`` and plotting ``api_key`` keywords require Heatfall 1.3.0 or newer.
   See :doc:`installation` to check your version or install from source.

Plotting functions return Pillow images. Heat layer methods mutate a context and
return ``None``. Coordinate lists use latitude, longitude order in decimal
degrees. ``opacity`` is keyword-only and defaults to 0.6. Legends are enabled
by default; set ``legend=False`` to disable a legend.

Choosing an entry point
-----------------------

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Task
     - Entry point
   * - Render geohash rectangles
     - :func:`heatfall.plot_heat_hashes`
   * - Render H3 cells
     - :func:`heatfall.plot_heat_h3s`
   * - Add heat to a composed map
     - :class:`heatfall.Context`

Both plotting functions require ``lats``, ``lons``, and ``precision``. Defaults
are ``color_scheme="heatmap"``, OpenStreetMap tiles, ``size=(800, 500)``,
``opacity=0.6``, and ``legend=True``. The context heat methods share the
coordinates, precision, palette, and opacity arguments; they also accept
``legend_label`` and ``count_colors``. Both entry points accept ``rng`` in
Heatfall 1.3.0. Configure tiles and dimensions when
rendering.

Plotting functions also accept an optional ``api_key`` for the selected tile
provider. Contexts inherit ``set_tile_provider(provider, api_key=...)``.
See :doc:`basemaps` for a keyed provider example.

See :doc:`usage` for legend placement and fixed color examples,
:doc:`data` for count semantics, and :doc:`basemaps` for image and SVG output.
The default ``heatmap`` color scheme runs from blue through green, yellow, and
orange to red as counts increase. The ``sequential`` scheme runs light to dark
blue. ``distinct``, ``wheel``, and ``random`` represent count levels without
implying an order.

Legends use nine named positions or arbitrary pixel/fraction coordinates,
anchors, signed offsets, and styling controls through
:class:`heatfall.LegendOptions`. ``context.heat_layers`` returns an immutable
sequence of :class:`heatfall.HeatLayerInfo` records with each layer's exact
count-to-RGBA palette.

Important input and validation details
---------------------------------------

* All coordinate lists must have matching lengths and contain finite decimal
  degree values. The plotting functions require at least one coordinate and
  raise ``ValueError`` for empty lists; context heat methods accept empty lists
  as a no-op. Heatfall also raises ``ValueError`` for invalid coordinates,
  unsupported precision, invalid colors, and opacity outside 0–1 inclusive.
* ``count_colors`` is a mapping of positive integer observation counts to
  color values. Every count in the input must have an entry; extra entries are
  allowed so a mapping can be shared across datasets. Values may be color
  names, hexadecimal strings, ``staticmaps.Color`` objects, or RGB/RGBA tuples.
  When supplied, this mapping takes precedence over ``color_scheme``.
* ``rng`` is an integer seed or ``None``. For ``"random"`` and ``"distinct"``,
  the same seed and the same sorted set of observed counts reproduce the
  palette. A seed does not affect ``"heatmap"``, ``"sequential"``, ``"wheel"``,
  or explicit ``count_colors``. Use a fixed mapping when datasets contain
  different count levels. Boolean and non-integer seeds raise ``ValueError``.
* ``LegendOptions.label_format`` must be a Python format string containing
  ``{count}``. Only that field is supported; a numeric format such as
  ``"{count:,} observations"`` is valid. For the default heatmap palette, the
  format is applied to both endpoints of each inclusive range.
* Legend ``position`` accepts a named anchor or a finite ``(x, y)`` pair.
  Named positions use ``margin`` in pixels. Custom positions use ``units``
  (``"pixels"`` or ``"fraction"``); ``anchor`` selects the point of the panel
  aligned to that position and ``offset`` remains in pixels. Layout that
  extends past the image raises ``ValueError`` unless ``allow_clipping=True``.
* ``background_opacity`` and ``shadow_opacity`` are finite values from 0 to 1.
  Font sizes, columns, and swatch size must be positive integers. See the
  :class:`heatfall.LegendOptions` members below for defaults and other fields.

``HeatLayerInfo`` fields
------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Field
     - Meaning
   * - ``grid``
     - ``"geohash"`` or ``"h3"``.
   * - ``precision``
     - Geohash precision or H3 resolution used for this layer.
   * - ``label``
     - Optional section label supplied with ``legend_label``.
   * - ``observation_count``
     - Number of input observations, including repeated coordinates.
   * - ``cell_count``
     - Number of occupied grid cells. Antimeridian display fragments count as
       their original cell, not as additional cells.
   * - ``counts``
     - Sorted distinct raw observation counts in occupied cells.
   * - ``count_colors``
     - Immutable ``(count, RGBA)`` pairs using the final colors and alpha.
   * - ``legend_ranges``
     - Immutable inclusive count ranges used by the default five-step
       ``"heatmap"`` palette; empty for other palettes and explicit mappings.

Legend titles wrap automatically to fit the entry width, keeping single-column
legends compact. Set ``title_wrap=False`` to keep each title paragraph on one
line, or ``title_max_width`` to choose a wrapping width in pixels. Long words
split if needed to meet an explicit width. Newline characters create deliberate
line breaks, and ``title_line_spacing`` sets the gap between wrapped lines.

``background_opacity`` ranges from 0 (transparent) to 1 (full color opacity).
It multiplies the alpha of ``background_color`` so heat cells show through the legend panel;
text, swatches, borders, and shadows keep their own colors and opacity. For
example, the default white panel is translucent; use a more transparent panel
and a narrower title like this:

.. code-block:: python

   legend = heatfall.LegendOptions(
       background_color="white",
       background_opacity=0.65,
       title_max_width=160,
   )

See :doc:`usage` for the legend placement and size gallery, background
transparency preview, and positioning examples.

Plotting functions
------------------

.. autofunction:: heatfall.plot_heat_hashes

.. autofunction:: heatfall.plot_heat_h3s

Map context
-----------

.. autoclass:: heatfall.Context
   :members: add_heat_hashes, add_heat_h3s, set_legend, heat_layers

Legend configuration
--------------------

.. autoclass:: heatfall.LegendOptions
   :members:

Heat layer metadata
-------------------

.. autoclass:: heatfall.HeatLayerInfo
   :members:

Rendering and ordinary map layers are inherited from
`Landfall's Context <https://landfall.readthedocs.io/en/latest/api/#context>`_
and py-staticmaps. For example, call ``context.render_pillow(800, 500)`` after
adding a heat layer.

For inherited functionality, see these Landfall guides:

* `Points <https://landfall.readthedocs.io/en/latest/shapes-and-styling/#points>`_
  for ``add_point`` and ``add_points`` styling.
* `Routes <https://landfall.readthedocs.io/en/latest/shapes-and-styling/#routes>`_
  for ``add_line`` and ``add_lines`` styling.
* `Circles <https://landfall.readthedocs.io/en/latest/shapes-and-styling/#circles>`_
  for radius units and fill colors.
* `Polygons <https://landfall.readthedocs.io/en/latest/shapes-and-styling/#polygons>`_
  for outlines, transparent fills, and interior holes.
* `GeoJSON and GeoPandas <https://landfall.readthedocs.io/en/latest/geospatial-data/>`_
  for plotting GIS data with ``context=heatfall.Context()``. See
  :doc:`usage` for examples that keep the heat layers and legend.
* `Combining shapes and exporting SVG <https://landfall.readthedocs.io/en/latest/shapes-and-styling/#combine-shapes-and-export-svg>`_
  for ``render_pillow`` and ``render_svg`` output.
* `Custom tile services <https://landfall.readthedocs.io/en/latest/custom-tile-service/>`_
  for basemap configuration.
* `Full py-staticmaps API <https://landfall.readthedocs.io/en/latest/py-staticmaps/>`_
  for native map objects, framing, bounds padding, and renderer controls inherited
  through Landfall.
