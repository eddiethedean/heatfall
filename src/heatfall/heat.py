"""
Functions for plotting heatmaps of points.
"""

from typing import Optional

import staticmaps
import pygeodesy
from range_key_dict import RangeKeyDict
from geodude import calculate_geohashes
from tinytim.columns import value_counts
from more_itertools import numeric_range


tp = staticmaps.tile_provider_OSM
TRED = staticmaps.Color(255, 0, 0, 100)
RED = staticmaps.RED
TYELLOW = staticmaps.Color(255, 255, 0, 100)
YELLOW = staticmaps.YELLOW
TGREEN = staticmaps.Color(0, 255, 0, 100)
GREEN = staticmaps.GREEN
TBLUE = staticmaps.Color(0, 0, 255, 100)
BLUE = staticmaps.BLUE


class Context(staticmaps.Context):
    def add_hash_poly(
        self,
        h,
        fill_color,
        width,
        color
    ) -> None:
        self.add_object(staticmaps.Area(
            make_hash_poly_points(h),
            fill_color=fill_color,
            width=width,
            color=color))

    def add_neighbor_hash_polys(
        self,
        h, 
        fill_color,
        width,
        color
    ) -> None:
        hashes = pygeodesy.geohash.neighbors(h)
        for n in hashes.values():
            self.add_object(staticmaps.Area(make_hash_poly_points(n),
                                            fill_color=fill_color,
                                            width=width,
                                            color=color))

    def add_cluster(
        self,
        cluster,
        size=6,
        color: staticmaps.Color=RED,
        fill_color: Optional[staticmaps.Color]=None,
        width=2,
        colors=None
    ) -> None:
        for lat, lon, id, day in zip(cluster.lats, cluster.lons, cluster.ids, cluster.days):
            if colors is not None:
                color = colors[id]
            point = staticmaps.create_latlng(lat, lon)
            self.add_object(staticmaps.Marker(point, color=color, size=size))
    def add_heat_hashes(self, lats, lons, precision):
        hashes = calculate_geohashes(lats, lons, precision)
        counts = dict(value_counts(hashes))
        colors = density_colors(list(counts.values()))
        for h, count in counts.items():
            c = colors[count]
            self.add_hash_poly(h, c, 1, staticmaps.TRANSPARENT)


def plot_heat_hashes(
    lats,
    lons,
    percision,
    tileprovider=tp,
    size=(800, 500)
):
    context = Context()
    context.set_tile_provider(tileprovider)
    context.add_heat_hashes(lats, lons, percision)
    return context.render_pillow(*size)


def density_colors(counts: list, transparency=150):
   RED = staticmaps.Color(255, 0, 0, transparency)
   ORANGE = staticmaps.Color(255, 128, 0, transparency)
   YELLOW = staticmaps.Color(255, 255, 0, transparency)
   GREEN = staticmaps.Color(0, 255, 0, transparency)
   BLUE = staticmaps.Color(0, 0, 255, transparency)
   colors = [BLUE, GREEN, YELLOW, ORANGE, RED]
   counts = [n for n in counts if n>0]
   chunks = len(colors)
   lowest = min(counts)
   highest = max(counts)

   if len(set(counts))==1:
       ranges =[(lowest, highest+.1)]
       return RangeKeyDict({r:c for r, c in zip(ranges, colors)})
   chunk_size = (highest - lowest) /chunks
   previous = None
   ranges = []
   for i in numeric_range(lowest, highest+.1, chunk_size):
       if previous is not None:
           ranges.append((previous, i))
       previous = i
   ranges[-1] = ranges[-1][0], ranges[-1][1]+.1
   return RangeKeyDict({r:c for r, c in zip(ranges, colors)})


def plot_cluster(cluster, tileprovider=tp, size=(800, 500)):
    context = Context()
    context.set_tile_provider(tileprovider)
    context.add_cluster(cluster,
                        fill_color=staticmaps.parse_color('#00FF003F'),
                        width=2,
                        color=staticmaps.BLUE)
    return context.render_pillow(*size)


def plot_super_cluster(hashes, tileprovider=tp, size=(800, 500)):
    context = Context()
    context.set_tile_provider(tileprovider)
    for h in hashes:
        context.add_hash_poly(h,
                             fill_color=staticmaps.parse_color('#00FF003F'),
                             width=2,
                             color=staticmaps.BLUE)
    return context.render_pillow(*size)


def plot_heat_map(super_cluster, p, tileprovider=tp, size=(800, 500)):
    context = Context()
    context.set_tile_provider(tileprovider)
    lats, lons = super_cluster.lats, super_cluster.lons
    context.add_heat_hashes(lats, lons, p)
    return context.render_pillow(*size)


def make_hash_poly_points(h):
    b = pygeodesy.geohash.bounds(h)
    sw = b.latS, b.lonW
    nw = b.latN, b.lonW
    ne = b.latN, b.lonE
    se = b.latS, b.lonE
    polygon = [sw, nw, ne, se, sw]
    return [staticmaps.create_latlng(lat, lon) for lat, lon in polygon]


def plot_hash(h, tileprovider=tp, size=(800, 500)):
    context = Context()
    context.set_tile_provider(tileprovider)
    context.add_hash_poly(h,
                          fill_color=staticmaps.parse_color('#00FF003F'),
                          width=2,
                          color=staticmaps.BLUE)
    return context.render_pillow(*size)


def plot_neighbors(h, tileprovider=tp, size=(800, 500)):
    context = Context()
    context.set_tile_provider(tileprovider)
    context.add_neighbor_hash_polys(
        h,
        fill_color=staticmaps.parse_color('#00FF003F'),
        width=2,
        color=staticmaps.BLUE)
    return context.render_pillow(*size)


def plot_nine(h, tileprovider=tp, size=(800, 500)):
    context = Context()
    context.set_tile_provider(tileprovider)
    context.add_hash_poly(h,
                          fill_color=staticmaps.parse_color('#00FF010F'),
                          width=5,
                          color=staticmaps.BLUE)
    context.add_neighbor_hash_polys(h,
                                    fill_color=staticmaps.parse_color('#00FF003F'),
                                    width=2,
                                    color=staticmaps.BLUE)
    return context.render_pillow(*size)