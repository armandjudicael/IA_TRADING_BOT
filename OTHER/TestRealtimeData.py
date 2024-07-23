import logging
from iqoptionapi.stable_api import IQ_Option

# Configure logging with a file handler
logging.basicConfig(filename='iqoption_realtime_candles.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


email = 'voahanginirina.noelline@gmail.com'
password = 'Noel!ne1969'

def connect_to_iq_option(email, password):
  """Connects to the IQ Option API and logs the result.

  Args:
      email: User's IQ Option email address.
      password: User's IQ Option password.

  Returns:
      An IQ_Option object if successful, None otherwise.
  """
  try:
      api = IQ_Option(email, password)
      api.connect()
      logging.info('Successfully connected to IQ Option API')
      return api
  except Exception as e:
      logging.error(f'Failed to connect to IQ Option API: {e}')
      return None

def get_realtime_candles(api, instrument, timeframe):
  """Retrieves real-time candles for the specified instrument and timeframe.

  Args:
      api: An IQ_Option object representing the connected API session.
      instrument: The financial instrument (e.g., "EURUSD").
      timeframe: The desired timeframe in seconds (e.g., 300 for 5 minutes).

  Returns:
      A dictionary containing real-time candles data if successful, None otherwise.
  """
  try:
      candles = api.get_realtime_candles(instrument, timeframe)
      logging.info(f'Retrieved real-time candles for {instrument} with {timeframe}s timeframe')
      return candles
  except Exception as e:
      logging.error(f'Error retrieving real-time candles: {e}')
      return None

def process_candles(candles):
  """Processes the retrieved real-time candles data.

  Args:
      candles: A dictionary containing real-time candles data.
  """
  for timestamp, candle in candles.items():
      logging.debug(f"Timestamp: {timestamp}, Open: {candle['open']}, High: {candle['max']}, Low: {candle['min']}, Close: {candle['close']}")

if __name__ == "__main__":
  # Connect to IQ Option
  api = connect_to_iq_option(email, password)

  # Check if connection successful
  if api is None:
      exit()

  # Define instrument and timeframe
  instrument = "EURUSD"
  timeframe = 300

  # Get real-time candles
  candles = get_realtime_candles(api, instrument, timeframe)

  # Check if candle retrieval successful
  if candles is None:
      exit()
      logging.info('Candle None')

  # Process candle data
  process_candles(candles)

  # Disconnect from IQ Option
  logging.info('Disconnected from IQ Option API')
