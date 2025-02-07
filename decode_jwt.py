import requests
import json
import base64

def decode_jwt(token):
    # Split the token into header, payload, and signature
    parts = token.split('.')
    if len(parts) != 3:
        return "Invalid JWT token format"
    
    # Decode header and payload
    try:
        header = json.loads(base64.urlsafe_b64decode(parts[0] + '=' * (4 - len(parts[0]) % 4)).decode('utf-8'))
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + '=' * (4 - len(parts[1]) % 4)).decode('utf-8'))
        
        print("\nJWT Header:")
        print(json.dumps(header, indent=2))
        print("\nJWT Payload:")
        print(json.dumps(payload, indent=2))
        
        # Look for any URLs or endpoints in the payload
        print("\nAnalyzing payload for API hints...")
        for key, value in payload.items():
            if isinstance(value, str):
                if any(x in value.lower() for x in ['http', 'api', 'endpoint', 'url', '/']):
                    print(f"\nPotential API hint in {key}:")
                    print(value)
        
        return header, payload
    except Exception as e:
        return f"Error decoding token: {str(e)}"

def main():
    print("Starting JWT token analysis...")
    
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
        decode_jwt(token)

if __name__ == "__main__":
    main() 