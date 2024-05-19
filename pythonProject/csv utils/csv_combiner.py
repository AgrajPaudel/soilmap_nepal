import csv
import os


def combine_csv_files(file1_path, file2_path, output_path):
    # Check if both files exist
    if not os.path.isfile(file1_path) or not os.path.isfile(file2_path):
        print("Error: One or both input files do not exist.")
        return

    # Read headers from both files
    with open(file1_path, 'r', newline='', encoding='utf-8') as file1, \
            open(file2_path, 'r', newline='', encoding='utf-8') as file2:
        reader1 = csv.DictReader(file1)
        reader2 = csv.DictReader(file2)

        headers1 = reader1.fieldnames
        headers2 = reader2.fieldnames

        # Check if headers are the same in both files
        if headers1 != headers2:
            print("Error: Headers of the input files do not match.")
            return

        # Combine headers and write to output file
        with open(output_path, 'w', newline='', encoding='utf-8') as output_file:
            writer = csv.DictWriter(output_file, fieldnames=headers1)
            writer.writeheader()

            # Write rows from the first file
            for row in reader1:
                writer.writerow(row)

            # Write rows from the second file
            for row in reader2:
                writer.writerow(row)

    print("CSV files combined successfully.")


# Example usage
file1_path = 'climate_data_nepal_district_wise_daily_part_i.csv'
file2_path = 'climate_data_nepal_district_wise_daily_part_ii.csv'
output_path = 'combined_file.csv'
combine_csv_files(file1_path, file2_path, output_path)
