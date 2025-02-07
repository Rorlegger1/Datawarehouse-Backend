import requests
import json
from datetime import datetime, timedelta

def main():
    print("Starting DataWarehouse API test for time registrations...")
    
    # Authentication details
    username = "datavarehus.integrasjon@ror-system.no"
    password = "qA02bRux!3eD"
    tenant_id = "3744c6ca-4149-4627-8e8f-ac95fb793b4e"
    
    # First authenticate
    print("\nAttempting authentication...")
    auth_response = requests.post(
        "https://api.smartcraft.cloud/auth",
        json={
            "username": username,
            "password": password,
            "tenantId": tenant_id
        },
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Auth Status Code: {auth_response.status_code}")
    
    if auth_response.status_code != 200:
        print("Authentication failed")
        return
        
    auth_token = auth_response.json().get("authToken")
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Base URL for DataWarehouse API
    base_url = "https://api.smartcraft.cloud/DataWarehouse"
    
    # Get all projects first
    projects_url = f"{base_url}/api/Projects"
    print(f"\nFetching projects from: {projects_url}")
    
    try:
        projects_response = requests.get(
            projects_url,
            headers=headers,
            params={
                "pageSize": 50,
                "pageNumber": 0,
                "submittedAfter": (datetime.utcnow() - timedelta(days=30)).isoformat()
            }
        )
        
        if projects_response.status_code == 200:
            projects_data = projects_response.json()
            if "payload" in projects_data:
                projects = projects_data["payload"]
                print(f"\nFound {len(projects)} projects")
                
                # Process each project
                for project in projects:
                    project_number = project.get("projectNumber")
                    project_name = project.get("projectName", "Unnamed")
                    print(f"\nAnalyzing Project {project_number}: {project_name}")
                    
                    # Check for time registrations in usedWork
                    used_work = project.get("usedWork", [])
                    if used_work:
                        print(f"Found {len(used_work)} time registrations")
                        print("\nTime registration summary:")
                        
                        # Group by employee
                        employee_hours = {}
                        for entry in used_work:
                            employee = entry.get("employeeName", "Unknown")
                            hours = entry.get("quantity", 0)
                            if employee not in employee_hours:
                                employee_hours[employee] = {
                                    "total_hours": 0,
                                    "entries": 0,
                                    "total_cost": 0
                                }
                            employee_hours[employee]["total_hours"] += hours
                            employee_hours[employee]["entries"] += 1
                            employee_hours[employee]["total_cost"] += entry.get("cost", 0)
                        
                        # Print summary
                        for employee, stats in employee_hours.items():
                            print(f"\nEmployee: {employee}")
                            print(f"Total Hours: {stats['total_hours']:.2f}")
                            print(f"Number of Entries: {stats['entries']}")
                            print(f"Total Cost: {stats['total_cost']:.2f}")
                    else:
                        print("No time registrations found")
                    
                    # Try to get more details about the project
                    project_url = f"{base_url}/api/Projects/{project_number}"
                    project_response = requests.get(
                        project_url,
                        headers=headers
                    )
                    
                    if project_response.status_code == 200:
                        project_details = project_response.json()
                        if "payload" in project_details:
                            details = project_details["payload"]
                            print("\nProject Details:")
                            print(f"Status: {details.get('status', 'Unknown')}")
                            print(f"Department: {details.get('department', 'Unknown')}")
                            print(f"Case Handler: {details.get('caseHandler', 'Unknown')}")
                    
            else:
                print("No projects found in response")
        else:
            print(f"Failed to get projects. Status code: {projects_response.status_code}")
            print("Response:", projects_response.text[:200])
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 