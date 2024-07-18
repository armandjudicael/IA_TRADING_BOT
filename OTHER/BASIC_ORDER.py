from iqoptionapi.stable_api import IQ_Option
import time

# Connect to the IQ Option API
email = "judicael.ratombotiana@gmail.com"
password = "Aj!30071999@jv"
api = IQ_Option(email, password)
status, reason = api.connect()

if not status:
    print('Failed to connect:', reason)
    exit()

# Verify the connection status
print('Connection Status:', status)
print('Reason:', reason)

# If 2FA is enabled
if reason == "2FA":
    code_sms = input("Enter the received code: ")
    status, reason = api.connect_2fa(code_sms)
    print('Second Attempt Status:', status)
    print('Reason:', reason)

# Basic Strategy: Moving Average Crossover (Example)
def moving_average(data, period):
    return sum(data[-period:]) / period

# Get current data for Euro/JPY
asset = "EURJPY"
duration = 1  # 1 minute
size = 60  # 60 seconds
prices = api.get_candles(asset, duration, size, time.time())

# Extract closing prices
close_prices = [price['close'] for price in prices]

# Calculate short-term and long-term moving averages
short_period = 5
long_period = 20
short_ma = moving_average(close_prices, short_period)
long_ma = moving_average(close_prices, long_period)

# Determine the trade direction
if short_ma > long_ma:
    direction = "call"  # Buy
else:
    direction = "put"  # Sell

# Set the trade amount
amount = 10  # Example amount

# Execute the trade
status, trade_id = api.buy(amount, asset, direction, duration)

if status:
    print(f"Trade executed successfully: {direction} on {asset}")
else:
    print(f"Trade execution failed: {reason}")

# Monitor the trade result
time.sleep(duration * 60)  # Wait for the trade to expire
status, trade_result = api.check_win_v3(trade_id)

if status:
    print(f"Trade result: {'Win' if trade_result > 0 else 'Loss'}")
    print(f"Profit/Loss: {trade_result}")
else:
    print("Failed to retrieve trade result")

# Close the API connection
api.close()
