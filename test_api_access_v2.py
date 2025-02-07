from cordel_api_client import CordelAPIClient
import requests

def main():
    # Initialize client
    client = CordelAPIClient()
    
    print("\nTesting API structure variations...")
    
    # Different base URL structures to try
    base_variations = [
        f"{client.base_url}",  # Current structure
        f"{client.base_url}/companies",  # Try companies endpoint
        f"{client.base_url}/tenants",    # Try tenants endpoint
        "https://api.smartcraft.cloud/companies",  # Try without version
        "https://api.smartcraft.cloud/tenants"     # Try without version
    ]
    
    for base in base_variations:
        try:
            print(f"\nTesting base URL: {base}")
            response = requests.get(
                base,
                headers=client._get_headers()
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
            if response.status_code == 200:
                print("Success! Found valid endpoint")
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"Found {len(data)} items")
                        if len(data) > 0:
                            print("First item structure:", list(data[0].keys()))
                    elif isinstance(data, dict):
                        print("Response structure:", list(data.keys()))
                except Exception as e:
                    print(f"Could not parse JSON: {str(e)}")
                    
        except Exception as e:
            print(f"Error: {str(e)}")
    
    print("\nTesting with API key in header...")
    # Try with API key in header instead of Basic Auth
    try:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-API-Key': client._get_basic_auth_token()  # Try using the token as API key
        }
        
        response = requests.get(
            "https://api.smartcraft.cloud/v1/companies",
            headers=headers
        )
        print(f"Status with API key: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
    except Exception as e:
        print(f"API key test error: {str(e)}")

if __name__ == "__main__":
    main() 