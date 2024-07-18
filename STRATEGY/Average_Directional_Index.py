def calculate_adx(candles, period=14):
    high_prices = [candle['high'] for candle in candles]
    low_prices = [candle['low'] for candle in candles]
    close_prices = [candle['close'] for candle in candles]

    # Calculate DM+ and DM-
    dm_plus = [
        high_prices[i] - high_prices[i - 1] if high_prices[i] - high_prices[i - 1] > low_prices[i - 1] - low_prices[
            i] and high_prices[i] - high_prices[i - 1] > 0 else 0 for i in range(1, len(candles))]
    dm_minus = [
        low_prices[i - 1] - low_prices[i] if low_prices[i - 1] - low_prices[i] > high_prices[i] - high_prices[i - 1] and
                                             low_prices[i - 1] - low_prices[i] > 0 else 0 for i in
        range(1, len(candles))]

    # Smooth DM+ and DM-
    smoothed_dm_plus = np.mean(dm_plus[-period:])
    smoothed_dm_minus = np.mean(dm_minus[-period:])

    tr = [max(high_prices[i] - low_prices[i], abs(high_prices[i] - close_prices[i - 1]),
              abs(low_prices[i] - close_prices[i - 1])) for i in range(1, len(candles))]
    smoothed_tr = np.mean(tr[-period:])

    # Calculate ADX
    dx = 100 * (smoothed_dm_plus / smoothed_tr) / (smoothed_dm_plus + smoothed_dm_minus)
    adx = np.mean(dx[-period:])
    return adx
