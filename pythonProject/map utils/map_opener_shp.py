import geopandas as gpd

# Read shapefile
gdf = gpd.read_file('D:/naarc/soil data/parentsoil/soilparent.shp')

# Convert GeoDataFrame to CSV
csv_file_path = 'soilparent.csv'  # Define the path for the CSV file
gdf.to_csv(csv_file_path, index=False)  # Convert and save GeoDataFrame to CSV

print("CSV file saved successfully:", csv_file_path)
