# payments/utils.py
app_name = 'payments'

import requests

from server.settings.base import TOSS_API_SECRET_BASE64

def create_billing_key(auth_key, customer_key):
    url = "https://api.tosspayments.com/v1/billing/authorizations/issue"
    
    # TOSS_API_SECRET should be the base64 encoded value from curl
    headers = {
        'Authorization': f'Basic {TOSS_API_SECRET_BASE64}',
        'Content-Type': 'application/json'
    }
    data = {
        "authKey": auth_key,
        "customerKey": customer_key
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        response_data = response.json()
        if 'error' in response_data:
            error_code = response_data.get('error', {}).get('code', 'UNKNOWN')
            error_message = response_data.get('error', {}).get('message', 'Unknown error')
            raise ValueError(f"Toss Payments API error: {error_code} - {error_message}")

        return response_data.get('billingKey')
        
    except requests.exceptions.RequestException as e:
        raise requests.RequestException(f"Failed to create billing key: {str(e)}")

    except ValueError as e:
        raise e

    except Exception as e:
        raise Exception(f"Unexpected error creating billing key: {str(e)}")