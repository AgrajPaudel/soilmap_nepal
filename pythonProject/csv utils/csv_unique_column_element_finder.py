import csv
from itertools import product

def unique_combinations_count(csv_file, header1, header2):
    unique_combinations = set()

    # Read the CSV file and extract unique combinations from the specified headers in each row
    with open(csv_file, 'r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            # Extract data from specified headers
            data1 = row[header1].strip()
            data2 = row[header2].strip()

            # Generate unique combinations of the data from the specified headers
            unique_combinations.add((data1, data2))

    # Count the number of unique combinations
    unique_count = len(unique_combinations)

    return list(unique_combinations), unique_count

# Example usage
csv_file = 'combined_file.csv'
header1 = 'LAT'  # Replace 'Header1' with the actual header name
header2 = 'LON'  # Replace 'Header2' with the actual header name
unique_combinations, count = unique_combinations_count(csv_file, header1, header2)
print("Unique combinations:", unique_combinations)
print("Count of unique combinations:", count)
