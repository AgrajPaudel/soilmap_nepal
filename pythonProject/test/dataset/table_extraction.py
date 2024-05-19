import fitz  # PyMuPDF
import tabula
import os
import pandas as pd


def extract_tables_from_pdf(pdf_path):
    # Extract the name of the PDF file without extension
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

    # Create a directory with the same name as the PDF file
    output_dir = os.path.join(os.getcwd(), pdf_name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Use tabula to extract tables
    tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)

    # Save each table as a separate CSV file
    for i, table in enumerate(tables):
        csv_filename = os.path.join(output_dir, f"table_{i + 1}.csv")
        table.to_csv(csv_filename, index=False)
        print(f"Saved {csv_filename}")


pdf_path = 'STATISTICAL-INFORMATION-ON-NEPALESE-AGRICULTURE-2077-78.pdf'
extract_tables_from_pdf(pdf_path)
