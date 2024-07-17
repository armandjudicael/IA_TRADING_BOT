import ta


def calculate_fibonacci_levels(high, low):
    # Example logic assuming 'ta' provides Fibonacci levels directly
    fib_levels = {
        '0%': low,
        '23.6%': low + (high - low) * 0.236,
        '38.2%': low + (high - low) * 0.382,
        '50%': (high + low) / 2,
        '61.8%': low + (high - low) * 0.618,
        '100%': high
    }
    return fib_levels


def main():
    # Example usage
    high = 100  # Replace with actual high value
    low = 50  # Replace with actual low value

    # Calculate Fibonacci retracement levels
    fibonacci_levels = calculate_fibonacci_levels(high, low)

    # Print the levels
    print("Fibonacci Retracement Levels:")
    for level, value in fibonacci_levels.items():
        print(f"{level}: {value}")


if __name__ == "__main__":
    main()
