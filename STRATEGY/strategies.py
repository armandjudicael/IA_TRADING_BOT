
from fibonacci_retracement import calculate_fibonacci_retracement

def advanced_combined_strategy(candles):
    # Fetch indicators
    direction_bollinger = bollinger_bands_strategy(candles)
    rsi = rsi_strategy(candles)
    macd_line, signal_line, macd_histogram = macd_strategy(candles)
    adx = calculate_adx(candles)
    atr = calculate_atr(candles)

    # Calculate Fibonacci retracement levels
    high_prices = [candle['high'] for candle in candles]
    low_prices = [candle['low'] for candle in candles]
    last_close_price = candles[-1]['close']
    fib_levels = calculate_fibonacci_retracement(high_prices, low_prices, last_close_price)

    # Define trade conditions including Fibonacci levels
    if direction_bollinger == 'call' and rsi < 30 and macd_line > signal_line and adx > 25 and last_close_price <= fib_levels['38.2']:
        direction = 'call'
    elif direction_bollinger == 'put' and rsi > 70 and macd_line < signal_line and adx > 25 and last_close_price >= fib_levels['61.8']:
        direction = 'put'
    else:
        direction = 'none'  # No trade

    return direction
