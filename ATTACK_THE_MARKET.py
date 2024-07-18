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
        # Configure logging
        logging.basicConfig(filename='trading_log.log', level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.config = self.load_config()
        try:
            self.email = self.config['IQOption']['email']
            self.password = self.config['IQOption']['password']
            self.global_amount = float(self.config['Trading']['amount'])
            self.martingale = float(self.config['Trading']['martingale'])
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
        except KeyError as e:
            raise KeyError(f"Missing key in config.ini: {e}")

    def load_config(self):
        # Load configuration from a file
        config = configparser.ConfigParser()
        config.read('config.ini')
        return config

    def connect_api(self):
        # Connect to the IQ Option API
        self.api = IQ_Option(self.email, self.password)
        status, reason = self.api.connect()

        if not status:
            logging.error(f'Failed to connect: {reason}')
            print('Failed to connect:', reason)
            exit()

        if reason == "2FA":
            code_sms = input("Enter the received code: ")
            status, reason = self.api.connect_2fa(code_sms)
            if not status:
                logging.error(f'Failed to connect with 2FA: {reason}')
                print('Failed to connect with 2FA:', reason)
                exit()

    def create_excel_writer(self, columns):
        """Create a new Excel file or open an existing one for logging backtesting results."""
        self.excel_file = f'trade_monitoring_{random.randint(1000, 9999)}.xlsx'

        if os.path.exists(self.excel_file):
            os.remove(self.excel_file)  # Remove the corrupted file to avoid BadZipFile error

        # Create a new Excel file
        self.writer = pd.ExcelWriter(self.excel_file, engine='openpyxl', mode='w')

        # Initialize results DataFrame
        self.results_df = pd.DataFrame(columns=columns)
        self.results_df.to_excel(self.writer, sheet_name='Results', index=False)
        self.writer._save()  # Save the file initially


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

    def get_demo_balance(self):
        # Function to calculate demo balance
        return self.demo_balance - self.api.get_balance()

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
            'Direction' : direction,
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

    def run_trading_strategy(self):
        try:
            self.create_excel_writer(
                ['Trade ID', 'Timestamp','Direction','Strategy', 'Status', 'Amount', 'Trade Result', 'Balance', 'Profit' , 'Duration', 'Martingale'])
            self.connect_api()

            while True:
                current_time = datetime.datetime.now()
                next_minute = (current_time + datetime.timedelta(minutes=self.duration)).replace(second=0, microsecond=0)
                sleep_duration = (next_minute - current_time).total_seconds()
                time.sleep(sleep_duration)

                end_time = time.time()  # Current time
                size = max(self.short_period, self.long_period)  # Number of candlesticks needed
                candles = self.api.get_candles(self.asset, self.duration, size, end_time)

                if len(candles) < size:
                    logging.warning("Not enough data for analysis")
                    print("Not enough data for analysis")
                    continue

                close_prices = [candle['close'] for candle in candles]
                short_ma = self.moving_average(close_prices, self.short_period)
                long_ma = self.moving_average(close_prices, self.long_period)

                if short_ma > long_ma:
                    direction = "call"  # Buy
                else:
                    direction = "put"  # Sell


                if direction != 'none':

                        status, trade_id = self.api.buy_digital_spot(self.asset,self.global_amount, direction, self.duration)

                        if status:
                            logging.info(
                                f"Trade executed successfully: {direction} on {self.asset} with Trade ID {trade_id} and Amount {self.global_amount}")
                            print(f"Trade executed successfully: {direction} on {self.asset}")

                            time.sleep(self.duration * 60)  # Wait for the trade to complete (duration + 10 seconds buffer)
                            result,trade_result = self.check_trade_result(trade_id)

                            if trade_result is not None:

                                result_str = 'Win' if trade_result > 0 else 'Loss'
                                logging.info(
                                    f"Trade result: {result_str} for Trade ID {trade_id}. Profit/Loss: {trade_result}. New Balance: {self.get_demo_balance()}")
                                print(f"Trade result: {result_str}")
                                print(f"Profit/Loss: {trade_result}")
                                print("Balance:", self.get_demo_balance())

                                self.log_trade_result(trade_id, direction, self.global_amount, result_str, self.get_demo_balance(), trade_result,self.duration,self.martingale)

                                if trade_result <= 0:

                                    if 2 * (self.martingale * self.global_amount) <= self.get_demo_balance():
                                        self.global_amount *= self.martingale
                                        logging.info(f"Martingale applied. New amount for the next trade: {self.global_amount}")
                                    else:
                                        self.global_amount = float(self.config['Trading']['amount'])
                                else:
                                    self.global_amount = float(self.config['Trading']['amount'])
                                    logging.info(
                                        f"Trade was successful. Resetting amount to {self.global_amount} for the next trade.")

                            else:
                                logging.error("Failed to retrieve trade result")
                                print("Failed to retrieve trade result")

                        else:
                            logging.error(f"Trade execution failed: {trade_id}")
                            print(f"Trade execution failed: {trade_id}")

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            print(f"An error occurred: {e}")
            time.sleep(10)  # Wait before retrying in case of an error

if __name__ == "__main__":
    bot = TradingBot()
    bot.run_trading_strategy()
