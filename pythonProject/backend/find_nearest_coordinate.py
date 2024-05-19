import pandas as pd
import matplotlib.pyplot as plt
import pickle

def find_closest_coordinate(lat, long, pickle_file):
    """
    Find the closest coordinate to the given latitude and longitude from a pickle file
    containing unique coordinates, based on longitude difference.

    Parameters:
    - lat: float, latitude of the input point
    - long: float, longitude of the input point
    - pickle_file: str, path to the pickle file containing unique coordinates

    Returns:
    - closest_coord: tuple, (latitude, longitude) of the closest coordinate
    """
    # Load unique coordinates from pickle file
    with open(pickle_file, 'rb') as f:
        unique_coordinates = pickle.load(f)

    # Find the closest coordinate based on longitude difference
    closest_distance = float('inf')
    closest_coord = None
    for coord_lat, coord_long in unique_coordinates:
        distance = abs(long - coord_long)*abs(long - coord_long)+abs(lat - coord_lat)*abs(lat - coord_lat)
        if distance < closest_distance:
            closest_distance = distance
            closest_coord = (coord_lat, coord_long)

    return closest_coord

def plot_time_series_for_coordinate(input_lat, input_long):
    """
    Plot the time series for a specified variable at the closest coordinate to the input latitude and longitude.

    Parameters:
    - input_lat: float, latitude of the input point
    - input_long: float, longitude of the input point

    Returns:
    - None
    """
    # Files and variables
    pickle_file = "unique_coordinates.pkl"
    weather_data_file = "combined_weather_data_with_dates.csv"
    variable = 'T2MDEW'

    # Find the closest coordinate
    closest_coordinate = find_closest_coordinate(input_lat, input_long, pickle_file)
    print("Closest coordinate:", closest_coordinate)

    # Load the weather data CSV file
    df = pd.read_csv(weather_data_file)

    # Filter the data based on the closest coordinate
    closest_lat, closest_long = closest_coordinate
    filtered_data = df[(df['Latitude'] == closest_lat) & (df['Longitude'] == closest_long)]

    # Convert the "Date" column to datetime format
    filtered_data['Date'] = pd.to_datetime(filtered_data['Date'])

    # Plot the time series
    plt.figure(figsize=(10, 6))
    plt.plot(filtered_data['Date'], filtered_data[variable], color='blue')
    plt.title(f'Time Series of {variable}')
    plt.xlabel('Date')
    plt.ylabel(variable)
    plt.grid(True)
    plt.show()

# Example usage:
#input_lat = 27.7172
#input_long = 85.3240

#plot_time_series_for_coordinate(input_lat, input_long)
