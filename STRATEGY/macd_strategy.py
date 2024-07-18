import pandas as pd
from ta.trend import MACD

def calculate_macd(close_prices, fast_period=12, slow_period=26, signal_period=9):
    """
    Calculate MACD for given historical price data.

    Parameters:
    - close_prices: List or array of closing prices.
    - fast_period: Window size for the fast EMA (default is 12).
    - slow_period: Window size for the slow EMA (default is 26).
    - signal_period: Window size for the signal line (default is 9).

    Returns:
    - macd_line: MACD line values.
    - signal_line: Signal line values.
    - macd_histogram: MACD histogram values.
    """
    df = pd.DataFrame({'Close': close_prices})
    macd = MACD(close=df['Close'], window_slow=slow_period, window_fast=fast_period, window_sign=signal_period)
    df['macd'] = macd.macd()
    df['signal'] = macd.macd_signal()
    df['histogram'] = macd.macd_diff()

    return df['macd'].iloc[-1], df['signal'].iloc[-1], df['histogram'].iloc[-1]

def macd_strategy(candles, fast_period=12, slow_period=26, signal_period=9):
    """
    Determine trade direction based on MACD strategy.

    Parameters:
    - candles: List of historical price data (dictionaries with 'close' key).
    - fast_period: Window size for the fast EMA (default is 12).
    - slow_period: Window size for the slow EMA (default is 26).
    - signal_period: Window size for the signal line (default is 9).

    Returns:
    - macd_line: MACD line values.
    - signal_line: Signal line values.
    - macd_histogram: MACD histogram values.
    """
    close_prices = [candle['close'] for candle in candles]
    return calculate_macd(close_prices, fast_period, slow_period, signal_period)
