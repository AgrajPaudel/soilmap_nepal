import rasterio
import numpy as np
from use_knn_model import predict_crop
from find_nearest_coordinates_daywise_regression import predict_weather_variable
import matplotlib.pyplot as plt
from flask_backend_for_coordinates import get_polygon_attributes

# Coordinates of the four corners of the TIFF map: (min_x, min_y, max_x, max_y)
map_corners = (79.95522816732222, 26.19, 88.23, 30.61170855608983)


# Function to calculate pixel indices from latitude and longitude coordinates
def latlon_to_pixel(lat, lon, src):
    # Calculate the ratio of latitude and longitude relative to the map corners
    x_ratio = (lon - map_corners[0]) / (map_corners[2] - map_corners[0])
    y_ratio = (map_corners[1] - lat) / (map_corners[1] - map_corners[3])
    # Calculate the pixel indices
    x_index = int(x_ratio * src.width)
    y_index = int(y_ratio * src.height)
    return x_index, y_index


# Function to retrieve value at given coordinates for a specific soil data type
def get_soil_value(x, y, soil_type, src):
    # Read the data at the given pixel indices
    tif_data = src.read()
    value = tif_data[0][y][x]
    return value


# Function to handle mouse click event
def onclick(event):
    if event.button == 1:  # Left mouse button clicked
        # Extract pixel coordinates
        x_index = int(event.xdata)
        y_index = int(event.ydata)

        # Open the TIFF files for each soil type
        with rasterio.open('D:/naarc/soil data/Phosphorus/p2o5.tif') as src_p2o5, \
                rasterio.open('D:/naarc/soil data/nitrogen/nitrogen.tif') as src_nitrogen, \
                rasterio.open('D:/naarc/soil data/potassium/K250.tif') as src_potassium, \
                rasterio.open('D:/naarc/soil data/ph/ph.tif') as src_ph:
            # Retrieve and display soil data values for the clicked point
            phosphorus_value = get_soil_value(x_index, y_index, 'phosphorus', src_p2o5)/2
            nitrogen_value = get_soil_value(x_index, y_index, 'nitrogen', src_nitrogen)*975
            potassium_value = get_soil_value(x_index, y_index, 'potassium', src_potassium)/2
            ph_value = get_soil_value(x_index, y_index, 'ph', src_ph)

            # Convert pixel coordinates to latitude and longitude
            lat, lon = pixel_to_latlon(x_index, y_index, src_p2o5)
            #temp is fine
            temperature=predict_weather_variable(input_lat=lat,input_long=lon,variable="T2M")
            #this is in mm take future avg, multiply by 365 and divide by 10
            precipitation=predict_weather_variable(input_lat=lat,input_long=lon,variable="PRECTOTCORR")
            #relative humidity is used
            relative_humidity=predict_weather_variable(input_lat=lat,input_long=lon,variable="RH2M")
            specific_humidity=predict_weather_variable(input_lat=lat,input_long=lon,variable="QV2M")
            print(temperature['future_data'])
            print(temperature)
            print(precipitation)
            print(relative_humidity)
            print(specific_humidity)

            # Print the results
            print(f"Latitude: {lat}, Longitude: {lon}")
            attributes=get_polygon_attributes(lat=lat,lon=lon)
            print(attributes)
            print(f"The Phosphorus value at pixel ({x_index}, {y_index}) is: {phosphorus_value}")
            print(f"The Nitrogen value at pixel ({x_index}, {y_index}) is: {nitrogen_value}")
            #nitrogen multiplied by 100
            print(f"The Potassium value at pixel ({x_index}, {y_index}) is: {potassium_value}")
            print(f"The pH value at pixel ({x_index}, {y_index}) is: {ph_value}")
            predicted_crop=predict_crop(pckl_file="knn_crop_classifier.pkl",
                         N=nitrogen_value,
                         P=phosphorus_value,
                         K=potassium_value,
                         humidity=relative_humidity['future_data'],
                         temperature=temperature['future_data'],
                         ph=ph_value,
                         rainfall=precipitation['future_data']*365/10
                         )
            print(predicted_crop)


# Function to calculate latitude and longitude from pixel coordinates
def pixel_to_latlon(x, y, src):
    # Get the affine transformation matrix
    transform = src.transform

    # Calculate longitude
    lon = transform[2] + x * transform[0] + y * transform[1]

    # Calculate latitude
    lat = transform[5] + x * transform[3] + y * transform[4]

    return lat, lon


# Open the TIFF file for the phosphorus map
with rasterio.open('D:/naarc/soil data/Phosphorus/p2o5.tif') as src:
    # Plot the original map
    plt.imshow(src.read()[0], cmap='gray')  # Assuming the original map is grayscale, adjust cmap as needed

    # Connect the mouse click event to the onclick function
    plt.gcf().canvas.mpl_connect('button_press_event', onclick)

    # Show the plot
    plt.show()
