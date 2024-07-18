def calculate_ema(prices, period):
    return pd.Series(prices).ewm(span=period, adjust=False).mean().iloc[-1]
