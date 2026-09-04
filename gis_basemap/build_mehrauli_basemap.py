"""Build a GIS basemap for Mehrauli, Delhi from OpenStreetMap.

Outputs GeoJSON layers suitable for QGIS/ArcGIS:
  data/mehrauli_boundary.geojson
  data/buildings.geojson
  data/roads.geojson
  data/landuse.geojson
  data/waterways.geojson
  data/pois.geojson
  data/greenspace.geojson

Note: OSM is volunteered geographic information. This is a planning base,
not a cadastral/survey base. Coordinate system for exported data: EPSG:4326.
"""
from pathlib import Path
import geopandas as gpd
import osmnx as ox

OUT = Path("data")
OUT.mkdir(exist_ok=True)
PLACE = "Mehrauli, Delhi, India"
ox.settings.use_cache = True
ox.settings.log_console = True

# 1. Geocoded Mehrauli polygon
boundary = ox.geocode_to_gdf(PLACE)
boundary = boundary[["geometry"]].to_crs(4326)
boundary.to_file(OUT / "mehrauli_boundary.geojson", driver="GeoJSON")
poly = boundary.geometry.iloc[0]

# 2. Building footprints
buildings = ox.features_from_polygon(poly, tags={"building": True})
if len(buildings):
    buildings = buildings.reset_index()
    buildings = buildings[[c for c in ["osmid","building","name","geometry"] if c in buildings.columns]]
    buildings = buildings.to_crs(4326)
    buildings.to_file(OUT / "buildings.geojson", driver="GeoJSON")

# 3. Road centre-lines
G = ox.graph_from_polygon(poly, network_type="all", simplify=True)
roads = ox.graph_to_gdfs(G, nodes=False, edges=True, fill_edge_geometry=True).reset_index()
keep = [c for c in ["u","v","key","osmid","name","highway","lanes","maxspeed","oneway","surface","geometry"] if c in roads.columns]
roads = roads[keep].to_crs(4326)
roads.to_file(OUT / "roads.geojson", driver="GeoJSON")

# 4. Land use / open areas
landuse = ox.features_from_polygon(poly, tags={"landuse": True})
if len(landuse):
    landuse = landuse.reset_index()
    keep = [c for c in ["osmid","landuse","name","geometry"] if c in landuse.columns]
    landuse = landuse[keep].to_crs(4326)
    landuse.to_file(OUT / "landuse.geojson", driver="GeoJSON")

# 5. Water
water = ox.features_from_polygon(poly, tags={"waterway": True})
if len(water):
    water = water.reset_index()
    keep = [c for c in ["osmid","waterway","name","geometry"] if c in water.columns]
    water = water[keep].to_crs(4326)
    water.to_file(OUT / "waterways.geojson", driver="GeoJSON")

# 6. Green/open space
green_tags = {"leisure": ["park","garden","pitch","sports_centre"], "natural": ["wood","grassland"]}
green = ox.features_from_polygon(poly, tags=green_tags)
if len(green):
    green = green.reset_index()
    keep = [c for c in ["osmid","leisure","natural","name","geometry"] if c in green.columns]
    green = green[keep].to_crs(4326)
    green.to_file(OUT / "greenspace.geojson", driver="GeoJSON")

# 7. Major POIs / landmarks
poi_tags = {"amenity": True, "tourism": True, "historic": True, "shop": True, "public_transport": True}
pois = ox.features_from_polygon(poly, tags=poi_tags)
if len(pois):
    pois = pois.reset_index()
    keep = [c for c in ["osmid","name","amenity","tourism","historic","shop","public_transport","geometry"] if c in pois.columns]
    pois = pois[keep].to_crs(4326)
    pois.to_file(OUT / "pois.geojson", driver="GeoJSON")

print("Mehrauli GIS basemap build complete. Layers written to data/.")
