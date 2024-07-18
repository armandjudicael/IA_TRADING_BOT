import pandas as pd
from ta.momentum import RSIIndicator

def calculate_rsi(close_prices, window=14):
    """
    Calculate Relative Strength Index (RSI) for given historical price data.

    Parameters:
    - close_prices: List or array of closing prices.
    - window: Window size for calculating RSI (default is 14).

    Returns:
    - rsi_value: The RSI value for the most recent closing price.
    """
    df = pd.DataFrame({'Close': close_prices})
    indicator_rsi = RSIIndicator(close=df['Close'], window=window)
    df['rsi'] = indicator_rsi.rsi()
    return df['rsi'].iloc[-1]

def rsi_strategy(candles, rsi_overbought=70, rsi_oversold=30, rsi_window=14):
    """
    Determine trade direction based on RSI strategy.

    Parameters:
    - candles: List of historical price data (dictionaries with 'close' key).
    - rsi_overbought: RSI value above which the asset is considered overbought (default is 70).
    - rsi_oversold: RSI value below which the asset is considered oversold (default is 30).
    - rsi_window: Window size for calculating RSI (default is 14).

    Returns:
    - direction: Trade direction ('put', 'call', or 'none').
    """
    close_prices = [candle['close'] for candle in candles]
    rsi_value = calculate_rsi(close_prices, window=rsi_window)

    if rsi_value > rsi_overbought:
        return 'put'  # Asset is overbought, potential for reversal down
    elif rsi_value < rsi_oversold:
        return 'call'  # Asset is oversold, potential for reversal up
    else:
        return 'none'  # No clear signal
