import datetime
import time
import configparser
import random
import logging
import smtplib
from email.mime.text import MIMEText
from iqoptionapi.stable_api import IQ_Option
import pandas as pd
import os

class TradingBot:
    def __init__(self):
        self.direction = None
        self.config = self.load_config()
        try:
            self.email = self.config['IQOption']['email']
            self.password = self.config['IQOption']['password']
            self.account_type = self.config['IQOption']['accountType']
            self.global_amount = float(self.config['Trading']['amount'])
            self.martingale = float(self.config['Trading']['martingale'])

            if self.account_type =='PRACTICE' :
               self.demo_balance = float(self.config['Trading']['demo_initial_balance'])

            self.short_period = int(self.config['Trading']['short_period'])
            self.long_period = int(self.config['Trading']['long_period'])
            self.asset = self.config['Trading']['asset']
            self.duration = int(self.config['Trading']['duration'])
            self.smtp_server = self.config['Email']['smtp_server']
            self.smtp_port = int(self.config['Email']['smtp_port'])
            self.smtp_user = self.config['Email']['smtp_user']
            self.smtp_password = self.config['Email']['smtp_password']
            self.notification_email = self.config['Email']['notification_email']

            self.excel_directory = self.config['Paths']['excel_directory']
            self.log_directory = self.config['Paths']['log_directory']

            # Initialize top assets
            self.top_assets = [
                self.config['top_assets']['1'],
                self.config['top_assets']['2'],
                self.config['top_assets']['3'],
                self.config['top_assets']['4'],
                self.config['top_assets']['5']
            ]

            # Ensure directories exist
            os.makedirs(self.excel_directory, exist_ok=True)
            os.makedirs(self.log_directory, exist_ok=True)

            # Initialize logging
            log_file = os.path.join(self.log_directory, 'trading_log.log')
            logging.basicConfig(filename=log_file, level=logging.INFO,
                                format='%(asctime)s - %(levelname)s - %(message)s')

            self.create_excel_writer(
                ['Trade ID', 'Timestamp', 'Direction', 'Strategy', 'Status', 'Amount', 'Trade Result', 'Balance',
                 'Profit',
                 'Duration', 'Martingale'], self.excel_directory)

            self.connect_api()

        except KeyError as e:
            raise KeyError(f"Missing key in config.ini: {e}")


    def load_config(self):
        # Load configuration from a file
        config = configparser.ConfigParser()
        config.read('config.ini')

        mode = config['Environment']['mode']

        # Construct the filename based on mode
        config_filename = f'config-{mode.lower()}.ini'

        # Read configuration from the constructed filename
        config.read(config_filename)

        return config

    def init_favorite_asset(self):
        logging.info("Initializing favorite asset...")
        for top_asset in self.top_assets:
            if self.is_pair_open(top_asset):
                logging.info(f"Top asset {top_asset} is open.")
                return top_asset
            else:
                logging.info(f"Top asset {top_asset} is not open. Fetching available pairs with payouts.")

        # If no top asset is open, check for the highest payout
        highest_payout_pair = self.get_highest_payout_pair()
        if highest_payout_pair:
            logging.info(f"No top assets are open. Highest payout pair is {highest_payout_pair}.")
            return highest_payout_pair

        logging.error("No suitable asset found.")
        return None

    def fetch_available_pairs_with_payouts(self, max_retries=3, delay=5):
        for attempt in range(max_retries):
            try:
                self.api.connect()
                pairs = self.api.get_all_open_time()
                available_pairs = [pair for pair in pairs['digital'] if pairs['digital'][pair]['open']]
                logging.info(f"Available pairs: {available_pairs}")
                return available_pairs
            except Exception as e:
                logging.error(
                    f"Error fetching available pairs with payouts: {e}. Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
        logging.error(f"Failed to fetch available pairs with payouts after {max_retries} attempts.")
        return []

    def get_payout(self, pair, max_retries=3, delay=5):
        for attempt in range(max_retries):
            try:
                instruments = self.api.get_all_init()
                if "instruments" in instruments and "digital-option" in instruments["instruments"]:
                    digital_options = instruments["instruments"]["digital-option"]
                    for option in digital_options:
                        if option["active_id"] == self.api.get_name_by_activeId(pair)["active_id"]:
                            payout = option["profit"]["commission"]
                            logging.info(f"Payout for {pair}: {payout}")
                            return payout
                logging.warning(f"No payout information found for {pair}.")
                return None
            except Exception as e:
                logging.error(f"Error fetching payout for {pair}: {e}. Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
        logging.error(f"Failed to fetch payout for {pair} after {max_retries} attempts.")
        return None

    def get_highest_payout_pair(self, max_retries=3, delay=5):
        for attempt in range(max_retries):
            try:
                available_pairs = self.fetch_available_pairs_with_payouts()
                highest_payout = 0
                highest_payout_pair = None
                for pair in available_pairs:
                    payout = self.get_payout(pair)
                    if payout and payout > highest_payout:
                        highest_payout = payout
                        highest_payout_pair = pair
                logging.info(f"Highest payout pair: {highest_payout_pair} with payout {highest_payout}")
                return highest_payout_pair
            except Exception as e:
                logging.error(f"Error fetching highest payout pair: {e}. Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
        logging.error(f"Failed to determine highest payout pair after {max_retries} attempts.")
        return None

    def is_pair_open(self, pair, max_retries=3, delay=5):
        for attempt in range(max_retries):
            try:
                self.api.connect()
                pairs = self.api.get_all_open_time()
                is_open = pairs['digital'][pair]['open']
                logging.info(f"Is pair {pair} open: {is_open}")
                return is_open
            except Exception as e:
                logging.error(f"Error checking if pair {pair} is open: {e}. Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
        logging.error(f"Failed to determine if pair {pair} is open after {max_retries} attempts.")
        return False
    def connect_api(self):
        try:
            # Connect to the IQ Option API
            self.api = IQ_Option(self.email, self.password)
            status, reason = self.api.connect()

            if not status:
                logging.error(f'Failed to connect: {reason}')
                return False

            if reason == "2FA":
                code_sms = input("Enter the received code: ")
                status, reason = self.api.connect_2fa(code_sms)
                if not status:
                    logging.error(f'Failed to connect with 2FA: {reason}')
                    return False

            return True

        except Exception as e:
            logging.exception(f'Exception occurred while connecting: {e}')
            return False

    def create_excel_writer(self, columns, directory='.'):
        """
        Create a new Excel file or open an existing one for logging backtesting results.

        Parameters:
        - columns: list
            List of column names for the DataFrame.
        - directory: str, optional
            Directory where the Excel file should be saved. Defaults to current directory ('.').

        """
        current_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self.excel_file = os.path.join(directory, f'trade_monitoring_{current_time}.xlsx')

        if os.path.exists(self.excel_file):
            os.remove(self.excel_file)  # Remove the existing file if it exists

        # Create a new Excel file
        self.writer = pd.ExcelWriter(self.excel_file, engine='openpyxl', mode='w')

        # Initialize results DataFrame
        self.results_df = pd.DataFrame(columns=columns)
        self.results_df.to_excel(self.writer, sheet_name='Results', index=False)

        # Save and close the Excel writer
        self.writer._save()

    def send_email(self, subject, body):
        # Function to send email notifications
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.smtp_user
        msg['To'] = self.notification_email

        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, self.notification_email, msg.as_string())
            logging.info(f"Notification sent: {subject}")
        except Exception as e:
            logging.error(f"Failed to send email notification: {e}")

    def get_balance(self):
        if self.account_type == 'REAL':
            self.api.change_balance(self.account_type)
            return self.api.get_balance()
        elif self.account_type == 'PRACTICE':
            return self.demo_balance
        else:
            raise ValueError("Unsupported account type")

    def moving_average(self, data, period):
        return sum(data[-period:]) / period if len(data) >= period else 0

    def log_trade_result(self, trade_id, direction, amount, result, balance, profit,duration, martingale):
        """Log the trade result to the Excel file."""
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        strategy = 'Moving Average Crossover Strategy'
        trade_status = 'Closed'

        new_row = {
            'Trade ID': trade_id,
            'Timestamp': timestamp,
            'Direction': direction,
            'Strategy': strategy,
            'Status': trade_status,
            'Amount': amount,
            'Trade Result': result,
            'Balance': balance,
            'Profit': profit,
            'Duration': duration,
            'Martingale': martingale
        }

        trade_df = pd.DataFrame([new_row])  # Create a DataFrame with one row
        self.results_df = pd.concat([self.results_df, trade_df], ignore_index=True)
        self.results_df.to_excel(self.writer, sheet_name='Results', index=False)
        self.writer._save()

    def check_trade_result(self, trade_id, max_retries=3, retry_delay=2):
        # Function to check trade result with retry mechanism
        retries = 0
        while retries < max_retries:
            try:
                result, profit = self.api.check_win_digital_v2(trade_id)
                if result is not None and profit is not None:
                    return result, profit
                else:
                    logging.warning("Failed to retrieve trade result, retrying...")
                    time.sleep(retry_delay)
            except Exception as e:
                logging.error(f"Error checking trade result: {e}, retrying...")
                time.sleep(retry_delay)
            retries += 1
        logging.error("Max retries exceeded, unable to retrieve trade result")
        return None, None

    def determine_trading_direction(self):
        """
        Determines the trading direction based on moving average crossover.
        """

        end_time = time.time()  # Current time
        size = max(self.short_period, self.long_period)  # Number of candlesticks needed

        try:
            # Fetch the candlestick data
            candles = self.api.get_candles(self.asset, self.duration, size, end_time)

            # Check if we have enough data for analysis
            if len(candles) < size:
                logging.warning("Not enough data for analysis")
                return None

            # Extract the closing prices from the candles
            close_prices = [candle['close'] for candle in candles]

            # Calculate short and long moving averages
            short_ma = self.moving_average(close_prices, self.short_period)
            long_ma = self.moving_average(close_prices, self.long_period)

            # Determine the trading direction based on moving average crossover
            if short_ma > long_ma:
                direction = "call"  # Buy
            else:
                direction = "put"  # Sell

            logging.info(f"Trading direction determined: {direction}")
            return direction

        except Exception as e:
            logging.error(f"Error determining trading direction: {e}")
            return None

    def sleep_until_next_interval(self):
        """
        Sleeps until the start of the next interval based on the specified duration.
        """

        try:
            # Get the current time
            current_time = datetime.datetime.now()

            # Calculate the time for the start of the next interval
            next_interval = (current_time + datetime.timedelta(minutes=self.duration)).replace(second=0, microsecond=0)

            # Calculate the sleep duration
            sleep_duration = (next_interval - current_time).total_seconds()

            # Sleep until the next interval
            if sleep_duration > 0:
                logging.info(f"Sleeping for {sleep_duration} seconds until the next interval.")
                time.sleep(sleep_duration)
            else:
                logging.warning("Sleep duration is non-positive. Skipping sleep.")

        except Exception as e:
            logging.error(f"Error during sleep operation: {e}")

    def handle_trade_result(self, trade_id):
        """
        Handles the result of an already executed trade and adjusts the trading parameters accordingly.
        """
        logging.info(
            f"Handling result for trade with Trade ID {trade_id}. Direction: {self.direction}, Asset: {self.asset}, Amount: {self.global_amount}")

        # Wait for the trade to complete (duration + 10 seconds buffer)
        time.sleep(self.duration * 50)

        try:
            result, trade_result = self.check_trade_result(trade_id)

            if trade_result is not None:

                result_str = 'Win' if trade_result > 0 else 'Loss'

                logging.info(
                    f"Trade result: {result_str} for Trade ID {trade_id}.  Result : {result_str}. New Balance: {self.get_balance()}")

                self.log_trade_result(trade_id, self.direction, self.global_amount, result_str, self.get_balance(),
                                      trade_result, self.duration, self.martingale)

                if trade_result < 0:

                    self.handle_loss(trade_result)

                else:

                    self.handle_win(trade_result)

            else:
                logging.error("Failed to retrieve trade result")

        except Exception as e:
            logging.error(f"Error handling trade result: {e}")

    def handle_loss(self, trade_result):
        """
        Handles the adjustments required after a loss.
        """
        if self.account_type == 'PRACTICE':
            # Update demo balance
            self.demo_balance -= abs(trade_result)

        if 2 * (self.martingale * self.global_amount) <= self.get_balance():
            self.apply_martingale()
        else:
            self.reset_global_amount()


    def reset_global_amount(self):
        """
        Resets the global amount to the initial value specified in the config.
        """
        self.global_amount = float(self.config['Trading']['amount'])

    def apply_martingale(self):
        """
        Applies the Martingale strategy to the global amount.
        """
        self.global_amount *= self.martingale
        logging.info(f"Martingale applied. New amount for the next trade: {self.global_amount}")


    def handle_win(self, trade_result):
        """
        Handles the adjustments required after a win.
        """
        self.reset_global_amount()
        self.demo_balance += abs(trade_result)
        logging.info(f"Trade was successful. Resetting amount to {self.global_amount} for the next trade.")



    def attack_the_market(self):
        try:
            while True:

                self.asset = self.init_favorite_asset()

                if self.asset is not None:

                    self.sleep_until_next_interval()

                    self.direction = self.determine_trading_direction()

                    if self.direction is not None:

                            status, trade_id = self.api.buy_digital_spot(self.asset,self.global_amount, self.direction, self.duration)

                            if status:

                                self.handle_trade_result(trade_id)

                            else:
                                logging.error(f"Trade execution failed: {trade_id}")


        except Exception as e:
            logging.error(f"An error occurred: {e}")
            time.sleep(2)  # Wait before retrying in case of an error

if __name__ == "__main__":
    bot = TradingBot()
    bot.attack_the_market()
