from cordel_api_client import CordelAPIClient
import requests

def main():
    # Initialize client
    client = CordelAPIClient()
    
    print("\nTesting basic endpoints...")
    
    # List of basic endpoints to test from the API rules
    endpoints = [
        "customers",
        "offers",
        "orders",
        "products",
        "invoices",
        "timeregistration"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\nTesting endpoint: {endpoint}")
            response = requests.get(
                f"{client.base_url}/{endpoint}",
                headers=client._get_headers()
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
        except Exception as e:
            print(f"Error: {str(e)}")
    
    print("\nTesting authentication...")
    # Try to get authentication details
    try:
        auth_headers = client._get_headers()
        print(f"Auth headers being used: {auth_headers}")
        
        # Try a test request with auth
        response = requests.get(
            f"{client.base_url}/customers",  # Try customers as it's usually a basic endpoint
            headers=auth_headers
        )
        print(f"\nAuth test response status: {response.status_code}")
        if response.status_code == 401:
            print("Authentication failed - Unauthorized")
        elif response.status_code == 403:
            print("Authentication succeeded but access forbidden - Permission issue")
        elif response.status_code == 404:
            print("Endpoint not found - Might be incorrect API structure")
        else:
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"Auth test error: {str(e)}")

if __name__ == "__main__":
    main() 