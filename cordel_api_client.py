import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import base64

class CordelAPIClient:
    def __init__(self, 
                 username: str = "datavarehus.integrasjon@ror-system.no", 
                 password: str = "qA02bRux!3eD", 
                 base_url: str = "https://api.smartcraft.cloud",  # Back to Smartcraft URL
                 tenant_id: str = "3744c6ca-4149-4627-8e8f-ac95fb793b4e"):
        """Initialize the API client with credentials."""
        self.username = username
        self.password = password
        self.base_url = base_url.rstrip('/')
        self.tenant_id = tenant_id
        self.auth_token = None
        self.token_expiry = None
        self.modules = ["90000", "93000"]  # From JWT token
        self._authenticate()

    def _authenticate(self):
        """
        Authenticate with the API and get a new token.
        """
        print("Authenticating with API...")
        auth_data = {
            "username": self.username,
            "password": self.password,
            "tenantId": self.tenant_id
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/auth",
                json=auth_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Auth response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if "authToken" in data:
                    self.auth_token = data["authToken"]
                    self.token_expiry = datetime.now() + timedelta(hours=1)
                    print("Successfully authenticated")
                else:
                    print("No auth token in response")
                    raise ValueError("Authentication failed - no token received")
            else:
                print(f"Authentication failed: {response.text}")
                raise ValueError(f"Authentication failed with status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"Authentication request failed: {str(e)}")
            raise ConnectionError("Could not connect to authentication endpoint")

    def _refresh_auth_token(self):
        """Refresh the auth token using refresh token"""
        if not self.refresh_token:
            self._authenticate()
            return
            
        try:
            response = requests.get(
                f"{self.base_url}/auth/refresh",
                headers={"Cookie": f"refreshToken={self.refresh_token}"}
            )
            
            if response.status_code == 200:
                auth_response = response.json()
                self.auth_token = auth_response.get("authToken")
                self.refresh_token = auth_response.get("refreshToken")
            else:
                self._authenticate()
                
        except Exception:
            self._authenticate()

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with auth token"""
        if not self.auth_token:
            self._authenticate()
            
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the API with proper authentication and error handling.
        """
        if not self.auth_token or self._should_refresh_token():
            self._authenticate()

        headers = self._get_headers()
        url = f"{self.base_url}{endpoint}"
        
        print(f"Making {method} request to {url}")
        print("Headers:", headers)
        print("Params:", params)
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params
            )
            
            print(f"Response status code: {response.status_code}")
            
            if response.status_code == 401:
                print("Token expired, refreshing...")
                self._authenticate()
                headers = self._get_headers()
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params
                )
            
            if response.status_code == 200:
                try:
                    return response.json()
                except ValueError:
                    print("Response is not JSON")
                    return {"payload": response.text}
            else:
                print(f"Error response: {response.text}")
                return {"payload": []}
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            return {"payload": []}

    def get_time_registrations(self,
                             project_number: Optional[str] = None,
                             date_from: Optional[str] = None,
                             date_to: Optional[str] = None) -> pd.DataFrame:
        """
        Get time registrations from the API.
        Args:
            project_number: Optional project number to filter by
            date_from: Optional start date in YYYY-MM-DD format
            date_to: Optional end date in YYYY-MM-DD format
        Returns:
            DataFrame containing time registration data
        """
        try:
            print(f"Fetching time registrations for period: {date_from} to {date_to}")
            
            # Use the DataWarehouse endpoint for time registrations
            endpoint = "/DataWarehouse/api/TimeRegistrations"
            
            # Add query parameters
            params = {
                "pageSize": 1000,  # Get more records at once
                "pageNumber": 0
            }
            if date_from:
                params["submittedAfter"] = date_from
            if date_to:
                params["submittedBefore"] = date_to
            if project_number:
                params["projectNumber"] = project_number
            
            # Make the API request
            print(f"Making request to endpoint: {endpoint}")
            response = self._make_request("GET", endpoint, params=params)
            
            print("API Response received")
            
            if isinstance(response, dict) and "payload" in response:
                data = response["payload"]
                if isinstance(data, list) and data:
                    return pd.DataFrame(data)
                else:
                    print("No time entries found")
                    return pd.DataFrame()
            else:
                print("Invalid response format")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Error fetching time registrations: {str(e)}")
            return pd.DataFrame()

    def get_customers(self, filters: Optional[Dict] = None) -> pd.DataFrame:
        """Get customer data with optional filters"""
        data = self._make_request("GET", "customers", params=filters)
        return pd.DataFrame(data.get("items", []))

    def get_offers(self, 
                  date_from: Optional[str] = None,
                  date_to: Optional[str] = None,
                  status: Optional[str] = None) -> pd.DataFrame:
        """Get offers with date filter and status"""
        params = {
            "dateFrom": date_from,
            "dateTo": date_to,
            "status": status,
            "pageSize": 100,
            "pageNumber": 0
        }
        data = self._make_request("GET", "offers", params=params)
        return pd.DataFrame(data.get("items", []))

    def get_orders(self, 
                  order_type: Optional[str] = None,
                  status: Optional[str] = None,
                  date_from: Optional[str] = None,
                  date_to: Optional[str] = None) -> pd.DataFrame:
        """
        Get order data with filters
        order_type: 'service', 'project', 'all'
        status: 'active', 'completed', 'cancelled'
        """
        params = {
            "type": order_type,
            "status": status,
            "dateFrom": date_from,
            "dateTo": date_to,
            "pageSize": 100,
            "pageNumber": 0
        }
        data = self._make_request("GET", "orders", params=params)
        return pd.DataFrame(data.get("items", []))

    def get_products(self) -> pd.DataFrame:
        """Get product data"""
        data = self._make_request("GET", "products")
        return pd.DataFrame(data.get("items", []))

    def get_invoices(self,
                    date_from: Optional[str] = None,
                    date_to: Optional[str] = None,
                    status: Optional[str] = None) -> pd.DataFrame:
        """Get invoice data with filters"""
        params = {
            "dateFrom": date_from,
            "dateTo": date_to,
            "status": status,
            "pageSize": 100,
            "pageNumber": 0
        }
        data = self._make_request("GET", "invoices", params=params)
        return pd.DataFrame(data.get("items", []))

    def get_project_total_hours(self,
                              project_number: str,
                              date_from: str,
                              date_to: str) -> Dict[str, float]:
        """
        Get total hours for a project in a period
        Returns dictionary with total hours and cost
        """
        try:
            time_data = self.get_time_registrations(
                project_number=project_number,
                date_from=date_from,
                date_to=date_to
            )
            
            if time_data.empty:
                return {"total_hours": 0.0, "total_cost": 0.0}
            
            total_hours = float(time_data["quantity"].sum()) if "quantity" in time_data.columns else 0.0
            total_cost = float(time_data["cost"].sum()) if "cost" in time_data.columns else 0.0
            
            return {
                "total_hours": total_hours,
                "total_cost": total_cost
            }
            
        except Exception as e:
            print(f"Error calculating project total hours: {str(e)}")
            return {"total_hours": 0.0, "total_cost": 0.0}

    def get_project_info(self, project_number: str) -> Dict:
        """Hent informasjon om et prosjekt"""
        endpoints = [
            f"api/Projects/{project_number}",
            f"api/Project/{project_number}",
            f"api/Orders/{project_number}"  # Project might be stored as an order
        ]
        
        last_error = None
        for endpoint in endpoints:
            try:
                print(f"\nTrying to get project info from: {endpoint}")
                return self._make_request("GET", endpoint)
            except Exception as e:
                print(f"Error with endpoint {endpoint}: {str(e)}")
                last_error = e
                continue
        
        if last_error:
            raise last_error
        return {}

    def get_project_structure(self, project_number: str) -> Dict:
        """Hent prosjektstruktur med alle tilgjengelige endepunkter"""
        base_endpoints = [
            "Documents",
            "Files",
            "Attachments",
            "Orders",
            "Invoices",
            "TimeRegistrations",
            "Hours",
            "Materials",
            "Notes"
        ]
        
        project_structure = {"project_number": project_number}
        
        for endpoint in base_endpoints:
            try:
                print(f"\nChecking endpoint: api/Projects/{project_number}/{endpoint}")
                response = self._make_request("GET", f"api/Projects/{project_number}/{endpoint}")
                project_structure[endpoint.lower()] = response
            except Exception as e:
                print(f"Endpoint {endpoint} not available: {str(e)}")
                continue
        
        return project_structure

    def get_project_documents(self,
                            project_number: str,
                            date_from: Optional[str] = None,
                            date_to: Optional[str] = None) -> pd.DataFrame:
        """Hent dokumenter for et spesifikt prosjekt"""
        # First try to get project info to understand the structure
        try:
            project_info = self.get_project_info(project_number)
            print("\nProject info:", project_info)
            
            # Try to get project structure
            project_structure = self.get_project_structure(project_number)
            print("\nAvailable endpoints:", list(project_structure.keys()))
            
            # Now try to get documents using the correct endpoint structure
            if "documents" in project_structure:
                endpoint = f"api/Projects/{project_number}/Documents"
            elif "files" in project_structure:
                endpoint = f"api/Projects/{project_number}/Files"
            else:
                # Try default endpoints
                endpoints = [
                    f"api/Projects/{project_number}/Documents",
                    f"api/Projects/{project_number}/Files",
                    f"api/Projects/{project_number}/Attachments"
                ]
                
                params = {
                    "fromDate": date_from,
                    "toDate": date_to,
                    "pageSize": 1000,
                    "pageNumber": 0
                }
                
                for endpoint in endpoints:
                    try:
                        print(f"\nTrying endpoint: {endpoint}")
                        data = self._make_request("GET", endpoint, params=params)
                        
                        if isinstance(data, dict):
                            if "items" in data:
                                return pd.DataFrame(data["items"])
                            elif "documents" in data:
                                return pd.DataFrame(data["documents"])
                            elif "files" in data:
                                return pd.DataFrame(data["files"])
                        elif isinstance(data, list):
                            return pd.DataFrame(data)
                            
                    except Exception as e:
                        print(f"Error with endpoint {endpoint}: {str(e)}")
                        continue
                
                return pd.DataFrame()  # Return empty if no endpoints work
                
        except Exception as e:
            print(f"Error getting project structure: {str(e)}")
            raise

    def get_project_document_by_id(self,
                                 project_number: str,
                                 document_id: str) -> Dict:
        """Hent et spesifikt dokument for et prosjekt"""
        endpoint = f"api/Projects/{project_number}/Documents/{document_id}"
        
        try:
            return self._make_request("GET", endpoint)
        except Exception as e:
            print(f"Error fetching document {document_id} for project {project_number}: {str(e)}")
            # Try alternative endpoint
            try:
                endpoint = f"api/Projects/{project_number}/Files/{document_id}"
                return self._make_request("GET", endpoint)
            except Exception as e2:
                print(f"Error with alternative endpoint: {str(e2)}")
                raise e

    def search_documents(self,
                        search_text: Optional[str] = None,
                        document_types: Optional[List[str]] = None,
                        date_from: Optional[str] = None,
                        date_to: Optional[str] = None) -> pd.DataFrame:
        """Søk etter dokumenter"""
        endpoint = "api/Documents/search"
        
        params = {
            "searchText": search_text,
            "types": document_types,
            "fromDate": date_from,
            "toDate": date_to,
            "pageSize": 1000,
            "pageNumber": 0
        }
        
        try:
            data = self._make_request("GET", endpoint, params=params)
            return pd.DataFrame(data.get("items", []))
        except Exception as e:
            print(f"Error searching documents: {str(e)}")
            raise 

    def _should_refresh_token(self) -> bool:
        """Check if the token needs to be refreshed."""
        if not self.token_expiry:
            return True
        # Refresh if token expires in less than 5 minutes
        return datetime.now() + timedelta(minutes=5) >= self.token_expiry 