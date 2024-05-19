import rasterio
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# Open the TIFF file
with rasterio.open('D:/naarc/soil data/ph/ph.tif') as src:
    # Read the data as a numpy array
    tif_data = src.read()

    # Check if the TIFF file is greater than 8-bit
    if src.dtypes[0] > np.dtype(np.uint8):
        # Convert the data to 8-bit
        tif_data = (tif_data / np.max(tif_data) * 255).astype(np.uint8)

        # Update nodata value to a valid value for uint8
        nodata_value = None
        if 'nodata' in src.profile:
            nodata_value = src.profile['nodata']
            if nodata_value > 255:  # If nodata value is beyond uint8 range
                nodata_value = None  # Set nodata value to None

        # Write the modified data to a new TIFF file
        profile = src.profile
        profile.update(dtype=rasterio.uint8, nodata=nodata_value)
        with rasterio.open('D:/naarc/soil data/newoverlay.tif', 'w', **profile) as dst:
            dst.write(tif_data)

