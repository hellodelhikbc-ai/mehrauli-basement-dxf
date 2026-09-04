# Mehrauli Delhi — GIS Basemap + CAD Base

This repository contains a reproducible GIS basemap workflow for Mehrauli, Delhi and the earlier CAD/DXF base.

## GIS basemap
The `gis_basemap/` workflow builds editable GIS layers from OpenStreetMap data:

- Mehrauli boundary / study polygon
- Building footprints
- Road centre-lines with available road attributes
- Land-use polygons
- Waterways
- Green/open-space features
- Points of interest / landmarks

Exports are GeoJSON in **EPSG:4326**, suitable for QGIS, ArcGIS Pro and further CAD/GIS conversion.

### Build automatically
GitHub Actions workflow:
`.github/workflows/build-mehrauli-gis.yml`

It installs the GIS dependencies, downloads the current OpenStreetMap features through OSMnx/Overpass, generates the GeoJSON layers, and publishes them as a workflow artifact named `mehrauli-gis-basemap`.

## Important accuracy note
This GIS base is an **OpenStreetMap planning base**, not a cadastral or survey-accurate municipal base. OSM completeness varies by feature and location. Do not treat building footprints or road edges as legal property boundaries.

The existing `MEHRAULI_WARD_155_GOOGLE_EARTH_BASEMAP.dxf` remains an image-space CAD template based on the user-supplied Google Earth PDF; it should not be represented as a georeferenced Ward 155 survey.

## Suggested QGIS layer order
1. Boundary
2. Water
3. Green / open space
4. Land use
5. Roads
6. Buildings
7. POIs / landmarks

## Files
- `gis_basemap/build_mehrauli_basemap.py` — GIS extraction/build script
- `gis_basemap/requirements.txt` — Python GIS dependencies
- `.github/workflows/build-mehrauli-gis.yml` — automated build
