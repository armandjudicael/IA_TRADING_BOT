from iqoptionapi.stable_api import IQ_Option
import time

# Connect to the IQ Option API
email = "voahanginirina.noelline@gmail.com"
password = "Noel!ne1969"
api = IQ_Option(email, password)
status, reason = api.connect()

if not status:
    print('Failed to connect:', reason)
    exit()

# If 2FA is enabled
if reason == "2FA":
    code_sms = input("Enter the received code: ")
    status, reason = api.connect_2fa(code_sms)

# Define the function to calculate SMA
def simple_moving_average(data, period):
    return sum(data[-period:]) / period

# Trade parameters
asset = "EURJPY"
duration = 1  # 1 minute candlesticks
amount = 1  # Trade amount

# Real-time trading loop
while True:
    try:
        # Fetch historical data (candlesticks)
        end_time = time.time()  # Current time
        size = 200  # Number of candlesticks needed for SMA calculation
        candles = api.get_candles(asset, duration, size, end_time)

        if len(candles) < 200:
            print("Not enough data. Waiting for more candlesticks...")
            time.sleep(10)
            continue

        # Extract closing prices for SMA calculation
        close_prices = [candle['close'] for candle in candles]

        # Calculate SMAs
        short_sma_period = 50
        long_sma_period = 200
        short_sma = simple_moving_average(close_prices, short_sma_period)
        long_sma = simple_moving_average(close_prices, long_sma_period)

        # Determine trade direction based on SMA crossover
        if short_sma > long_sma:
            direction = "call"  # Buy signal (short-term SMA crosses above long-term SMA)
        else:
            direction = "put"  # Sell signal (short-term SMA crosses below long-term SMA)

        # Execute the trade
        status, trade_id = api.buy_digital_spot(amount, asset, direction, duration)

        if status:
            print(f"Trade executed successfully: {direction} on {asset}, Amount : {amount} , Trade ID : {trade_id}")
        else:
            print(f"Trade execution failed: {reason}")

        # Wait for the trade to expire
        time.sleep(duration * 60)

        # Check the trade result
        trade_result = api.check_win_v3(trade_id)

        if trade_result is not None:
            print(f"Trade result: {'Win' if trade_result > 0 else 'Loss'}")
            print(f"Profit/Loss: {trade_result}")
            if trade_result <= 0:
                amount *= 3
            else:
                amount = 1
        else:
            print("Failed to retrieve trade result")

        # Wait before the next iteration
        time.sleep(10)  # Wait 10 seconds before fetching new data and trading again

    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(10)  # Wait before retrying in case of an error

