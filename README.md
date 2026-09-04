# Mehrauli Delhi — Detailed Urban-Planning GIS + CAD Base

This repository contains a reproducible QGIS-ready GIS workflow for Mehrauli, Delhi, together with the earlier CAD/DXF base.

## Detailed QGIS package
The `gis_basemap/` workflow builds a structured urban-planning base from OpenStreetMap-derived data and produces a master GeoPackage:

`data/mehrauli_urban_planning.gpkg`

### Layer groups

1. **Administrative / Study Area** — `01_study_area`
2. **Buildings** — `02_buildings` with footprint area and available levels/height/use fields
3. **Roads** — `03_roads_all` plus separate hierarchy layers:
   - `03A_road_arterial`
   - `03B_road_secondary`
   - `03C_road_tertiary`
   - `03D_road_local`
   - `03E_road_service`
   - `03F_road_lane_path`
4. **Land Use** — `04_landuse`
5. **Parks / Open Space / Vegetation** — `05_parks_open_space`
6. **Water / Drainage** — `06_water_drainage`, `06A_water_bodies`
7. **Metro / Transport** — `07_metro_transport`
8. **Monuments / Heritage** — `08_monuments_heritage`
9. **Public / Institutional Facilities** — `09_public_facilities`
10. **Activity / POIs** — `10_poi_activity`
11. **Labels** — `11_labels`
12. **Plots** — documented as `12_plots`, but cadastral geometry is deliberately not fabricated

### CRS
- **EPSG:4326** — source/interchange GeoJSON
- **EPSG:32643** — projected metric planning copies for area, distance and network analysis

### Ward 155 and plots
The supplied Google Earth PDF is an aerial reference image with an 8.34 m measurement and visible place/landmark labels; it does not show a defensible official Ward 155 boundary. Therefore the workflow does not convert the 2 km analytical study area into a fake Ward 155 boundary.

`data/WARD_155_boundary_REQUIRED.csv` documents the missing authoritative Ward 155 geometry.

Similarly, cadastral plot boundaries are not invented from building footprints. An authoritative MCD/DDA/GSDL/cadastral parcel layer should be imported as `12_plots` before using plot-level FAR, coverage, frontage or parcel statistics.

## Automated build
`.github/workflows/build-mehrauli-gis.yml` runs the extraction and publishes:

- master GeoPackage
- GeoJSON layers
- metric projected GeoPackage copies
- Ward 155 boundary requirement metadata
- plot-layer documentation

The workflow artifact is named **`mehrauli-qgis-urban-planning-base`**.

## Source and accuracy
The GIS extraction is OSM-derived and should be treated as a planning/reference base, not a legal cadastral or survey base. The Google Earth PDF supplied by the user is retained conceptually as visual/reference evidence; its imagery should not be represented as authoritative survey geometry.

The earlier `MEHRAULI_WARD_155_GOOGLE_EARTH_BASEMAP.dxf` remains available as a separate image-space CAD template.
