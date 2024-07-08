# Import the library
from iqoptionapi.api import IQOptionAPI
from iqoptionapi.stable_api import IQ_Option
#
# email = "judicael.ratombotiana@gmail.com"
# password = "Aj!30071999@react"

email = "voahanginirina.noelline@gmail.com"
password = "Noel!ne1969"

print("Connecting...")
api = IQ_Option(email, password)
status, reason = api.connect()
print('##### First Attempt #####')
print('Status:', status)
print('Reason:', reason)
print("Email:", api.email)

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
