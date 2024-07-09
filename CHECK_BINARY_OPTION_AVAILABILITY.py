from iqoptionapi.stable_api import IQ_Option
import time

# Your IQ Option credentials
email = "armandjudicaelratombotiana@gmail.com"
password = "Aj!30071999@angular"

# Initialize IQ Option API
api = IQ_Option(email, password)
status, reason = api.connect()

if not status:
    print(f"Failed to connect: {reason}")
    exit()

print(f"Connection Status: {status}\nReason: {reason}")

# Function to fetch and list all binary option assets
def list_binary_option_assets():
    binary_option_assets = api.get_binary_option_detail()
    if binary_option_assets:
        print("Binary Option Assets:")
        for asset in binary_option_assets:
            print(asset)
    else:
        print("No binary option assets available.")

# Function to fetch and list all available assets
def list_available_assets():
    available_assets = api.get_all_open_time()
    if available_assets:
        print("Available Assets:")
        for asset in available_assets:
            print(asset)
    else:
        print("No assets available.")

# Call the function to list available assets
list_available_assets()
# Function to check if an asset is available
def is_asset_available(asset):
    available_assets = api.get_all_open_time()
    if asset in available_assets:
        print(f"{asset} is available for trading.")
        return True
    else:
        print(f"{asset} is not available for trading.")
        return False

# Example usage
list_binary_option_assets()