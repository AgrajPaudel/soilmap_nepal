import csv
from shapely.geometry import Polygon, Point

# Function to extract polygon coordinates from the geometry column
def extract_polygon(geometry):
    coordinates = geometry.split("POLYGON ((")[1].split("))")[0].split(", ")
    coordinates = [coord.replace(")", '').replace("(", '') for coord in coordinates]

    polygon = []
    for i in range(len(coordinates)):
        lon, lat = map(float, coordinates[i].split())
        next_index = (i + 1) % len(coordinates)
        next_lon, next_lat = map(float, coordinates[next_index].split())
        polygon.append((lat, lon))
        polygon.append((next_lat, next_lon))
    return polygon

# Increase the field size limit
csv.field_size_limit(100000000)

def get_polygon_attributes(lat, lon):
    with open('soilparent.csv', 'r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            geometry = row['geometry']
            polygon = extract_polygon(geometry)
            if is_point_inside_polygon(lat, lon, polygon):
                # Extract desired attributes
                attributes = {
                    'OBJECTID_1': row['OBJECTID_1'],
                    'OBJECTID': row['OBJECTID'],
                    'AREA': row['AREA'],
                    'PERIMETER': row['PERIMETER'],
                    'LCODE_GEN': row['LCODE_GEN'],
                    'SQKM': row['SQKM'],
                    'REC_NUM_1': row['REC_NUM_1'],
                    'Elev_min': row['Elev_min'],
                    'Elev_max': row['Elev_max'],
                    'Slope_med': row['Slope_med'],
                    'Relief_med': row['Relief_med'],
                    'linkfield': row['linkfield'],
                    'Landform': row['Landform'],
                    'Parent_Mat': row['Parent_Mat'],
                    'Dominant_S': row['Dominant_S'],
                    'CODE': row['CODE'],
                    'NAME': row['NAME'],
                    'Shape_Leng': row['Shape_Leng'],
                    'Shape_Le_1': row['Shape_Le_1'],
                    'Shape_Area': row['Shape_Area']
                }
                return attributes
    return None

def is_point_inside_polygon(lat, lon, polygon):
    point = Point(lat, lon)
    poly = Polygon(polygon)
    return poly.contains(point)


