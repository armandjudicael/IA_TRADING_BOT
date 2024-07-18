import numpy as np

def calculate_bollinger_bands(data, period=20, num_std_dev=2):
    sma = np.mean(data[-period:])
    rolling_std = np.std(data[-period:])
    upper_band = sma + (rolling_std * num_std_dev)
    lower_band = sma - (rolling_std * num_std_dev)
    return upper_band, lower_band

# Bollinger Bands Strategy
def bollinger_bands_strategy(candles):
    close_prices = [candle['close'] for candle in candles]
    upper_band, lower_band = calculate_bollinger_bands(close_prices, period=20, num_std_dev=2)

    if close_prices[-1] > upper_band:
        direction = 'put'  # Sell signal
    elif close_prices[-1] < lower_band:
        direction = 'call'  # Buy signal
    else:
        direction = 'none'  # No trade

    return direction
