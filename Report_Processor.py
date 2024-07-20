import datetime
import pandas as pd
import os


class ReportProcessor:
    def __init__(self, report_file_path):
        """Initialize the ReportProcessor with the path to the report file."""

        current_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self.report_file_path = os.path.join(report_file_path, f'trade_monitoring_{current_time}.xlsx')

        # Load existing DataFrame or initialize an empty DataFrame
        try:
            self.results_df = pd.read_excel(self.report_file_path, sheet_name='Results', header=None)
        except FileNotFoundError:
            self.results_df = pd.DataFrame()  # Start with an empty DataFrame if file does not exist


    def log_trade_result(self, trade_id, direction, amount, result, balance, profit, duration, timestamp, strategy,total_profit):
        """Log the trade result to the report file."""
        try:
            # Create a new row as a DataFrame
            new_row = {
                'Trade ID': trade_id,
                'Timestamp': timestamp,
                'Strategy': strategy,
                'Direction': direction,
                'Amount': amount,
                'Trade Result': result,
                'Balance': balance,
                'Profit': profit,
                'Duration': duration,
                'Total Profit': total_profit
            }

            trade_df = pd.DataFrame([new_row])  # Create a DataFrame with one row

            # Append the new row to the existing DataFrame
            self.results_df = pd.concat([self.results_df, trade_df], ignore_index=True)

            # Create a new Excel file or overwrite existing file
            with pd.ExcelWriter(self.report_file_path, engine='openpyxl', mode='w') as writer:
                self.results_df.to_excel(writer, sheet_name='Results', index=False, header=False)
        except Exception as e:
            print(f"ERROR - Error handling trade result: {e}")