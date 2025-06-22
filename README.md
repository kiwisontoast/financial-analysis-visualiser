# Financial-Analysis-Visualiser
Financial Analysis Visualiser is a visualization tool that compares stock price patterns with Big O complexity patterns. It helps users to understand how different stock price movements correlate with various mathematical growth patterns by providing real-time data visualization and comparison.
Downloadable as exe @ https://finatk.devshroff.com/

## Key Features
- Compares up to three different stocks simultaneously 
- Uses real-time stock data using yfinance
- Compares stock patterns with standard Big O Notations:
  - O(1) - Constant
  - O(log n) - Logarithmic
  - O(n) - Linear
  - O(n log n) - Log-linear
  - O(n²) - Quadratic
  - O(n³) - Cubic
  - O(2ⁿ) - Exponential
  - O(n!) - Factorial
- Statistical analysis using R-squared calculation
- User-friendly interface 
  - Real-time graph updates
  - Adjustable coefficient
  - Customizable date ranges
  - Dark/Light mode button

## Dependencies
- This project requires:
  ~ yfinance
  ~ matplotlib
  ~ numpy
  ~ scikit-learn
  ~ tkinter
  ~ sv_ttk

## Usage
Use the GUI to:
   - Enter stock tickers (e.g.,GOOGL, META, MSFT)
   - Select comparison mode (1-3 stocks)
   - Choose a function you wish the stocks to be compared to
   - Adjust the coefficient value 
   - Set your preferred date range
   - Toggle the light/dark mode 
   - Update visualization

## Warnings
   **Operating Systems**
   This is optimized for Windows. While it may run on other operating systems, 
   some visual elements and GUI components might behave differently.
   **Default Values**
   - Default stocks are set to "GOOGL", "AAPL", and "MSFT"
   - Default date range is set from April 23, 2019 to January 23, 2022
   - Default complexity function is set to "O(n²) - Quadratic"
   - Default coefficient is set to 1.0
   - Default theme is set to "Dark Mode"
   **Data Retrieval**
   - Some stocks might not have data for the selected date range
   - Invalid stock tickers will result in data fetch errors
   - Stock data availability depends on yfinance

## Authors
- Dev Shroff & Krishnika Anandan





