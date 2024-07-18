def ichimoku_cloud(candles):
    high_prices = [candle['high'] for candle in candles]
    low_prices = [candle['low'] for candle in candles]
    close_prices = [candle['close'] for candle in candles]

    # Calculate Ichimoku Cloud components
    tenkan_sen = (max(high_prices[-9:]) + min(low_prices[-9:])) / 2
    kijun_sen = (max(high_prices[-26:]) + min(low_prices[-26:])) / 2
    senkou_span_a = ((tenkan_sen + kijun_sen) / 2)[-26:]
    senkou_span_b = ((max(high_prices[-52:]) + min(low_prices[-52:])) / 2)[-26:]

    return tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b
