"""Build a detailed QGIS-ready Mehrauli urban-planning base from OSM.

Outputs a master GeoPackage plus GeoJSON exports and metric copies.
The official Ward 155 boundary and cadastral plots are NOT fabricated: if an
official boundary/parcel file is supplied, place it in data/source and add it
through the documented import step.

CRS:
  EPSG:4326 = interchange/source format
  EPSG:32643 = metric planning/analysis format for Delhi
"""
from pathlib import Path
import geopandas as gpd
import osmnx as ox
from shapely.geometry import Point
import requests

OUT = Path("data")
PROJECTED = OUT / "projected"
OUT.mkdir(exist_ok=True)
PROJECTED.mkdir(exist_ok=True)
SRC_CRS = "EPSG:4326"
WORK_CRS = "EPSG:32643"
GPKG = OUT / "mehrauli_urban_planning.gpkg"
PLACE = "Mehrauli, Delhi, India"
ox.settings.use_cache = True
ox.settings.log_console = True

if GPKG.exists():
    GPKG.unlink()

def save_layer(gdf, name):
    if gdf is None or gdf.empty:
        print(f"SKIP empty layer: {name}")
        return
    gdf = gdf.copy().to_crs(SRC_CRS)
    gdf.to_file(GPKG, layer=name, driver="GPKG")
    gdf.to_file(OUT / f"{name}.geojson", driver="GeoJSON")
    gdf.to_crs(WORK_CRS).to_file(PROJECTED / f"{name}.gpkg", layer=name, driver="GPKG")
    print(f"OK {name}: {len(gdf)} features")

def features(poly, tags):
    try:
        return ox.features_from_polygon(poly, tags=tags)
    except Exception as exc:
        print(f"WARN feature query failed: {exc}")
        return gpd.GeoDataFrame(geometry=[], crs=SRC_CRS)

# 1. Mehrauli analytical study area.
# Nominatim does not consistently return a polygon for Mehrauli. A 2 km buffer
# around the geocoded place point is therefore explicitly labelled as analytical
# study area and must NOT be treated as the official Ward 155 boundary.
r = requests.get("https://nominatim.openstreetmap.org/search", params={
    "q": PLACE, "format": "json", "limit": 1
}, headers={"User-Agent":"mehrauli-qgis-basemap/1.0"}, timeout=60)
r.raise_for_status()
hit = r.json()[0]
lon, lat = float(hit["lon"]), float(hit["lat"])
center = gpd.GeoSeries([Point(lon, lat)], crs=SRC_CRS).to_crs(WORK_CRS)
study_poly = center.buffer(2000).to_crs(SRC_CRS).iloc[0]
study_area = gpd.GeoDataFrame({
    "name":["Mehrauli 2 km planning study area"],
    "source":["OSM geocoded point + 2 km analytical buffer"]
}, geometry=[study_poly], crs=SRC_CRS)
save_layer(study_area, "01_study_area")
poly = study_poly

# Ward 155 is intentionally not inferred from the study-area polygon.
(OUT / "WARD_155_boundary_REQUIRED.csv").write_text(
    "ward_no,status,source\n155,TEMPLATE - OFFICIAL BOUNDARY REQUIRED,Not inferred from OSM\n",
    encoding="utf-8")

# 2. Buildings
b = features(poly, {"building": True}).reset_index()
if not b.empty:
    keep = [c for c in ["osmid","building","name","levels","height","addr:housenumber","addr:street","geometry"] if c in b.columns]
    b = b[keep]
    b["building_id"] = range(1, len(b)+1)
    b["footprint_m2"] = b.to_crs(WORK_CRS).geometry.area.round(2)
    b["use_class"] = b["building"].fillna("unknown").astype(str)
    save_layer(b, "02_buildings")

# 3. Roads: master centre-lines plus planning hierarchy.
try:
    G = ox.graph_from_polygon(poly, network_type="all", simplify=True)
    roads = ox.graph_to_gdfs(G, nodes=False, edges=True, fill_edge_geometry=True).reset_index()
except Exception as exc:
    print(f"WARN road graph failed: {exc}")
    roads = gpd.GeoDataFrame(geometry=[], crs=SRC_CRS)
if not roads.empty:
    keep = [c for c in ["u","v","key","osmid","name","highway","lanes","maxspeed","oneway","surface","lit","width","geometry"] if c in roads.columns]
    roads = roads[keep]
    roads["road_type"] = roads["highway"].apply(lambda x: x[0] if isinstance(x,list) else x).fillna("unknown")
    roads["road_id"] = range(1, len(roads)+1)
    roads["length_m"] = roads.to_crs(WORK_CRS).geometry.length.round(2)
    save_layer(roads, "03_roads_all")
    hierarchy = {
        "03A_road_arterial": ["motorway","trunk","primary"],
        "03B_road_secondary": ["secondary"],
        "03C_road_tertiary": ["tertiary"],
        "03D_road_local": ["residential","unclassified","living_street"],
        "03E_road_service": ["service"],
        "03F_road_lane_path": ["footway","path","pedestrian","track","cycleway","steps"]
    }
    for name, classes in hierarchy.items():
        save_layer(roads[roads["road_type"].isin(classes)].copy(), name)

# 4. Land use
lu = features(poly, {"landuse": True}).reset_index()
if not lu.empty:
    keep=[c for c in ["osmid","landuse","name","geometry"] if c in lu.columns]
    lu=lu[keep]
    lu["planning_use"] = lu["landuse"].fillna("unknown").astype(str)
    save_layer(lu, "04_landuse")

# 5. Parks/open space/vegetation
green = features(poly, {"leisure":["park","garden","pitch","sports_centre","playground","nature_reserve"], "natural":["wood","grassland","scrub"]}).reset_index()
if not green.empty:
    keep=[c for c in ["osmid","leisure","natural","name","geometry"] if c in green.columns]
    save_layer(green[keep], "05_parks_open_space")

# 6. Water and drainage
waterway = features(poly, {"waterway": True}).reset_index()
if not waterway.empty:
    keep=[c for c in ["osmid","waterway","name","geometry"] if c in waterway.columns]
    save_layer(waterway[keep], "06_water_drainage")
waterbody = features(poly, {"natural":"water", "water":True}).reset_index()
if not waterbody.empty:
    keep=[c for c in ["osmid","natural","water","name","geometry"] if c in waterbody.columns]
    save_layer(waterbody[keep], "06A_water_bodies")

# 7. Metro / transport
metro = features(poly, {"railway":["subway","subway_entrance","station"], "station":["subway","light_rail","train"]}).reset_index()
if not metro.empty:
    keep=[c for c in ["osmid","railway","station","name","geometry"] if c in metro.columns]
    save_layer(metro[keep], "07_metro_transport")

# 8. Monuments / heritage
heritage = features(poly, {"historic":True, "heritage":True, "tourism":["attraction","museum"]}).reset_index()
if not heritage.empty:
    keep=[c for c in ["osmid","historic","heritage","name","tourism","geometry"] if c in heritage.columns]
    save_layer(heritage[keep], "08_monuments_heritage")

# 9. Public / institutional facilities
fac = features(poly, {"amenity":True, "office":True, "education":True, "healthcare":True}).reset_index()
if not fac.empty:
    keep=[c for c in ["osmid","name","amenity","office","education","healthcare","geometry"] if c in fac.columns]
    save_layer(fac[keep], "09_public_facilities")

# 10. Activity / POIs
poi = features(poly, {"shop":True, "amenity":True, "tourism":True, "public_transport":True}).reset_index()
if not poi.empty:
    keep=[c for c in ["osmid","name","shop","amenity","tourism","public_transport","geometry"] if c in poi.columns]
    save_layer(poi[keep], "10_poi_activity")

# 11. Labels from named features.
label_frames=[]
for path in ["08_monuments_heritage","09_public_facilities","10_poi_activity"]:
    gp=OUT/f"{path}.geojson"
    if gp.exists(): label_frames.append(gpd.read_file(gp))
if label_frames:
    labels=gpd.GeoDataFrame(gpd.pd.concat(label_frames,ignore_index=True),crs=SRC_CRS)
    labels=labels[labels.geometry.notna()].copy()
    labels["label"]=labels["name"].fillna("").astype(str)
    labels=labels[labels["label"].str.len()>0]
    labels["geometry"]=labels.geometry.centroid
    save_layer(labels[["label","geometry"]],"11_labels")

# 12. Cadastral/plot layer documentation only; synthetic plots are deliberately avoided.
(OUT/"PLOTS_REQUIRED.md").write_text(
    "# 12_plots — authoritative cadastral input required\n\n"
    "No synthetic plot boundaries are generated. Import an authoritative MCD/DDA/GSDL/cadastral parcel layer and save it as `12_plots`. Recommended fields: `plot_id`, `area_m2`, `frontage_m`, `land_use`, `source`, `survey_date`.\n",
    encoding="utf-8")

print(f"Completed: {GPKG}")
