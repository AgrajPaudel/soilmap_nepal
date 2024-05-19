import folium
import pandas as pd
from shapely import wkt

# Path to the CSV file
csv_file_path = "data/polbnda_npl.csv"

# Read the CSV file into a DataFrame
df = pd.read_csv(csv_file_path)

# Create a folium map centered at an average location of polygons
center_lat = df['geometry'].apply(lambda x: wkt.loads(x).centroid.coords[0][1]).mean()
center_lon = df['geometry'].apply(lambda x: wkt.loads(x).centroid.coords[0][0]).mean()
m = folium.Map(location=[center_lat, center_lon], zoom_start=7)

# Add polygons to the map
for idx, row in df.iterrows():
    # Convert polygon from WKT format to Shapely geometry
    polygon = wkt.loads(row['geometry'])
    # Extract coordinates from the polygon
    polygon_coords = list(polygon.exterior.coords)
    # Convert coordinates to folium format
    polygon_coords_folium = [(lat, lon) for lon, lat in polygon_coords]
    # Add polygon to the map
    folium.Polygon(locations=polygon_coords_folium, color='blue', fill=True, fill_color='blue',
                   fill_opacity=0.4).add_to(m)

    # Add name of the polygon as a label inside the polygon
    nam = row['LAA']
    centroid_lat, centroid_lon = polygon.centroid.coords[0][1], polygon.centroid.coords[0][0]
    # Calculate the position for the label based on the centroid
    label_lat, label_lon = centroid_lat, centroid_lon
    # Add the label to the map
    folium.Marker([label_lat, label_lon],
                  icon=folium.DivIcon(html=f'<div style="font-size: 10pt; color: black;">{nam}</div>')).add_to(m)

# Save the map to an HTML file
m.save("polygon_map.html")

# Display the map
m
