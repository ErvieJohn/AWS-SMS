import boto3
import random
from datetime import datetime
import pytz
from dotenv import load_dotenv
import os

current_date = datetime.now(pytz.timezone("Asia/Manila")).strftime("%m/%d/%y %I:%M%p %Z")

# Generate a random verification code
def generate_verification_code():
    return str(random.randint(100000, 999999))

# Load the environment variables from the .env file
load_dotenv()

# Initialize SNS client
ACCESS_KEY_ID=os.getenv("AWS_ACCESS_KEY_ID")
SECRET_ACCESS_KEY=os.getenv("AWS_SECRET_ACCESS_KEY")
REGION_NAME=os.getenv("AWS_REGION")

# Initialize the client for STS
sts_client = boto3.client('sts', 
    aws_access_key_id=ACCESS_KEY_ID,
    aws_secret_access_key=SECRET_ACCESS_KEY,
    region_name=REGION_NAME)

response = sts_client.get_session_token(DurationSeconds=43200)  # 12 hours max duration
CREDENTIALS = response['Credentials']
# print(response['Credentials'])


sns = boto3.client('sns', 
                    region_name=REGION_NAME,
                    aws_access_key_id=CREDENTIALS['AccessKeyId'],
                    aws_secret_access_key=CREDENTIALS['SecretAccessKey'],
                    aws_session_token=CREDENTIALS['SessionToken']
                   )

# Function to send SMS
def send_sms(phone_number,code):
    for number in phone_number: 
        
        message = f"ErvieJohn\n{code}\n[Test SMS only - {current_date}]"
        #message = f"[Test SMS only - {current_date}]\n22222"
        response = sns.publish(
            PhoneNumber=number,
            Message=message,
            MessageAttributes={
            'AWS.SNS.SMS.SMSType': {
                'DataType': 'String',
                'StringValue': 'Transactional'  # Use 'Promotional' for marketing messages
            }
        }
        )

        print("Sending to: ", number)
        print("Message: \n", message)

        print(f"Verification code sent! Response: {response}")

    # return response

# Example usage
#phone_number = '+639615254051'  # PH NUMBER
#phone_number = '+639765527288'
#phone_number = '+818039888485' # Japan Number
#phone_number = '+84332856336' # VIETNAM NUMBER

phone_numbers = ["+84941414422"]  # JAPAN AND VIETNAM NUMBER
verification_code = generate_verification_code()
send_sms(phone_numbers, verification_code)

# print(f"Verification code sent! Response: {response}")

# attributes = sns.get_sms_attributes()
# print(f"Attributes: {attributes}")

while True:
    verCode = input("Enter the code you received: ")
    if verification_code == verCode:
        print("The Verification Code is matched!")
        break
    else:
        print("Incorrect Verification Code! \nPlease try again.")
