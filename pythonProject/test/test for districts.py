import geopandas as gpd

# Path to the shapefile
shp_file_path = "data/polbnda_npl.shp"

# Open the shapefile
gdf = gpd.read_file(shp_file_path)

# Specify the path for the CSV file
csv_file_path = "data/polbnda_npl.csv"

# Save GeoDataFrame to CSV
gdf.to_csv(csv_file_path, index=False)

print(f"CSV file saved at: {csv_file_path}")
