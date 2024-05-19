import pandas as pd

# Load the existing weather data CSV file
df = pd.read_csv("combined_weather_data_1.csv")

# Generate a DataFrame with all possible dates
dates = pd.date_range(start="1981-01-01", end="2024-04-10", freq="D")

# Iterate over each unique combination of latitude and longitude
unique_coordinates = df[['Latitude', 'Longitude']].drop_duplicates()
for index, row in unique_coordinates.iterrows():
    lat, long = row['Latitude'], row['Longitude']
    # Filter the DataFrame for the current latitude and longitude
    subset_df = df[(df['Latitude'] == lat) & (df['Longitude'] == long)]
    # Assign dates to the subset DataFrame
    subset_df['Date'] = dates[:len(subset_df)]
    # Update the original DataFrame with the subset DataFrame
    df.loc[(df['Latitude'] == lat) & (df['Longitude'] == long), 'Date'] = subset_df['Date'].values

# Save the DataFrame to a new CSV file
df.to_csv("combined_weather_data_with_dates.csv", index=False)

print("Dates added and saved to 'combined_weather_data_with_dates.csv'")
