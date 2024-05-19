import pandas as pd


def extract_unique_latlon(input_file, output_file):
    # Read the input CSV file
    df = pd.read_csv(input_file)

    # Extract unique combinations of latitude and longitude
    unique_latlon = df[['Latitude', 'Longitude']].drop_duplicates()

    # Save the unique combinations to a new CSV file
    unique_latlon.to_csv(output_file, index=False)


# Example usage:
input_file = 'D:/naarc/pythonProject/combined_weather_data_with_dates.csv'  # Specify the input CSV file
output_file = 'D:/naarc/pythonProject/coordinates.csv'  # Specify the output CSV file
extract_unique_latlon(input_file, output_file)
