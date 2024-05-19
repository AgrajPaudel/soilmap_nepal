import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import mplcursors

# Open the TIFF file
with rasterio.open('D:/naarc/soil data/nitrogen/nitrogen.tif') as src:
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

# Define classification thresholds and corresponding colors
thresholds = {
    'low': (0, 0.06),
    'medium': (0.06, 0.1),
    'high': (0.1, 0.2),
    'very high': (0.2, 100)  # Assuming 100 as an upper limit, adjust as needed
}

colors = {
    'low': 'red',
    'medium': 'khaki',
    'high': 'skyblue',
    'very high': 'darkblue'
}

# Create a colormap with custom colors
cmap = LinearSegmentedColormap.from_list('custom_colormap', list(colors.values()))

# Classify pixels based on pixel values and assign colors
classified_data = np.zeros_like(tif_data[0], dtype=np.uint8)
for cls, (low, high) in thresholds.items():
    classified_data[(tif_data[0] >= low) & (tif_data[0] < high)] = list(thresholds.keys()).index(cls)
    np.savetxt('classified_data.txt', classified_data, fmt='%f', delimiter=',', newline='\n')

# Plot the original map
plt.imshow(tif_data[0], cmap='gray')  # Assuming the original map is grayscale, adjust cmap as needed

# Overlay the classified data on top of the original map
img = plt.imshow(classified_data, cmap=cmap, alpha=0.5)  # Use the custom colormap and adjust transparency as needed

# Add a colorbar for the classified data
cbar = plt.colorbar(img, ticks=np.arange(len(thresholds)) + 0.5)
cbar.set_ticklabels(list(colors.keys()))

# Add cursor tooltip
mplcursors.cursor(hover=True).connect("add", lambda sel: sel.annotation.set_text(
    f"Value: {tif_data[0][sel.target.index]} \nClass: {list(thresholds.keys())[classified_data[sel.target.index]]}"
))

# Show the plot
plt.show()
