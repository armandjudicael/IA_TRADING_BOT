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

# Function to fetch trading history
def get_trading_history(api, instrument_type, start_time, end_time, limit=1000, offset=0):
    status, positions = api.get_position_history_v2(instrument_type, limit, offset, start_time, end_time)
    if status:
        return positions
    else:
        print("Failed to retrieve positions")
        return None

# Define the time range for fetching the trading history
end_time = int(time.time())
start_time = end_time - (7 * 24 * 60 * 60)  # One week ago
instrument_type = "turbo-option"

# Get the trading history
trading_history = get_trading_history(api, instrument_type, start_time, end_time)

# Print the trading history
if trading_history and 'positions' in trading_history:
    for position in trading_history['positions']:
        print(f"Trade ID: {position['id']}")
        print(f"Asset: {position['raw_event']['active_id']}")
        print(f"Amount: {position['invest']}")
        print(f"Open Time: {position['open_time']}")
        print(f"Close Time: {position['close_time']}")
        print(f"Profit/Loss: {position['close_profit']}")
        print("-----")
else:
    print("No trading history found")

