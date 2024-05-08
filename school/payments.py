import requests
from decouple import config

def flutterwave_verify_transaction(transaction_id):
    # Replace 'YOUR_API_KEY' with your actual Flutterwave API key
    API_KEY = config('FW_PUBLIC_KEY')
    VERIFY_URL = f'https://api.flutterwave.com/v3/transactions/{transaction_id}/verify'
    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(VERIFY_URL, headers=headers)
        response.raise_for_status()  # Raise an exception for any HTTP errors
        return response
    except requests.RequestException as e:
        # Handle request errors
        print(f"Error while verifying transaction: {e}")
        return None