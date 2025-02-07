from cordel_api_client import CordelAPIClient
import requests
import json

def main():
    print("Starting API test...")
    
    # Initialize client
    client = CordelAPIClient()
    
    print("\nTesting API endpoints...")
    
    # Get auth token
    auth_headers = client._get_headers()
    
    # Different endpoint patterns to try
    endpoint_patterns = [
        # Module 90000 endpoints
        "/90000/api/timeregistration",
        "/90000/api/v1/timeregistration",
        "/90000/api/v2/timeregistration",
        "/90000/timeregistration",
        "/api/90000/timeregistration",
        
        # Module 93000 endpoints
        "/93000/api/timeregistration",
        "/93000/api/v1/timeregistration",
        "/93000/api/v2/timeregistration",
        "/93000/timeregistration",
        "/api/93000/timeregistration",
        
        # Alternative paths with modules
        "/api/v1/90000/timeregistration",
        "/api/v1/93000/timeregistration",
        "/api/v2/90000/timeregistration",
        "/api/v2/93000/timeregistration",
        
        # Try with 'c' prefix from issuer URL
        "/c/api/v1/90000/timeregistration",
        "/c/api/v1/93000/timeregistration",
        "/c/api/v2/90000/timeregistration",
        "/c/api/v2/93000/timeregistration"
    ]
    
    # Different parameter combinations
    param_variations = [
        {"tenantId": client.tenant_id},
        {"moduleId": "90000"},
        {"moduleId": "93000"},
        {"tenantId": client.tenant_id, "moduleId": "90000"},
        {"tenantId": client.tenant_id, "moduleId": "93000"},
        {}
    ]
    
    for endpoint in endpoint_patterns:
        for params in param_variations:
            try:
                print(f"\nTrying endpoint: {endpoint}")
                print(f"With params: {params}")
                
                url = f"{client.base_url}{endpoint}"
                response = requests.get(
                    url,
                    headers=auth_headers,
                    params=params
                )
                
                print(f"Status Code: {response.status_code}")
                print(f"Response Headers: {dict(response.headers)}")
                print(f"Response: {response.text[:200]}")
                
                if response.status_code == 200:
                    print("Success! Found working endpoint!")
                    print(f"Working URL: {response.url}")
                    try:
                        data = response.json()
                        print("Response structure:", json.dumps(data, indent=2)[:500])
                    except:
                        print("Could not parse response as JSON")
                    
            except Exception as e:
                print(f"Error: {str(e)}")
                continue

if __name__ == "__main__":
    main() 