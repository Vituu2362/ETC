import requests
import json

# API endpoint
api_url = 'https://gateway.donedealonline.com/mobile-money/v1/collect'

# Data to be sent in the request
data = {
    'api_key': 'your-apiKey',  # Replace with your actual API key
    'reference': 'Transaction description',
    'msisdn': '980057498',  # Airtel Malawi phone number (without +265 or 0)
    'amount': '50.00',  # Transaction amount
    'currency': 'MWK',
    'mno': 'AIRTEL_MWI',
    'unique_id': 'unique-Id',  # Optional
    'email': 'vituluthersibale@gmail.com',  # Optional
    'name': 'Vitumbiko Sibale',  # Optional
    'collections_app_id': '15',  # Optional
}

# Set headers
headers = {
    'Content-Type': 'application/json',
}

# Send POST request
try:
    response = requests.post(api_url, data=json.dumps(data), headers=headers)
    
    # Check for errors
    if response.status_code == 200:
        print("Response:", response.json())
    else:
        print("Error:", response.status_code, response.text)
        
except requests.exceptions.RequestException as e:
    print(f"Request error: {e}")