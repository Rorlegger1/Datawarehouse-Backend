from cordel_api_client import CordelAPIClient
import requests
import json

def main():
    print("Starting API test...")
    
    # Initialize client
    client = CordelAPIClient()
    
    print("\nTesting direct authentication...")
    try:
        # Try direct authentication request without tenant ID
        auth_data = {
            "username": client.username,
            "password": client.password
        }
        
        print("Auth request data:", json.dumps(auth_data, indent=2))
        
        # Try different auth endpoints
        auth_endpoints = [
            "/auth",
            "/api/auth",
            "/api/v1/auth",
            "/datawarehouse/auth"
        ]
        
        for auth_endpoint in auth_endpoints:
            print(f"\nTrying auth endpoint: {auth_endpoint}")
            try:
                auth_response = requests.post(
                    f"{client.base_url}{auth_endpoint}",
                    json=auth_data,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"Auth Status Code: {auth_response.status_code}")
                print(f"Auth Response Headers: {dict(auth_response.headers)}")
                print(f"Auth Response: {auth_response.text[:500]}")
                
                if auth_response.status_code == 200:
                    auth_token = auth_response.json().get("authToken")
                    print("\nTesting endpoint with auth token...")
                    
                    # Try to get time registrations
                    headers = {
                        "Authorization": f"Bearer {auth_token}",
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    }
                    
                    # Try different API endpoints
                    api_endpoints = [
                        "/timeregistration",
                        "/api/timeregistration",
                        "/api/v1/timeregistration",
                        "/datawarehouse/timeregistration"
                    ]
                    
                    for api_endpoint in api_endpoints:
                        print(f"\nTrying API endpoint: {api_endpoint}")
                        try:
                            response = requests.get(
                                f"{client.base_url}{api_endpoint}",
                                headers=headers,
                                params={
                                    "pageSize": 50,
                                    "pageNumber": 0
                                }
                            )
                            
                            print(f"Endpoint Status Code: {response.status_code}")
                            print(f"Endpoint Response Headers: {dict(response.headers)}")
                            print(f"Endpoint Response: {response.text[:500]}")
                            
                        except Exception as e:
                            print(f"API endpoint error: {str(e)}")
                            continue
                    
            except Exception as e:
                print(f"Auth endpoint error: {str(e)}")
                continue
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 