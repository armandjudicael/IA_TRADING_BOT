import asyncio
import pandas as pd
import ta
import logging
from iqoptionapi.stable_api import IQ_Option
import pandas_ta as ta

# Constants
EMAIL = "voahanginirina.noelline@gmail.com"
PASSWORD = "Noel!ne1969"
SYMBOL = 'NZDUSD-OTC'  # Using the OTC suffix
INTERVAL = 60
AMOUNT = 1
DURATION = 1
SLEEP_INTERVAL = 60  # Time in seconds to wait between checks
RECONNECT_ATTEMPTS = 3
HISTORICAL_PERIOD = 100  # Number of periods for historical data analysis

# Global variable to store the trade direction
trade_direction = None
trade_lock = asyncio.Lock()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')


async def connect_to_iq_option(email, password):
    """
    Connect to IQ Option and handle reconnection attempts.
    """
    api = IQ_Option(email, password)
    for attempt in range(RECONNECT_ATTEMPTS):
        if api.connect():
            logging.info("Connected to IQ Option")
            # Start the candle stream
            api.start_candles_stream(SYMBOL, INTERVAL, 100)
            return api
        else:
            logging.warning(f"Connection attempt {attempt + 1} failed. Retrying...")
            await asyncio.sleep(5)
    logging.error("Failed to connect to IQ Option after multiple attempts.")
    raise Exception("Failed to connect to IQ Option")


async def get_realtime_data(api, symbol, interval=60):
    """
    Retrieve real-time data from IQ Option.

    Parameters:
    api : object
        IQ Option API instance.
    symbol : str
        Trading symbol, e.g., 'EURUSD'.
    interval : int
        Time interval in seconds for the candles. Default is 60 seconds.

    Returns:
    dict
        Real-time candle data.
    """
    logging.info(f"Starting candle stream for {symbol} with interval {interval} seconds.")

    try:
        # Fetch real-time candle data
        data = api.get_realtime_candles(symbol, interval)

        # Log the number of data points retrieved
        if data:
            logging.info(f"Retrieved {len(data)} data points for {symbol}.")

            # Log details of the first few data points (adjust the range as needed)
            for i, (timestamp, candle) in enumerate(data.items()):
                logging.info(f"Data point {i + 1}: {candle}")
                if i >= 4:  # Log only the first 5 data points
                    break
        else:
            logging.info(f"No data retrieved for {symbol}.")

        return data
    except Exception as e:
        logging.error(f"Error fetching data for {symbol}: {e}")
        return {}


def analyze_market_conditions(df):
    """
    Analyze market conditions to adjust indicator parameters dynamically.

    Parameters:
    df : DataFrame
        DataFrame containing historical market data with columns 'high', 'low', and 'close'.

    Returns:
    rolling_window : int
        Rolling window size for indicators based on market conditions.
    trend : str
        Identified market trend ("uptrend" or "downtrend").
    additional_info : dict
        Dictionary containing values of calculated indicators.
    """
    # Ensure the DataFrame has enough data
    if len(df) < 14:
        raise ValueError("Insufficient data to analyze market conditions")

    # Calculate ATR (Average True Range)
    df['ATR'] = ta.atr(high=df['high'], low=df['low'], close=df['close'], length=14)
    avg_atr = df['ATR'].mean()

    # Calculate MACD (Moving Average Convergence Divergence)
    df['MACD'], df['MACD_signal'], df['MACD_hist'] = ta.macd(df['close'])
    macd_diff = df['MACD'].iloc[-1] - df['MACD_signal'].iloc[-1]

    # Calculate RSI (Relative Strength Index)
    df['RSI'] = ta.rsi(df['close'], length=14)

    # Calculate Bollinger Bands
    df['BB_upper'], df['BB_middle'], df['BB_lower'] = ta.bbands(df['close'], length=20, std=2)

    # Calculate SMA (Simple Moving Average)
    df['SMA'] = ta.sma(df['close'], length=20)

    # Determine the rolling window size based on average ATR
    close_mean = df['close'].mean()
    if avg_atr < close_mean * 0.01:
        rolling_window = 10  # Lower window for low volatility
    elif avg_atr < close_mean * 0.02:
        rolling_window = 20  # Medium window for medium volatility
    else:
        rolling_window = 30  # Higher window for high volatility

    # Determine the market trend based on MACD
    trend = "uptrend" if macd_diff > 0 else "downtrend"

    # Collect additional indicator information
    additional_info = {
        'avg_atr': avg_atr,
        'macd_diff': macd_diff,
        'rsi': df['RSI'].iloc[-1],
        'bb_upper': df['BB_upper'].iloc[-1],
        'bb_middle': df['BB_middle'].iloc[-1],
        'bb_lower': df['BB_lower'].iloc[-1],
        'sma': df['SMA'].iloc[-1]
    }

    return rolling_window, trend, additional_info


def calculate_indicators(df, rolling_window, trend):
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

    # Confirmed false breakout with trend consideration
    if trend == "uptrend":
        df['Confirmed'] = (df['close'] > df['SMA']) & (df['RSI'] > 70) & (df['close'] < df['Bollinger_High'])
    else:
        df['Confirmed'] = (df['close'] < df['SMA']) & (df['RSI'] < 30) & (df['close'] > df['Bollinger_Low'])

    return df


async def direction_calculation_task(api):
    """
    Async task for calculating trade direction.
    """
    global trade_direction
    try:
        while True:
            data = await get_realtime_data(api, SYMBOL, INTERVAL)
            if data:
                # Log the raw data to inspect its structure
                logging.info(f"Raw data: {data}")

                # Convert the retrieved data into a DataFrame
                try:
                    df = pd.DataFrame.from_dict(data, orient='index')
                    logging.info(f"DataFrame columns: {df.columns.tolist()}")
                    # Adjust DataFrame columns based on available fields
                    if 'from' in df.columns:
                        df['time'] = pd.to_datetime(df['from'], unit='s')
                    if 'open' in df.columns:
                        df['open'] = df['open'].astype(float)
                    if 'close' in df.columns:
                        df['close'] = df['close'].astype(float)
                    if 'min' in df.columns:
                        df['low'] = df['min'].astype(float)
                    if 'max' in df.columns:
                        df['high'] = df['max'].astype(float)

                    df.set_index('time', inplace=True)

                    # Log DataFrame structure
                    logging.info(f"DataFrame structure: {df.head()}")
                except Exception as e:
                    logging.error(f"Error converting data to DataFrame: {e}")
                    continue

                rolling_window, trend = analyze_market_conditions(df)
                df = calculate_indicators(df, rolling_window, trend)

                async with trade_lock:
                    if df[df['False_Breakout'] & df['Confirmed']].shape[0] > 0:
                        trade_direction = 'put' if trend == "downtrend" else 'call'
                    else:
                        trade_direction = None

            await asyncio.sleep(SLEEP_INTERVAL)
    except Exception as e:
        logging.error(f"Error in direction calculation task: {e}")


async def place_trade(api, symbol, amount, direction, duration):
    """
    Place a trade on IQ Option and check the result.
    """
    result, trade_id = api.buy_digital_spot(symbol, amount, direction, duration)
    if result:
        logging.info(f"Trade placed: {direction} {amount} {symbol}")
        await check_trade_result(api, trade_id)
    else:
        logging.error("Failed to place trade")


async def check_trade_result(api, trade_id):
    """
    Check the result of a trade.
    """
    while True:
        trade_result = api.check_win_v3(trade_id)
        if trade_result is not None:
            logging.info(f"Trade result: {'Win' if trade_result > 0 else 'Loss'} (Profit: {trade_result})")
            break
        await asyncio.sleep(1)


async def trade_execution_task(api):
    """
    Async task for executing trades based on calculated direction.
    """
    global trade_direction
    try:
        while True:
            async with trade_lock:
                if trade_direction:
                    await place_trade(api, SYMBOL, AMOUNT, trade_direction, DURATION)
                    trade_direction = None  # Reset after placing the trade

            await asyncio.sleep(SLEEP_INTERVAL)
    except Exception as e:
        logging.error(f"Error in trade execution task: {e}")


async def main():
    """
    Main function to start the trading strategy.
    """
    api = await connect_to_iq_option(EMAIL, PASSWORD)

    # Start direction calculation task
    direction_task = asyncio.create_task(direction_calculation_task(api))

    # Start trade execution task
    trade_task = asyncio.create_task(trade_execution_task(api))

    # Wait for both tasks to complete
    await asyncio.gather(direction_task, trade_task)


if __name__ == "__main__":
    asyncio.run(main())
