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
        # Module-based endpoints
        "/api/2.0/module/90000/timeregistration",
        "/api/2.0/module/93000/timeregistration",
        "/api/1.0/module/90000/timeregistration",
        "/api/1.0/module/93000/timeregistration",
        
        # Tenant-based endpoints
        f"/api/2.0/tenant/{client.tenant_id}/timeregistration",
        f"/api/1.0/tenant/{client.tenant_id}/timeregistration",
        
        # Direct endpoints with tenant in query
        "/api/2.0/timeregistration",
        "/api/1.0/timeregistration",
        
        # Alternative paths
        "/api/2.0/time",
        "/api/2.0/hours",
        "/api/2.0/projects/hours",
        "/api/2.0/projects/time"
    ]
    
    # Different parameter combinations
    param_variations = [
        {"tenantId": client.tenant_id},
        {"tenant": client.tenant_id},
        {"tenantid": client.tenant_id},
        {"tenant_id": client.tenant_id},
        {}  # Try without tenant ID in params
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