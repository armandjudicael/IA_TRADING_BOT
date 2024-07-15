import logging
import random

from iqoptionapi.stable_api import IQ_Option
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Connect to the IQ Option API
email = "judicael.ratombotiana@gmail.com"
password = "Aj!30071999@jv"
api = IQ_Option(email, password)
status, reason = api.connect()

if not status:
    print('Failed to connect:', reason)
    exit()

# If 2FA is enabled
if reason == "2FA":
    code_sms = input("Enter the received code: ")
    status, reason = api.connect_2fa(code_sms)


# Define the moving average function
def moving_average(data, period):
    return sum(data[-period:]) / period


# Trade parameters
asset = "EURUSD"
duration = 1  # Trade duration in minutes
amount = 2  # Trade amount
short_period = 5  # Short-term moving average period
long_period = 20  # Long-term moving average period

# Real-time trading loop
while True:
    try:
        # Fetch the latest candlestick data
        end_time = time.time()  # Current time
        size = max(short_period,long_period)  # Number of candlesticks needed
        candles = api.get_candles(asset, duration, size, end_time)

        # Extract closing prices
        close_prices = [candle['close'] for candle in candles]

        # Calculate moving averages
        short_ma = moving_average(close_prices, short_period)
        long_ma = moving_average(close_prices, long_period)

        # Determine trade direction
        if short_ma > long_ma:
            direction = "call"  # Buy
        else:
            direction = "put"  # Sell

        # Execute the trade
        status, trade_id = api.buy(amount, asset, direction, duration)

        if status:
            print(f"Trade executed successfully: {direction} on {asset}")
        else:
            print(f"Trade execution failed: {reason}")

        # Wait for the trade to expire
        time.sleep(duration * 60)

        # Check the trade result
        trade_result = api.check_win_v3(trade_id)

        if trade_result is not None:
            print(f"Trade result: {'Win' if trade_result > 0 else 'Loss'}")
            print(f"Profit/Loss: {trade_result}")
            print("Balance:", api.get_balance())
            if trade_result <= 0:
                amount *= 2
                amount += random.randint(1, 5)
            else:
                amount = 2 + random.randint(1, 10)
        else:
            print("Failed to retrieve trade result")

    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(10)  # Wait before retrying in case of an error
