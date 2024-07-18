def calculate_cci(candles, period=20):
    typical_prices = [(candle['high'] + candle['low'] + candle['close']) / 3 for candle in candles]
    sma = np.mean(typical_prices[-period:])
    mean_deviation = np.mean([abs(tp - sma) for tp in typical_prices[-period:]])
    cci = (typical_prices[-1] - sma) / (0.015 * mean_deviation)
    return cci
