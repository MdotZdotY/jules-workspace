import matplotlib.pyplot as plt
import pandas as pd
import numpy as np # For numerical operations, e.g., for bar chart x-axis

def create_chart(data_df: pd.DataFrame, x_column: str, y_columns: list[str], chart_type: str):
    """
    Generates a chart based on the provided DataFrame and configuration.

    Args:
        data_df (pd.DataFrame): The pandas DataFrame containing the data for plotting.
        x_column (str): The name of the column to be used for the X-axis.
        y_columns (list[str]): A list of column names to be used for the Y-axis.
        chart_type (str): The type of chart to generate. Supported types are
                          "Line", "Bar", and "Scatter".

    Returns:
        matplotlib.figure.Figure: The generated Matplotlib figure object. This allows
                                  the caller (e.g., the UI) to manage how the chart is
                                  displayed (e.g., using `plt.show()`, embedding in a GUI,
                                  or saving to a file).

    Raises:
        ValueError: If `x_column` or any of `y_columns` are not found in `data_df`,
                    if `x_column` or `y_columns` are not specified, or if `chart_type`
                    is unsupported.
        TypeError: If `data_df` is not a pandas DataFrame, or if the data types of
                   the selected columns are incompatible with the chosen `chart_type`
                   (e.g., non-numeric data for a line chart's Y-axis).
    """
    if not isinstance(data_df, pd.DataFrame):
        raise TypeError("Input 'data_df' must be a pandas DataFrame.")
    if not x_column or not y_columns:
        raise ValueError("X-axis column and at least one Y-axis column must be specified.")
    if x_column not in data_df.columns:
        raise ValueError(f"X-axis column '{x_column}' not found in DataFrame.")
    for y_col in y_columns:
        if y_col not in data_df.columns:
            raise ValueError(f"Y-axis column '{y_col}' not found in DataFrame.")

    fig, ax = plt.subplots(figsize=(10, 6)) # Create a new figure and axes

    try:
        # Validate X column data type for Line and Scatter charts
        if chart_type in ["Line", "Scatter"]:
             if not (pd.api.types.is_numeric_dtype(data_df[x_column]) or \
                     pd.api.types.is_datetime64_any_dtype(data_df[x_column])):
                 raise TypeError(f"X-axis column '{x_column}' must be numeric or datetime for {chart_type} charts. Current type: {data_df[x_column].dtype}.")

        if chart_type == "Line":
            for y_col in y_columns:
                if not (pd.api.types.is_numeric_dtype(data_df[y_col]) or \
                        pd.api.types.is_datetime64_any_dtype(data_df[y_col])):
                    raise TypeError(f"Y-axis column '{y_col}' must be numeric or datetime for Line charts. Current type: {data_df[y_col].dtype}.")
                ax.plot(data_df[x_column], data_df[y_col], label=y_col, marker='o')

        elif chart_type == "Bar":
            num_y_cols = len(y_columns)
            # For Bar charts, X-axis is typically categorical. Convert to string for robust handling.
            x_data_labels = data_df[x_column].astype(str)
            x_indices = np.arange(len(x_data_labels))

            total_bar_width_space = 0.8 # Total width allocated for bars at each x-tick
            bar_width = total_bar_width_space / num_y_cols

            for i, y_col in enumerate(y_columns):
                if not pd.api.types.is_numeric_dtype(data_df[y_col]):
                    raise TypeError(f"Y-axis column '{y_col}' must be numeric for Bar charts. Current type: {data_df[y_col].dtype}.")
                # Calculate offset for each bar in a group to position them side-by-side
                offset = (i - (num_y_cols - 1) / 2) * bar_width
                ax.bar(x_indices + offset, data_df[y_col], width=bar_width, label=y_col)

            ax.set_xticks(x_indices)
            ax.set_xticklabels(x_data_labels, rotation=45, ha="right")

        elif chart_type == "Scatter":
            # X-axis type already validated for Scatter charts above
            for y_col in y_columns:
                if not pd.api.types.is_numeric_dtype(data_df[y_col]):
                    raise TypeError(f"Y-axis column '{y_col}' must be numeric for Scatter charts. Current type: {data_df[y_col].dtype}.")
                ax.scatter(data_df[x_column], data_df[y_col], label=y_col)

        else:
            # This case should ideally be prevented by the UI's ComboBox choices.
            raise ValueError(f"Unsupported chart type: '{chart_type}'. Supported types are 'Line', 'Bar', 'Scatter'.")

        ax.set_xlabel(str(x_column)) # Ensure x_column name is a string for the label
        ax.set_ylabel("Values") # Generic Y-label; can be customized further if needed
        ax.set_title(f"{chart_type} Chart: {', '.join(y_columns)} vs {x_column}")
        ax.legend()
        ax.grid(True) # Add a grid for better readability

        fig.tight_layout() # Adjust layout to prevent labels from overlapping

        return fig

    except Exception as e:
        plt.close(fig) # Clean up the Matplotlib figure if an error occurs during plotting
        raise # Re-raise the caught exception to be handled by the caller (UI)


if __name__ == '__main__':
    # This block is for direct testing of chart_generator.py.
    # It will attempt to create chart figures but not display them with plt.show()
    # to avoid issues in headless environments.
    print("Testing chart_generator.py...")

    sample_data = {
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Sales_Product_A': [150, 200, 180, 220, 250, 210],
        'Sales_Product_B': [120, 190, 160, 200, 230, 190],
        'Temperature': [10, 12, 15, 18, 22, 25],
        'Rainfall_mm': [50.5, 40.2, 60.1, 30.7, 20.0, 10.3],
        'Customer_Count': [20,22,25,23,28,30],
        'Categories': ['Cat1', 'Cat2', 'Cat1', 'Cat3', 'Cat2', 'Cat1']
    }
    df_test = pd.DataFrame(sample_data)
    df_test['Date'] = pd.to_datetime(['2023-01-01', '2023-02-01', '2023-03-01', '2023-04-01', '2023-05-01', '2023-06-01'])

    print("Sample DataFrame created for testing.")
    # print(df_test) # Keep console output minimal for review

    test_configs = [
        {"x": "Date", "y": ["Sales_Product_A", "Sales_Product_B"], "type": "Line"},
        {"x": "Month", "y": ["Sales_Product_A", "Sales_Product_B"], "type": "Bar"},
        {"x": "Categories", "y": ["Customer_Count"], "type": "Bar"},
        {"x": "Temperature", "y": ["Rainfall_mm", "Sales_Product_A"], "type": "Scatter"},
        {"x": "Customer_Count", "y": ["Sales_Product_A"], "type": "Line"},
    ]

    print("\n--- Running Valid Test Cases ---")
    for i, config in enumerate(test_configs):
        print(f"Test Case {i+1}: Type='{config['type']}', X='{config['x']}', Y={config['y']}")
        try:
            fig = create_chart(df_test, config["x"], config["y"], config["type"])
            if fig:
                print(f"  Result: Chart figure created successfully.")
                plt.close(fig)
            else: # Should not happen if create_chart is correct
                print("  Result: Chart creation returned None (Error in logic).")
        except (ValueError, TypeError) as e:
            print(f"  Result: Failed with expected error - {type(e).__name__}: {e}")
        except Exception as e:
            print(f"  Result: Failed with unexpected error - {type(e).__name__}: {e}")

    print("\n--- Running Error Handling Test Cases ---")
    error_configs = [
        {"x": "NonExistentColumn", "y": ["Sales_Product_A"], "type": "Line", "expected": ValueError},
        {"x": "Month", "y": ["NonExistentColumn"], "type": "Bar", "expected": ValueError},
        {"x": "Month", "y": ["Sales_Product_A"], "type": "UnsupportedChart", "expected": ValueError},
        {"x": "Month", "y": ["Sales_Product_A"], "type": "Line", "expected": TypeError}, # X (Month) is string
        {"x": "Temperature", "y": ["Month"], "type": "Scatter", "expected": TypeError}, # Y (Month) is string
        {"x": "Date", "y": ["Categories"], "type": "Line", "expected": TypeError},      # Y (Categories) is string
        {"x": "Categories", "y": ["Date"], "type": "Bar", "expected": TypeError},     # Y (Date) is datetime
    ]
    for i, config in enumerate(error_configs):
        print(f"Error Test Case {i+1}: Type='{config['type']}', X='{config['x']}', Y={config['y']}, Expected: {config['expected'].__name__}")
        try:
            fig = create_chart(df_test, config["x"], config["y"], config["type"])
            if fig:
                plt.close(fig)
                print(f"  Result: Chart created - Test Failed (expected {config['expected'].__name__}).")
        except config['expected'] as e:
            print(f"  Result: Caught expected error - {type(e).__name__}: {e}")
        except Exception as e:
            print(f"  Result: Caught unexpected error - {type(e).__name__}: {e} (Test Failed, expected {config['expected'].__name__})")

    print("\nChart generator tests finished.")
