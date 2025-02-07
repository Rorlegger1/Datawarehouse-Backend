import requests
import json
from datetime import datetime, timedelta
import pandas as pd

def main():
    print("Testing DataWarehouse API Time Registration Endpoints...")
    
    # Authentication details
    username = "datavarehus.integrasjon@ror-system.no"
    password = "qA02bRux!3eD"
    
    # First authenticate
    print("\nAttempting authentication...")
    auth_response = requests.post(
        "https://api.smartcraft.cloud/auth",
        json={
            "username": username,
            "password": password
        },
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Auth Status Code: {auth_response.status_code}")
    
    if auth_response.status_code == 200:
        auth_token = auth_response.json().get("authToken")
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Base URL for DataWarehouse API
        base_url = "https://api.smartcraft.cloud/DataWarehouse"
        
        # Test endpoints
        endpoints = [
            {
                "url": "/api/Projects",
                "description": "Get all projects with time registrations",
                "params": {
                    "pageSize": 50,
                    "pageNumber": 0
                }
            },
            {
                "url": "/api/Projects/1000",
                "description": "Get specific project time registrations",
                "params": {}
            },
            {
                "url": "/api/Employees",
                "description": "Get employee information",
                "params": {
                    "pageSize": 50,
                    "pageNumber": 0
                }
            }
        ]
        
        print("\nTesting endpoints...")
        
        for endpoint in endpoints:
            url = f"{base_url}{endpoint['url']}"
            print(f"\nTesting: {endpoint['description']}")
            print(f"URL: {url}")
            
            try:
                # Try GET request
                response = requests.get(
                    url,
                    headers=headers,
                    params=endpoint["params"]
                )
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if "payload" in data:
                        items = data["payload"]
                        if isinstance(items, list):
                            print(f"Found {len(items)} items")
                            if items:
                                # For projects, look for time registrations
                                if "Projects" in endpoint["url"]:
                                    for item in items:
                                        if "usedWork" in item and item["usedWork"]:
                                            print(f"\nProject {item.get('projectNumber')}: {item.get('projectName')}")
                                            work_data = pd.DataFrame(item["usedWork"])
                                            if not work_data.empty:
                                                print("\nTime Registration Summary:")
                                                print(f"Total Hours: {work_data['quantity'].sum():.2f}")
                                                print(f"Total Cost: {work_data['cost'].sum():.2f}")
                                                print("\nBy Employee:")
                                                employee_summary = work_data.groupby('employeeName').agg({
                                                    'quantity': 'sum',
                                                    'cost': 'sum'
                                                }).reset_index()
                                                print(employee_summary)
                                # For employees, show basic info
                                elif "Employees" in endpoint["url"]:
                                    print("\nEmployee Information:")
                                    for item in items[:5]:  # Show first 5 employees
                                        print(f"- {item.get('employeeNumber')}: {item.get('employeeName')}")
                        else:
                            print("Single item response:", json.dumps(items, indent=2)[:500])
                else:
                    print("Response:", response.text[:200])
                    
            except Exception as e:
                print(f"Error: {str(e)}")
                continue

if __name__ == "__main__":
    main() 