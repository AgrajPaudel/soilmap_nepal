import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
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
        distance = abs(long - coord_long) ** 2 + abs(lat - coord_lat) ** 2
        if distance < closest_distance:
            closest_distance = distance
            closest_coord = (coord_lat, coord_long)

    return closest_coord

def calculate_averages(data, future_predictions):
    """
    Calculate average T2MDEW values for different time intervals.

    Parameters:
    - data: numpy array, historical T2MDEW values
    - future_predictions: dict, predicted T2MDEW values for future dates

    Returns:
    - avg_values: dict, average T2MDEW values for different time intervals
    """
    avg_values = {}
    avg_values['overall'] = np.mean(data)
    avg_values['past_data'] = np.mean(data)
    avg_values['future_data'] = np.mean(list(future_predictions.values()))
    avg_values['combined_data'] = np.mean(np.concatenate((data, list(future_predictions.values()))))

    return avg_values


def predict_weather_variable(variable, input_lat, input_long):
    """
    Predict the specified weather variable values for the next 365 days at the closest coordinate
    to the input latitude and longitude.

    Parameters:
    - variable: str, name of the weather variable (e.g., 'T2M', 'T2MDEW', etc.)
    - input_lat: float, latitude of the input point
    - input_long: float, longitude of the input point

    Returns:
    - avg_values: dict, average weather variable values for different time intervals
    """
    # Files and variables
    pickle_file = "D:/naarc/pythonProject/unique_coordinates.pkl"
    weather_data_file = "D:/naarc/pythonProject/combined_weather_data_with_dates.csv"
    prediction_days = 365

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

    # Prepare dictionary to store predictions
    predictions = {}

    # Iterate over each future date
    for i in range(prediction_days):
        # Calculate the future date
        future_date = filtered_data['Date'].iloc[-1] + timedelta(days=i + 1)

        # Filter historical data for the same date across multiple years
        historical_data = filtered_data[filtered_data['Date'].dt.month == future_date.month]
        historical_data = historical_data[historical_data['Date'].dt.day == future_date.day]

        # Extract features (index) and target variable
        X = np.arange(len(historical_data)).reshape(-1, 1)
        y = historical_data[variable].values.ravel()

        # Fit linear regression model
        model = LinearRegression()
        model.fit(X, y)

        # Predict the weather variable for the future date
        prediction = model.predict(np.array([[len(historical_data)]]))[0]

        # Store prediction
        predictions[future_date] = prediction

    # Calculate averages
    avg_values = calculate_averages(filtered_data[variable].values, predictions)

    return avg_values


"""
# Example usage:

variable = 'T2M'  # Specify the weather variable here
input_lat = 27.7172
input_long = 85.3240

avg_values = predict_weather_variable(variable, input_lat, input_long)
print("Average", variable, "values:")
for interval, value in avg_values.items():
    print(f"{interval}: {value}")

"""