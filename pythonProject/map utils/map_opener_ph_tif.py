import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# Open the TIFF file
with rasterio.open('D:/naarc/soil data/ph/ph.tif') as src:
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
        'very high acidic': (0, 5),
        'high acidic': (5.1, 5.5),
        'medium acidic': (5.6, 6),
        'low acidic': (6.1, 6.5),
        'neutral': (6.6, 7.3),
        'low alkaline': (7.4, 7.8),
        'medium alkaline': (7.9, 8.4),
        'high alkaline': (8.5, 9.0),
        'very high alkaline': (9, 14)  # Assuming 14 as an upper limit, adjust as needed
    }

    colors = {
        'very high acidic': 'white',
        'high acidic': 'red',
        'medium acidic': 'orange',
        'low acidic': 'yellow',
        'neutral': 'green',
        'low alkaline': 'skyblue',
        'medium alkaline': 'darkblue',
        'high alkaline': 'purple',
        'very high alkaline': 'black',
    }

    # Create a colormap with custom colors without interpolation
    cmap = ListedColormap(list(colors.values()))

    # Classify pixels based on pixel values and assign colors
    classified_data = np.zeros_like(tif_data[0], dtype=np.uint8)
    for cls, (low, high) in thresholds.items():
        classified_data[(tif_data[0] >= low) & (tif_data[0] < high)] = list(thresholds.keys()).index(cls)

    # Save the classified data into a text file with each row on a separate line
    np.savetxt('classified_data.txt', classified_data, fmt='%f', delimiter=',', newline='\n')

    # Plot the original map
    plt.imshow(tif_data[0], cmap='gray')  # Assuming the original map is grayscale, adjust cmap as needed

    # Overlay the classified data on top of the original map
    plt.imshow(classified_data, cmap=cmap, alpha=0.5)  # Use the custom colormap and adjust transparency as needed

    # Add a colorbar for the classified data
    cbar = plt.colorbar(ticks=np.arange(len(thresholds)))
    cbar.set_ticklabels(list(colors.keys()))

    # Show the plot
    plt.show()
