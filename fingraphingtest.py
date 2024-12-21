# Import required libraries
import yfinance as yf  # For fetching stock data
import matplotlib.pyplot as plt  # For creating plots
# For embedding plots in tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np  # For numerical operations
from datetime import datetime, timezone  # For date handling
from sklearn.metrics import r2_score  # For calculating R-squared values
import tkinter as tk  # For creating the GUI
from tkinter import ttk  # For themed tkinter widgets
import sv_ttk  # For modern tkinter styling

# Define mathematical functions representing different complexity classes


def constant(x, coef):
    """Return a constant function O(1)"""
    return coef * np.ones_like(x)


def logarithmic(x, coef):
    """Return a logarithmic function O(log n)"""
    return coef * np.log2(x + 1)


def linear(x, coef):
    """Return a linear function O(n)"""
    return coef * x


def loglinear(x, coef):
    """Return a log-linear function O(n log n)"""
    return coef * x * np.log2(x + 1)


def quadratic(x, coef):
    """Return a quadratic function O(n²)"""
    return coef * (x**2)


def cubic(x, coef):
    """Return a cubic function O(n³)"""
    return coef * (x**3)


def factorial(x, coef):
    """Return a factorial function O(n!)"""
    def fact(n):
        if n <= 1:
            return 1
        return n * fact(n-1)
    # Scale x to prevent overflow
    x_scaled = x / len(x) * 12
    return coef * np.array([fact(min(float(i), 12)) for i in x_scaled])


def exponential(x, coef):
    """Return an exponential function O(2ⁿ)"""
    return coef * (2 ** (x / 20))


# Dictionary mapping function names to their implementations
FUNCTIONS = {
    "O(1) - Constant": constant,
    "O(log n) - Logarithmic": logarithmic,
    "O(n) - Linear": linear,
    "O(n log n) - Log-linear": loglinear,
    "O(n²) - Quadratic": quadratic,
    "O(n³) - Cubic": cubic,
    "O(2ⁿ) - Exponential": exponential,
    "O(n!) - Factorial": factorial
}


def create_date_dropdowns(parent, row, label_text):
    """Create a set of dropdowns for date selection (day, month, year)"""
    frame = ttk.Frame(parent)
    frame.grid(row=row, column=1, sticky=tk.W, pady=5)
    ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=tk.W)

    # Create dropdowns for day, month, and year
    day = ttk.Combobox(frame, width=3, values=[
                       str(i).zfill(2) for i in range(1, 32)])
    month = ttk.Combobox(frame, width=3, values=[
                         str(i).zfill(2) for i in range(1, 13)])
    year = ttk.Combobox(frame, width=5, values=[
                        str(i) for i in range(2000, 2025)])

    # Position the dropdowns
    day.grid(row=0, column=0, padx=2)
    month.grid(row=0, column=1, padx=2)
    year.grid(row=0, column=2, padx=2)
    return day, month, year


def get_date_string(day_var, month_var, year_var):
    """Convert separate day, month, year values into a date string"""
    return f"{year_var.get()}-{month_var.get()}-{day_var.get()}"


def toggle_comparison_mode():
    """Handle visibility of comparison-related UI elements based on checkbox states"""
    # Enforce logical dependencies between checkboxes
    if compare_3_var.get() == 1:
        compare_2_var.set(1)  # Enable 2-stock comparison if 3-stock is enabled

    # Handle visibility of second stock inputs
    if compare_2_var.get() == 1:
        ticker2_label.grid()
        ticker2_entry.grid()
    else:
        ticker2_label.grid_remove()
        ticker2_entry.grid_remove()
        # Disable 3-stock comparison if 2-stock is disabled
        compare_3_var.set(0)

    # Handle visibility of third stock inputs
    if compare_3_var.get() == 1:
        ticker3_label.grid()
        ticker3_entry.grid()
        comparison_result_label.grid()
    else:
        ticker3_label.grid_remove()
        ticker3_entry.grid_remove()

    # Hide comparison results if no comparisons are active
    if compare_2_var.get() == 0:
        comparison_result_label.grid_remove()


def toggle_theme():
    """Switch between light and dark themes"""
    current_theme = sv_ttk.get_theme()
    if current_theme == "dark":
        # Switch to light theme
        sv_ttk.set_theme("light")
        theme_toggle_button.config(text="Switch to Dark Mode")
        # Update plot colors for light theme
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')
        ax.tick_params(colors='black')
        ax.set_title(ax.get_title(), color='black')
        ax.set_xlabel(ax.get_xlabel(), color='black')
        ax.set_ylabel(ax.get_ylabel(), color='black')
        ax.legend(facecolor='white', edgecolor='black', labelcolor='black')
    else:
        # Switch to dark theme
        sv_ttk.set_theme("dark")
        theme_toggle_button.config(text="Switch to Light Mode")
        # Update plot colors for dark theme
        fig.patch.set_facecolor('#333333')
        ax.set_facecolor('#333333')
        ax.tick_params(colors='white')
        ax.set_title(ax.get_title(), color='white')
        ax.set_xlabel(ax.get_xlabel(), color='white')
        ax.set_ylabel(ax.get_ylabel(), color='white')
        ax.legend(facecolor='gray', edgecolor='white', labelcolor='white')
    canvas.draw()


def get_stock_data(ticker, start_date, end_date):
    """Fetch stock data from Yahoo Finance"""
    try:
        company = yf.Ticker(ticker)
        data = company.history(start=start_date, end=end_date)["Close"]
        return data
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None


def calculate_r_squared(data, func, coefficient):
    """Calculate R-squared value and comparison values for a given function"""
    days = np.arange(len(data))
    comparison_values = func(days, coefficient)

    # Scale the function to match the data's magnitude (except for constant function)
    if func != constant:
        baseline_values = func(days, 1.0)
        scale_factor = data.mean() / baseline_values.mean()
        comparison_values = comparison_values * scale_factor

    return r2_score(data.values, comparison_values), comparison_values


def update_graph():
    """Update the graph with current settings and data"""
    # Get input values
    ticker1 = ticker1_entry.get().upper()
    selected_function = function_var.get()

    # Parse coefficient
    try:
        coefficient = float(coefficient_entry.get())
    except ValueError:
        coefficient = 1.0
        coefficient_entry.delete(0, tk.END)
        coefficient_entry.insert(0, "1.0")

    # Get date range
    start_date = get_date_string(start_day, start_month, start_year)
    end_date = get_date_string(end_day, end_month, end_year)

    # Clear previous plot
    ax.clear()

    # Get and plot first stock data
    data1 = get_stock_data(ticker1, start_date, end_date)
    if data1 is None:
        r_squared_label.config(text="Error: Invalid input or data unavailable")
        return

    # Calculate and plot function comparison
    func = FUNCTIONS[selected_function]
    r2_1, comparison_values1 = calculate_r_squared(data1, func, coefficient)
    ax.plot(data1.index, data1, label=ticker1, color='cyan')
    ax.plot(data1.index, comparison_values1,
            label=f"{coefficient}×{selected_function}",
            linestyle='--', color='orange')

    # Handle second stock comparison if enabled
    if compare_2_var.get() == 1:
        ticker2 = ticker2_entry.get().upper()
        data2 = get_stock_data(ticker2, start_date, end_date)
        if data2 is not None:
            r2_2, comparison_values2 = calculate_r_squared(
                data2, func, coefficient)
            ax.plot(data2.index, data2, label=ticker2, color='magenta')
            ax.plot(data2.index, comparison_values2,
                    label=f"{coefficient}×{selected_function}",
                    linestyle='--', color='red')

            # Update comparison results
            comparison_result = (f"{ticker1} R² ({r2_1:.4f}) vs {ticker2} R² ({r2_2:.4f})\n"
                                 f"Best fit: {max([(ticker1, r2_1), (ticker2, r2_2)], key=lambda x: x[1])[0]}")
            comparison_result_label.config(text=comparison_result)
            comparison_result_label.grid()

    # Handle third stock comparison if enabled
    if compare_3_var.get() == 1:
        ticker3 = ticker3_entry.get().upper()
        data3 = get_stock_data(ticker3, start_date, end_date)
        if data3 is not None:
            r2_3, comparison_values3 = calculate_r_squared(
                data3, func, coefficient)
            ax.plot(data3.index, data3, label=ticker3, color='yellow')
            ax.plot(data3.index, comparison_values3,
                    label=f"{coefficient}×{selected_function}",
                    linestyle='--', color='green')

            # Update comparison results for three stocks
            comparison_result = (f"{ticker1} R² ({r2_1:.4f}) vs {ticker2} R² ({r2_2:.4f}) vs {ticker3} R² ({r2_3:.4f})\n"
                                 f"Best fit: {max([(ticker1, r2_1), (ticker2, r2_2), (ticker3, r2_3)], key=lambda x: x[1])[0]}")
            comparison_result_label.config(text=comparison_result)
    else:
        if compare_2_var.get() == 0:
            comparison_result_label.config(text="")
            comparison_result_label.grid_remove()

    # Update plot styling
    ax.set_title(f"Stock Prices vs {coefficient}×{
                 selected_function}", color='white')
    ax.set_xlabel("Date", color='white')
    ax.set_ylabel("Price (USD)", color='white')
    ax.legend(facecolor='gray', edgecolor='white', labelcolor='white')
    ax.tick_params(colors='white')
    ax.grid(True, color='gray')
    canvas.draw()
    r_squared_label.config(text=f"R-squared: {r2_1:.4f}")


def on_closing():
    """Handle application closure"""
    plt.close('all')
    root.quit()
    root.destroy()


# Create and configure main window
root = tk.Tk()
root.title("Stock Price vs Big O Complexity Comparator")
root.protocol("WM_DELETE_WINDOW", on_closing)

# Set window size to 95% of screen height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_height = int(screen_height * 0.95)
window_width = screen_width
root.geometry(f"{window_width}x{window_height}+0+0")

# Create and configure main frame
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
frame.rowconfigure(11, weight=1)
frame.columnconfigure(0, weight=1)

# Create UI elements
theme_toggle_button = ttk.Button(
    frame, text="Switch to Light Mode", command=toggle_theme)
theme_toggle_button.grid(row=0, column=0, sticky=tk.W, pady=5)

# Create comparison checkboxes
compare_2_var = tk.IntVar(value=0)
compare_3_var = tk.IntVar(value=0)
compare_2_check = ttk.Checkbutton(frame, text="Compare 2 Stocks",
                                  variable=compare_2_var, command=toggle_comparison_mode)
compare_3_check = ttk.Checkbutton(frame, text="Compare 3 Stocks",
                                  variable=compare_3_var, command=toggle_comparison_mode)
compare_2_check.grid(row=0, column=1, sticky=tk.W, pady=5)
compare_3_check.grid(row=0, column=2, sticky=tk.W, pady=5)

# Create stock ticker inputs
ticker1_label = ttk.Label(frame, text="Enter first stock ticker:")
ticker1_label.grid(row=1, column=0, sticky=tk.W, pady=5)
ticker1_entry = ttk.Entry(frame, width=10)
ticker1_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
ticker1_entry.insert(0, "GOOGL")

ticker2_label = ttk.Label(frame, text="Enter second stock ticker:")
ticker2_label.grid(row=2, column=0, sticky=tk.W, pady=5)
ticker2_entry = ttk.Entry(frame, width=10)
ticker2_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
ticker2_entry.insert(0, "AAPL")

ticker3_label = ttk.Label(frame, text="Enter third stock ticker:")
ticker3_label.grid(row=3, column=0, sticky=tk.W, pady=5)
ticker3_entry = ttk.Entry(frame, width=10)
ticker3_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
ticker3_entry.insert(0, "MSFT")

# Create comparison result label
comparison_result_label = ttk.Label(frame, text="")
comparison_result_label.grid(
    row=9, column=0, columnspan=6, sticky=tk.W, pady=5)
comparison_result_label.grid_remove()

# Function selection
function_label = ttk.Label(frame, text="Select complexity:")
function_label.grid(row=4, column=0, sticky=tk.W, pady=5)
function_var = tk.StringVar(value="O(n²) - Quadratic")
function_dropdown = ttk.Combobox(frame, textvariable=function_var, values=list(
    FUNCTIONS.keys()), width=20, state="readonly")
function_dropdown.grid(row=4, column=1, columnspan=2, sticky=tk.W, pady=5)

# Coefficient input
coefficient_label = ttk.Label(frame, text="Coefficient:")
coefficient_label.grid(row=5, column=0, sticky=tk.W, pady=5)
coefficient_entry = ttk.Entry(frame, width=5)
coefficient_entry.grid(row=5, column=1, sticky=tk.W, pady=5)
coefficient_entry.insert(0, "1.0")

# Date selection dropdowns
start_day, start_month, start_year = create_date_dropdowns(
    frame, 6, "Start Date:")
end_day, end_month, end_year = create_date_dropdowns(frame, 7, "End Date:")

# Update button
update_button = ttk.Button(frame, text="Update Graph", command=update_graph)
update_button.grid(row=8, column=1, sticky=tk.E, pady=5)

# R-squared label
r_squared_label = ttk.Label(frame, text="R-squared: ")
r_squared_label.grid(row=8, column=2, columnspan=3, sticky=tk.W, pady=5)

# Set up the plot
fig, ax = plt.subplots(figsize=(25, 12.5))
fig.patch.set_facecolor('#333333')
ax.set_facecolor('#333333')
canvas = FigureCanvasTkAgg(fig, master=frame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(row=11, column=0, columnspan=7,
                   sticky=(tk.W, tk.E, tk.N, tk.S))

# Set default dates
start_year.set("2019")
start_month.set("04")
start_day.set("23")
end_year.set("2022")
end_month.set("01")
end_day.set("23")

# Set theme
sv_ttk.set_theme("dark")

# Initial graph update
update_graph()

# Ensure the UI reflects the initial comparison mode
toggle_comparison_mode()

# Start application
root.mainloop()
