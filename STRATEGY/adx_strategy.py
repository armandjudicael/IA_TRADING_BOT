import pandas as pd
from ta.trend import ADXIndicator

def calculate_adx(candles, window=14):
    """
    Calculate ADX (Average Directional Index) for given historical price data.

    Parameters:
    - candles: List of historical price data (dictionaries with 'high', 'low', and 'close' keys).
    - window: Window size for the ADX calculation (default is 14).

    Returns:
    - adx: ADX values.
    """
    df = pd.DataFrame(candles)
    adx_indicator = ADXIndicator(high=df['high'], low=df['low'], close=df['close'], window=window)
    df['adx'] = adx_indicator.adx()

    return df['adx'].iloc[-1]

def adx_strategy(candles, window=14):
    """
    Determine the strength of the trend based on ADX strategy.

    Parameters:
    - candles: List of historical price data (dictionaries with 'high', 'low', and 'close' keys).
    - window: Window size for the ADX calculation (default is 14).

    Returns:
    - adx: ADX value indicating the strength of the trend.
    """
    return calculate_adx(candles, window)
