import requests
import json
import base64

def decode_jwt(token):
    # Split the token into parts
    parts = token.split('.')
    if len(parts) != 3:
        return None
    
    # Decode the payload (second part)
    try:
        # Add padding if needed
        padding = len(parts[1]) % 4
        if padding:
            parts[1] += '=' * (4 - padding)
            
        payload = base64.b64decode(parts[1])
        return json.loads(payload)
    except Exception as e:
        print(f"Error decoding token: {str(e)}")
        return None

def main():
    print("Starting JWT token analysis (v10)...")
    
    # Auth details
    tenant_id = "3744c6ca-4149-4627-8e8f-ac95fb793b4e"
    
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
        print("\nDecoding JWT token...")
        
        # Decode and analyze token
        payload = decode_jwt(token)
        if payload:
            print("\nToken payload:")
            print(json.dumps(payload, indent=2))
            
            # Look for potential API hints
            print("\nAnalyzing payload for API hints...")
            
            # Check for URLs
            for key, value in payload.items():
                if isinstance(value, str):
                    if "http" in value.lower() or "api" in value.lower():
                        print(f"Potential API URL in {key}: {value}")
            
            # Check for module information
            if "modules" in payload:
                print(f"\nModule information found: {payload['modules']}")
            
            # Check for scope information
            if "scope" in payload:
                print(f"\nScope information found: {payload['scope']}")
            
            # Check for any other interesting fields
            interesting_keys = ["aud", "iss", "sub", "tenant", "permissions"]
            for key in interesting_keys:
                if key in payload:
                    print(f"\n{key.upper()} found: {payload[key]}")
            
            # Try to construct API patterns from token information
            print("\nConstructing potential API patterns from token info...")
            patterns = []
            
            if "iss" in payload:
                base = payload["iss"].rstrip("/")
                patterns.append(f"{base}/api/v1")
                patterns.append(f"{base}/api/v2")
            
            if "tenant" in payload:
                tenant = payload["tenant"]
                patterns.append(f"/tenants/{tenant}/api")
                patterns.append(f"/t/{tenant}/api")
            
            if patterns:
                print("\nPotential API patterns to try:")
                for pattern in patterns:
                    print(f"- {pattern}")

if __name__ == "__main__":
    main() 