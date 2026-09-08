"""Geospatial helpers: GeoJSON <-> shapely conversion, zone grid generation,
point-in-polygon lookups, and distance calculation.

Zone grid generation uses a local equirectangular (flat-earth) projection
centered on the field's centroid. This is an intentional approximation
suitable for farm-sized fields (tens to a few hundred metres across); it is
not valid for large-scale geodesy.
"""
import math

from shapely.geometry import LineString, Point, Polygon, mapping, shape
from shapely.ops import transform

EARTH_RADIUS_M = 6371000.0


def geojson_to_shapely(geojson: dict):
    return shape(geojson)


def shapely_to_geojson(geom) -> dict:
    return mapping(geom)


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def _local_projection(lat0: float, lon0: float):
    """Returns (to_local, to_geo) coordinate transform functions (metres <-> lon/lat)."""
    m_per_deg_lat = 110540.0
    m_per_deg_lon = 111320.0 * math.cos(math.radians(lat0))

    def to_local(lon, lat, z=None):
        return ((lon - lon0) * m_per_deg_lon, (lat - lat0) * m_per_deg_lat)

    def to_geo(x, y, z=None):
        return (lon0 + x / m_per_deg_lon, lat0 + y / m_per_deg_lat)

    return to_local, to_geo


def point_in_polygon(lat: float, lon: float, polygon: Polygon) -> bool:
    return polygon.contains(Point(lon, lat)) or polygon.touches(Point(lon, lat))


def generate_zone_grid(boundary: Polygon, resolution_m: float) -> list[tuple[str, Polygon]]:
    """Generate a resolution_m x resolution_m grid clipped to the field boundary.
    Returns a list of (zone_code, polygon-in-lon/lat) tuples ordered row-major (Z1, Z2, ...).
    """
    centroid = boundary.centroid
    to_local, to_geo = _local_projection(centroid.y, centroid.x)

    local_boundary = transform(to_local, boundary)
    minx, miny, maxx, maxy = local_boundary.bounds

    cols = max(1, math.ceil((maxx - minx) / resolution_m))
    rows = max(1, math.ceil((maxy - miny) / resolution_m))

    zones: list[tuple[str, Polygon]] = []
    index = 1
    for r in range(rows):
        for c in range(cols):
            cell_minx = minx + c * resolution_m
            cell_miny = miny + r * resolution_m
            cell = Polygon(
                [
                    (cell_minx, cell_miny),
                    (cell_minx + resolution_m, cell_miny),
                    (cell_minx + resolution_m, cell_miny + resolution_m),
                    (cell_minx, cell_miny + resolution_m),
                    (cell_minx, cell_miny),
                ]
            )
            clipped = cell.intersection(local_boundary)
            if clipped.is_empty or clipped.area <= 0:
                continue
            geo_clipped = transform(to_geo, clipped)
            if geo_clipped.geom_type != "Polygon":
                # MultiPolygon slivers from an irregular boundary edge; keep the largest piece
                largest = max(geo_clipped.geoms, key=lambda g: g.area, default=None)
                if largest is None or largest.is_empty:
                    continue
                geo_clipped = largest
            zones.append((f"Z{index}", geo_clipped))
            index += 1

    return zones


def polygon_area_local_m2(boundary: Polygon) -> float:
    """Approximate planar area in m^2 using the local equirectangular projection.
    Used as a fallback when PostGIS geography area isn't available (e.g. unit tests)."""
    centroid = boundary.centroid
    to_local, _ = _local_projection(centroid.y, centroid.x)
    return abs(transform(to_local, boundary).area)


def route_distance_m(points: list[tuple[float, float]]) -> float:
    """points: list of (lat, lon) ordered by time."""
    total = 0.0
    for (lat1, lon1), (lat2, lon2) in zip(points, points[1:]):
        total += haversine_m(lat1, lon1, lat2, lon2)
    return total


def points_to_linestring_geojson(points: list[tuple[float, float]]) -> dict:
    """points: list of (lat, lon) -> GeoJSON LineString (lon, lat)."""
    ls = LineString([(lon, lat) for lat, lon in points]) if len(points) >= 2 else None
    return mapping(ls) if ls else {"type": "LineString", "coordinates": []}
