import pandas as pd

data = {
    'Timestamp': ['2024-07-17 14:00'],
    'Pair': ['EURUSD'],
    'Action': ['PUT'],
    'Stake': [10.0],
    'Martingale': [1],
    'Result': ['WIN'],
    'Profit': [2.0],
    'Total Profit': [2.0]
}

df = pd.DataFrame(data)
df.to_excel('test_backtest_results.xlsx', index=False)