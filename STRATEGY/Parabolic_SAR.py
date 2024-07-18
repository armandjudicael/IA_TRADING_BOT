def parabolic_sar(candles, acceleration=0.02, maximum_acceleration=0.2):
    high_prices = [candle['high'] for candle in candles]
    low_prices = [candle['low'] for candle in candles]
    sar = [low_prices[0]]  # Initialize SAR with the first low price
    ep = high_prices[0]  # Extreme Price
    af = acceleration  # Acceleration Factor

    for i in range(1, len(candles)):
        sar.append(sar[-1] + af * (ep - sar[-1]))

        if sar[-1] > high_prices[i]:  # Reverse to uptrend
            sar[-1] = high_prices[i]
            ep = low_prices[i]
            af = acceleration
        elif sar[-1] < low_prices[i]:  # Reverse to downtrend
            sar[-1] = low_prices[i]
            ep = high_prices[i]
            af = acceleration
        else:
            af = min(af + acceleration, maximum_acceleration)

    return sar
