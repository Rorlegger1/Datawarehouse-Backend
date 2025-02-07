import requests
import json

def main():
    print("Starting module-specific API test (v13)...")
    
    # Auth details
    tenant_id = "3744c6ca-4149-4627-8e8f-ac95fb793b4e"
    modules = ["90000", "93000"]
    
    # Get auth token from smartcraft
    auth_url = "https://api.smartcraft.cloud/auth"
    auth_data = {
        "username": "datavarehus.integrasjon@ror-system.no",
        "password": "qA02bRux!3eD",
        "tenantId": tenant_id
    }
    
    print("\nAttempting authentication...")
    auth_response = requests.post(auth_url, json=auth_data)
    print(f"Auth Status Code: {auth_response.status_code}")
    
    if auth_response.status_code == 200:
        token = auth_response.json()["authToken"]
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-CustomHeader': 'true',
            'X-Requested-With': 'XMLHttpRequest',
            'If-Modified-Since': 'Mon, 26 Jul 1997 05:00:00 GMT',
            'Cache-Control': 'no-cache'
        }
        
        base_url = "https://api.smartcraft.cloud"
        
        # Base endpoints to try with Cordel3 patterns
        base_endpoints = [
            "/cordel3/api/v1/module/{module}/timeregistration",
            "/cordel3/api/v2/module/{module}/timeregistration",
            "/cordel3/api/module/{module}/timeregistration",
            "/cordel3/module/{module}/timeregistration",
            "/api/cordel3/v1/module/{module}/timeregistration",
            "/api/cordel3/v2/module/{module}/timeregistration",
            "/api/v1/cordel3/module/{module}/timeregistration",
            "/api/v2/cordel3/module/{module}/timeregistration"
        ]
        
        # Parameter combinations to try
        param_combinations = [
            {"tenantId": tenant_id},
            {"cordel3_tenantId": tenant_id},
            {"cordel3_module": "{module}"},
            {}  # Try without tenant ID since it might be in the token
        ]
        
        # First try OPTIONS request
        print(f"\nTesting with base URL: {base_url}")
        
        for endpoint in base_endpoints:
            for module in modules:
                current_endpoint = endpoint.format(module=module)
                print(f"\nTesting OPTIONS for endpoint: {current_endpoint}")
                
                for params in param_combinations:
                    # Replace any {module} in params
                    current_params = {k: v.format(module=module) if isinstance(v, str) else v for k, v in params.items()}
                    print(f"\nTrying with parameters: {current_params}")
                    
                    try:
                        response = requests.options(
                            f"{base_url}{current_endpoint}",
                            headers=headers,
                            params=current_params
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
        
        # Then try GET requests
        for endpoint in base_endpoints:
            for module in modules:
                current_endpoint = endpoint.format(module=module)
                print(f"\nTesting GET for endpoint: {current_endpoint}")
                
                for params in param_combinations:
                    # Replace any {module} in params
                    current_params = {k: v.format(module=module) if isinstance(v, str) else v for k, v in params.items()}
                    print(f"\nTrying with parameters: {current_params}")
                    
                    try:
                        response = requests.get(
                            f"{base_url}{current_endpoint}",
                            headers=headers,
                            params=current_params
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