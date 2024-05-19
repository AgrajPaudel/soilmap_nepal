import requests
import pandas as pd
from shapely.geometry import Point, Polygon
import csv

class PowerAPI:
    """
    Query the NASA Power API.
    Check https://power.larc.nasa.gov/ for documentation
    """
    url = "https://power.larc.nasa.gov/api/temporal/daily/point?"

    def __init__(self, start, end, coordinates_file, parameters=None):
        """
        Parameters
        ----------
        start: Union[date, datetime, pd.Timestamp]
            Start date for data retrieval
        end: Union[date, datetime, pd.Timestamp]
            End date for data retrieval
        coordinates_file: str
            Path to the CSV file containing longitude and latitude coordinates
        parameters: Optional[List[str]]
            List of parameters to query (e.g., ['T2M', 'WS10M'])
        """
        self.start = start
        self.end = end
        self.parameters = parameters or ['T2M_RANGE', 'TS', 'T2MDEW', 'T2MWET', 'T2M_MAX', 'T2M_MIN', 'T2M', 'QV2M',
                                         'RH2M', 'PRECTOTCORR', 'PS', 'WS10M', 'WS10M_MAX', 'WS10M_MIN', 'WS10M_RANGE',
                                         'WS50M', 'WS50M_MAX', 'WS50M_MIN', 'WS50M_RANGE']
        self.coordinates_polygon = self._read_coordinates(coordinates_file)
        self.points = self._generate_points()

    def _read_coordinates(self, file):
        """
        Read coordinates from a CSV file and create a Polygon
        """
        with open(file, 'r') as f:
            reader = csv.DictReader(f)
            points = [(float(row['Latitude']), float(row['Longitude'])) for row in reader]
        return Polygon(points)

    def _generate_points(self):
        """
        Generate 200 points within a specified range of latitude and longitude
        """
        min_lat, max_lat, min_long, max_long = 26.19, 30.61, 79.96, 88.23
        lat_step = (max_lat - min_lat) / 20
        long_step = (max_long - min_long) / 40
        points = []
        for i in range(20):
            for j in range(40):
                lat = min_lat + i * lat_step
                long = min_long + j * long_step
                points.append((lat, long))
        return points

    def _build_request(self, longitude, latitude):
        """
        Build the request URL for a specific coordinate
        """
        params = {
            'parameters': ','.join(self.parameters),
            'community': 'RE',
            'longitude': longitude,
            'latitude': latitude,
            'start': self.start.strftime('%Y%m%d'),
            'end': self.end.strftime('%Y%m%d'),
            'format': 'JSON'
        }
        return requests.get(self.url, params=params)

    def get_weather(self):
        """
        Retrieve weather data from the API for points inside the polygon
        """
        all_data = []
        x=0
        for point in self.points:
            latitude, longitude = point
            if self.coordinates_polygon.contains(Point(point)):
                x=x+1
                print(x)
                print(latitude,longitude)
                response = self._build_request(longitude, latitude)
                response.raise_for_status()  # Raise an error for non-200 status codes
                data_json = response.json()
                records = data_json['properties']['parameter']
                df = pd.DataFrame.from_dict(records)
                df['Longitude'] = longitude
                df['Latitude'] = latitude
                all_data.append(df)
        if all_data:
            return pd.concat(all_data, ignore_index=True)
        else:
            print("No weather data found for any coordinates.")
            return None

# Example usage:
api = PowerAPI(start=pd.Timestamp('1981-01-01'), end=pd.Timestamp('2024-04-10'), coordinates_file='nepal_coordinates.csv')
weather_data = api.get_weather()
if weather_data is not None:
    weather_data.to_csv('combined_weather_data_1.csv', index=False)
    print(weather_data)
