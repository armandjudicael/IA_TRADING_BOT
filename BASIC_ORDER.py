from time import time, sleep, gmtime
from iqoptionapi.stable_api import IQ_Option


def is_otc():
    current_time = gmtime()
    current_hour = current_time.tm_hour
    current_day = current_time.tm_wday
    # Forex market closes at 22:00 GMT on Friday and opens at 22:00 GMT on Sunday
    if current_day == 5 and current_hour >= 22:  # Friday 22:00 GMT
        return True
    elif current_day == 6:  # Saturday
        return True
    elif current_day == 0 and current_hour < 22:  # Sunday before 22:00 GMT
        return True
    else:
        return False

email = "judicael.ratombotiana@gmail.com"
password = "Aj!30071999@jv"
# Initialize and connect to IQ Option
api = IQ_Option(email, password)
status, reason = api.connect()

if not status:
    print(f"Failed to connect: {reason}")
    exit()

print(f"Connection Status: {status}\nReason: {reason}")

# Handle 2FA if enabled
if reason == "2FA":
    code_sms = input("Enter the received code: ")
    status, reason = api.connect_2fa(code_sms)
    print(f"Second Attempt Status: {status}\nReason: {reason}")
    if not status:
        print(f"Failed to connect with 2FA: {reason}")
        exit()


# Function to calculate moving average
def moving_average(data, period):
    if len(data) < period:
        raise ValueError(f"Not enough data to calculate {period}-period moving average.")
    return sum(data[-period:]) / period


# Function to fetch closing prices for an asset
def get_closing_prices(asset, duration, size):
    prices = api.get_candles(asset, duration, size, time())
    return [price['close'] for price in prices]


# Function to execute a trade based on moving average crossover strategy
def execute_trade(asset, short_period, long_period, amount, duration):
    try:
        close_prices = get_closing_prices(asset, duration, long_period)
    except Exception as e:
        print(f"Error fetching closing prices: {e}")
        return None

    try:
        short_ma = moving_average(close_prices, short_period)
        long_ma = moving_average(close_prices, long_period)
    except ValueError as e:
        print(f"Error calculating moving averages: {e}")
        return None

    direction = "call" if short_ma > long_ma else "put"

    status, trade_id = api.buy_digital_spot(asset, amount, direction, duration)

    if status:
        print(f"Trade executed successfully: {direction} on {asset}")
        return trade_id
    else:
        print(f"Trade execution failed: {reason}")
        return None


# Function to monitor trade result
def monitor_trade(trade_id, duration):
    sleep(duration * 60)  # Wait for the trade to expire
    status, trade_result = api.check_win_v3(trade_id)

    if status:
        result = 'Win' if trade_result > 0 else 'Loss'
        print(f"Trade result: {result}")
        print(f"Profit/Loss: {trade_result}")
    else:
        print("Failed to retrieve trade result")


# Set trading parameters
asset = "EURUSD-OTC" if is_otc() else "EURUSD"
duration = 1  # 1 minute
short_period = 5
long_period = 20
amount = 10  # Example amount

# Execute and monitor trade
trade_id = execute_trade(asset, short_period, long_period, amount, duration)
if trade_id:
    monitor_trade(trade_id, duration)

# Close API connection
api.close()
