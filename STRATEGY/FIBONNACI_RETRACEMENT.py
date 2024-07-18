import ta
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Fetch historical data
ticker = 'AAPL'
start_date = '2023-01-01'
end_date = '2024-01-01'

data = yf.download(ticker, start=start_date, end=end_date)

# Identify the high and low
high_price = data['High'].max()
low_price = data['Low'].min()

# Calculate Fibonacci retracement levels
diff = high_price - low_price
levels = {
    '0%': high_price,
    '23.6%': high_price - 0.236 * diff,
    '38.2%': high_price - 0.382 * diff,
    '50%': high_price - 0.5 * diff,
    '61.8%': high_price - 0.618 * diff,
    '100%': low_price
}

# Plot the closing price
plt.figure(figsize=(12, 6))
plt.plot(data['Close'], label='Close Price', color='blue')

# Plot Fibonacci retracement levels
for level, price in levels.items():
    plt.axhline(y=price, linestyle='--', alpha=0.7, label=f'Fib {level} ({price:.2f})')

# Add titles and labels
plt.title(f'Fibonacci Retracement Levels for {ticker}')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.grid(True)

# Show the plot
plt.show()
