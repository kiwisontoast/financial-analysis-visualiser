import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime, timezone
from sklearn.metrics import r2_score
import tkinter as tk
from tkinter import ttk
import sv_ttk

# Mathematical functions representing different complexity classes
def constant(x, coef):
    """Return constant function: f(x) = coef"""
    return coef * np.ones_like(x)

def logarithmic(x, coef):
    """Return logarithmic function: f(x) = coef * log2(x + 1)"""
    return coef * np.log2(x + 1)

def linear(x, coef):
    """Return linear function: f(x) = coef * x"""
    return coef * x

def loglinear(x, coef):
    """Return log-linear function: f(x) = coef * x * log2(x + 1)"""
    return coef * x * np.log2(x + 1)

def quadratic(x, coef):
    """Return quadratic function: f(x) = coef * x^2"""
    return coef * (x**2)

def cubic(x, coef):
    """Return cubic function: f(x) = coef * x^3"""
    return coef * (x**3)

def factorial(x, coef):
    """Return factorial function with smoothing"""
    def fact(n):
        if n <= 1:
            return 1
        return n * fact(n-1)
    
    x_scaled = x / len(x) * 12
    return coef * np.array([fact(min(float(i), 12)) for i in x_scaled])

def exponential(x, coef):
    """Return exponential function with reduced growth rate"""
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
    """Create and return date selection dropdowns"""
    frame = ttk.Frame(parent)
    frame.grid(row=row, column=1, sticky=tk.W, pady=5)

    ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=tk.W)

    day = ttk.Combobox(frame, width=3, values=[str(i).zfill(2) for i in range(1, 32)])
    month = ttk.Combobox(frame, width=3, values=[str(i).zfill(2) for i in range(1, 13)])
    year = ttk.Combobox(frame, width=5, values=[str(i) for i in range(2000, 2025)])

    day.grid(row=0, column=0, padx=2)
    month.grid(row=0, column=1, padx=2)
    year.grid(row=0, column=2, padx=2)

    return day, month, year

def get_date_string(day_var, month_var, year_var):
    """Convert date components to string format"""
    return f"{year_var.get()}-{month_var.get()}-{day_var.get()}"

def toggle_comparison_mode():
    """Toggle between single and comparison mode"""
    if comparison_var.get():
        ticker2_label.grid()
        ticker2_entry.grid()
        comparison_result_label.grid()
    else:
        ticker2_label.grid_remove()
        ticker2_entry.grid_remove()
        comparison_result_label.grid_remove()

def get_stock_data(ticker, start_date, end_date):
    """Fetch and return stock data for given ticker and date range"""
    try:
        company = yf.Ticker(ticker)
        data = company.history(start=start_date, end=end_date)["Close"]
        return data
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

def calculate_r_squared(data, func, coefficient):
    """Calculate R-squared value for given data and function"""
    days = np.arange(len(data))
    comparison_values = func(days, coefficient)
    
    if func != constant:
        baseline_values = func(days, 1.0)
        scale_factor = data.mean() / baseline_values.mean()
        comparison_values = comparison_values * scale_factor
    
    return r2_score(data.values, comparison_values), comparison_values

def update_graph():
    """Update the graph based on current settings"""
    ticker1 = ticker1_entry.get().upper()
    selected_function = function_var.get()
    try:
        coefficient = float(coefficient_entry.get())
    except ValueError:
        coefficient = 1.0
        coefficient_entry.delete(0, tk.END)
        coefficient_entry.insert(0, "1.0")

    start_date = get_date_string(start_day, start_month, start_year)
    end_date = get_date_string(end_day, end_month, end_year)

    ax.clear()
    
    # Get data for first stock
    data1 = get_stock_data(ticker1, start_date, end_date)
    if data1 is None:
        r_squared_label.config(text="Error: Invalid input or data unavailable")
        return

    func = FUNCTIONS[selected_function]
    r2_1, comparison_values1 = calculate_r_squared(data1, func, coefficient)

    # Plot first stock
    ax.plot(data1.index, data1, label=ticker1, color='cyan')
    ax.plot(data1.index, comparison_values1, 
            label=f"{coefficient}×{selected_function}", 
            linestyle='--', 
            color='orange')

    if comparison_var.get():
        ticker2 = ticker2_entry.get().upper()
        data2 = get_stock_data(ticker2, start_date, end_date)
        if data2 is not None:
            r2_2, comparison_values2 = calculate_r_squared(data2, func, coefficient)
            
            # Plot second stock
            ax.plot(data2.index, data2, label=ticker2, color='magenta')
            ax.plot(data2.index, comparison_values2, 
                    label=f"{coefficient}×{selected_function}", 
                    linestyle='--', 
                    color='red')

            # Compare R-squared values
            comparison_result = f"{ticker1} R² ({r2_1:.4f}) vs {ticker2} R² ({r2_2:.4f})\n"
            comparison_result += f"Better fit: {ticker1 if r2_1 > r2_2 else ticker2}"
            comparison_result_label.config(text=comparison_result)
    
    ax.set_title(f"Stock Prices vs {coefficient}×{selected_function}", color='white')
    ax.set_xlabel("Date", color='white')
    ax.set_ylabel("Price (USD)", color='white')
    ax.legend(facecolor='gray', edgecolor='white', labelcolor='white')
    ax.tick_params(colors='white')
    ax.grid(True, color='gray')

    canvas.draw()
    r_squared_label.config(text=f"R-squared: {r2_1:.4f}")

def on_closing():
    """Clean up and close the application"""
    plt.close('all')
    root.quit()
    root.destroy()


# Create main window
root = tk.Tk()
root.title("Stock Price vs Big O Complexity Comparator")
root.protocol("WM_DELETE_WINDOW", on_closing)

# Create main frame
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Create comparison mode toggle
comparison_var = tk.BooleanVar(value=False)
comparison_check = ttk.Checkbutton(frame, text="Compare Two Stocks", 
                                 variable=comparison_var, 
                                 command=toggle_comparison_mode)
comparison_check.grid(row=0, column=0, sticky=tk.W, pady=5)

# First ticker input
ticker1_label = ttk.Label(frame, text="Enter first stock ticker:")
ticker1_label.grid(row=1, column=0, sticky=tk.W, pady=5)
ticker1_entry = ttk.Entry(frame, width=10)
ticker1_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
ticker1_entry.insert(0, "GOOGL")

# Second ticker input (initially hidden)
ticker2_label = ttk.Label(frame, text="Enter second stock ticker:")
ticker2_label.grid(row=1, column=2, sticky=tk.W, pady=5)
ticker2_entry = ttk.Entry(frame, width=10)
ticker2_entry.grid(row=1, column=3, sticky=(tk.W, tk.E), pady=5)
ticker2_entry.insert(0, "AAPL")
# Initially hide second ticker inputs
ticker2_label.grid_remove()
ticker2_entry.grid_remove()

# Comparison result label
comparison_result_label = ttk.Label(frame, text="")
comparison_result_label.grid(row=1, column=4, columnspan=2, sticky=tk.W, pady=5)
comparison_result_label.grid_remove()

# Function selection
function_label = ttk.Label(frame, text="Select complexity:")
function_label.grid(row=2, column=0, sticky=tk.W, pady=5)
function_var = tk.StringVar(value="O(n²) - Quadratic")
function_dropdown = ttk.Combobox(frame, textvariable=function_var, 
                               values=list(FUNCTIONS.keys()), 
                               width=20, state="readonly")
function_dropdown.grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=5)

# Coefficient input
coefficient_label = ttk.Label(frame, text="Coefficient:")
coefficient_label.grid(row=2, column=3, sticky=tk.W, pady=5, padx=(10, 0))
coefficient_entry = ttk.Entry(frame, width=5)
coefficient_entry.grid(row=2, column=4, sticky=tk.W, pady=5)
coefficient_entry.insert(0, "1.0")

# Date selection dropdowns
start_day, start_month, start_year = create_date_dropdowns(frame, 3, "Start Date:")
end_day, end_month, end_year = create_date_dropdowns(frame, 4, "End Date:")

# Update button
update_button = ttk.Button(frame, text="Update Graph", command=update_graph)
update_button.grid(row=5, column=1, sticky=tk.E, pady=5)

# R-squared label
r_squared_label = ttk.Label(frame, text="R-squared: ")
r_squared_label.grid(row=5, column=2, columnspan=3, sticky=tk.W, pady=5)

# Set up the plot
fig, ax = plt.subplots(figsize=(25, 12.5))
fig.patch.set_facecolor('#333333')
ax.set_facecolor('#333333')

canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(row=6, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

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

# Start application
root.mainloop()
