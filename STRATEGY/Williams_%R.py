def williams_r(candles, period=14):
    close_prices = [candle['close'] for candle in candles]
    high_prices = [candle['high'] for candle in candles]
    low_prices = [candle['low'] for candle in candles]

    highest_high = max(high_prices[-period:])
    lowest_low = min(low_prices[-period:])
    wr = -100 * ((highest_high - close_prices[-1]) / (highest_high - lowest_low))
    return wr
