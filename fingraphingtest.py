import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime, timezone
from sklearn.metrics import r2_score
import tkinter as tk
from tkinter import ttk
import sv_ttk

def n_squared(x):
    return x**2 / 10000 + 50

def n_cubed(x):
    return x**3 / 1000000 + 50

def exponential(x):
    return np.exp(x/100) + 40

def logarithmic(x):
    return np.log(x + 1) * 20 + 50

# Dictionary of available functions
FUNCTIONS = {
    "n²": n_squared,
    "n³": n_cubed,
    "exponential": exponential,
    "logarithmic": logarithmic
}

def create_date_dropdowns(parent, row, label_text):
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
    return f"{year_var.get()}-{month_var.get()}-{day_var.get()}"

def update_graph():
    ticker = ticker_entry.get().upper()
    selected_function = function_var.get()
    
    try:
        company = yf.Ticker(ticker)
        start_date = get_date_string(start_day, start_month, start_year)
        end_date = get_date_string(end_day, end_month, end_year)
        
        data = company.history(start=start_date, end=end_date)["Close"]
        
        ax.clear()
        
        ax.plot(data.index, data, label=ticker, color='cyan')
        
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        days = [(date.tz_convert(timezone.utc) - start_datetime).days for date in data.index]
        
        # Use the selected function from the dictionary
        comparison_values = [FUNCTIONS[selected_function](day) for day in days]
        
        ax.plot(data.index, comparison_values, label=selected_function, linestyle='--', color='orange')
        
        r2 = r2_score(data.values, comparison_values)
        
        ax.set_title(f"Stock Prices and {selected_function} Function (R-squared: {r2:.4f})", color='white')
        ax.set_xlabel("Date", color='white')
        ax.set_ylabel("Price (USD) / Function value", color='white')
        ax.legend(facecolor='gray', edgecolor='white', labelcolor='white')
        
        ax.tick_params(colors='white')
        ax.grid(True, color='gray')
        
        canvas.draw()
        r_squared_label.config(text=f"R-squared: {r2:.4f}")
    except Exception as e:
        print(f"Error: {e}")
        r_squared_label.config(text="Error: Invalid ticker or data unavailable")

def on_closing():
    plt.close('all')
    root.quit()
    root.destroy()

# Create the main window
root = tk.Tk()
root.title("Stock Price vs Custom Function")
root.protocol("WM_DELETE_WINDOW", on_closing)

# Create and pack the input fields
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Ticker input
ticker_label = ttk.Label(frame, text="Enter stock ticker:")
ticker_label.grid(row=0, column=0, sticky=tk.W, pady=5)

ticker_entry = ttk.Entry(frame, width=10)
ticker_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
ticker_entry.insert(0, "GOOGL")

# Function selection dropdown
function_label = ttk.Label(frame, text="Select function:")
function_label.grid(row=0, column=2, sticky=tk.W, pady=5, padx=(10, 0))

function_var = tk.StringVar(value="n²")
function_dropdown = ttk.Combobox(frame, textvariable=function_var, values=list(FUNCTIONS.keys()), width=10, state="readonly")
function_dropdown.grid(row=0, column=3, sticky=tk.W, pady=5)

# Date selection dropdowns
start_day, start_month, start_year = create_date_dropdowns(frame, 1, "Start Date:")
end_day, end_month, end_year = create_date_dropdowns(frame, 2, "End Date:")

# Update button
update_button = ttk.Button(frame, text="Update Graph", command=update_graph)
update_button.grid(row=3, column=1, sticky=tk.E, pady=5)

# R-squared label
r_squared_label = ttk.Label(frame, text="R-squared: ")
r_squared_label.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=5)

# Create the plot
fig, ax = plt.subplots(figsize=(25, 12.5))
fig.patch.set_facecolor('#333333')
ax.set_facecolor('#333333')

canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Set default dates
start_year.set("2019")
start_month.set("04")
start_day.set("23")
end_year.set("2022")
end_month.set("01")
end_day.set("23")

# Update the graph initially
update_graph()

# Set SV TTK theme to dark
sv_ttk.set_theme("dark")

# Start the Tkinter event loop
root.mainloop()
