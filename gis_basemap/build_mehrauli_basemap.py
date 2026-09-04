"""Build a QGIS-ready Mehrauli, Delhi planning basemap from OpenStreetMap.

Outputs:
  data/mehrauli_gis_basemap.gpkg       -> master QGIS GeoPackage
  data/*.geojson                       -> portable source exports
  data/projected/*.gpkg                -> metric EPSG:32643 copies

Layer names are deliberately standardized for direct QGIS use.
Note: OSM is volunteered geographic information; this is not a cadastral,
survey, or official Ward 155 boundary dataset.
"""
from pathlib import Path
import geopandas as gpd
import osmnx as ox

OUT = Path("data")
PROJECTED = OUT / "projected"
OUT.mkdir(exist_ok=True)
PROJECTED.mkdir(exist_ok=True)
PLACE = "Mehrauli, Delhi, India"
SRC_CRS = "EPSG:4326"
WORK_CRS = "EPSG:32643"
GPKG = OUT / "mehrauli_gis_basemap.gpkg"
ox.settings.use_cache = True
ox.settings.log_console = True

# Remove old master GeoPackage so reruns are deterministic.
if GPKG.exists():
    GPKG.unlink()

def save_layer(gdf, name):
    if gdf is None or gdf.empty:
        return
    gdf = gdf.copy().to_crs(SRC_CRS)
    gdf.to_file(GPKG, layer=name, driver="GPKG")
    gdf.to_file(OUT / f"{name}.geojson", driver="GeoJSON")
    gdf.to_crs(WORK_CRS).to_file(PROJECTED / f"{name}.gpkg", layer=name, driver="GPKG")

# 1. Mehrauli geocoded planning boundary
boundary = ox.geocode_to_gdf(PLACE)[["geometry"]].to_crs(SRC_CRS)
boundary["layer"] = "BOUNDARY"
save_layer(boundary, "boundary")
poly = boundary.geometry.iloc[0]

# 2. Buildings
buildings = ox.features_from_polygon(poly, tags={"building": True})
if len(buildings):
    buildings = buildings.reset_index()
    keep = [c for c in ["osmid","building","name","levels","height","geometry"] if c in buildings.columns]
    save_layer(buildings[keep], "buildings")

# 3. Roads / centre-lines
G = ox.graph_from_polygon(poly, network_type="all", simplify=True)
roads = ox.graph_to_gdfs(G, nodes=False, edges=True, fill_edge_geometry=True).reset_index()
keep = [c for c in ["u","v","key","osmid","name","highway","lanes","maxspeed","oneway","surface","lit","geometry"] if c in roads.columns]
roads = roads[keep]
if "highway" in roads.columns:
    roads["road_class"] = roads["highway"].apply(lambda x: x[0] if isinstance(x, list) else x)
save_layer(roads, "roads")

# 4. Land use
landuse = ox.features_from_polygon(poly, tags={"landuse": True})
if len(landuse):
    landuse = landuse.reset_index()
    keep = [c for c in ["osmid","landuse","name","geometry"] if c in landuse.columns]
    save_layer(landuse[keep], "landuse")

# 5. Waterways
water = ox.features_from_polygon(poly, tags={"waterway": True})
if len(water):
    water = water.reset_index()
    keep = [c for c in ["osmid","waterway","name","geometry"] if c in water.columns]
    save_layer(water[keep], "waterways")

# 6. Green/open space
green = ox.features_from_polygon(poly, tags={"leisure": ["park","garden","pitch","sports_centre"], "natural": ["wood","grassland"]})
if len(green):
    green = green.reset_index()
    keep = [c for c in ["osmid","leisure","natural","name","geometry"] if c in green.columns]
    save_layer(green[keep], "greenspace")

# 7. POIs and landmarks
pois = ox.features_from_polygon(poly, tags={"amenity": True, "tourism": True, "historic": True, "shop": True, "public_transport": True})
if len(pois):
    pois = pois.reset_index()
    keep = [c for c in ["osmid","name","amenity","tourism","historic","shop","public_transport","geometry"] if c in pois.columns]
    save_layer(pois[keep], "pois")

print(f"QGIS-ready basemap written to {GPKG} with metric copies in {PROJECTED}/")
