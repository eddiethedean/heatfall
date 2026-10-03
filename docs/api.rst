API reference
=============

Plotting functions return Pillow images. Heat layer methods mutate a context and
return ``None``. Coordinate lists use latitude, longitude order in decimal
degrees. ``opacity`` is keyword-only and defaults to 0.6.

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
