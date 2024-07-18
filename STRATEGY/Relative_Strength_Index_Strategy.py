def calculate_rsi(data, period=14):
    gains = []
    losses = []

    for i in range(1, len(data)):
        change = data[i] - data[i - 1]
        if change >= 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(-change)

    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])

    if avg_loss == 0:
        rsi = 100  # Avoid division by zero
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

    return rsi


# RSI Strategy
def rsi_strategy(candles):
    close_prices = [candle['close'] for candle in candles]
    rsi = calculate_rsi(close_prices, period=14)

    if rsi > 70:
        direction = 'put'  # Sell signal
    elif rsi < 30:
        direction = 'call'  # Buy signal
    else:
        direction = 'none'  # No trade

    return direction
