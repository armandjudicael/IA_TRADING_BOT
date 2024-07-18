import requests
import pandas as pd
from datetime import datetime, timedelta

# OANDA API credentials and settings
api_token = 'YOUR_OANDA_API_TOKEN'
account_id = 'YOUR_OANDA_ACCOUNT_ID'
base_url = 'https://api-fxtrade.oanda.com'
instrument = 'EUR_JPY'  # Instrument to trade


# Function to fetch historical candlestick data from OANDA
def fetch_historical_data(start_time, end_time, granularity='H1'):
    url = f"{base_url}/v3/instruments/{instrument}/candles"
    params = {
        'from': start_time.isoformat('T') + 'Z',
        'to': end_time.isoformat('T') + 'Z',
        'granularity': granularity,
        'count': 5000,  # Max number of candles to fetch (up to 5000)
    }
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if 'candles' in data:
        candles = data['candles']
        df = pd.DataFrame(candles)
        df['time'] = pd.to_datetime(df['time'], format='%Y-%m-%dT%H:%M:%S.%fZ')
        df.set_index('time', inplace=True)
        df.rename(columns={'mid': 'close'}, inplace=True)
        df['close'] = df['close'].apply(lambda x: x['c'])
        return df
    else:
        print(f"Error fetching data: {data}")
        return None


# Function to calculate Simple Moving Average (SMA)
def calculate_sma(data, window=50):
    data['SMA'] = data['close'].rolling(window=window).mean()
    return data


# Function to simulate basic trading strategy based on SMA
def simulate_trading_strategy(df):
    initial_balance = 10000  # Initial balance in base currency (e.g., EUR)
    investment_amount = 1000  # Amount to invest per trade in base currency
    trade_count = 0
    win_count = 0
    loss_count = 0

    for i in range(len(df) - 1):
        current_price = df['close'].iloc[i]
        current_sma = df['SMA'].iloc[i]
        next_price = df['close'].iloc[i + 1]

        if pd.isna(current_sma):
            continue

        # Simple strategy: Buy when price crosses above SMA, sell when price crosses below SMA
        if current_price < current_sma and next_price > current_sma:
            action = 'BUY'
        elif current_price > current_sma and next_price < current_sma:
            action = 'SELL'
        else:
            continue

        # Simulate trade outcome (assume 50% win rate)
        if action == 'BUY' and next_price > current_price:
            outcome = 'WIN'
            win_count += 1
            initial_balance += investment_amount
        elif action == 'SELL' and next_price < current_price:
            outcome = 'WIN'
            win_count += 1
            initial_balance += investment_amount
        else:
            outcome = 'LOSS'
            loss_count += 1
            initial_balance -= investment_amount

        trade_count += 1

        # Print trade details
        print(f"Trade {trade_count}: Action={action}, Outcome={outcome}, Balance={initial_balance:.2f}")

    # Print final results
    print(
        f"\nSimulation completed.\nTotal trades: {trade_count}\nWins: {win_count}, Losses: {loss_count}\nFinal balance: {initial_balance:.2f}")


# Main function to run the example
if __name__ == "__main__":
    # Fetch historical data for the past 30 days (adjust as needed)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=30)
    historical_data = fetch_historical_data(start_time, end_time)

    if historical_data is not None:
        # Calculate SMA
        historical_data = calculate_sma(historical_data)

        # Simulate trading strategy
        simulate_trading_strategy(historical_data)
