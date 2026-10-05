"""
Heatfall: Heatmap visualization for geographic data using geohash and H3.

Built on top of landfall for robust geospatial plotting infrastructure.
"""

__version__ = "1.2.0"

from heatfall.heat import (
    plot_heat_hashes,
    plot_heat_h3s,
    Context,
)
from heatfall.legend import HeatLayerInfo, LegendOptions

__all__ = [
    "plot_heat_hashes",
    "plot_heat_h3s",
    "Context",
    "LegendOptions",
    "HeatLayerInfo",
]
