import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from .excel_parser import load_excel_data
from .chart_generator import create_chart
import matplotlib.pyplot as plt
import pandas as pd
# import numpy as np # Not directly used in this file, pandas handles NaN checks.

class DataAnalyzerApp:
    def __init__(self, root):
        """
        Initializes the DataAnalyzerApp GUI.

        Sets up the main window, frames, widgets for file loading, data display (Treeview),
        chart configuration (Comboboxes for X/Y axis, chart type), action buttons,
        and a status bar.

        Args:
            root: The root Tkinter window for the application.
        """
        self.root = root
        self.root.title("Excel Data Analyzer")
        self.root.geometry("850x700")

        self.loaded_file_data = []
        self.selected_sheet_data_for_config = None
        self.current_figure = None

        # --- Main layout frames ---
        top_frame = ttk.Frame(root, padding="5")
        top_frame.pack(fill=tk.X, side=tk.TOP)

        middle_frame = ttk.Frame(root, padding="5")
        middle_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        action_frame = ttk.Frame(root, padding="5")
        action_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding="2 5")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self._update_status("Ready. Load Excel file(s) to begin.")

        # --- Widgets ---
        self.load_button = ttk.Button(top_frame, text="Load Excel File(s)", command=self._load_files)
        self.load_button.pack(side=tk.LEFT, padx=5)
        self.progress_bar = ttk.Progressbar(top_frame, orient=tk.HORIZONTAL, length=200, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        paned_window = ttk.PanedWindow(middle_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        data_display_frame = ttk.Labelframe(paned_window, text="Loaded Sheets (Ctrl/Shift to multi-select)", padding="5")
        paned_window.add(data_display_frame, weight=1)

        self.tree_columns = ("file_path", "sheet_name", "rows", "cols")
        self.data_treeview = ttk.Treeview(data_display_frame, columns=self.tree_columns, show="headings", height=8, selectmode='extended')
        self.data_treeview.heading("file_path", text="File Path"); self.data_treeview.column("file_path", width=180, stretch=tk.YES)
        self.data_treeview.heading("sheet_name", text="Sheet Name"); self.data_treeview.column("sheet_name", width=130, stretch=tk.YES)
        self.data_treeview.heading("rows", text="Rows"); self.data_treeview.column("rows", width=50, anchor=tk.E)
        self.data_treeview.heading("cols", text="Columns"); self.data_treeview.column("cols", width=50, anchor=tk.E)

        tree_scrollbar_y = ttk.Scrollbar(data_display_frame, orient=tk.VERTICAL, command=self.data_treeview.yview)
        self.data_treeview.configure(yscrollcommand=tree_scrollbar_y.set)
        tree_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.data_treeview.pack(fill=tk.BOTH, expand=True)
        self.data_treeview.bind('<<TreeviewSelect>>', self._on_treeview_selection_change)

        chart_config_frame = ttk.Labelframe(paned_window, text="Chart Configuration (from last focused sheet)", padding="5")
        paned_window.add(chart_config_frame, weight=1)

        ttk.Label(chart_config_frame, text="X-Axis Column:").grid(row=0, column=0, padx=5, pady=3, sticky=tk.W)
        self.x_axis_var = tk.StringVar()
        self.x_axis_combobox = ttk.Combobox(chart_config_frame, textvariable=self.x_axis_var, state="readonly", width=25)
        self.x_axis_combobox.grid(row=0, column=1, padx=5, pady=3, sticky=tk.EW)
        self.x_axis_combobox.bind('<<ComboboxSelected>>', lambda e: self._update_generate_button_state())

        ttk.Label(chart_config_frame, text="Y-Axis Column(s):").grid(row=1, column=0, padx=5, pady=3, sticky=tk.W)
        self.y_axis_listbox = tk.Listbox(chart_config_frame, selectmode=tk.MULTIPLE, exportselection=False, height=4, width=27)
        y_scroll = ttk.Scrollbar(chart_config_frame, orient=tk.VERTICAL, command=self.y_axis_listbox.yview)
        self.y_axis_listbox.configure(yscrollcommand=y_scroll.set)
        self.y_axis_listbox.grid(row=1, column=1, padx=5, pady=3, sticky=tk.EW)
        y_scroll.grid(row=1, column=2, sticky=tk.NS)
        self.y_axis_listbox.bind('<<ListboxSelect>>', lambda e: self._update_generate_button_state())

        ttk.Label(chart_config_frame, text="Chart Type:").grid(row=2, column=0, padx=5, pady=3, sticky=tk.W)
        self.chart_type_var = tk.StringVar()
        self.chart_type_combobox = ttk.Combobox(chart_config_frame, textvariable=self.chart_type_var, state="readonly", width=25)
        self.chart_type_combobox['values'] = ["Line", "Bar", "Scatter"]
        self.chart_type_combobox.grid(row=2, column=1, padx=5, pady=3, sticky=tk.EW)
        if self.chart_type_combobox['values']: self.chart_type_combobox.current(0)
        self.chart_type_combobox.bind('<<ComboboxSelected>>', lambda e: self._update_generate_button_state())

        self.generate_chart_button = ttk.Button(action_frame, text="Generate Chart", command=self._generate_chart)
        self.generate_chart_button.pack(side=tk.RIGHT, padx=5, pady=5)
        self.generate_chart_button.config(state=tk.DISABLED)

    def _update_status(self, message: str, is_error: bool = False, clear_after_ms: int = None):
        """
        Updates the status bar text and color.

        Args:
            message (str): The message to display.
            is_error (bool): If True, message is displayed in red. Defaults to False.
            clear_after_ms (int, optional): If provided, message is cleared after this
                                            many milliseconds. Defaults to None.
        """
        # print(f"Status Update: {message}" + (" (Error)" if is_error else "")) # For headless test
        self.status_var.set(message)
        self.status_bar.config(foreground="red" if is_error else "black")

        if clear_after_ms and clear_after_ms > 0 :
            self.root.after(clear_after_ms, lambda: self.status_var.set("") if self.status_var.get() == message else None)

    def _progress_update_ui(self, current_file_index: int, total_files: int):
        """
        Callback function to update the progress bar during file loading.

        Args:
            current_file_index (int): The index of the file currently processed (1-based).
            total_files (int): The total number of files to process.
        """
        self.progress_bar['value'] = (current_file_index / total_files) * 100
        self.root.update_idletasks()

    def _load_files(self):
        """
        Handles the "Load Excel File(s)" button click.

        Opens a file dialog for selecting multiple Excel files.
        Calls `excel_parser.load_excel_data` to process them.
        Populates the Treeview with loaded sheet information or errors.
        Updates UI elements like progress bar and status bar.
        """
        _print_instead_of_messagebox = False
        try:
            _test_root = tk.Tk(); _test_root.withdraw(); _test_root.destroy()
        except tk.TclError: _print_instead_of_messagebox = True

        file_paths = filedialog.askopenfilenames(title="Select Excel Files", filetypes=(("Excel files", "*.xlsx *.xls"),("All files", "*.*")))
        if not file_paths:
            self._update_status("File loading cancelled.", clear_after_ms=3000)
            return

        self._update_status(f"Loading {len(file_paths)} file(s)...")
        self.loaded_file_data.clear()
        for item in self.data_treeview.get_children(): self.data_treeview.delete(item)
        self._clear_chart_config()
        self.selected_sheet_data_for_config = None

        self.progress_bar['value'] = 0
        try:
            self.loaded_file_data = load_excel_data(list(file_paths), progress_callback=self._progress_update_ui)
        except Exception as e:
            msg = f"An unexpected error occurred during file loading: {e}"
            if _print_instead_of_messagebox: print(f"MessageBox Error: {msg}")
            else: messagebox.showerror("Error Loading Files", msg)
            self._update_status(f"Error loading files: {e}", is_error=True)
            return # Ensure progress bar is reset if error occurs before load_excel_data finishes
        finally:
            self.progress_bar['value'] = 100 # Ensure progress bar completes regardless of outcome after this point

        if not self.loaded_file_data: # Should be redundant if excel_parser always returns a list, even of errors
            msg = "No data or sheets found in selected file(s) (or parser returned empty list)."
            if _print_instead_of_messagebox: print(f"MessageBox Info: {msg}")
            else: messagebox.showinfo("No Data", msg)
            self._update_status(msg, is_error=True, clear_after_ms=5000)
            self._update_generate_button_state()
            return

        num_actual_data_entries = 0
        for idx, item_data in enumerate(self.loaded_file_data):
            iid = str(idx)
            if 'error' in item_data and item_data['error']:
                self.data_treeview.insert("", tk.END, iid=iid, values=(item_data['file_path'], item_data.get('sheet_name', 'N/A'), "Error", item_data['error']))
            elif item_data.get('dataframe') is not None: # Check for dataframe presence
                 self.data_treeview.insert("", tk.END, iid=iid, values=(item_data['file_path'], item_data['sheet_name'], item_data['rows'], item_data['columns']))
                 num_actual_data_entries +=1
            else:
                 self.data_treeview.insert("", tk.END, iid=iid, values=(item_data['file_path'], item_data.get('sheet_name', 'N/A'), "Error", "Invalid entry, no data/error"))

        if num_actual_data_entries == 0: # Check if any valid data was actually loaded
            msg = "No data could be loaded. Selected files might be empty, corrupted, or have no valid sheets."
            if _print_instead_of_messagebox: print(f"MessageBox Info: {msg}")
            else: messagebox.showinfo("No Data Loaded", msg)
            self._update_status(msg, is_error=True)
        else:
             self._update_status(f"{num_actual_data_entries} sheet(s) loaded successfully. Ready to configure chart.", clear_after_ms=5000)

        if self.data_treeview.get_children(): # If treeview has any items (data or errors)
            first_item_iid = self.data_treeview.get_children()[0]
            self.data_treeview.focus(first_item_iid)
            self.data_treeview.selection_set(first_item_iid)
        self._on_treeview_selection_change()

    def _clear_chart_config(self):
        """Resets chart configuration UI elements to their default states."""
        self.x_axis_combobox['values'] = []
        self.x_axis_var.set('')
        self.y_axis_listbox.delete(0, tk.END)
        if self.chart_type_combobox['values']: self.chart_type_combobox.current(0)
        self._update_status("Chart configuration cleared.", clear_after_ms=3000)

    def _on_treeview_selection_change(self, event=None):
        """
        Handles selection changes in the Treeview.

        Updates the X/Y axis column choices based on the currently focused sheet.
        Calls `_update_generate_button_state` to reflect eligibility for chart generation.
        """
        focused_item_id = self.data_treeview.focus()

        if not focused_item_id :
            self.selected_sheet_data_for_config = None
            self._clear_chart_config() # Also updates status
            self._update_generate_button_state()
            return

        try:
            data_idx = int(focused_item_id)
            sheet_info = self.loaded_file_data[data_idx]
            df_for_config = sheet_info.get('dataframe') # Get dataframe if it exists

            if 'error' in sheet_info or df_for_config is None:
                self.selected_sheet_data_for_config = None
                self._clear_chart_config()
                self._update_status(f"Focused item '{sheet_info.get('file_path','Unknown')}/{sheet_info.get('sheet_name', 'N/A')}' has error or no data.", is_error=True, clear_after_ms=5000)
            elif df_for_config.empty:
                self.selected_sheet_data_for_config = sheet_info
                self._clear_chart_config()
                self._update_status(f"Focused sheet '{sheet_info['sheet_name']}' is empty. No columns to select.", clear_after_ms=5000)
            else:
                self.selected_sheet_data_for_config = sheet_info
                column_names = list(df_for_config.columns)
                self.x_axis_combobox['values'] = column_names
                self.y_axis_listbox.delete(0, tk.END)
                for col_name in column_names: self.y_axis_listbox.insert(tk.END, col_name)

                if column_names: self.x_axis_var.set(column_names[0]) # Default to first column
                else: self.x_axis_var.set('') # Should not happen if df_for_config is not empty
                self._update_status(f"Chart config using columns from: {sheet_info['file_path'].split('/')[-1]}/{sheet_info['sheet_name']}", clear_after_ms=5000)

        except (ValueError, IndexError): # Error converting IID or accessing loaded_file_data
            self.selected_sheet_data_for_config = None
            self._clear_chart_config()
            self._update_status(f"Error processing focused sheet (ID: {focused_item_id}).", is_error=True, clear_after_ms=5000)

        self._update_generate_button_state()

    def _update_generate_button_state(self):
        """
        Updates the state (enabled/disabled) of the 'Generate Chart' button.
        The button is enabled if:
        - At least one sheet is selected in the Treeview.
        - An X-axis column is selected.
        - At least one Y-axis column is selected.
        - A chart type is selected (always true due to default).
        - The sheet used for configuring column choices (`selected_sheet_data_for_config`)
          is valid (has a non-empty DataFrame).
        """
        # print("UI Debug: Updating button state...") # For headless test
        state_to_set = tk.DISABLED
        tooltip_message = ""

        if not self.data_treeview.selection():
            tooltip_message = "Select one or more sheets from the list."
        elif not self.x_axis_var.get():
            tooltip_message = "Select an X-axis column for the chart."
        elif not self.y_axis_listbox.curselection():
            tooltip_message = "Select at least one Y-axis column."
        # Chart type var always has a value due to default setting
        # elif not self.chart_type_var.get():
        #     tooltip_message = "Select a chart type." (This condition is unlikely to be met)
        elif self.selected_sheet_data_for_config is None or \
             self.selected_sheet_data_for_config.get('dataframe') is None:
             tooltip_message = "Focused sheet (used for column names) has an error or no data."
        elif self.selected_sheet_data_for_config.get('dataframe').empty:
             tooltip_message = f"Focused sheet '{self.selected_sheet_data_for_config['sheet_name']}' is empty. Cannot determine columns."
        else:
            state_to_set = tk.NORMAL
            tooltip_message = "Ready to generate chart."

        self.generate_chart_button.config(state=state_to_set)
        if state_to_set == tk.DISABLED and tooltip_message:
             self._update_status(tooltip_message, is_error=True, clear_after_ms=4000)
        elif state_to_set == tk.NORMAL: # Clear error/instruction if button becomes enabled
             if self.status_var.get() == tooltip_message : self._update_status("") # Clear only if it's the same message
             else: self._update_status(tooltip_message, clear_after_ms=4000)


    def _generate_chart(self):
        """
        Generates a chart based on selected sheets and UI configurations.

        Aggregates data from all sheets selected in the Treeview that are compatible
        with the X/Y column configuration (derived from the focused sheet).
        Performs data validation before calling `chart_generator.create_chart`.
        Displays the chart or error messages.
        """
        _print_instead_of_messagebox = False
        try:
            _test_root = tk.Tk(); _test_root.withdraw(); _test_root.destroy()
        except tk.TclError: _print_instead_of_messagebox = True

        selected_item_ids = self.data_treeview.selection()
        if not selected_item_ids: # Should be prevented by button state, but as a safeguard
            msg = "No sheets selected. Please select one or more sheets from the list."
            if _print_instead_of_messagebox: print(f"MessageBox Error: {msg}")
            else: messagebox.showerror("Selection Error", msg)
            self._update_status(msg, is_error=True, clear_after_ms=5000)
            return

        x_col = self.x_axis_var.get()
        y_col_indices = self.y_axis_listbox.curselection()
        y_cols = [self.y_axis_listbox.get(i) for i in y_col_indices]
        chart_type = self.chart_type_var.get()

        if not x_col or not y_cols or not chart_type: # Safeguard
            msg = "Missing chart configuration: Ensure X-axis, Y-axis, and chart type are selected."
            if _print_instead_of_messagebox: print(f"MessageBox Error: {msg}")
            else: messagebox.showerror("Configuration Error", msg)
            self._update_status(msg, is_error=True, clear_after_ms=5000)
            return

        self._update_status(f"Generating '{chart_type}' chart...")
        valid_dataframes = []
        processed_sheet_display_names = []

        for item_id in selected_item_ids:
            try:
                data_idx = int(item_id)
                sheet_info = self.loaded_file_data[data_idx]
                df_current_sheet = sheet_info.get('dataframe')

                if 'error' in sheet_info or df_current_sheet is None:
                    self._update_status(f"Skipping '{sheet_info.get('sheet_name',item_id)}': has error or no data.", clear_after_ms=3000)
                    continue
                if df_current_sheet.empty:
                    self._update_status(f"Skipping '{sheet_info['sheet_name']}': sheet is empty.", clear_after_ms=3000)
                    continue

                missing_cols = [col for col in [x_col] + y_cols if col not in df_current_sheet.columns]
                if not missing_cols:
                    valid_dataframes.append(df_current_sheet)
                    processed_sheet_display_names.append(f"{sheet_info['file_path'].split('/')[-1]}/{sheet_info['sheet_name']}")
                else:
                    msg = f"Skipping sheet '{sheet_info['sheet_name']}': missing required columns: {', '.join(missing_cols)} (based on focused sheet config)."
                    if _print_instead_of_messagebox: print(f"MessageBox Warning: {msg}")
                    else: messagebox.showwarning("Skipped Sheet", msg)
                    self._update_status(msg, is_error=True, clear_after_ms=5000)
            except (ValueError, IndexError):
                self._update_status(f"Error processing sheet ID '{item_id}'. Skipping.", is_error=True, clear_after_ms=5000)
                continue

        if not valid_dataframes:
            msg = "No selected sheets were compatible or contained data for the chosen X/Y columns."
            if _print_instead_of_messagebox: print(f"MessageBox Error: {msg}")
            else: messagebox.showerror("Data Error", msg)
            self._update_status(msg, is_error=True, clear_after_ms=5000)
            return

        try:
            combined_df = pd.concat(valid_dataframes, ignore_index=True)
        except Exception as e:
            msg = f"Failed to combine data from selected sheets: {e}"
            if _print_instead_of_messagebox: print(f"MessageBox Error: {msg}")
            else: messagebox.showerror("Data Combination Error", msg)
            self._update_status(msg, is_error=True, clear_after_ms=5000)
            return

        if combined_df.empty:
            msg = "Combined data from selected sheets is empty. Cannot generate chart."
            if _print_instead_of_messagebox: print(f"MessageBox Error: {msg}")
            else: messagebox.showerror("Data Error", msg)
            self._update_status(msg, is_error=True, clear_after_ms=5000)
            return

        # Pre-charting validation on combined_df
        if x_col not in combined_df.columns or any(y_c not in combined_df.columns for y_c in y_cols):
             msg = "X or Y columns (from focused sheet) are not present in the final combined data. This can happen if selected sheets have very different structures."
             if _print_instead_of_messagebox: print(f"MessageBox Error: {msg}")
             else: messagebox.showerror("Data Error", msg)
             self._update_status(msg, is_error=True, clear_after_ms=5000)
             return

        if combined_df[x_col].isnull().all() or all(combined_df[y_c].isnull().all() for y_c in y_cols):
            msg = f"X-axis column ('{x_col}') or all selected Y-axis columns ({', '.join(y_cols)}) contain only NaN/empty values in the combined data."
            if _print_instead_of_messagebox: print(f"MessageBox Error: {msg}")
            else: messagebox.showerror("Data Error",msg)
            self._update_status(msg, is_error=True, clear_after_ms=5000)
            return

        # Type checks specific to chart_type, now on combined_df
        if chart_type in ["Line", "Scatter"]:
            if not pd.api.types.is_numeric_dtype(combined_df[x_col]) and not pd.api.types.is_datetime64_any_dtype(combined_df[x_col]):
                msg = f"X-axis ('{x_col}') must be numeric or datetime for {chart_type} charts. Current type: {combined_df[x_col].dtype}."
                if _print_instead_of_messagebox: print(f"MessageBox Error: {msg}")
                else: messagebox.showerror("Data Type Error",msg)
                self._update_status(msg, is_error=True, clear_after_ms=5000)
                return
            for y_c in y_cols:
                if not pd.api.types.is_numeric_dtype(combined_df[y_c]) and not pd.api.types.is_datetime64_any_dtype(combined_df[y_c]):
                    msg = f"Y-axis ('{y_c}') must be numeric or datetime for {chart_type} charts. Current type: {combined_df[y_c].dtype}."
                    if _print_instead_of_messagebox: print(f"MessageBox Error: {msg}")
                    else: messagebox.showerror("Data Type Error",msg)
                    self._update_status(msg, is_error=True, clear_after_ms=5000)
                    return
        elif chart_type == "Bar": # Bar charts need numeric Y, X can be categorical (already handled by chart_generator)
            for y_c in y_cols:
                if not pd.api.types.is_numeric_dtype(combined_df[y_c]):
                    msg = f"Y-axis ('{y_c}') must be numeric for Bar charts. Current type: {combined_df[y_c].dtype}."
                    if _print_instead_of_messagebox: print(f"MessageBox Error: {msg}")
                    else: messagebox.showerror("Data Type Error",msg)
                    self._update_status(msg, is_error=True, clear_after_ms=5000)
                    return

        title_suffix = f" (From: {', '.join(processed_sheet_display_names)})" if len(processed_sheet_display_names) > 1 else f" (From: {processed_sheet_display_names[0] if processed_sheet_display_names else 'N/A'})"

        try:
            if self.current_figure and plt.fignum_exists(self.current_figure.number): plt.close(self.current_figure)

            self.current_figure = create_chart(combined_df, x_col, y_cols, chart_type)
            if self.current_figure:
                current_chart_title = self.current_figure.axes[0].get_title()
                self.current_figure.axes[0].set_title(current_chart_title + title_suffix, fontsize='small') # Append to existing title
                self.current_figure.tight_layout() # Re-adjust layout
                self._update_status(f"Chart '{current_chart_title}' generated successfully.", clear_after_ms=5000)
                if not _print_instead_of_messagebox: plt.show(block=False)
                else: print("UI (headless): Skipping plt.show(). Chart ready if running with display.")
            else:
                msg="Chart creation failed: No figure returned from chart generator."
                if _print_instead_of_messagebox: print(f"MessageBox Error: {msg}")
                else: messagebox.showerror("Chart Error", msg)
                self._update_status(msg, is_error=True)
        except (ValueError, TypeError) as e: # Errors from create_chart
            msg = f"Chart generation error: {e}"
            if _print_instead_of_messagebox: print(f"MessageBox Error: {msg}")
            else: messagebox.showerror("Chart Error", msg)
            self._update_status(msg, is_error=True, clear_after_ms=10000)
        except Exception as e:
            msg = f"An unexpected error occurred during chart display: {type(e).__name__} - {e}"
            if _print_instead_of_messagebox: print(f"MessageBox Error: {msg}")
            else: messagebox.showerror("Display Error", msg)
            self._update_status(msg, is_error=True, clear_after_ms=10000)


if __name__ == '__main__':
    print("UI Enhancements Test (headless): Attempting to instantiate DataAnalyzerApp...")
    root_test = None
    app_test = None
    try:
        root_test = tk.Tk()
        app_test = DataAnalyzerApp(root_test)
        print("UI Test: DataAnalyzerApp instance created successfully (includes status bar).")

        if app_test:
            print("UI Test: Testing status bar updates...")
            app_test._update_status("Test status message.")
            app_test._update_status("Test error message.", is_error=True)
            app_test._update_status("Test temporary message.", clear_after_ms=10)
            print("UI Test: Status bar update calls completed.")
            print("UI Test: Review _update_generate_button_state logic and bindings manually.")

    except tk.TclError as e:
        if "no display name" in str(e):
            print(f"UI Test: Caught TclError (expected in headless for full app init): {e}")
        else:
            print(f"UI Test: Caught unexpected TclError: {e}")
    except Exception as e:
        import traceback
        print(f"UI Test: An unexpected error occurred during __main__ test: {e}")
        print(traceback.format_exc())
    finally:
        if app_test and hasattr(app_test, 'current_figure') and app_test.current_figure:
             try: plt.close(app_test.current_figure)
             except: pass
        if root_test:
            try: root_test.destroy()
            except: pass

    print("\nUI enhancements direct test finished (limited by headless environment).")
