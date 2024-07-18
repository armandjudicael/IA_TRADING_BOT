# Import the library
from iqoptionapi.stable_api import IQ_Option


# Define your subclass with the reset_practice_balance method
class CustomIQOption(IQ_Option):
    def reset_practice_balance(self):
        self.api.training_balance_reset_request = None
        self.api.reset_training_balance()

        while True:
            # Wait for the training balance reset message
            message = self.websocket.receive_message()
            if message["name"] == "training_balance_reset":
                self.api.training_balance_reset_request = message["msg"]["isSuccessful"]
                break

        return self.api.training_balance_reset_request


# Credentials
email = "voahanginirina.noelline@gmail.com"
password = "Noel!ne1969"

print("Connecting...")
api = CustomIQOption(email, password)  # Use CustomIQOption instead of IQ_Option
status, reason = api.connect()

print('##### First Attempt #####')
print('Status:', status)
print('Reason:', reason)
print("Email:", api.email)

# # Call the reset_practice_balance method
# reset_result = api.reset_practice_balance()
# print("Practice Balance Reset Result:", reset_result)

if reason == "2FA":
    print('##### 2FA ENABLED #####')
    print("An SMS with a code has been sent to your number")

    code_sms = input("Enter the received code: ")
    status, reason = api.connect_2fa(code_sms)

    print('##### Second Attempt #####')
    print('Status:', status)
    print('Reason:', reason)
    print("Email:", api.email)

print("Balance:", api.get_balance())
print("##############################")
