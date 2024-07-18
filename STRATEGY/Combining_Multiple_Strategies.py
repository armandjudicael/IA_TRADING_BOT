# Combined Strategy
def combined_strategy(candles):
    bollinger_signal = bollinger_bands_strategy(candles)
    rsi_signal = rsi_strategy(candles)
    macd_signal = macd_strategy(candles)

    if bollinger_signal == 'call' and rsi_signal == 'call' and macd_signal == 'call':
        return 'call'
    elif bollinger_signal == 'put' and rsi_signal == 'put' and macd_signal == 'put':
        return 'put'
    else:
        return 'none'


# Combined Strategy with Multiple Indicators
def advanced_combined_strategy(candles):
    # Fetch indicators
    direction_bollinger = bollinger_bands_strategy(candles)
    rsi = rsi_strategy(candles)
    macd_line, signal_line, macd_histogram = macd_strategy(candles)
    adx = calculate_adx(candles)
    atr = calculate_atr(candles)

    # Define trade conditions
    if direction_bollinger == 'call' and rsi < 30 and macd_line > signal_line and adx > 25:
        direction = 'call'
    elif direction_bollinger == 'put' and rsi > 70 and macd_line < signal_line and adx > 25:
        direction = 'put'
    else:
        direction = 'none'  # No trade

    return direction


# Trading loop with combined strategy
while True:
    try:
        # Sleep until the start of the next minute
        current_time = datetime.datetime.now()
        next_minute = (current_time + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)
        sleep_duration = (next_minute - current_time).total_seconds()
        time.sleep(sleep_duration)

        # Fetch the latest candlestick data
        end_time = time.time()  # Current time
        size = max(short_period, long_period)  # Number of candlesticks needed
        candles = api.get_candles(asset, duration, size, end_time)

        if len(candles) < size:
            logging.warning("Not enough data for analysis")
            print("Not enough data for analysis")
            continue

        # Use the combined strategy for decision-making
        direction = combined_strategy(candles)

        if direction != 'none':
            # Execute the trade
            status, trade_id = api.buy(global_amount, asset, direction, duration)
            if status:
                logging.info(f"Trade executed: {direction} on {asset} with Trade ID {trade_id} and Amount {global_amount}")
                send_email("Trade Executed Successfully", f"Trade executed: {direction} on {asset} with Trade ID {trade_id} and Amount {global_amount}")

                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                strategy = 'Combined Strategies'
                trade_status = 'Open'

                # Write data to Excel
                sheet.append([trade_id, timestamp, strategy, trade_status, global_amount, None, api.get_balance()])
            else:
                logging.error(f"Trade execution failed: {reason}")
                send_email("Trade Execution Error", f"Trade execution failed: {reason}")
                print(f"Trade execution failed: {reason}")

            # Check the trade result
            time.sleep(duration * 60 + 10)  # Wait for the trade to complete (duration + 10 seconds buffer)
            trade_result = api.check_win_v3(trade_id)

            if trade_result is not None:
                result_str = 'Win' if trade_result > 0 else 'Loss'
                logging.info(f"Trade result: {result_str} for Trade ID {trade_id}. Profit/Loss: {trade_result}. New Balance: {api.get_balance()}")
                send_email(f"Trade Result: {result_str}", f"Trade result: {result_str} for Trade ID {trade_id}. Profit/Loss: {trade_result}. New Balance: {api.get_balance()}")
                print(f"Trade result: {result_str}")
                print(f"Profit/Loss: {trade_result}")
                print("Balance:", api.get_balance())

                # Update trade result in the Excel sheet
                for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row):
                    if row[0].value == trade_id:
                        row[5].value = 'Win' if trade_result > 0 else 'Loss'
                        row[6].value = api.get_balance()
                        break

                # Apply Martingale strategy
                if trade_result <= 0:
                    global_amount *= martingale
                    logging.info(f"Martingale applied. New amount for the next trade: {global_amount}")
                    send_email("Martingale Applied", f"Martingale applied. New amount for the next trade: {global_amount}")
                else:
                    global_amount = 1
            else:
                logging.error("Failed to retrieve trade result")
                send_email("Trade Result Retrieval Error", "Failed to retrieve trade result")
                print("Failed to retrieve trade result")

        # Wait before the next iteration
        time.sleep(10)  # Wait 10 seconds before fetching new data and trading again

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        send_email("Script Error", f"An error occurred: {e}")
        time.sleep(10)  # Wait before retrying in case of an error

# Save workbook to Excel file with a random number appended to the filename
random_number = random.randint(1000, 9999)
excel_file = f'trade_monitoring_{random_number}.xlsx'
workbook.save(filename=excel_file)

