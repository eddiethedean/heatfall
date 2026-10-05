API reference
=============

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
``legend_label`` and ``count_colors``. Configure tiles and dimensions when
rendering.

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
* `Combining shapes and exporting SVG <https://landfall.readthedocs.io/en/latest/shapes-and-styling/#combine-shapes-and-export-svg>`_
  for ``render_pillow`` and ``render_svg`` output.
* `Custom tile services <https://landfall.readthedocs.io/en/latest/custom-tile-service/>`_
  for basemap configuration.
