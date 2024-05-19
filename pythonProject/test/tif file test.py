import folium
import pandas as pd
from shapely.geometry import Point, Polygon
from shapely.ops import transform
import rasterio
from flask import Flask, request

# Load CSV file with polygons
df = pd.read_csv("data/polbnda_npl.csv")

# Create a Folium map centered at a specific location
m = folium.Map(location=[28.3949, 84.1240], zoom_start=7)

# Add polygons to the map
for idx, row in df.iterrows():
    polygon_coords = row['geometry'].replace('POLYGON ((', '').replace('))', '').split(', ')
    polygon_coords = [(float(coord.split()[1]), float(coord.split()[0])) for coord in polygon_coords]
    polygon = folium.Polygon(locations=polygon_coords, fill=True, color='blue', fill_color='blue', fill_opacity=0.4)
    m.add_child(polygon)

# Create a Flask application
app = Flask(__name__)

# Load nitrogen.tif file
nitrogen_file_path = "D:/naarc/soil data/nitrogen/nitrogen.tif"
with rasterio.open(nitrogen_file_path) as src:
    transformer = src.transform
    nitrogen_img = src.read(1)

# Function to handle mouse click event
def on_map_click(lat, lon):
    point = Point(lon, lat)
    found = False

    # Check if the point is inside any of the polygons
    for idx, row in df.iterrows():
        polygon_coords = row['geometry'].replace('POLYGON ((', '').replace('))', '').split(', ')
        polygon_coords = [(float(coord.split()[1]), float(coord.split()[0])) for coord in polygon_coords]
        polygon = Polygon(polygon_coords)
        if polygon.contains(point):
            found = True
            print(f"Clicked inside polygon {row['NAM']}")
            # Reverse engineering to find pixel coordinates
            x, y = transform(transformer, lon, lat)
            x, y = int(x), int(y)
            # Get the pixel value from nitrogen.tif
            value = nitrogen_img[y, x]
            print(f"Value at clicked location: {value}")
            break

    if not found:
        print("Target outside range")

# Route to handle click events
@app.route('/click', methods=['GET'])
def handle_click():
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))
    on_map_click(lat, lon)
    return 'OK'

# Convert the function to a string
js_function = """
function(event) {
    var latlng = event.latlng;
    var lat = latlng.lat;
    var lon = latlng.lng;
    console.log('Clicked at:', lat, lon);
    var xhr = new XMLHttpRequest();
    xhr.open('GET', 'http://localhost:5000/click?lat=' + lat + '&lon=' + lon);
    xhr.send();
}
"""

# Add the JavaScript function to the map
m.get_root().html.add_child(folium.Element(f"""
<script>
{js_function}
</script>
"""))

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True, port=5000)
