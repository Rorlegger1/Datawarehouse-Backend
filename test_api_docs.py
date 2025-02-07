from cordel_api_client import CordelAPIClient
import requests
import json
import base64

def main():
    print("Starting API documentation test with Basic auth...")
    
    # Credentials for Basic auth
    username = "datavarehus.integrasjon@ror-system.no"
    password = "qA02bRux!3eD"
    
    # Create Basic auth header
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    basic_headers = {
        'Authorization': f'Basic {encoded_credentials}'
    }

    # Create Bearer auth header from previous successful auth
    bearer_headers = {
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'  # Add your token here
    }

    # Try both auth methods and no auth
    auth_methods = [
        ('Basic Auth', basic_headers),
        ('Bearer Auth', bearer_headers),
        ('Combined Auth', {**basic_headers, **bearer_headers}),
        ('No Auth', {})
    ]

    base_url = "https://api.smartcraft.cloud"
    endpoint = "/swagger"

    for auth_name, headers in auth_methods:
        print(f"\nTrying {auth_name} for {endpoint}")
        try:
            response = requests.get(f"{base_url}{endpoint}", headers=headers)
            print(f"Status Code: {response.status_code}")
            print("Response Headers:", response.headers)
            if response.status_code == 200:
                print("Response Content:", response.text[:500])  # First 500 chars
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 