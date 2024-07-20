from iqoptionapi.stable_api import IQ_Option
import pandas as pd
import time

# Credentials
email = "voahanginirina.noelline@gmail.com"
password = "Noel!ne1969"

# Connect to IQ Option
api = IQ_Option(email, password)
api.connect()

if api.check_connect():
    print("Connected to IQ Option")


def get_realtime_data(symbol, interval=60):
    api.subscribe_candle(symbol, interval)
    data = api.get_candles(symbol, interval, 100, time.time())
    return data


def detect_false_breakout(data):
    df = pd.DataFrame(data)
    df['Resistance'] = df['close'].rolling(window=20).max()
    df['Support'] = df['close'].rolling(window=20).min()
    df['False_Breakout'] = (df['close'] > df['Resistance'].shift(1)) & (df['close'] < df['Resistance'])
    return df


def place_trade(symbol, amount, direction, duration):
    result, trade_id = api.buy(amount, symbol, direction, duration)
    if result:
        print(f"Trade placed: {direction} {amount} {symbol}")
    else:
        print("Failed to place trade")


def main():
    symbol = 'EURUSD'
    interval = 60
    amount = 1
    duration = 1

    data = get_realtime_data(symbol, interval)
    df = detect_false_breakout(data)

    if df[df['False_Breakout']].shape[0] > 0:
        direction = 'put'  # Assume we detected a false breakout and want to sell
        place_trade(symbol, amount, direction, duration)


if __name__ == "__main__":
    main()
