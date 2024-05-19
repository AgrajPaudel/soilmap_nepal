from pyproj import CRS

# Read projection file
with open('D:/naarc/soil data/parentsoil/soilparent.prj', 'r') as f:
    prj_text = f.read()

# Parse projection
crs = CRS.from_wkt(prj_text)
print(crs)