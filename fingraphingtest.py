import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime, timezone
from sklearn.metrics import r2_score
import tkinter as tk
from tkinter import ttk
import sv_ttk

def on_closing():
    plt.close('all')  # Close all matplotlib figures
    root.quit()       # Stop the mainloop
    root.destroy()    # Destroy the window[1][2]

def update_graph():
    ticker = ticker_entry.get().upper()

    try:
        company = yf.Ticker(ticker)
        start_date = "2019-04-23"
        end_date = "2022-01-23"

        data = company.history(start=start_date, end=end_date)["Close"]

        ax.clear()  # Clear the axes instead of creating a new figure

        # Line color to contrast with dark background
        ax.plot(data.index, data, label=ticker, color='cyan')

        # Calculate n^2 function
        start_datetime = datetime.strptime(
            start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        days = [(date.tz_convert(timezone.utc) -
                 start_datetime).days for date in data.index]
        # Adjusted the scaling factor
        n_squared = [day ** 2 / 10000 + 50 for day in days]

        # Plot n^2 function
        ax.plot(data.index, n_squared, label='n^2',
                linestyle='--', color='orange')

        # Calculate R-squared
        r2 = r2_score(data.values, n_squared)

        # Set title, labels, and legend with dark theme colors
        ax.set_title(
            f"Stock Prices and n^2 Function (R-squared: {r2:.4f})", color='white')
        ax.set_xlabel("Date", color='white')
        ax.set_ylabel("Price (USD) / n^2 value", color='white')
        ax.legend(facecolor='gray', edgecolor='white', labelcolor='white')

        # Set tick label colors
        ax.tick_params(colors='white')

        # Set grid color for better visibility in dark mode
        ax.grid(True, color='gray')

        # Redraw the canvas to reflect changes
        canvas.draw()
        r_squared_label.config(text=f"R-squared: {r2:.4f}")
    except Exception as e:
        print(f"Error: {e}")
        r_squared_label.config(
            text="Error: Invalid ticker or data unavailable")
    pass



def on_closing():
    plt.close('all')  # Close all matplotlib figures
    root.quit()       # Stop the mainloop
    root.destroy()    # Destroy the window[1]

# Create the main window
root = tk.Tk()
root.title("Stock Price vs n^2 Function")

# Set the window close handler - remove the [1][8] indexing
root.protocol("WM_DELETE_WINDOW", on_closing)


# Create and pack the input field and button
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

ticker_label = ttk.Label(frame, text="Enter stock ticker:")
ticker_label.grid(row=0, column=0, sticky=tk.W, pady=5)

ticker_entry = ttk.Entry(frame, width=10)
ticker_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
ticker_entry.insert(0, "GOOGL")

update_button = ttk.Button(frame, text="Update Graph", command=update_graph)
update_button.grid(row=0, column=2, sticky=tk.E, pady=5)

r_squared_label = ttk.Label(frame, text="R-squared: ")
r_squared_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=5)

# Create a figure and canvas to display the plot
# Define fig, ax globally to avoid creating new figures
fig, ax = plt.subplots(figsize=(25, 12.5))

# Apply a dark background to the figure and axes
fig.patch.set_facecolor('#333333')  # Set figure background to match dark theme
ax.set_facecolor('#333333')  # Set axes background

canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Update the graph initially
update_graph()

# Set SV TTK theme to dark
sv_ttk.set_theme("dark")

# Start the Tkinter event loop
root.mainloop()
