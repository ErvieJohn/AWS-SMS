import boto3
import random
import time
from datetime import datetime
import pytz
from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify

load_dotenv()

app = Flask(__name__)

# Initialize SNS client
ACCESS_KEY_ID=os.getenv("AWS_ACCESS_KEY_ID")
SECRET_ACCESS_KEY=os.getenv("AWS_SECRET_ACCESS_KEY")
REGION_NAME=os.getenv("AWS_REGION")
SENDER_ID=os.getenv("AWS_SENDER_ID")

# Initialize the client for STS
sns_client = boto3.client('sns', 
    aws_access_key_id=ACCESS_KEY_ID,
    aws_secret_access_key=SECRET_ACCESS_KEY,
    region_name=REGION_NAME)

# response = sns_client.get_session_token(DurationSeconds=43200)  # 12 hours max duration
# CREDENTIALS = response['Credentials']

# In-memory store for verification codes (use a database in production)
verification_store = {}

# Generate and send verification code
@app.route('/send-code', methods=['POST'])
def send_code():
    data = request.json
    phone_number = data.get('phone_number')
    
    if not phone_number:
        return jsonify({"error": "Phone number is required"}), 400

    # Generate a 6-digit verification code
    code = random.randint(100000, 999999)
    verification_store[phone_number] = {"code": code, "expires_at": time.time() + 300}  # Expire in 5 mins

    # Send SMS via AWS SNS
    try:
        sns_client.publish(
            PhoneNumber=phone_number,
            Message=f"Your verification code is {code}.\nCode will expire in 5 minutes.",
            MessageAttributes={
                'AWS.SNS.SMS.SenderID': {
                    'DataType': 'String',
                    'StringValue': SENDER_ID
                }
            }
        )
        return jsonify({"message": "Verification code sent!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Verify code
@app.route('/verify-code', methods=['POST'])
def verify_code():
    data = request.json
    phone_number = data.get('phone_number')
    user_code = data.get('code')

    if not phone_number or not user_code:
        return jsonify({"error": "Phone number and code are required"}), 400

    record = verification_store.get(phone_number)
    if record and record['expires_at'] > time.time():
        if record['code'] == int(user_code):
            return jsonify({"message": "Phone verified!"}), 200
        else:
            return jsonify({"error": "Invalid code"}), 400
    else:
        return jsonify({"error": "Code expired or not found"}), 400

if __name__ == '__main__':
    app.run(debug=True)
    

    
