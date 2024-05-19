import rasterio

# Coordinates of the four corners of the TIFF map: (min_x, min_y, max_x, max_y)
map_corners = (79.96, 26.19, 88.23, 30.61)


# Function to calculate pixel indices from latitude and longitude coordinates
def latlon_to_pixel(lat, lon, src):
    # Calculate the ratio of latitude and longitude relative to the map corners
    x_ratio = (lon - map_corners[0]) / (map_corners[2] - map_corners[0])
    y_ratio = (map_corners[1] - lat) / (map_corners[1] - map_corners[3])
    # Calculate the pixel indices
    x_index = int(x_ratio * src.width)
    y_index = int(y_ratio * src.height)
    return x_index, y_index


# User inputs latitude and longitude
latitude = float(input("Enter latitude: "))
longitude = float(input("Enter longitude: "))

# Open the TIFF file
with rasterio.open('D:/naarc/soil data/Phosphorus/p2o5.tif') as src:
    # Calculate the pixel indices corresponding to the input latitude and longitude
    pixel_x, pixel_y = latlon_to_pixel(latitude, longitude, src)

    # Read the data at the calculated pixel indices
    tif_data = src.read()
    value = tif_data[0][pixel_y][pixel_x]

    print(f"The value at latitude {latitude} and longitude {longitude} is: {value}")
