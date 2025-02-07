from cordel_api_client import CordelAPIClient
import requests
import json

def main():
    print("Starting modules test...")
    
    # Initialize client
    client = CordelAPIClient()
    
    # Get auth token
    auth_headers = client._get_headers()
    
    # Different module-related endpoints to try
    endpoints = [
        "/c/api/modules",
        "/c/api/v1/modules",
        "/c/api/v2/modules",
        "/c/modules",
        "/c/90000",
        "/c/93000",
        "/c/90000/api",
        "/c/93000/api",
        "/c/api/90000",
        "/c/api/93000",
        "/c/api/v1/90000",
        "/c/api/v1/93000",
        "/c/api/v2/90000",
        "/c/api/v2/93000",
        "/api/modules",
        "/api/v1/modules",
        "/api/v2/modules",
        "/modules",
        "/90000",
        "/93000",
        "/90000/api",
        "/93000/api",
        "/api/90000",
        "/api/93000",
        "/api/v1/90000",
        "/api/v1/93000",
        "/api/v2/90000",
        "/api/v2/93000"
    ]
    
    # Different parameter combinations
    params_list = [
        {"tenantId": client.tenant_id},
        {"moduleId": "90000"},
        {"moduleId": "93000"},
        {"tenantId": client.tenant_id, "moduleId": "90000"},
        {"tenantId": client.tenant_id, "moduleId": "93000"},
        {}
    ]
    
    for endpoint in endpoints:
        for params in params_list:
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
                
                if response.status_code == 200:
                    print("Success! Found working endpoint!")
                    print(f"Working URL: {response.url}")
                    try:
                        data = response.json()
                        print("Response structure:", json.dumps(data, indent=2)[:500])
                    except:
                        print("Response (text):", response.text[:500])
                    
            except Exception as e:
                print(f"Error: {str(e)}")
                continue

if __name__ == "__main__":
    main() 