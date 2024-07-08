from iqoptionapi.stable_api import IQ_Option
import time

# Connect to the IQ Option API
email = "judicael.ratombotiana@gmail.com"
password = "Aj!30071999@react"
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

# Get candlestick data for Euro/JPY
asset = "EURJPY"
duration = 1  # Time frame in minutes
size = 60  # Number of candlesticks
end_time = time.time()  # End time is current time

# Fetch the candlestick data
candles = api.get_candles(asset, duration, size, end_time)

# Print the retrieved candlestick data
for candle in candles:
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(candle['from']))}")
    print(f"Open: {candle['open']}, High: {candle['max']}, Low: {candle['min']}, Close: {candle['close']}, Volume: {candle['volume']}")
    print("-" * 50)


