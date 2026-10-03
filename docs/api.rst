API reference
=============

Plotting functions return Pillow images. Heat layer methods mutate a context and
return ``None``. Coordinate lists use latitude, longitude order in decimal
degrees. ``opacity`` is keyword-only and defaults to 0.6.

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
are ``color_scheme="distinct"``, OpenStreetMap tiles, ``size=(800, 500)``, and
``opacity=0.6``. The context heat methods share the coordinates, precision,
palette, and opacity arguments; configure tiles and dimensions when rendering.

See :doc:`usage` for examples, :doc:`data` for count semantics, and
:doc:`basemaps` for image and SVG output. Colors represent distinct count levels
within one layer; they do not form a guaranteed sequential scale.

Plotting functions
------------------

.. autofunction:: heatfall.plot_heat_hashes

.. autofunction:: heatfall.plot_heat_h3s

Map context
-----------

.. autoclass:: heatfall.Context
   :members: add_heat_hashes, add_heat_h3s

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
