import pandas as pd
import pickle


def extract_unique_coordinates(csv_file, pickle_file):
    """
    Extract unique combinations of Latitude and Longitude variables from a CSV file
    and save them to a pickle file.

    Parameters:
    - csv_file: str, path to the CSV file
    - pickle_file: str, path to save the pickle file
    """
    # Load the CSV file
    df = pd.read_csv(csv_file)

    # Extract unique combinations of Latitude and Longitude
    unique_coordinates = df[['Latitude', 'Longitude']].drop_duplicates()

    # Convert to a list of tuples
    coordinates_list = list(zip(unique_coordinates['Latitude'], unique_coordinates['Longitude']))

    # Save the list of unique coordinates to a pickle file
    with open(pickle_file, 'wb') as f:
        pickle.dump(coordinates_list, f)

    print("Unique coordinates extracted and saved to '{}'".format(pickle_file))


# Example usage:
#extract_unique_coordinates("combined_weather_data_1.csv", "unique_coordinates.pkl")
