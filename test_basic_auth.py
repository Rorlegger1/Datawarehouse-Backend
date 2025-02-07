from cordel_api_client import CordelAPIClient
import requests
import json
import base64

def main():
    print("Starting Basic Auth test...")
    
    # Initialize client
    client = CordelAPIClient()
    
    # Credentials
    username = "datavarehus.integrasjon@ror-system.no"
    password = "qA02bRux!3eD"
    
    # Create Basic auth header
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    basic_auth_headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Accept': 'application/json'
    }
    
    # Get Bearer token headers
    bearer_headers = client._get_headers()
    
    # Endpoints to try
    endpoints = [
        "/swagger",
        "/swagger/",
        "/swagger/v1",
        "/swagger/v2",
        "/swagger/index.html",
        "/api/swagger",
        "/api/swagger/",
        "/api/swagger/v1",
        "/api/swagger/v2",
        "/api/swagger/index.html",
        "/c/swagger",
        "/c/swagger/",
        "/c/swagger/v1",
        "/c/swagger/v2",
        "/c/swagger/index.html"
    ]
    
    # Try with both Basic and Bearer auth
    auth_headers = [
        ("Basic Auth", basic_auth_headers),
        ("Bearer Auth", bearer_headers),
        ("Combined Auth", {**basic_auth_headers, **bearer_headers}),
        ("No Auth", {})
    ]
    
    for endpoint in endpoints:
        for auth_name, headers in auth_headers:
            try:
                print(f"\nTrying endpoint: {endpoint}")
                print(f"Using: {auth_name}")
                
                url = f"{client.base_url}{endpoint}"
                response = requests.get(
                    url,
                    headers=headers,
                    verify=True  # Enable SSL verification
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