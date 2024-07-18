import os
import pandas as pd
import ta
from iqoptionapi.stable_api import IQ_Option
import time
import datetime
import threading
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

class TradingBot:
    def __init__(self):
        # Initialize bot parameters
        self.email = "judicael.ratombotiana@gmail.com"
        self.password = "Aj!30071999@jv"
        self.account_type = 'demo'
        self.available_pairs = {}
        self.solde_initial = 0.00

        # Initialize the Excel writer
        self.excel_file = '../backtest_results.xlsx'
        self.create_excel_writer()

        self.connect_api()
        self.fetch_pairs()
        self.select_pair_and_stake()
        self.reset_trade_variables()

    def create_excel_writer(self):
        """Create a new Excel file or open an existing one for logging backtesting results."""
        if os.path.exists(self.excel_file):
            os.remove(self.excel_file)  # Remove the corrupted file to avoid BadZipFile error
            # Ensure a fresh file is created
            self.writer = pd.ExcelWriter(self.excel_file, engine='openpyxl', mode='w')
        else:
            # Create a new Excel file
            self.writer = pd.ExcelWriter(self.excel_file, engine='openpyxl', mode='w')

        # Initialize results DataFrame
        self.results_df = pd.DataFrame(
            columns=['Timestamp', 'Pair', 'Action', 'Stake', 'Martingale', 'Result', 'Profit', 'Total Profit'])
        self.results_df.to_excel(self.writer, sheet_name='Results', index=False)
        self.writer._save()  # Save the file initially

    def connect_api(self):
        """Connect to the IQ Option API."""
        try:
            self.api = IQ_Option(self.email, self.password)
            connect_result, connect_message = self.api.connect()
            if connect_result:
                print(Fore.YELLOW + "Connexion établie, récupération des paires disponibles..." + Style.RESET_ALL)
            else:
                raise ConnectionError(f"Erreur de connexion : {connect_message}")
        except Exception as e:
            print(Fore.RED + f"Exception lors de la connexion : {e}" + Style.RESET_ALL)
            raise

    def fetch_pairs(self):
        """Fetch available trading pairs and initialize the account balance."""
        self.api.connect()
        pairs = self.api.get_all_open_time()
        self.available_pairs = {idx: pair for idx, pair in enumerate(pairs['digital']) if pairs['digital'][pair]['open']}
        self.solde_initial = self.api.get_balance()
        self.api.api.close()  # Close the connection after fetching the pairs

        print("\nPaires disponibles :")
        for idx, pair in self.available_pairs.items():
            print(f"{idx + 1}. {pair}")

    def select_pair_and_stake(self):
        """Select the trading pair and initial stake."""
        pair_index = int(input("\nSélectionnez le numéro de la paire : ")) - 1
        self.pair = self.available_pairs[pair_index].strip().upper()
        self.stake = float(input("Mise initiale: "))
        self.martingale = float(input("Martingale: "))
        self.current_stake = self.stake

    def reset_trade_variables(self):
        """Reset trade variables."""
        self.action_ = "null"
        self.action = "default"
        self.status = ""
        self.total_profit = 0.00
        self.profit = 0.00
        self.profit_aff = 0.00
        self.id = 0
        self.recuperation_martingale = 0
        self.somme_marge_perdu = 0
        self.result = "default"
        self.time = "default"
        self.initial = "true"
        self.initial_testing_action = "default"

    def fetch_market_data(self, symbol, period, count=50):
        """Fetch market data and return as a DataFrame."""
        candles = self.api.get_candles(symbol, period, count, time.time())
        df = pd.DataFrame(candles)
        df['timestamp'] = pd.to_datetime(df['from'], unit='s')
        df.set_index('timestamp', inplace=True)
        return df

    def fetch_market_data_1(self, candles):
        """Convert candles to a DataFrame."""
        df = pd.DataFrame(candles)
        df['timestamp'] = pd.to_datetime(df['from'], unit='s')
        df.set_index('timestamp', inplace=True)
        return df

    def check_trade_result(self, order_id):
        """Check the result of a trade and update trade variables."""
        max_attempts = 5
        for attempt in range(max_attempts):
            if self.action != "default":
                result, profit = self.api.check_win_digital_v2(order_id)
                if result is not None and profit is not None:
                    self.profit = round(profit, 2)
                    self.somme_marge_perdu += self.profit
                    if profit > 0:
                        self.profit_aff = self.profit / self.current_stake
                        self.total_profit += self.profit_aff
                        self.result = "win"
                    else:
                        self.result = "loss"
                    return True
            time.sleep(1)
        return False

    def calculate_indicators(self, df):
        """Calculate technical indicators and add them to the DataFrame."""
        df['SMA_21'] = df['close'].rolling(window=21).mean()
        df['SMA_9'] = df['close'].rolling(window=9).mean()
        df['RSI'] = ta.momentum.rsi(df['close'], window=14)
        df.fillna(0, inplace=True)
        return df

    def log_trade_result(self):
        """Log the trade result to the Excel file."""
        new_row = {
            'Timestamp': self.time,
            'Pair': self.pair,
            'Action': self.action_,
            'Stake': self.current_stake,
            'Martingale': self.recuperation_martingale,
            'Result': self.result.upper(),
            'Profit': self.profit_aff,
            'Total Profit': self.total_profit
        }
        trade_df = pd.DataFrame([new_row])  # Create a DataFrame with one row
        self.results_df = pd.concat([self.results_df, trade_df], ignore_index=True)
        self.results_df.to_excel(self.writer, sheet_name='Results', index=False)
        self.writer._save()  # Use the correct save method

    def start_trading(self):
        """Start the trading process in a separate thread."""
        def run_trading():
            try:
                self.api.connect()
                self.api.change_balance("PRACTICE" if self.account_type == "demo" else "REAL")

                if (balance := self.api.get_balance()) is None or balance <= 0:
                    raise ValueError("Solde du compte insuffisant ou non disponible.")
                self.solde_initial = balance
                self.status = "Robot en cours d'exécution"
                martingale_multiplier = self.martingale

                while True:
                    if not self.is_pair_open(self.pair):
                        print(f"La paire {self.pair} est fermée. Sélection d'une nouvelle paire...")
                        self.select_new_pair()

                    # Sleep until the start of the next minute
                    current_time = datetime.datetime.now()
                    next_minute = (current_time + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)
                    sleep_duration = (next_minute - current_time).total_seconds()
                    time.sleep(sleep_duration)

                    try:
                        candles = self.api.get_candles(self.pair, 60, 50, time.time())
                        if not candles:
                            print("Erreur lors de la récupération des données de marché. Réessayez...")
                            continue
                    except Exception as e:
                        print(Fore.RED + f"Erreur lors de la récupération des données de marché : {e}" + Style.RESET_ALL)
                        continue

                    df = self.fetch_market_data_1(candles)
                    df.rename(columns={'max': 'high', 'min': 'low', 'close': 'close'}, inplace=True)

                    if 'high' not in df.columns or 'low' not in df.columns or 'close' not in df.columns:
                        raise ValueError("Colonnes nécessaires (high, low, close) manquantes dans le DataFrame.")

                    df = self.calculate_indicators(df)

                    if self.id != 0 and self.check_trade_result(self.id):
                        if self.result == "win":
                            self.initial_testing_action = "default"
                            action_color = Fore.GREEN + f"{self.action_}" if self.action == "call" else Fore.RED + f"{self.action_}"
                            result_color = Fore.GREEN + "WIN"
                            profit_color = Fore.GREEN + f"{round(self.profit_aff, 2)}"
                            pair_color = Fore.YELLOW + f"{self.pair}"
                            total_color = Fore.BLUE + f"{self.total_profit:.2f}"
                            print(f"|{self.time}    |  {pair_color}   |    {action_color}    |   {self.current_stake:.2f}    | {self.recuperation_martingale}  |   {result_color}    |    {profit_color}    | {total_color} ")
                            self.current_stake = self.stake
                            self.recuperation_martingale = 0
                        elif self.result == "loss":
                            self.current_stake *= martingale_multiplier
                            self.recuperation_martingale += 1

                        self.log_trade_result()  # Log the trade result to Excel

                    if self.recuperation_martingale <= 2:
                        if df['close'].iloc[-1] < df['open'].iloc[-1]:
                            self.action, self.action_ = "put", "PUT "
                        elif df['close'].iloc[-1] > df['open'].iloc[-1]:
                            self.action, self.action_ = "call", "CALL"
                    else:
                        if df['SMA_9'].iloc[-1] < df['SMA_21'].iloc[-1] and df['RSI'].iloc[-1] < 50:
                            self.action, self.action_ = "put", "PUT "
                        elif df['SMA_9'].iloc[-1] > df['SMA_21'].iloc[-1] and df['RSI'].iloc[-1] > 50:
                            self.action, self.action_ = "call", "CALL"

                    if self.action != "default":
                        try:
                            result, order_id = self.api.buy_digital_spot(self.pair, self.current_stake, self.action, 1)
                            self.id = order_id
                        except Exception as e:
                            self.status = f"Exception: {e}"

                    self.time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

            except Exception as e:
                self.status = f"Erreur: {e}"
            finally:
                self.api.api.close()
                print(f"\n----------------------------------------------------------------------------------")
                print(f"|-> {self.status} , total profit : {self.total_profit}")

        threading.Thread(target=run_trading).start()

    def is_pair_open(self, pair):
        """Check if the trading pair is open."""
        return self.api.get_all_open_time()['digital'].get(pair, {}).get('open', False)

    def select_new_pair(self):
        """Select a new trading pair if the current one is closed."""
        self.fetch_pairs()
        self.select_pair_and_stake()

# To run the bot
if __name__ == "__main__":
    bot = TradingBot()
    bot.start_trading()
