def calculate_macd(data, short_period=12, long_period=26, signal_period=9):
    short_ema = pd.Series(data).ewm(span=short_period, adjust=False).mean()
    long_ema = pd.Series(data).ewm(span=long_period, adjust=False).mean()
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()

    return macd_line, signal_line

# MACD Strategy
def macd_strategy(candles):
    close_prices = [candle['close'] for candle in candles]
    macd_line, signal_line = calculate_macd(close_prices)

    if macd_line[-1] > signal_line[-1]:
        direction = 'call'  # Buy signal
    elif macd_line[-1] < signal_line[-1]:
        direction = 'put'  # Sell signal
    else:
        direction = 'none'  # No trade

    return direction
