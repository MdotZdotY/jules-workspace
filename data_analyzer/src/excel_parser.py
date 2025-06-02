import pandas as pd
import openpyxl # Used by pandas as an engine for reading/writing .xlsx files
import zipfile # For BadZipFile error detection

def load_excel_data(file_paths: list[str], progress_callback=None) -> list[dict]:
    """
    Loads data from specified Excel files and their sheets into pandas DataFrames.

    Args:
        file_paths (list[str]): A list of string paths to Excel files.
        progress_callback (callable, optional): An optional function to call after each
            file is processed. It should accept two arguments:
            (current_file_index: int, total_files: int). Defaults to None.

    Returns:
        list[dict]: A list of dictionaries. Each dictionary represents a single sheet
        from an Excel file or an error encountered at the file/sheet level.

        For successfully loaded sheets, the dictionary contains:
            'file_path' (str): Path to the Excel file.
            'sheet_name' (str): Name of the sheet.
            'dataframe' (pd.DataFrame): Loaded data.
            'rows' (int): Number of rows in the DataFrame.
            'columns' (int): Number of columns in the DataFrame.
            'column_names' (list[str]): List of column names.

        For errors or issues, the dictionary contains:
            'file_path' (str): Path to the Excel file.
            'sheet_name' (str or None): Name of the sheet if error is sheet-specific,
                                       None if file-level error.
            'dataframe' (None): No DataFrame is loaded in case of error.
            'rows' (int): 0.
            'columns' (int): 0.
            'column_names' (list): Empty list.
            'error' (str): A user-friendly message describing the error.

    Catches and reports errors like:
        - FileNotFoundError if a file path is invalid.
        - zipfile.BadZipFile for corrupted .xlsx files or password-protection.
        - Empty files or files with no sheets.
        - Errors during parsing of specific sheets.
        - Other general processing errors.
    """
    loaded_files_data = []
    total_files = len(file_paths)

    if not isinstance(file_paths, list):
        # This is a programmatic error, should ideally be caught by the caller.
        # Returning it as an error entry for robustness in the UI.
        error_info = {
            'file_path': 'N/A', 'sheet_name': 'N/A', 'dataframe': None,
            'rows': 0, 'columns': 0, 'column_names': [],
            'error': 'Internal Error: file_paths argument was not a list of file paths.'
        }
        return [error_info]

    for i, file_path in enumerate(file_paths):
        try:
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names

            if not sheet_names:
                # File-level issue: Excel file contains no sheets.
                loaded_files_data.append({
                    'file_path': file_path, 'sheet_name': None, # No specific sheet
                    'dataframe': None, 'rows': 0, 'columns': 0, 'column_names': [],
                    'error': 'The Excel file contains no sheets.'
                })
                # Ensure progress callback is called even for files with errors/no sheets
                if progress_callback: progress_callback(i + 1, total_files)
                continue # Move to the next file

            for sheet_name in sheet_names:
                try:
                    df = excel_file.parse(sheet_name)
                    rows, columns = df.shape
                    column_names = list(df.columns)
                    sheet_data = {
                        'file_path': file_path, 'sheet_name': sheet_name, 'dataframe': df,
                        'rows': rows, 'columns': columns, 'column_names': column_names
                    }
                    loaded_files_data.append(sheet_data)
                except Exception as e_sheet:
                    # Error reading a specific sheet
                    loaded_files_data.append({
                        'file_path': file_path, 'sheet_name': sheet_name, 'dataframe': None,
                        'rows': 0, 'columns': 0, 'column_names': [],
                        'error': f"Error reading sheet '{sheet_name}': {type(e_sheet).__name__} - {e_sheet}"
                    })

        except FileNotFoundError:
            loaded_files_data.append({
                'file_path': file_path, 'sheet_name': None, 'dataframe': None,
                'rows': 0, 'columns': 0, 'column_names': [],
                'error': 'File not found at the specified path.' # Slightly more user-friendly
            })
        except zipfile.BadZipFile:
            loaded_files_data.append({
                'file_path': file_path, 'sheet_name': None, 'dataframe': None,
                'rows': 0, 'columns': 0, 'column_names': [],
                'error': 'File is corrupted, not a valid XLSX/ZIP file, or may be password-protected.'
            })
        except pd.errors.ParserError as e_parse:
             loaded_files_data.append({
                'file_path': file_path, 'sheet_name': None, 'dataframe': None,
                'rows': 0, 'columns': 0, 'column_names': [],
                'error': f"Error parsing the Excel file structure: {type(e_parse).__name__} - {e_parse}"
            })
        except ValueError as e_val: # Catches issues like "Excel file format cannot be determined"
            loaded_files_data.append({
                'file_path': file_path, 'sheet_name': None, 'dataframe': None,
                'rows': 0, 'columns': 0, 'column_names': [],
                'error': f"Error opening file (e.g., unsupported format, empty file, or invalid Excel structure): {type(e_val).__name__} - {e_val}"
            })
        except Exception as e_file: # Generic catch-all
            loaded_files_data.append({
                'file_path': file_path, 'sheet_name': None, 'dataframe': None,
                'rows': 0, 'columns': 0, 'column_names': [],
                'error': f"An unexpected error occurred while processing the file: {type(e_file).__name__} - {e_file}"
            })

        if progress_callback:
            progress_callback(i + 1, total_files)

    return loaded_files_data

if __name__ == "__main__":
    import os

    # Test progress callback function
    def simple_progress_update(current, total):
        print(f"Progress: File {current}/{total} processed.")

    # Setup: Create dummy files for various test scenarios
    dummy_files_to_create = {
        "good_data.xlsx": pd.DataFrame({'colA': [1, 2], 'colB': [3, 4]}),
        "empty_file.xlsx": None, # Represents a zero-byte file
        # "no_sheets.xlsx": "empty_workbook", # Creation of this is problematic with pandas/openpyxl
        "corrupted_text_as.xlsx": "This is not a valid Excel file content at all.", # Simulates a non-Excel file with .xlsx extension
        "actually_a_zip.zip.xlsx": None # Will create an empty zip file named .xlsx
    }

    created_files_for_test = []
    print("--- Test File Creation ---")
    for filename, content in dummy_files_to_create.items():
        try:
            if filename == "actually_a_zip.zip.xlsx":
                with zipfile.ZipFile(filename, 'w') as zf:
                    zf.writestr("dummy.txt", "this is a dummy_zip_file") # Make it a valid zip, but not xlsx
                created_files_for_test.append(filename)
                print(f"Created '{filename}' (valid zip, but not Excel).")
            elif content is None:
                open(filename, 'w').close()
                created_files_for_test.append(filename)
                print(f"Created '{filename}' (zero bytes).")
            elif isinstance(content, str):
                with open(filename, 'w') as f:
                    f.write(content)
                created_files_for_test.append(filename)
                print(f"Created '{filename}' (simulated corrupted/text file).")
            else:
                content.to_excel(filename, sheet_name="Sheet1", index=False)
                created_files_for_test.append(filename)
                print(f"Created '{filename}' (good data).")
        except Exception as e:
            print(f"Error creating dummy file {filename}: {e}")

    # Test with a file that simulates being password protected (triggers BadZipFile often)
    # For this, we can create a text file that starts with PK header like a zip but is not valid.
    # However, a more reliable way to test BadZipFile is a truly corrupted zip or a password-protected one,
    # which is hard to create programmatically without external tools/libs.
    # The "actually_a_zip.zip.xlsx" should be caught by pandas ValueError or similar.
    # A specific BadZipFile might be from a file that *is* an Office XML but malformed.
    # For now, the existing "corrupted_text_as.xlsx" and "actually_a_zip.zip.xlsx" will test general parsing failures.

    test_file_paths = created_files_for_test + ["non_existent_file.xlsx"]
    # Manually add a path that might represent a password-protected file if one could be created
    # test_file_paths.append("password_protected.xlsx") # Placeholder if such a file existed

    print(f"\n--- Testing load_excel_data with files: {test_file_paths} ---")
    loaded_data = load_excel_data(test_file_paths, progress_callback=simple_progress_update)

    print("\n--- Loaded Data Summary ---")
    for item in loaded_data:
        print(f"File: {item['file_path']}, Sheet: {item.get('sheet_name', 'N/A')}")
        if 'error' in item and item['error']:
            print(f"  Error: {item['error']}")
        elif item.get('dataframe') is not None:
            print(f"  Rows: {item['rows']}, Columns: {item['columns']}, Column Names: {item['column_names']}")
        else: # Should not happen if logic is correct, errors should be populated
            print(f"  No DataFrame and no specific error message (unexpected state).")
        print("-" * 20)

    print("\n--- Testing with invalid file_paths argument (not a list) ---")
    invalid_input_data = load_excel_data("not_a_list.xlsx") # type: ignore
    for item in invalid_input_data:
        print(f"File: {item['file_path']}, Sheet: {item.get('sheet_name', 'N/A')}, Error: {item.get('error')}")
        print("-" * 20)

    # Cleanup
    print("\n--- Cleaning up dummy files ---")
    for fname in created_files_for_test:
        try:
            if os.path.exists(fname):
                os.remove(fname)
                print(f"Removed '{fname}'.")
        except Exception as e:
            print(f"Error removing {fname}: {e}")
    print("--- Test finished ---")
