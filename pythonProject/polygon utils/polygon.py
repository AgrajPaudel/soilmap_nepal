import folium
from shapely.geometry import Polygon
import csv

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

# Read the CSV file and extract polygon coordinates
polygons = []
with open('soilparent.csv', 'r', newline='', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)
    for row in csvreader:
        geometry = row[-1]
        polygon = extract_polygon(geometry)
        polygons.append(polygon)

# Create a Folium Map
m = folium.Map(location=[polygons[0][0][0], polygons[0][0][1]], zoom_start=10)

# Draw Polygons on the map
for polygon in polygons:
    folium.PolyLine(locations=polygon, color='blue').add_to(m)

# Function to handle click event
js_click_script = """
<script>
    document.addEventListener('DOMContentLoaded', function() {
        function onClick(e) {
        console.log(e.originalEvent)
            if (e.latlng) {
                console.log("Clicked at: ", e.latlng.lat, e.latlng.lng);
                // You can perform any additional actions with the coordinates here
            } else {
                console.error("Latitude and longitude not found in click event.");
            }
        }
        var mapContainer = document.querySelector('.folium-map');
        if (mapContainer) {
            mapContainer.addEventListener('click', onClick);
        } else {
            console.error("Map container not found.");
        }
    });
</script>
"""
m.get_root().html.add_child(folium.Element(js_click_script))

# Display the map
m.save("map_with_click.html")
