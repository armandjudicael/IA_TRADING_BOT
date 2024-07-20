import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Function to load data using yfinance
def load_data(ticker, start_date, end_date):
    df = yf.download(ticker, start=start_date, end=end_date)
    df.reset_index(inplace=True)  # Reset index to get 'Date' as a column
    return df

# Function to define breakout levels
def define_levels(df, window=20):
    df['High_Max'] = df['High'].rolling(window=window).max()
    df['Low_Min'] = df['Low'].rolling(window=window).min()
    return df

# Function to detect false breakouts
def detect_false_breakouts(df, threshold=0.01):
    df['False_Breakout'] = np.nan
    for i in range(1, len(df)):
        if pd.notna(df['High_Max'][i]) and pd.notna(df['Low_Min'][i]):
            if df['Close'][i] > df['High_Max'][i] * (1 + threshold):
                if df['Close'][i] < df['High'][i-1]:  # Check if price reverses
                    df.loc[df.index[i], 'False_Breakout'] = df['Close'][i]
            elif df['Close'][i] < df['Low_Min'][i] * (1 - threshold):
                if df['Close'][i] > df['Low'][i-1]:  # Check if price reverses
                    df.loc[df.index[i], 'False_Breakout'] = df['Close'][i]
    return df

# Function to visualize the results
def plot_results(df):
    plt.figure(figsize=(14, 7))
    plt.plot(df['Date'], df['Close'], label='Close Price', color='blue')
    plt.plot(df['Date'], df['High_Max'], label='Resistance Level', color='red', linestyle='--')
    plt.plot(df['Date'], df['Low_Min'], label='Support Level', color='green', linestyle='--')
    plt.scatter(df['Date'], df['False_Breakout'], color='orange', label='False Breakouts', marker='o')
    plt.title('False Breakout Strategy')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.show()

# Main execution
ticker = 'AAPL'  # Example ticker symbol
start_date = '2023-01-01'
end_date = '2024-01-01'

df = load_data(ticker, start_date, end_date)
df = define_levels(df)
df = detect_false_breakouts(df)
plot_results(df)
