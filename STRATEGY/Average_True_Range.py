def calculate_atr(candles, period=14):
    high_prices = [candle['high'] for candle in candles]
    low_prices = [candle['low'] for candle in candles]
    close_prices = [candle['close'] for candle in candles]

    tr = [max(high_prices[i] - low_prices[i], abs(high_prices[i] - close_prices[i-1]), abs(low_prices[i] - close_prices[i-1])) for i in range(1, len(candles))]
    atr = np.mean(tr[-period:])
    return atr
