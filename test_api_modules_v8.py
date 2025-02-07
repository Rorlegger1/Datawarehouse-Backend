import requests
import json

def main():
    print("Starting module-specific API test (v8)...")
    
    # Auth details
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
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-CustomHeader': 'true',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        base_url = "https://api.smartcraft.cloud"
        
        # Test patterns based on working client patterns
        endpoint_patterns = [
            # Direct module patterns from client code
            "/api/v1/module/{module}/timeregistration",
            "/api/v1/{module}/timeregistration",
            "/api/v1/module/{module}/time",
            "/api/v1/{module}/time",
            
            # With tenant patterns
            "/api/v1/module/{module}/timeregistration?tenantId={tenant}",
            "/api/v1/{module}/timeregistration?tenantId={tenant}",
            "/api/v1/module/{module}/time?tenantId={tenant}",
            "/api/v1/{module}/time?tenantId={tenant}",
            
            # Alternative version patterns
            "/api/v2/module/{module}/timeregistration",
            "/api/v2/{module}/timeregistration",
            "/api/v2/module/{module}/time",
            "/api/v2/{module}/time",
            
            # With additional parameters
            "/api/v1/module/{module}/timeregistration?pageSize=100&pageNumber=0",
            "/api/v1/{module}/timeregistration?pageSize=100&pageNumber=0",
            "/api/v2/module/{module}/timeregistration?pageSize=100&pageNumber=0",
            "/api/v2/{module}/timeregistration?pageSize=100&pageNumber=0"
        ]
        
        # First try OPTIONS request
        for module in modules:
            print(f"\nTesting OPTIONS for module {module}...")
            
            for pattern in endpoint_patterns:
                endpoint = pattern.format(tenant=tenant_id, module=module)
                print(f"\nTrying OPTIONS on endpoint: {endpoint}")
                
                try:
                    response = requests.options(
                        f"{base_url}{endpoint}",
                        headers=headers
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
        for module in modules:
            print(f"\nTesting GET for module {module}...")
            
            for pattern in endpoint_patterns:
                endpoint = pattern.format(tenant=tenant_id, module=module)
                print(f"\nTrying GET on endpoint: {endpoint}")
                
                try:
                    response = requests.get(
                        f"{base_url}{endpoint}",
                        headers=headers
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