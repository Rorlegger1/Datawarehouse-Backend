import requests
import json

def main():
    print("Starting DataWarehouse API test...")
    
    # Authentication details
    username = "datavarehus.integrasjon@ror-system.no"
    password = "qA02bRux!3eD"
    tenant_id = "3744c6ca-4149-4627-8e8f-ac95fb793b4e"
    
    # First authenticate
    print("\nAttempting authentication...")
    auth_response = requests.post(
        "https://api.smartcraft.cloud/auth",
        json={
            "username": username,
            "password": password,
            "tenantId": tenant_id
        },
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Auth Status Code: {auth_response.status_code}")
    
    if auth_response.status_code != 200:
        print("Authentication failed")
        return
        
    auth_token = auth_response.json().get("authToken")
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "DataWarehouse-API-Test/1.0"  # Required according to docs
    }
    
    # Base URL for DataWarehouse API
    base_url = "https://api.smartcraft.cloud/DataWarehouse"
    
    # Test endpoints
    endpoints = [
        "/api/TimeRegistrations",
        "/api/Projects",
        "/api/Orders",
        "/api/Customers",
        "/api/Invoices"
    ]
    
    # Parameters to try
    params = {
        "pageSize": 50,
        "pageNumber": 0
    }
    
    print("\nTesting DataWarehouse API endpoints...")
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\nTesting endpoint: {url}")
        
        try:
            # Try OPTIONS first
            options_response = requests.options(url, headers=headers)
            print(f"OPTIONS Status Code: {options_response.status_code}")
            print("OPTIONS Headers:", options_response.headers)
            
            # Then try GET
            get_response = requests.get(url, headers=headers, params=params)
            print(f"GET Status Code: {get_response.status_code}")
            
            if get_response.status_code == 200:
                data = get_response.json()
                print("Success! First 100 chars of response:", str(data)[:100])
            else:
                print("GET Headers:", get_response.headers)
                print("GET Response:", get_response.text[:200])
                
        except Exception as e:
            print(f"Error: {str(e)}")
            continue

if __name__ == "__main__":
    main() 