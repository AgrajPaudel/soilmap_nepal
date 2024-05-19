import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import mplcursors

# Coordinates of the four corners of the TIFF map: (min_x, min_y, max_x, max_y)
map_corners = (79.96, 26.19, 88.23, 30.61)

# Open the TIFF file
with rasterio.open('D:/naarc/soil data/Phosphorus/p2o5.tif') as src:
    # Print basic information
    print("TIFF File Information:")
    print("Number of Bands:", src.count)
    print("Image Width:", src.width)
    print("Image Height:", src.height)
    print("CRS (Coordinate Reference System):", src.crs)
    print("Transform Matrix:", src.transform)
    print("Metadata:")
    for key, value in src.meta.items():
        print(f"  {key}: {value}")

    # Read the data as a numpy array
    tif_data = src.read()

# Calculate the minimum and maximum values
min_value = np.min(tif_data)
max_value = np.max(tif_data)

# Define classification thresholds and corresponding colors
thresholds = {
    'very low': (min_value, min_value + (max_value - min_value) / 5),
    'low': (min_value + (max_value - min_value) / 5, min_value + 2 * (max_value - min_value) / 5),
    'medium': (min_value + 2 * (max_value - min_value) / 5, min_value + 3 * (max_value - min_value) / 5),
    'high': (min_value + 3 * (max_value - min_value) / 5, min_value + 4 * (max_value - min_value) / 5),
    'very high': (min_value + 4 * (max_value - min_value) / 5, max_value)
}

colors = {
    'very low': 'darkblue',
    'low': 'skyblue',
    'medium': 'khaki',
    'high': 'orange',
    'very high': 'red'
}

# Create a colormap with custom colors
cmap = LinearSegmentedColormap.from_list('custom_colormap', list(colors.values()))

# Classify pixels based on pixel values and assign colors
classified_data = np.zeros_like(tif_data[0], dtype=np.uint8)
for cls, (low, high) in thresholds.items():
    classified_data[(tif_data[0] >= low) & (tif_data[0] < high)] = list(thresholds.keys()).index(cls)

# Plot the original map
plt.imshow(tif_data[0], cmap='gray')  # Assuming the original map is grayscale, adjust cmap as needed

# Overlay the classified data on top of the original map
img = plt.imshow(classified_data, cmap=cmap, alpha=0.5)  # Use the custom colormap and adjust transparency as needed


# Function to calculate latitude and longitude from pixel coordinates
def pixel_to_latlon(x, y):
    print((x,y))
    print(src.width,src.height)
    # Extract y coordinate from the tuple
    x_index=x
    y_index = y
    x_ratio = 1-x_index / src.width
    y_ratio = 1 - y_index / src.height
    lon = map_corners[2] + (map_corners[0] - map_corners[2]) * x_ratio
    lat = map_corners[1] - (map_corners[1] - map_corners[3]) * y_ratio
    return lat, lon

# Add cursor tooltip with value, class, and latitude/longitude
mplcursors.cursor(hover=True).connect("add", lambda sel: sel.annotation.set_text(
f"Value: {tif_data[0][sel.target.index]}"
   f"\nLatitude, Longitude: {pixel_to_latlon(sel.target.index[1] % src.width, sel.target.index[0]%src.height)}"

))

# Show the plot
plt.show()
