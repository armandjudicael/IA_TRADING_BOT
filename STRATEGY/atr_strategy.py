import pandas as pd
from ta.volatility import AverageTrueRange

def calculate_atr(candles, window=14):
    """
    Calculate ATR (Average True Range) for given historical price data.

    Parameters:
    - candles: List of historical price data (dictionaries with 'high', 'low', and 'close' keys).
    - window: Window size for the ATR calculation (default is 14).

    Returns:
    - atr: ATR value.
    """
    df = pd.DataFrame(candles)
    atr_indicator = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=window)
    df['atr'] = atr_indicator.average_true_range()

    return df['atr'].iloc[-1]

def atr_strategy(candles, window=14):
    """
    Determine the market volatility based on ATR strategy.

    Parameters:
    - candles: List of historical price data (dictionaries with 'high', 'low', and 'close' keys).
    - window: Window size for the ATR calculation (default is 14).

    Returns:
    - atr: ATR value indicating market volatility.
    """
    return calculate_atr(candles, window)
