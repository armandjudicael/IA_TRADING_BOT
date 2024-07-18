def stochastic_oscillator(candles, period=14):
    close_prices = [candle['close'] for candle in candles]
    high_prices = [candle['high'] for candle in candles]
    low_prices = [candle['low'] for candle in candles]

    lowest_low = min(low_prices[-period:])
    highest_high = max(high_prices[-period:])
    k = 100 * ((close_prices[-1] - lowest_low) / (highest_high - lowest_low))
    d = np.mean([k])  # Calculate the %D line
    return k, d
