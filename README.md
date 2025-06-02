# Excel Data Analyzer & Chart Generator

## Description

The Excel Data Analyzer is a Python application designed to help users load data from Microsoft Excel files, select sheets, and generate various types of charts (Line, Bar, Scatter) based on the data. It provides a user-friendly graphical interface built with Tkinter for easy interaction.

This tool is useful for quick data exploration and visualization directly from Excel files without needing complex BI tools or extensive coding for simple plotting tasks.

## Features

*   **Load Multiple Excel Files:** Supports loading data from one or more `.xlsx` or `.xls` files.
*   **Sheet Selection:** Users can select one or multiple sheets from the loaded files to combine data for charting.
*   **Dynamic Chart Configuration:**
    *   Select X-axis column from the data.
    *   Select one or more Y-axis columns.
    *   Choose chart type: Line, Bar, or Scatter.
*   **Chart Generation:** Displays charts using Matplotlib in a separate window.
*   **Error Handling:** Provides feedback for issues like file not found, corrupted files, empty sheets, or incompatible data types for selected chart configurations.
*   **Progress Bar:** Shows progress during file loading.
*   **Status Bar:** Displays contextual information and messages.
*   **Multi-Sheet Plotting:** Ability to combine data from multiple selected sheets (if columns are compatible) into a single chart.

## Requirements

*   Python 3.7+
*   The following Python libraries (also listed in `data_analyzer/requirements.txt`):
    *   `pandas`
    *   `openpyxl` (for reading `.xlsx` files)
    *   `matplotlib`
    *   `Tkinter` (usually included with standard Python installations, but may require separate installation on some systems, e.g., `python3-tk` on Debian/Ubuntu).

## Setup

1.  **Clone the Repository (or Download Files):**
    ```bash
    # If this were a git repository:
    # git clone <repository_url>
    # cd <repository_directory>

    # For now, ensure you have the 'data_analyzer' directory and this README.md
    # in your project's root folder.
    ```

2.  **Create a Virtual Environment (Recommended):**
    From the project root directory (the directory containing the `data_analyzer` folder):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    Ensure your virtual environment is activated. From the project root directory:
    ```bash
    pip install -r data_analyzer/requirements.txt
    ```
    If you are on a system where Tkinter is separate (like some Linux distributions), you might also need to install it system-wide:
    ```bash
    sudo apt-get update
    sudo apt-get install python3-tk  # For Debian/Ubuntu based systems
    ```

## Running the Application

There are two main ways to run the application from your project's root directory (the directory that contains the `data_analyzer` folder):

1.  **Using the `python -m` option (Recommended for proper package handling):**
    This command tells Python to run the `main` module located within the `data_analyzer` package.
    ```bash
    python3 -m data_analyzer.main
    ```

2.  **Directly executing the `main.py` script:**
    This also works if Python correctly resolves the package structure. Make sure your current working directory is the project root.
    ```bash
    python3 data_analyzer/main.py
    ```

Upon running, the application's GUI should appear, allowing you to load Excel files and generate charts.

## Project Structure
```
<project_root>/
├── data_analyzer/
│   ├── __init__.py
│   ├── main.py                 # Main script to run the application
│   ├── requirements.txt        # Python package dependencies
│   └── src/
│       ├── __init__.py
│       ├── excel_parser.py     # Handles loading and parsing Excel files
│       ├── chart_generator.py  # Handles creation of charts
│       └── ui.py               # Defines the Tkinter GUI and its logic
└── README.md                   # This file
```
