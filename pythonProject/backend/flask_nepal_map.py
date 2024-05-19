from flask import Flask, request, jsonify, send_from_directory
import csv
from backend_for_polygon import process_polygon_points
from path import coordinates_csv_path,soil_tiff_paths
import numpy as np
import json
from shapely.wkt import loads as wkt_loads
import sys




app = Flask(__name__)

# Load Nepal's polygon coordinates from CSV file
def load_polygon_from_csv(csv_file):
    polygon = []
    with open(csv_file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        for row in reader:
            lat, lng = map(float, row)
            polygon.append([lng, lat])  # Reversed order to match Leaflet's [lat, lng]
    return polygon

# Function to check if a point is inside Nepal's polygon
def is_inside_polygon(point, polygon):
    # Check if the point is inside the polygon using ray casting algorithm
    # Adapted from: https://www.geeksforgeeks.org/how-to-check-if-a-given-point-lies-inside-a-polygon/
    n = len(polygon)
    inside = False
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if point[1] > min(p1y, p2y):
            if point[1] <= max(p1y, p2y):
                if point[0] <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (point[1] - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or point[0] <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside

# Load Nepal's polygon coordinates from CSV file
nepal_polygon = load_polygon_from_csv('D:/naarc/pythonProject/nepal_coordinates.csv')

# Endpoint for point analysis
@app.route('/point-analysis', methods=['POST'])
def point_analysis():
    data = request.json
    point = data.get("coordinates")  # Use .get() to handle missing key gracefully
    if point is None or len(point) != 2:
        return jsonify({"error": "Invalid point data"}), 400

    # Log the received coordinates for point analysis
    print("Received coordinates for point analysis:", point)

    # Return a response
    return jsonify({"message": "Received coordinates for point analysis", "point": point}), 200


# Convert non-serializable elements to serializable ones
def serialize_data(data):
    if isinstance(data, np.ndarray):
        # Convert NumPy arrays to lists
        return data.tolist()
    elif isinstance(data, (np.float32, np.float64)):
        # Convert NumPy float types to native Python float
        return float(data)
    elif isinstance(data, (np.int32, np.int64)):
        # Convert NumPy integer types to native Python int
        return int(data)
    elif isinstance(data, (np.str_, np.unicode_)):
        # Convert NumPy string types to native Python str
        return str(data)
    elif isinstance(data, dict):
        # Serialize nested dictionaries
        return {key: serialize_data(value) for key, value in data.items()}
    elif isinstance(data, (list, tuple)):
        # Serialize nested lists or tuples
        return [serialize_data(item) for item in data]
    # Handle other types as is
    return data



# Endpoint for polygon analysis
@app.route('/polygon-analysis', methods=['POST'])
def polygon_analysis():
    data = request.json
    print("here")
    print(data)  # For debugging purposes

    # Check if data is a list and has at least 3 points
    if not isinstance(data, list) or len(data) < 3:
        return jsonify({"error": "Invalid polygon data"}), 400

    # Log the received polygon for polygon analysis
    print("Received polygon for polygon analysis:", data)
    statistics, weather_data = process_polygon_points(data, soil_tiff_paths, coordinates_csv_path)

    # Convert non-serializable elements to serializable ones
    serialized_statistics = serialize_data(statistics)
    serialized_weather_data = serialize_data(weather_data)
    print(serialized_weather_data)
    print(serialized_statistics)
    # Return a response
    return jsonify(
        {"message": "Received polygon for polygon analysis", "polygon": data, "statistics": serialized_statistics,
         "weather_data": serialized_weather_data}), 200

# Endpoint to serve the CSV file
@app.route('/nepal_coordinates.csv')
def get_csv():
    return send_from_directory('D:/naarc/pythonProject', 'nepal_coordinates.csv')

# Serve the frontend HTML file
@app.route('/')
def index():
    return send_from_directory('D:/naarc/pythonProject/backend', 'frontend.html')

########
# Function to load district polygons from CSV file

# Function to load district polygons from CSV file
def load_district_polygons_from_csv(csv_file):
    district_polygons = {}
    with open(csv_file, newline='') as csvfile:
        csv.field_size_limit(2**30)  # Set field size limit to 1 GB
        reader = csv.DictReader(csvfile)
        index=0
        for row in reader:
            index=index+1
            district_name = row.get('LAA')
            geometry_wkt = row.get('geometry')
            if district_name and geometry_wkt:
                try:
                    geometry = wkt_loads(geometry_wkt)
                    district_polygons[district_name] = geometry
                except Exception as e:
                    print(f"Error parsing WKT geometry in row: {index}, Error: {e}")
                    continue
            else:
                print("Missing district name or geometry data in row:", row)
    return district_polygons

# Load district polygons from CSV file
district_polygons = load_district_polygons_from_csv('D:/naarc/pythonProject/test/data/polbnda_npl.csv')

# Endpoint to serve the district polygons CSV file
@app.route('/district-polygons.csv')
def get_district_polygons_csv():
    return send_from_directory('D:/naarc/pythonProject/test/data', 'polbnda_npl.csv')
##########

@app.route('/district-analysis', methods=['POST'])
def handle_district_analysis():
    # Get the JSON data from the request
    data = request.get_json()

    # Extract districtName and geometry from the data
    district_name = data.get('districtName')
    geometry = data.get('geometry')

    # Convert the geometry to the required format
    modified_geometry = []
    for level_1 in geometry:
        for level_2 in level_1:
            lat, lon = level_2
            modified_geometry.append([lon, lat])  # Reversed order to match Leaflet's [lat, lon]

    # Perform the same processing as polygon-analysis
    statistics, weather_data = process_polygon_points(modified_geometry, soil_tiff_paths, coordinates_csv_path)

    # Convert non-serializable elements to serializable ones
    serialized_statistics = serialize_data(statistics)
    serialized_weather_data = serialize_data(weather_data)
    print(serialized_weather_data)
    print(serialized_statistics)
    # Return the response with the modified geometry and district name, along with statistics and weather data
    return jsonify({
        'districtName': district_name,
        'geometry': modified_geometry,
        'statistics': serialized_statistics,
        'weather_data': serialized_weather_data
    }), 200



if __name__ == '__main__':
    app.run(debug=True)
