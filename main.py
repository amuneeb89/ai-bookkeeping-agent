import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
import hmac
import hashlib
import base64

load_dotenv()

app = Flask(__name__)

LEMON_WEBHOOK_SECRET = os.getenv("LEMON_WEBHOOK_SECRET")
LEMON_API_KEY = os.getenv("LEMON_API_KEY")

@app.route('/')
def home():
    return "LemonSqueezy Webhook is live!"

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    sig = request.headers.get('X-Signature')
    payload = request.data

    expected_sig = base64.b64encode(
        hmac.new(
            LEMON_WEBHOOK_SECRET.encode(),
            payload,
            hashlib.sha256
        ).digest()
    ).decode()

    if sig != expected_sig:
        return jsonify({'error': 'Invalid signature'}), 400

    data = request.json
    print("Webhook received:", data)

    # Example: Handle subscription_created or license_validated
    event_type = data.get('meta', {}).get('event_name', '')
    if event_type == "order_created":
        # Handle your logic (e.g., provisioning access, sending email, etc.)
        print("New order received!")
    
    return jsonify({'status': 'success'}), 200

@app.route('/validate-license', methods=['POST'])
def validate_license():
    license_key = request.json.get('license_key')

    response = requests.post(
        'https://api.lemonsqueezy.com/v1/licenses/validate',
        headers={
            "Authorization": f"Bearer {LEMON_API_KEY}",
            "Accept": "application/vnd.api+json"
        },
        json={"license_key": license_key}
    )

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'License validation failed'}), 400

if __name__ == '__main__':
    app.run(debug=True)
