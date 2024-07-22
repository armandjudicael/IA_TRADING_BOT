from iqoptionapi.stable_api import IQ_Option
import pandas as pd
import time
import ta
import logging

# Constants
EMAIL = "voahanginirina.noelline@gmail.com"
PASSWORD = "Noel!ne1969"
SYMBOL = 'EURUSD-OTC'  # Using the OTC suffix
INTERVAL = 60
AMOUNT = 1
DURATION = 1
SLEEP_INTERVAL = 60  # Time in seconds to wait between checks
RECONNECT_ATTEMPTS = 3
HISTORICAL_PERIOD = 500  # Number of periods for historical data analysis

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')


def connect_to_iq_option(email, password):
    """
    Connect to IQ Option and handle reconnection attempts.
    """
    api = IQ_Option(email, password)
    for attempt in range(RECONNECT_ATTEMPTS):
        if api.connect():
            logging.info("Connected to IQ Option")
            return api
        else:
            logging.warning(f"Connection attempt {attempt + 1} failed. Retrying...")
            time.sleep(5)
    logging.error("Failed to connect to IQ Option after multiple attempts.")
    raise Exception("Failed to connect to IQ Option")


def get_realtime_data(api, symbol, interval=60):
    """
    Retrieve real-time data from IQ Option.
    """
    try:
        data = api.get_candles(symbol, interval, HISTORICAL_PERIOD, time.time())
        return data
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        return []


def analyze_market_conditions(df):
    """
    Analyze market conditions to adjust indicator parameters dynamically.
    """
    # Example logic: Adjust rolling window based on market volatility
    volatility = df['close'].rolling(window=10).std().mean()

    if volatility < df['close'].mean() * 0.01:
        rolling_window = 10  # Lower window for low volatility
    elif volatility < df['close'].mean() * 0.02:
        rolling_window = 20  # Medium window for medium volatility
    else:
        rolling_window = 30  # Higher window for high volatility

    return rolling_window


def calculate_indicators(df, rolling_window):
    """
    Calculate technical indicators for the given DataFrame with dynamic parameters.
    """
    df['Resistance'] = df['close'].rolling(window=rolling_window).max()
    df['Support'] = df['close'].rolling(window=rolling_window).min()
    df['SMA'] = ta.trend.sma_indicator(df['close'], window=rolling_window)
    df['RSI'] = ta.momentum.rsi(df['close'], window=14)
    df['Bollinger_High'] = ta.volatility.bollinger_hband(df['close'], window=rolling_window)
    df['Bollinger_Low'] = ta.volatility.bollinger_lband(df['close'], window=rolling_window)
    df['False_Breakout'] = (df['close'] > df['Resistance'].shift(1)) & (df['close'] < df['Resistance'])
    df['Confirmed'] = (df['close'] > df['SMA']) & (df['RSI'] > 70) & (df['close'] < df['Bollinger_High'])
    return df


def place_trade(api, symbol, amount, direction, duration):
    """
    Place a trade on IQ Option and check the result.
    """
    result, trade_id = api.buy_digital_spot(symbol,amount, direction, duration)
    if result:
        logging.info(f"Trade placed: {direction} {amount} {symbol}")
        check_trade_result(api, trade_id)
    else:
        logging.error("Failed to place trade")


def check_trade_result(api, trade_id):
    """
    Check the result of a trade.
    """
    while True:
        trade_result = api.check_win_v3(trade_id)
        if trade_result is not None:
            logging.info(f"Trade result: {'Win' if trade_result > 0 else 'Loss'} (Profit: {trade_result})")
            break
        time.sleep(1)


def main():
    """
    Main function to execute the trading strategy.
    """
    api = connect_to_iq_option(EMAIL, PASSWORD)

    try:
        while True:
            data = get_realtime_data(api, SYMBOL, INTERVAL)
            if data:
                df = pd.DataFrame(data)
                df['time'] = pd.to_datetime(df['from'], unit='s')
                df.set_index('time', inplace=True)

                rolling_window = analyze_market_conditions(df)
                df = calculate_indicators(df, rolling_window)

                if df[df['False_Breakout'] & df['Confirmed']].shape[0] > 0:
                    direction = 'put'  # Assume we detected a false breakout and want to sell
                    place_trade(api, SYMBOL, AMOUNT, direction, DURATION)
                else:
                    logging.info("No confirmed false breakout detected")

            time.sleep(SLEEP_INTERVAL)
    except KeyboardInterrupt:
        logging.info("Trading stopped by user")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        api.close()


if __name__ == "__main__":
    main()
