import rasterio
import numpy as np
import pandas as pd
from shapely.geometry import Point, Polygon
from backend.find_nearest_coordinates_daywise_regression import predict_weather_variable

# Function to calculate pixel indices from latitude and longitude coordinates
def latlon_to_pixel(lat, lon, src):
    transform = src.transform
    x = int((lon - transform[2]) / transform[0])
    y = int((lat - transform[5]) / transform[4])
    return x, y

# Function to retrieve value at given coordinates for a specific soil data type
def get_soil_value(x, y, src):
    tif_data = src.read()
    value = tif_data[0][y][x]
    return value

# Function to calculate latitude and longitude from pixel coordinates
def pixel_to_latlon(x, y, src):
    transform = src.transform
    lon = transform[2] + x * transform[0] + y * transform[1]
    lat = transform[5] + x * transform[3] + y * transform[4]
    return lat, lon

# Function to calculate distance between two points
def calculate_distance(point1, point2):
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

# Function to fetch weather data for a given latitude and longitude
def fetch_weather_data(lat, lon, coordinates_csv_path):
    # Fetch weather data using appropriate method (not provided)
    # Placeholder code:
    temperature = predict_weather_variable(input_lat=lat, input_long=lon, variable="T2M")
    precipitation = predict_weather_variable(input_lat=lat, input_long=lon, variable="PRECTOTCORR")
    relative_humidity = predict_weather_variable(input_lat=lat, input_long=lon, variable="RH2M")
    specific_humidity = predict_weather_variable(input_lat=lat, input_long=lon, variable="QV2M")
    weather_data = {
        'temperature': temperature['future_data'],
        'precipitation': precipitation['future_data'],
        'relative_humidity': relative_humidity['future_data'],
        'specific_humidity': specific_humidity['future_data']
    }
    return weather_data

# Function to find the closest point to the polygon
def find_closest_point_to_polygon(polygon, data, src):
    closest_point = None
    min_distance = float('inf')
    for index, row in data.iterrows():
        lat = row['Latitude']
        lon = row['Longitude']
        pixel_x, pixel_y = latlon_to_pixel(lat, lon, src)
        point = Point(pixel_x, pixel_y)
        if polygon.distance(point) < min_distance:
            closest_point = row
            min_distance = polygon.distance(point)
    return closest_point


# Function to process polygon points and extract soil values
def process_polygon_points(polygon_points, soil_tiff_paths, coordinates_csv_path):
    # Open soil tiff files
    srcs = [rasterio.open(path) for path in soil_tiff_paths]

    # Convert polygon points to pixel coordinates for soil data
    pixel_points = []
    for point in polygon_points:
        lat, lon = point
        x, y = latlon_to_pixel(lat, lon, srcs[0])  # Using the first source for transformation
        pixel_points.append((x, y))

    # Create polygon
    polygon = Polygon(pixel_points)

    # Read coordinates.csv
    coordinates_data = pd.read_csv(coordinates_csv_path)

    # Initialize lists to store weather data for points inside the polygon
    weather_data_list = []

    # Iterate over each point in coordinates.csv
    for index, row in coordinates_data.iterrows():
        lat, lon = row['Latitude'], row['Longitude']
        # Convert latitude and longitude to pixel coordinates
        x, y = latlon_to_pixel(lat, lon, srcs[0])

        # Check if the point is inside the polygon
        if Point(x, y).within(polygon):
            # Fetch weather data for the point
            weather_data = fetch_weather_data(lat, lon, coordinates_csv_path)
            # Append weather data to the list
            weather_data_list.append(weather_data)

    # If no points fall inside the polygon, find the closest point from coordinates.csv
    if not weather_data_list:
        print("no point for weather in polygon")
        # Find the closest point to the polygon
        closest_point = find_closest_point_to_polygon(polygon, coordinates_data, srcs[0])
        if closest_point is not None:  # Check if a closest point was found
            # Fetch weather data for the closest point
            closest_lat, closest_lon = closest_point['Latitude'], closest_point['Longitude']
            weather_data = fetch_weather_data(closest_lat, closest_lon, coordinates_csv_path)
            # Append weather data to the list
            weather_data_list.append(weather_data)

    # Calculate mean values of weather parameters for points inside the polygon

    if weather_data_list:
        print("point in weather for given polygon")
        if len(weather_data_list) > 1:
            print(weather_data_list)
            # Initialize mean weather data dictionary
            mean_weather_data = {}
            # Iterate over the keys of the dictionaries
            for key in weather_data_list[0].keys():
                # Calculate the mean for each key
                mean_weather_data[key] = np.mean([data[key] for data in weather_data_list])
        else:
            # If there is only one data point, return it directly
            mean_weather_data = weather_data_list[0]
    else:
        mean_weather_data = None

    # Calculate bounding box of the polygon
    min_x, min_y, max_x, max_y = polygon.bounds

    # Calculate step size for iterating over pixels
    step_size_x = 20
    step_size_y = 10

    # Initialize statistics dictionary
    statistics = {}

    # Iterate over each soil raster file
    for src in srcs:
        # Extract soil values for pixels inside the polygon
        polygon_values = []
        for x in range(int(min_x), int(max_x) + 1, step_size_x):
            for y in range(int(min_y), int(max_y) + 1, step_size_y):
                if Point(x, y).within(polygon):
                    # Convert pixel coordinates to latitude and longitude
                    lat, lon = pixel_to_latlon(x, y, src)

                    # Extract soil value at the pixel coordinates
                    soil_value = get_soil_value(x, y, src)

                    # Append soil value to the list
                    polygon_values.append(soil_value)

        # Calculate statistics for soil values
        statistics[src.name] = {
            'mean': np.mean(polygon_values),
            'median': np.median(polygon_values),
            'max': np.max(polygon_values),
            'min': np.min(polygon_values)
        }

    # Close rasterio sources
    for src in srcs:
        src.close()

    return statistics, mean_weather_data


# Example usage:
#polygon_points = [[28.497660832963472, 83.3174941738621], [28.14950321154457, 83.08687522744172], [28.023500048883022, 83.50418570191675], [28.44937385955666, 83.73480464833712], [28.484987639037996, 83.3998238605786], [28.490419194161678, 83.35938978285897], [28.475934426272353, 83.33948517141198], [28.484384115665033, 83.32335557248078], [28.49192790988262, 83.33110221281869], [28.49615219918497, 83.33968178671832], [28.505656231934704, 83.33470563385653], [28.501884892812107, 83.325096511089], [28.497924841657532, 83.31752057363559], [28.497660832963472, 83.3174941738621]]




#print("Soil statistics:", statistics)
#print("Weather data:", weather_data)
