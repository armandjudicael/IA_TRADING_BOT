import asyncio
import aiohttp
import pandas as pd
import time
import ta
import logging
from iqoptionapi.stable_api import IQ_Option
from aiohttp import ClientSession

# Constants
EMAIL = "voahanginirina.noelline@gmail.com"
PASSWORD = "Noel!ne1969"
SYMBOL = 'EURUSD-OTC'  # Using the OTC suffix
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
            return api
        else:
            logging.warning(f"Connection attempt {attempt + 1} failed. Retrying...")
            await asyncio.sleep(5)
    logging.error("Failed to connect to IQ Option after multiple attempts.")
    raise Exception("Failed to connect to IQ Option")


async def get_realtime_data(api, symbol, interval=60):
    """
    Retrieve real-time data from IQ Option.
    """
    try:
        data = api.full_realtime_get_candle(symbol,HISTORICAL_PERIOD,500)
        return data
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        return []


def analyze_market_conditions(df):
    """
    Analyze market conditions to adjust indicator parameters dynamically.
    """
    # Volatility analysis using ATR
    df['ATR'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=14)
    avg_atr = df['ATR'].mean()

    # Trend analysis using MACD
    df['MACD'] = ta.trend.macd(df['close'])
    df['MACD_signal'] = ta.trend.macd_signal(df['close'])
    macd_diff = (df['MACD'] - df['MACD_signal']).iloc[-1]

    if avg_atr < df['close'].mean() * 0.01:
        rolling_window = 10  # Lower window for low volatility
    elif avg_atr < df['close'].mean() * 0.02:
        rolling_window = 20  # Medium window for medium volatility
    else:
        rolling_window = 30  # Higher window for high volatility

    if macd_diff > 0:
        trend = "uptrend"
    else:
        trend = "downtrend"

    return rolling_window, trend


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
                df = pd.DataFrame(data)
                df['time'] = pd.to_datetime(df['from'], unit='s')
                df.set_index('time', inplace=True)

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
    result, trade_id = api.buy(amount, symbol, direction, duration)
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
