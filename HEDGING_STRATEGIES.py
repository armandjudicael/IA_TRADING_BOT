from iqoptionapi.stable_api import IQ_Option
import asyncio

# Replace with your actual credentials
email = "judicael.ratombotiana@gmail.com"
password = "Aj!30071999@jv"

# Initialize IQ Option API
api = IQ_Option(email, password)


async def main():
    try:
        await api.connect()

        # Example hedging strategy for EURUSD
        asset_name = 'EURUSD'
        call_strike = 1.15  # Example strike price for Call option
        put_strike = 1.10   # Example strike price for Put option
        expiration_time = 1  # Example expiration time in minutes
        amount = 10          # Example amount to invest

        # Place Call option (Buy)
        call_option = await api.buy(option_type='call', asset=asset_name, amount=amount, price=call_strike, action='buy', expiration_time=expiration_time)

        # Place Put option (Buy)
        put_option = await api.buy(option_type='put', asset=asset_name, amount=amount, price=put_strike, action='buy', expiration_time=expiration_time)

        # Check if both trades are successfully placed
        if call_option and put_option:
            print("Both hedging trades successfully placed.")
            # Implement logic to monitor trades or manage positions here
        else:
            print("Error placing hedging trades.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        await api.disconnect()

# Run the asynchronous main function
if __name__ == "__main__":
    asyncio.run(main())
