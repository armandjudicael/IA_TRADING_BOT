import numpy as np


def calculate_fibonacci_retracement(high_prices, low_prices, last_close_price):
    """
    Calculate Fibonacci retracement levels.

    Parameters:
    - high_prices: List or array of high prices.
    - low_prices: List or array of low prices.
    - last_close_price: Last closing price for the current period.

    Returns:
    - fib_levels: Dictionary with Fibonacci retracement levels.
    """
    highest_high = np.max(high_prices)
    lowest_low = np.min(low_prices)

    # Calculate Fibonacci levels
    fib_levels = {}
    fib_levels['0.0'] = last_close_price
    fib_levels['23.6'] = last_close_price - 0.236 * (highest_high - lowest_low)
    fib_levels['38.2'] = last_close_price - 0.382 * (highest_high - lowest_low)
    fib_levels['50.0'] = last_close_price - 0.5 * (highest_high - lowest_low)
    fib_levels['61.8'] = last_close_price - 0.618 * (highest_high - lowest_low)
    fib_levels['100.0'] = lowest_low
    fib_levels['161.8'] = lowest_low - 1.618 * (highest_high - lowest_low)

    return fib_levels
