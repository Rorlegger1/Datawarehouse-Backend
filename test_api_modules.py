import requests
import json

def main():
    print("Starting module-specific API test...")
    
    # Auth details from successful token
    tenant_id = "3744c6ca-4149-4627-8e8f-ac95fb793b4e"
    modules = ["90000", "93000"]
    
    # Get auth token
    auth_url = "https://api.smartcraft.cloud/auth"
    auth_data = {
        "username": "datavarehus.integrasjon@ror-system.no",
        "password": "qA02bRux!3eD"
    }
    
    print("\nAttempting authentication...")
    auth_response = requests.post(auth_url, json=auth_data)
    print(f"Auth Status Code: {auth_response.status_code}")
    
    if auth_response.status_code == 200:
        token = auth_response.json()["authToken"]
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        base_url = "https://api.smartcraft.cloud"
        
        # Test patterns for each module
        endpoint_patterns = [
            "/c/{module}/api/timeregistration",
            "/c/api/{module}/timeregistration",
            "/api/v1/module/{module}/timeregistration",
            "/api/v1/{module}/timeregistration",
            "/api/v2/module/{module}/timeregistration",
            "/api/v2/{module}/timeregistration",
            "/datawarehouse/{module}/timeregistration",
            "/datawarehouse/api/{module}/timeregistration"
        ]
        
        # Parameters to try
        param_combinations = [
            {'tenantId': tenant_id},
            {'moduleId': '90000'},
            {'moduleId': '93000'},
            {'tenantId': tenant_id, 'moduleId': '90000'},
            {'tenantId': tenant_id, 'moduleId': '93000'},
            {}  # No parameters
        ]
        
        for module in modules:
            print(f"\nTesting endpoints for module {module}...")
            
            for pattern in endpoint_patterns:
                endpoint = pattern.format(module=module)
                print(f"\nTrying endpoint: {endpoint}")
                
                for params in param_combinations:
                    try:
                        print(f"\nWith parameters: {params}")
                        response = requests.get(
                            f"{base_url}{endpoint}",
                            headers=headers,
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