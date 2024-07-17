import datetime
from iqoptionapi.stable_api import IQ_Option
import time
import openpyxl
from openpyxl import Workbook
import numpy as np
import ta


# Create a new workbook and select the active sheet
workbook = Workbook()
sheet = workbook.active
sheet.title = 'Trade Monitoring'

# Headers for the table
headers = ['Trade ID', 'Timestamp', 'Strategy', 'Status', 'Amount', 'Trade Result', 'Balance']
sheet.append(headers)

# Connect to the IQ Option API
email = "judicael.ratombotiana@gmail.com"
password = "Aj!30071999@jv"
api = IQ_Option(email, password)
status, reason = api.connect()

if not status:
    print('Failed to connect:', reason)
    exit()

# Handle 2FA if enabled
if reason == "2FA":
    code_sms = input("Enter the received code: ")
    status, reason = api.connect_2fa(code_sms)

# Define the moving average function (for trend direction)
def moving_average(data, period):
    return np.mean(data[-period:])

# Define Fibonacci retracement levels function
def calculate_fibonacci_levels(high, low):
    fib_levels = ta.FibonacciRetracement(high, low)
    return fib_levels

# Trade parameters
asset = "EURUSD"
duration = 1  # Trade duration in minutes
global_amount = 1
amount = global_amount  # Initial trade amount
martingale = 2

# Real-time trading loop
while True:
    try:
        # Fetch the latest candlestick data
        end_time = time.time()  # Current time
        size = 20  # Number of candlesticks needed
        candles = api.get_candles(asset, duration, size, end_time)
        close_prices = np.array([candle['close'] for candle in candles])

        # Calculate moving averages
        short_ma = moving_average(close_prices, 5)
        long_ma = moving_average(close_prices, 20)

        # Determine trade direction based on moving averages
        if short_ma > long_ma:
            trend_direction = "uptrend"
        else:
            trend_direction = "downtrend"

        # Calculate Fibonacci retracement levels based on recent high and low
        high = np.max(close_prices)
        low = np.min(close_prices)
        fib_levels = calculate_fibonacci_levels(high, low)

        # Determine trade direction based on Fibonacci levels and trend
        if trend_direction == "uptrend" and close_prices[-1] >= fib_levels[0]:
            direction = "call"  # Buy option (upward trend continuation)
        elif trend_direction == "downtrend" and close_prices[-1] <= fib_levels[0]:
            direction = "put"  # Sell option (downward trend continuation)
        else:
            direction = None  # No trade

        # Execute the trade
        if direction:
            status, trade_id = api.buy(amount, asset, direction, duration)

            if status:
                print(f"Trade executed successfully: {direction} on {asset}")
            else:
                print(f"Trade execution failed: {reason}")

            # Simulated data for other columns
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            strategy = 'Moving Average + Fibonacci Retracement'
            status = 'Closed'

            # Wait for the trade to expire
            time.sleep(duration * 60)

            # Check the trade result
            trade_result = api.check_win_v3(trade_id)

            if trade_result is not None:
                print(f"Trade result: {'Win' if trade_result > 0 else 'Loss'}")
                print(f"Profit/Loss: {trade_result}")
                print("Balance:", api.get_balance())
                if trade_result <= 0:
                    amount *= martingale  # Apply Martingale strategy on loss
                else:
                    amount = global_amount  # Reset amount on win
            else:
                print("Failed to retrieve trade result")

            # Write data to Excel
            sheet.append([trade_id, timestamp, strategy, status, amount, {'Win' if trade_result > 0 else 'Loss'}, api.get_balance()])

            # Save workbook periodically to avoid data loss
            if len(sheet['A']) % 10 == 0:  # Save every 10 trades
                workbook.save('trade_monitoring.xlsx')

        # Wait before the next iteration
        time.sleep(10)  # Wait 10 seconds before fetching new data and trading again

    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(10)  # Wait before retrying in case of an error

# Save workbook to Excel file
excel_file = 'trade_monitoring.xlsx'
workbook.save(filename=excel_file)
