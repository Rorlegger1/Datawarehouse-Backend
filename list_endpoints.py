from cordel_api_client import CordelAPIClient
import requests

def main():
    client = CordelAPIClient()
    
    # Try to get API documentation or available endpoints
    try:
        # Try swagger/OpenAPI documentation
        endpoints = [
            "swagger/v1/swagger.json",
            "api/swagger/v1/swagger.json",
            "api-docs",
            "api/api-docs",
            "swagger",
            "api/swagger"
        ]
        
        for endpoint in endpoints:
            try:
                print(f"\nTrying to get API documentation from: {endpoint}")
                response = requests.get(
                    f"{client.base_url}/{endpoint}",
                    headers=client._get_headers()
                )
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    print("Content:", response.text[:500])
                    break
            except Exception as e:
                print(f"Error: {str(e)}")
                continue
                
        # Try to list available endpoints by making OPTIONS request
        print("\nTrying OPTIONS request to get available methods:")
        response = requests.options(
            f"{client.base_url}/api",
            headers=client._get_headers()
        )
        print(f"Status: {response.status_code}")
        print("Headers:", response.headers)
        if response.status_code == 200:
            print("Content:", response.text[:500])
            
    except Exception as e:
        print(f"Error getting API documentation: {str(e)}")

if __name__ == "__main__":
    main() 