# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from sklearn.svm import SVC
# from sklearn.model_selection import train_test_split
#
# # Simulated price data generation
# np.random.seed(42)
# dates = pd.date_range('2023-01-01', '2023-12-31', freq='B')
# prices = pd.Series(np.random.randn(len(dates)).cumsum(), index=dates)
#
# # Ensure 'prices' series is numeric
# prices = pd.to_numeric(prices, errors='coerce')
#
# # Parameters for moving averages
# short_window = 20  # Short-term moving average window
# long_window = 50   # Long-term moving average window
#
# # Calculate moving averages
# prices_ma_short = prices.rolling(window=short_window).mean()
# prices_ma_long = prices.rolling(window=long_window).mean()
#
# # Plotting the moving averages
# plt.figure(figsize=(14, 7))
# plt.plot(prices.index, prices, label='Price')
# plt.plot(prices_ma_short.index, prices_ma_short, label=f'Short-term MA ({short_window} days)')
# plt.plot(prices_ma_long.index, prices_ma_long, label=f'Long-term MA ({long_window} days)')
# plt.title('Moving Averages')
# plt.legend()
# plt.grid(True)
# plt.show()


# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from sklearn.svm import SVC
# from sklearn.model_selection import train_test_split
#
# # Simulated price data generation
# np.random.seed(42)
# dates = pd.date_range('2023-01-01', '2023-12-31', freq='B')
# prices = pd.Series(np.random.randn(len(dates)).cumsum(), index=dates)
#
# # Ensure 'prices' series is numeric
# prices = pd.to_numeric(prices, errors='coerce')
#
# # Parameters for moving averages
# short_window = 20  # Short-term moving average window
# long_window = 50   # Long-term moving average window
#
# # Calculate moving averages
# prices_ma_short = prices.rolling(window=short_window).mean()
# prices_ma_long = prices.rolling(window=long_window).mean()
#
# # Function to calculate RSI
# def calculate_rsi(prices, window=14):
#     delta = prices.diff()
#     gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
#     loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
#     rs = gain / loss
#     rsi = 100 - (100 / (1 + rs))
#     return rsi
#
# # Calculate RSI
# rsi = calculate_rsi(prices)
#
# # Prepare DataFrame with features and target
# data = pd.DataFrame({
#     'Price': prices,
#     'Short_MA': prices_ma_short,
#     'Long_MA': prices_ma_long,
#     'RSI': rsi
# })
#
# # Drop NaN values
# data.dropna(inplace=True)
#
# # Generate target variable: 1 if price goes up, -1 if price goes down
# data['Target'] = np.where(data['Price'].shift(-1) > data['Price'], 1, -1)
#
# # Features (X) and target (y)
# X = data[['Short_MA', 'Long_MA', 'RSI']]
# y = data['Target']
#
# # Split data into training and testing sets
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
#
# # Initialize SVM classifier
# clf = SVC(kernel='linear')
#
# # Train the classifier
# clf.fit(X_train, y_train)
#
# # Predict signals using SVM model
# data['ML_Signal'] = clf.predict(X)
#
# # Plotting the signals and strategy performance
# plt.figure(figsize=(14, 7))
#
# # Plot price and moving averages
# plt.plot(data.index, data['Price'], label='Price')
# plt.plot(data.index, data['Short_MA'], label=f'Short-term MA ({short_window} days)')
# plt.plot(data.index, data['Long_MA'], label=f'Long-term MA ({long_window} days)')
#
# # Plot buy and sell signals based on ML predictions
# plt.plot(data.loc[data['ML_Signal'] == 1].index, data['Short_MA'][data['ML_Signal'] == 1],
#          '^', markersize=10, color='g', lw=0, label='Buy Signal (ML)')
# plt.plot(data.loc[data['ML_Signal'] == -1].index, data['Short_MA'][data['ML_Signal'] == -1],
#          'v', markersize=10, color='r', lw=0, label='Sell Signal (ML)')
#
# # Add labels and legend
# plt.title('Binary Options Strategy Performance with MA, RSI, and ML Signals')
# plt.xlabel('Date')
# plt.ylabel('Price')
# plt.legend()
# plt.grid(True)
# plt.show()


# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.model_selection import train_test_split
#
# # Simulated price data generation
# np.random.seed(42)
# dates = pd.date_range('2023-01-01', '2023-12-31', freq='B')
# prices = pd.Series(np.random.randn(len(dates)).cumsum(), index=dates)
#
# # Ensure 'prices' series is numeric
# prices = pd.to_numeric(prices, errors='coerce')
#
# # Parameters for moving averages
# short_window = 20  # Short-term moving average window
# long_window = 50   # Long-term moving average window
#
# # Calculate moving averages
# prices_ma_short = prices.rolling(window=short_window).mean()
# prices_ma_long = prices.rolling(window=long_window).mean()
#
# # Function to calculate RSI
# def calculate_rsi(prices, window=14):
#     delta = prices.diff()
#     gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
#     loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
#     rs = gain / loss
#     rsi = 100 - (100 / (1 + rs))
#     return rsi
#
# # Calculate RSI
# rsi = calculate_rsi(prices)
#
# # Prepare DataFrame with features and target
# data = pd.DataFrame({
#     'Price': prices,
#     'Short_MA': prices_ma_short,
#     'Long_MA': prices_ma_long,
#     'RSI': rsi
# })
#
# # Drop NaN values
# data.dropna(inplace=True)
#
# # Generate target variable: 1 if price goes up, -1 if price goes down
# data['Target'] = np.where(data['Price'].shift(-1) > data['Price'], 1, -1)
#
# # Features (X) and target (y)
# X = data[['Short_MA', 'Long_MA', 'RSI']]
# y = data['Target']
#
# # Split data into training and testing sets
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
#
# # Initialize Random Forest classifier
# clf_rf = RandomForestClassifier(n_estimators=100, random_state=42)
#
# # Train the Random Forest classifier
# clf_rf.fit(X_train, y_train)
#
# # Predict signals using Random Forest model
# data['ML_Signal_RF'] = clf_rf.predict(X)
#
# # Plotting the signals and strategy performance
# plt.figure(figsize=(14, 7))
#
# # Plot price and moving averages
# plt.plot(data.index, data['Price'], label='Price')
# plt.plot(data.index, data['Short_MA'], label=f'Short-term MA ({short_window} days)')
# plt.plot(data.index, data['Long_MA'], label=f'Long-term MA ({long_window} days)')
#
# # Plot buy and sell signals based on RF predictions
# plt.plot(data.loc[data['ML_Signal_RF'] == 1].index, data['Short_MA'][data['ML_Signal_RF'] == 1],
#          '^', markersize=10, color='g', lw=0, label='Buy Signal (RF)')
# plt.plot(data.loc[data['ML_Signal_RF'] == -1].index, data['Short_MA'][data['ML_Signal_RF'] == -1],
#          'v', markersize=10, color='r', lw=0, label='Sell Signal (RF)')
#
# # Add labels and legend
# plt.title('Binary Options Strategy Performance with MA, RSI, and RF Signals')
# plt.xlabel('Date')
# plt.ylabel('Price')
# plt.legend()
# plt.grid(True)
# plt.show()


# import pandas as pd
# import numpy as np
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import accuracy_score, classification_report
# import matplotlib.pyplot as plt
#
# # Simulated price data generation (replace with your own data)
# np.random.seed(42)
# dates = pd.date_range('2023-01-01', '2023-12-31', freq='B')
# prices = pd.Series(np.random.randn(len(dates)).cumsum(), index=dates)
#
# # Ensure 'prices' series is numeric
# prices = pd.to_numeric(prices, errors='coerce')
#
# # Parameters for moving averages
# short_window = 20  # Short-term moving average window
# long_window = 50   # Long-term moving average window
#
# # Calculate moving averages
# prices_ma_short = prices.rolling(window=short_window).mean()
# prices_ma_long = prices.rolling(window=long_window).mean()
#
# # Function to calculate RSI
# def calculate_rsi(prices, window=14):
#     delta = prices.diff()
#     gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
#     loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
#     rs = gain / loss
#     rsi = 100 - (100 / (1 + rs))
#     return rsi
#
# # Calculate RSI
# rsi = calculate_rsi(prices)
#
# # Prepare DataFrame with features and target
# data = pd.DataFrame({
#     'Price': prices,
#     'Short_MA': prices_ma_short,
#     'Long_MA': prices_ma_long,
#     'RSI': rsi
# })
#
# # Drop NaN values
# data.dropna(inplace=True)
#
# # Generate target variable: 1 if price goes up, 0 if price goes down
# data['Target'] = np.where(data['Price'].shift(-1) > data['Price'], 1, 0)
#
# # Features (X) and target (y)
# X = data[['Short_MA', 'Long_MA', 'RSI']]
# y = data['Target']
#
# # Split data into training and testing sets
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
#
# # Initialize Random Forest classifier
# clf_rf = RandomForestClassifier(n_estimators=100, random_state=42)
#
# # Train the Random Forest classifier
# clf_rf.fit(X_train, y_train)
#
# # Predictions on the test set
# y_pred = clf_rf.predict(X_test)
#
# # Model evaluation
# print("Accuracy:", accuracy_score(y_test, y_pred))
# print("\nClassification Report:")
# print(classification_report(y_test, y_pred))
#
# # Plotting the signals and strategy performance (optional)
# plt.figure(figsize=(14, 7))
# plt.plot(data.index, data['Price'], label='Price')
# plt.plot(data.index, data['Short_MA'], label=f'Short-term MA ({short_window} days)')
# plt.plot(data.index, data['Long_MA'], label=f'Long-term MA ({long_window} days)')
# plt.legend()
# plt.title('Binary Option Trading Strategy with MA and RSI')
# plt.xlabel('Date')
# plt.ylabel('Price')
# plt.grid(True)
# plt.show()


import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt

# Simulated price data generation (replace with your actual data)
np.random.seed(42)
dates = pd.date_range('2023-01-01', '2023-12-31', freq='B')
prices = pd.Series(np.random.randn(len(dates)).cumsum(), index=dates)

# Ensure 'prices' series is numeric
prices = pd.to_numeric(prices, errors='coerce')

# Parameters for moving averages
short_window = 20  # Short-term moving average window
long_window = 50   # Long-term moving average window

# Calculate moving averages
prices_ma_short = prices.rolling(window=short_window).mean()
prices_ma_long = prices.rolling(window=long_window).mean()

# Function to calculate RSI (optional)
def calculate_rsi(prices, window=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Calculate RSI (optional)
rsi = calculate_rsi(prices)

# Prepare DataFrame with features and target
data = pd.DataFrame({
    'Price': prices,
    'Short_MA': prices_ma_short,
    'Long_MA': prices_ma_long,
    # Add more features as needed
})

# Drop NaN values
data.dropna(inplace=True)

# Generate target variable: 1 if price goes up, 0 if price goes down
data['Target'] = np.where(data['Price'].shift(-1) > data['Price'], 1, 0)

# Features (X) and target (y)
X = data[['Short_MA', 'Long_MA']]
y = data['Target']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize XGBoost classifier
clf_xgb = XGBClassifier(learning_rate=0.1, n_estimators=100, max_depth=3, random_state=42)

# Train the XGBoost classifier
clf_xgb.fit(X_train, y_train)

# Predictions on the test set
y_pred_xgb = clf_xgb.predict(X_test)

# Evaluate XGBoost model
print("XGBoost Accuracy:", accuracy_score(y_test, y_pred_xgb))
print("\nClassification Report (XGBoost):")
print(classification_report(y_test, y_pred_xgb))

# Plotting the signals and strategy performance (optional)
plt.figure(figsize=(14, 7))
plt.plot(data.index, data['Price'], label='Price')
plt.plot(data.index, data['Short_MA'], label=f'Short-term MA ({short_window} days)')
plt.plot(data.index, data['Long_MA'], label=f'Long-term MA ({long_window} days)')
plt.legend()
plt.title('Binary Option Trading Strategy with MA and XGBoost')
plt.xlabel('Date')
plt.ylabel('Price')
plt.grid(True)
plt.show()





