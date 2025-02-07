import requests
import json

def main():
    print("Starting module-specific API test (v11)...")
    
    # Auth details
    tenant_id = "3744c6ca-4149-4627-8e8f-ac95fb793b4e"
    modules = ["90000", "93000"]
    
    # Get auth token
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
            'Accept': 'application/json'
        }
        
        base_url = "https://api.smartcraft.cloud"
        
        # Base endpoints to try with cordel3_ prefix
        base_endpoints = [
            "/api/v1/cordel3/timeregistration",
            "/api/v2/cordel3/timeregistration",
            "/cordel3/api/timeregistration",
            "/cordel3/timeregistration"
        ]
        
        # Parameter combinations to try with cordel3_ prefix
        param_combinations = [
            {"cordel3_tenantId": tenant_id, "cordel3_moduleId": "90000"},
            {"cordel3_tenantId": tenant_id, "cordel3_moduleId": "93000"},
            {"cordel3_tenant": tenant_id, "cordel3_module": "90000"},
            {"cordel3_tenant": tenant_id, "cordel3_module": "93000"},
            # Try without cordel3_ prefix as well
            {"tenantId": tenant_id, "moduleId": "90000"},
            {"tenantId": tenant_id, "moduleId": "93000"}
        ]
        
        # First try OPTIONS request
        for endpoint in base_endpoints:
            print(f"\nTesting OPTIONS for endpoint: {endpoint}")
            
            for params in param_combinations:
                print(f"\nTrying with parameters: {params}")
                
                try:
                    response = requests.options(
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
        
        # Then try GET requests
        for endpoint in base_endpoints:
            print(f"\nTesting GET for endpoint: {endpoint}")
            
            for params in param_combinations:
                print(f"\nTrying with parameters: {params}")
                
                try:
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