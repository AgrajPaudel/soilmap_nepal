import rasterio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon as ShapelyPolygon
from backend.find_nearest_coordinates_daywise_regression import predict_weather_variable

# Coordinates of the four corners of the TIFF map: (min_x, min_y, max_x, max_y)
map_corners = (79.96, 26.19, 88.23, 30.61)

# Function to calculate pixel indices from latitude and longitude coordinates
def latlon_to_pixel(lat, lon, src):
    # Get the affine transformation matrix
    transform = src.transform

    # Calculate pixel coordinates
    x = int((lon - transform[2]) / transform[0])
    y = int((lat - transform[5]) / transform[4])

    return x, y


# Function to retrieve value at given coordinates for a specific soil data type
def get_soil_value(x, y, src):
    # Read the data at the given pixel indices
    tif_data = src.read()
    value = tif_data[0][y][x]
    return value

# Function to calculate latitude and longitude from pixel coordinates
def pixel_to_latlon(x, y, src):
    # Get the affine transformation matrix
    transform = src.transform

    # Calculate longitude
    lon = transform[2] + x * transform[0] + y * transform[1]

    # Calculate latitude
    lat = transform[5] + x * transform[3] + y * transform[4]

    return lat, lon

# Function to calculate distance between two points
def calculate_distance(point1, point2):
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


def fetch_weather_data(lat, lon):
    # Function to fetch weather data for a given latitude and longitude
    # Fetch temperature, precipitation, relative humidity, and specific humidity
    temperature = predict_weather_variable(input_lat=lat, input_long=lon, variable="T2M")
    precipitation = predict_weather_variable(input_lat=lat, input_long=lon, variable="PRECTOTCORR")
    relative_humidity = predict_weather_variable(input_lat=lat, input_long=lon, variable="RH2M")
    specific_humidity = predict_weather_variable(input_lat=lat, input_long=lon, variable="QV2M")

    # Store fetched weather data in a dictionary
    weather_data = {
        'temperature': temperature['future_data'],
        'precipitation': precipitation,
        'relative_humidity': relative_humidity,
        'specific_humidity': specific_humidity
    }
    return weather_data


def onclick(event, src):
    global poly_points, all_points
    if event.button == 1:  # Left mouse button clicked
        new_point = (int(event.xdata), int(event.ydata))
        if len(poly_points) > 0 and calculate_distance(new_point, poly_points[-1]) < 10:
            poly_points.append(poly_points[0])  # Close the polygon
            plt.plot(poly_points[0][0],poly_points[0][1], 'ro')######
            # Print latitude and longitude coordinates of the boundary points
            boundary_latlon = [pixel_to_latlon(point[0], point[1], src) for point in poly_points]
            print("Boundary Latitude and Longitude Coordinates:")
            for lat, lon in boundary_latlon:
                print(f"Lat: {lat}, Lon: {lon}")

            # Calculate values for pixels inside the polygon
            polygon = ShapelyPolygon(poly_points)
            min_x, min_y, max_x, max_y = polygon.bounds
            step_size_x = 20
            step_size_y = 10
            polygon_values = {'nitrogen': [], 'phosphorus': [], 'potassium': [], 'ph': []}
            points_inside_polygon = []  # List to store coordinates falling inside the polygon
            latlong_inside_polygon=[]
            for x in range(int(min_x), int(max_x) + 1, step_size_x):
                for y in range(int(min_y), int(max_y) + 1, step_size_y):
                    if Point(x, y).within(polygon):
                        lat, lon = pixel_to_latlon(x, y, src)
                        nitrogen_value = get_soil_value(x, y, src) * 975
                        phosphorus_value = get_soil_value(x, y, src) / 2
                        potassium_value = get_soil_value(x, y, src) / 2
                        ph_value = get_soil_value(x, y, src)
                        polygon_values['nitrogen'].append(nitrogen_value)
                        polygon_values['phosphorus'].append(phosphorus_value)
                        polygon_values['potassium'].append(potassium_value)
                        polygon_values['ph'].append(ph_value)
                        print(f"Inside Polygon - Lat: {lat}, Lon: {lon}")
                        points_inside_polygon.append((lat, lon))

            # Read the CSV file
            weather_data = pd.read_csv('D:/naarc/pythonProject/coordinates.csv')  # Use coordinate only file

            # Check if any coordinate from CSV falls inside the polygon
            csv_points_inside_polygon = False
            for index, row in weather_data.iterrows():
                lat, lon = latlon_to_pixel(row['Latitude'], row['Longitude'], src)
                if Point(lat, lon).within(polygon):
                    print(f"Lat: {row['Latitude']}, Lon: {row['Longitude']}")
                    latlong_inside_polygon.append((row['Latitude'],row['Longitude']))
                    csv_points_inside_polygon = True

            if not csv_points_inside_polygon:
                print("No points from coordinates.csv falling inside the polygon. Finding the closest point...")
                closest_point = find_closest_point_to_polygon(polygon, weather_data, src)
                if closest_point is not None:  # Check if a closest point was found
                    print(f"Closest point to the polygon: Lat: {closest_point['Latitude']}, Lon: {closest_point['Longitude']}")
                    weather_data = fetch_weather_data(closest_point['Latitude'], closest_point['Longitude'])
                    #print("Weather data for closest point:", weather_data['future_data'])
                else:
                    print("No points available in the dataset.")
            else:
                print("Points from coordinates.csv falling inside the polygon.")
                # Fetch weather data for each point inside the polygon
                for lat, lon in latlong_inside_polygon:
                    weather_data = fetch_weather_data(lat, lon)
                    print("Weather data for point:", weather_data)

            # Print values for pixels inside the polygon
            print("\nValues for pixels inside the polygon:")
            for nutrient, values in polygon_values.items():
                print(f"\n{nutrient.capitalize()} values:")
                print(f"  Mean {nutrient} value: {np.mean(values)}")
                print(f"  Median {nutrient} value: {np.median(values)}")
                print(f"  Maximum {nutrient} value: {np.max(values)}")
                print(f"  Minimum {nutrient} value: {np.min(values)}")

            plt.close()
            draw_plot()  # After closing, immediately draw the plot again

        else:
            poly_points.append(new_point)
            all_points.append(new_point)
            plt.plot(event.xdata, event.ydata, 'ro')  # Mark the clicked points
            if len(poly_points) > 1:
                plt.plot([poly_points[-2][0], new_point[0]], [poly_points[-2][1], new_point[1]],
                         'r-')  # Connect the points
            plt.draw()

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



def draw_plot():
    with rasterio.open('D:/naarc/soil data/Phosphorus/p2o5.tif') as src:
        # Plot the original map
        plt.imshow(src.read()[0], cmap='gray')  # Assuming the original map is grayscale, adjust cmap as needed

        # Connect the mouse click event to the onclick function
        global poly_points, all_points
        poly_points = []
        all_points = []
        cid = plt.gcf().canvas.mpl_connect('button_press_event', lambda event: onclick(event, src))

        # Enable scroll wheel zooming
        plt.gca().set_aspect('auto')
        plt.gca().autoscale(enable=True)
        plt.gca().set_autoscale_on(True)
        plt.gca().format_coord = lambda x, y: f'x={x:.2f}, y={y:.2f}'

        # Show the plot
        plt.show()

# Initial draw
draw_plot()
