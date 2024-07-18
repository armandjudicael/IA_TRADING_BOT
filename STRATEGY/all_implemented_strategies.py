import pandas as pd
from ta.volatility import BollingerBands, AverageTrueRange
from ta.momentum import RSIIndicator
from ta.trend import MACD, ADXIndicator


def bollinger_bands_strategy(candles, window=20, std_dev=2):
    close_prices = [candle['close'] for candle in candles]
    df = pd.DataFrame({'Close': close_prices})
    indicator_bb = BollingerBands(close=df['Close'], window=window, window_dev=std_dev)
    df['bb_bbm'] = indicator_bb.bollinger_mavg()
    df['bb_bbh'] = indicator_bb.bollinger_hband()
    df['bb_bbl'] = indicator_bb.bollinger_lband()

    if close_prices[-1] > df['bb_bbh'].iloc[-1]:
        return 'put'
    elif close_prices[-1] < df['bb_bbl'].iloc[-1]:
        return 'call'
    else:
        return 'none'


def rsi_strategy(candles, window=14):
    close_prices = [candle['close'] for candle in candles]
    df = pd.DataFrame({'Close': close_prices})
    rsi_indicator = RSIIndicator(close=df['Close'], window=window)
    return rsi_indicator.rsi().iloc[-1]


def macd_strategy(candles, window_slow=26, window_fast=12, window_sign=9):
    close_prices = [candle['close'] for candle in candles]
    df = pd.DataFrame({'Close': close_prices})
    macd_indicator = MACD(close=df['Close'], window_slow=window_slow, window_fast=window_fast, window_sign=window_sign)
    return macd_indicator.macd().iloc[-1], macd_indicator.macd_signal().iloc[-1], macd_indicator.macd_diff().iloc[-1]


def calculate_adx(candles, window=14):
    high_prices = [candle['high'] for candle in candles]
    low_prices = [candle['low'] for candle in candles]
    close_prices = [candle['close'] for candle in candles]
    df = pd.DataFrame({'High': high_prices, 'Low': low_prices, 'Close': close_prices})
    adx_indicator = ADXIndicator(high=df['High'], low=df['Low'], close=df['Close'], window=window)
    return adx_indicator.adx().iloc[-1]


def calculate_atr(candles, window=14):
    high_prices = [candle['high'] for candle in candles]
    low_prices = [candle['low'] for candle in candles]
    close_prices = [candle['close'] for candle in candles]
    df = pd.DataFrame({'High': high_prices, 'Low': low_prices, 'Close': close_prices})
    atr_indicator = AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close'], window=window)
    return atr_indicator.average_true_range().iloc[-1]

def calculate_ichimoku_cloud(candles, tenkan_sen_window=9, kijun_sen_window=26, senkou_span_b_window=52, chikou_span_window=26):
    """
    Calculate Ichimoku Cloud components based on historical candlestick data using ta library.

    Parameters:
    - candles: List of dictionaries containing candlestick data with keys 'high', 'low', 'close'.
    - tenkan_sen_window: Period for Tenkan-sen calculation.
    - kijun_sen_window: Period for Kijun-sen calculation.
    - senkou_span_b_window: Period for Senkou Span B calculation.
    - chikou_span_window: Period for Chikou Span calculation.

    Returns:
    - tenkan_sen: List of Tenkan-sen values corresponding to each candle.
    - kijun_sen: List of Kijun-sen values corresponding to each candle.
    - senkou_span_a: List of Senkou Span A values corresponding to each candle.
    - senkou_span_b: List of Senkou Span B values corresponding to each candle.
    - chikou_span: List of Chikou Span values corresponding to each candle.
    """
    high_prices = [candle['high'] for candle in candles]
    low_prices = [candle['low'] for candle in candles]
    close_prices = [candle['close'] for candle in candles]

    df = pd.DataFrame({'High': high_prices, 'Low': low_prices, 'Close': close_prices})

    # Calculate Ichimoku Cloud using ta library
    ichimoku = IchimokuIndicator(df['High'], df['Low'], df['Close'], n1=tenkan_sen_window, n2=kijun_sen_window, n3=senkou_span_b_window, visual=True)
    tenkan_sen = ichimoku.ichimoku_base_line()
    kijun_sen = ichimoku.ichimoku_conversion_line()
    senkou_span_a = ichimoku.ichimoku_a()
    senkou_span_b = ichimoku.ichimoku_b()
    chikou_span = ichimoku.ichimoku_visual()

    return tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span

def advanced_combined_strategy(candles):
    # Fetch indicators
    direction_bollinger = bollinger_bands_strategy(candles)
    rsi = rsi_strategy(candles)
    macd_line, signal_line, macd_histogram = macd_strategy(candles)
    adx = calculate_adx(candles)
    atr = calculate_atr(candles)

    # Calculate Ichimoku Cloud components
    tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span = calculate_ichimoku_cloud(candles)

    # Calculate Fibonacci retracement levels
    high_prices = [candle['high'] for candle in candles]
    low_prices = [candle['low'] for candle in candles]
    last_close_price = candles[-1]['close']
    fib_levels = calculate_fibonacci_retracement(high_prices, low_prices, last_close_price)

    # Define trade conditions including Ichimoku Cloud and Fibonacci levels
    if direction_bollinger == 'call' and rsi < 30 and macd_line > signal_line and adx > 25 and last_close_price <= fib_levels['38.2']:
        direction = 'call'
    elif direction_bollinger == 'put' and rsi > 70 and macd_line < signal_line and adx > 25 and last_close_price >= fib_levels['61.8']:
        direction = 'put'
    elif tenkan_sen[-1] > kijun_sen[-1] and last_close_price > senkou_span_a[-1] and last_close_price > senkou_span_b[-1] and last_close_price > max(high_prices[-senkou_span_b_window:]):
        direction = 'call'  # Bullish signals from Ichimoku Cloud
    elif tenkan_sen[-1] < kijun_sen[-1] and last_close_price < senkou_span_a[-1] and last_close_price < senkou_span_b[-1] and last_close_price < min(low_prices[-senkou_span_b_window:]):
        direction = 'put'   # Bearish signals from Ichimoku Cloud
    else:
        direction = 'none'  # No trade

    return direction