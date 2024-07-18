from iqoptionapi.stable_api import IQ_Option
import time

# Your IQ Option credentials
email = "armandjudicaelratombotiana@gmail.com"
password = "Aj!30071999@angular"

# Initialize IQ Option API
api = IQ_Option(email, password)
status, reason = api.connect()

if not status:
    print(f"Failed to connect: {reason}")
    exit()

print(f"Connection Status: {status}\nReason: {reason}")


# Function to handle reconnect and get candles
def get_candles_retry(asset, duration, size, retry_attempts=3):
    for _ in range(retry_attempts):
        try:
            candles = api.get_candles(asset, duration, size, time.time())
            return candles
        except Exception as e:
            print(f"Error fetching candles: {e}")
            print("Attempting to reconnect...")
            api.connect()
            time.sleep(5)  # Wait before retrying
    return None


# Function to get historical closing prices
def get_prices(asset, duration, size):
    candles = get_candles_retry(asset, duration, size)

    if candles is not None:
        return [candle['close'] for candle in candles]
    else:
        return None


# Function to calculate moving average
def moving_average(data, period):
    if len(data) < period:
        raise ValueError(f"Not enough data to calculate {period}-period moving average.")
    return sum(data[-period:]) / period


# Function to execute a trade based on trend direction
def execute_trade(asset, amount, direction, duration, retry_attempts=3):
    for _ in range(retry_attempts):
        try:
            status, trade_id = api.buy_digital_spot(asset, amount, direction, duration)
            if status:
                print(f"Trade executed successfully: {direction} on {asset}")
                return trade_id
            else:
                print(f"Trade execution failed with status: {status}. Retrying...")
                time.sleep(5)  # Wait before retrying
        except Exception as e:
            print(f"Error executing trade: {e}")
            print("Attempting to reconnect...")
            api.connect()
            time.sleep(5)  # Wait before retrying
    return None


# Function to monitor trade result and manage money/risk
def monitor_trade(trade_id, amount, initial_balance, risk_percentage):
    # Wait for the trade to expire
    time.sleep(duration * 60)

    trade_result = api.check_win_v3(trade_id)

    if trade_result is not None:
        result = 'Win' if trade_result > 0 else 'Loss'
        print(f"Trade result: {result}")
        print(f"Profit/Loss: {trade_result}")

        # Get current balance after trade
        balance = api.get_balance()
        print(f"Current Balance: {balance}")

        # Adjust trade size based on risk management rules
        if trade_result <= 0:
            # Calculate maximum amount to risk based on initial balance
            max_amount_to_risk = initial_balance * (risk_percentage / 100.0)

            # Adjust trade amount for next trade
            if balance > (max_amount_to_risk * 4):
                amount = max_amount_to_risk
            else:
                amount *= 2
        else:
            amount = 10  # Reset amount to initial value

        print(f"Updated amount for next trade: {amount}")

        return amount
    else:
        print("Failed to retrieve trade result")
        return amount


# Function to list available binary option assets
def list_binary_option_assets():
    binary_option_assets = api.get_binary_option_detail()
    if binary_option_assets:
        return binary_option_assets
    else:
        print("No binary option assets available.")
        return None


# Set initial trading parameters
initial_asset = "EURUSD"  # Initial asset to trade
duration = 1  # 1 minute timeframe for short-term trading
amount = 10  # Example trade amount
initial_balance = api.get_balance()  # Get initial account balance
risk_percentage = 2  # Risk 2% of account balance per trade

# Execute trades in an infinite loop (example)
while True:
    try:
        # Get recent closing prices of the current asset
        close_prices = get_prices(initial_asset, duration, 20)  # Example long-term MA period
        if close_prices is None:
            continue

        # Calculate short-term and long-term moving averages
        short_ma = moving_average(close_prices, 5)  # Example short-term MA period
        long_ma = moving_average(close_prices, 20)  # Example long-term MA period

        # Determine trade direction based on moving average crossover
        if short_ma > long_ma:
            direction = "call"  # Buy call option if short-term MA crosses above long-term MA
        else:
            direction = "put"  # Buy put option if short-term MA crosses below long-term MA

        # Execute trade based on direction and initial asset
        trade_id = execute_trade(initial_asset, amount, direction, duration)
        print(trade_id)

        # Monitor trade result and adjust trade size
        if trade_id:
            amount = monitor_trade(trade_id, amount, initial_balance, risk_percentage)
        else:
            print("Attempting to trade with another asset...")
            # List available assets
            binary_option_assets = list_binary_option_assets()

            if binary_option_assets:
                # Choose another asset from the list
                for asset in binary_option_assets:
                    if asset != initial_asset:
                        initial_asset = asset
                        print(f"Switching to trade with {initial_asset}")
                        break

        # Wait before the next trade
        time.sleep(60)  # Wait 1 minute before the next trade

    except KeyboardInterrupt:
        print("\nStopping trading loop.")
        break
    except Exception as e:
        print(f"Error in trading loop: {e}")
        continue
