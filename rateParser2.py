import tabula
import PyPDF2
import pandas as pd
import os
import re
import warnings

#PDFBox library used by Tabula for PDF processing generates warnings which are not relevant to the functionality of the code.
warnings.filterwarnings("ignore")

def extract_area_code_from_page(pdf_path, page_number):
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        # Extract text from the specified page
        page = reader.pages[page_number - 1]
        text = page.extract_text()
        # Use regex to find the area code in the format "AREA \d+"
        match = re.search(r'AREA \d+', text)
        if match:
            return match.group(0)
    return None

def extract_area_code_from_table(df):
    # Convert all items to strings and combine them into a single string
    combined_text = ' '.join(df.astype(str).values.flatten())

    # Use regex to find the area code in the format "AREA \d+"
    match = re.search(r'AREA \d+', combined_text)
    if match:
        return match.group(0)
    return None

def extract_tables_from_pdf(pdf_path, start_page):
    # Get the total number of pages in the PDF
    total_pages = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
    total_pages_count = len(total_pages)
    table_counts = []
    # Loop through the pages from start_page till the end
    for page_number in range(start_page, total_pages_count):
        # Extract tables from the specified page
        tables = tabula.read_pdf(pdf_path, pages=page_number + 1, multiple_tables=True)
        # Count the number of tables
        table_count = len(tables)
        # Append the page number and table count to the list
        table_counts.append((page_number + 1, table_count))  # + to convert zero-indexed to one-indexed
        # Process each table
        for table in tables:
            # Convert the table to a DataFrame
            df = pd.DataFrame(table)
            # Print the first line of the extracted table
            if not df.empty:
                # Extract the area code from the top of the page
                area_code = extract_area_code_from_page(pdf_path, page_number + 1)
                if not area_code:
                    # If area code is not found in the page text, check inside the table
                    area_code = extract_area_code_from_table(df)
                print(f"Area code for page {page_number + 1}: {area_code}")  # Debug print
                table_head = df.head(0)
                header_columns_list = table_head.columns.tolist()
                header_columns_length = len(header_columns_list)
                carrier_details = [df.iloc[0, 0], df.iloc[0, 1], df.iloc[0, 2]]
                plan_type = header_columns_list[0]
                age_details = header_columns_list[2:header_columns_length - 1]

                # Open text file to write the extracted data
                output_file_path = os.path.join(os.path.dirname(__file__), 'outputData.txt')
                with open(output_file_path, 'a') as f:
                    # Loop through the DataFrame starting from row 1 to the last row
                    for index, row in df.iterrows():
                        if index == 0:
                            continue
                        carrier_details_data = [row.iloc[0], row.iloc[1], row.iloc[2]]
                        carrier_age_data = row.iloc[3:len(age_details) + 3]
                        for i in range(len(carrier_age_data)):
                            row_output = f"{area_code} ,{plan_type} , {carrier_details_data[0]} , {carrier_details_data[1]} , {carrier_details_data[2]} , {age_details[i]} , {carrier_age_data[i]}"
                            f.write(f"{row_output}" '\n')
    return table_counts

def main():
    data_folder = "data"
    pdf_file_name = "rateGuide.pdf"
    pdf_path = os.path.join(data_folder, pdf_file_name)

    table_counts = extract_tables_from_pdf(pdf_path, 7)

if __name__ == "__main__":
    main()