import pandas as pd
from ta.volatility import BollingerBands

def calculate_bollinger_bands(close_prices, window=20, std_dev=2):
    """
    Calculate Bollinger Bands for given historical price data.

    Parameters:
    - close_prices: List or array of closing prices.
    - window: Window size for calculating the moving average.
    - std_dev: Number of standard deviations for the bands.

    Returns:
    - bb_bbm: Bollinger Bands middle line (moving average).
    - bb_bbh: Bollinger Bands upper line.
    - bb_bbl: Bollinger Bands lower line.
    """
    df = pd.DataFrame({'Close': close_prices})
    indicator_bb = BollingerBands(close=df['Close'], window=window, window_dev=std_dev)
    df['bb_bbm'] = indicator_bb.bollinger_mavg()
    df['bb_bbh'] = indicator_bb.bollinger_hband()
    df['bb_bbl'] = indicator_bb.bollinger_lband()

    return df['bb_bbm'].iloc[-1], df['bb_bbh'].iloc[-1], df['bb_bbl'].iloc[-1]

def determine_trade_direction(close_prices, short_period, long_period):
    """
    Determine trade direction based on Bollinger Bands.

    Parameters:
    - close_prices: List or array of closing prices.

    Returns:
    - direction: Trade direction ('put', 'call', or 'none').
    """
    bb_middle, bb_upper, bb_lower = calculate_bollinger_bands(close_prices, window=short_period, std_dev=long_period)

    if close_prices[-1] > bb_upper:
        return 'put'  # Price is above upper band, potential for reversal down
    elif close_prices[-1] < bb_lower:
        return 'call'   # Price is below lower band, potential for reversal up
    else:
        return 'none'  # Price is within bands, no clear signal
