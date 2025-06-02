import tkinter as tk
# Assuming main.py is executed from the project root (e.g., /app),
# and /app is in sys.path.
# Then, 'data_analyzer' is a top-level package.
from data_analyzer.src.ui import DataAnalyzerApp

def main():
    """
    Main function to initialize and run the Data Analyzer application.
    """
    # Check for Tkinter availability, especially for headless environments or minimal installs.
    try:
        # Create a temporary, hidden root window to initialize Tkinter.
        # This helps confirm if Tkinter is usable before committing to the main app window.
        temp_root = tk.Tk()
        temp_root.withdraw() # Make it invisible
        temp_root.destroy()  # Clean up immediately
    except tk.TclError as e:
        # This error often means no display is available or Tkinter components are missing.
        print("Error: Tkinter is not available or not configured correctly.")
        print(f"Details: {e}")
        print("The application cannot start without a graphical environment.")
        return # Exit if GUI cannot be initialized

    # Create the main application window and run the app
    root = tk.Tk()
    app = DataAnalyzerApp(root) # DataAnalyzerApp is responsible for its own layout.
    root.mainloop()

if __name__ == "__main__":
    # This is the main entry point when the script is executed.
    main()
