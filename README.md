# mehrauli-basement-dxf

Repository for generating a Mehrauli Google Earth basemap / DXF using Python + ezdxf.

## Current source
The current drawing is based **only on the user-supplied Google Earth PDF**. The PDF contains Google Earth satellite imagery and an 8.34 m map measurement; it does **not** visibly contain a Ward 155 boundary. Therefore this repository does not fabricate or import a ward boundary from another source.

## DXF
`MEHRAULI_WARD_155_GOOGLE_EARTH_BASEMAP.dxf`

The DXF is an unreferenced image-space template with CAD layers prepared for:
- WARD_155_BOUNDARY
- BUILDING_FOOTPRINT
- ROAD_PRIMARY
- ROAD_SECONDARY
- ROAD_LOCAL
- LANE
- OPEN_SPACE
- WATER
- VEGETATION
- LANDMARK
- TEXT_LABEL

## Required for a true Ward 155-only basemap
Provide a Google Earth screenshot/PDF in which the Ward 155 boundary is visible or drawn. The boundary can then be traced and the basemap clipped to that boundary while continuing to use Google Earth imagery only.

## Accuracy
This is not survey/cadastral control. The supplied PDF does not provide a complete georeferencing control set, so the current DXF uses image-space coordinates.
