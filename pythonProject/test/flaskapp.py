from flask import Flask, request
import pandas as pd
from shapely.geometry import Point, Polygon
from shapely.ops import transform
import rasterio

# Load CSV file with polygons
df = pd.read_csv("data/polbnda_npl.csv")

# Create a Flask application
app = Flask(__name__)

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
    print(lat,lon)
    on_map_click(lat, lon)
    return 'OK'

# Load nitrogen.tif file
nitrogen_file_path = "D:/naarc/soil data/nitrogen/nitrogen.tif"
with rasterio.open(nitrogen_file_path) as src:
    transformer = src.transform
    nitrogen_img = src.read(1)

if __name__ == '__main__':
    # Run the Flask application
    app.run(debug=True,port=8000)
