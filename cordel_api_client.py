import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

class CordelAPIClient:
    def __init__(self, api_key: str, base_url: str = "https://api.cordel.no"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def get_customers(self, filters: Optional[Dict] = None) -> pd.DataFrame:
        """Hent kundedata med valgfrie filtre"""
        endpoint = f"{self.base_url}/customers"
        response = requests.get(endpoint, headers=self.headers, params=filters)
        return pd.DataFrame(response.json())

    def get_offers(self, 
                  date_from: Optional[str] = None,
                  date_to: Optional[str] = None,
                  status: Optional[str] = None) -> pd.DataFrame:
        """Hent tilbudsdata med datofilter og status"""
        endpoint = f"{self.base_url}/offers"
        params = {
            "date_from": date_from,
            "date_to": date_to,
            "status": status
        }
        response = requests.get(endpoint, headers=self.headers, params=params)
        return pd.DataFrame(response.json())

    def get_product_packages(self) -> pd.DataFrame:
        """Hent pakker/produkter med priser"""
        endpoint = f"{self.base_url}/packages"
        response = requests.get(endpoint, headers=self.headers)
        return pd.DataFrame(response.json())

    def analyze_sales_by_period(self,
                              start_date: str,
                              end_date: str,
                              group_by: str = "month") -> pd.DataFrame:
        """Analyser salg i en periode"""
        sales_data = self.get_offers(date_from=start_date, date_to=end_date)
        sales_data['date'] = pd.to_datetime(sales_data['date'])
        return sales_data.groupby(pd.Grouper(key='date', freq=group_by[0].upper())).sum()

    def get_suppliers(self, filters: Optional[Dict] = None) -> pd.DataFrame:
        """Hent leverandørdata med valgfrie filtre"""
        endpoint = f"{self.base_url}/suppliers"
        response = requests.get(endpoint, headers=self.headers, params=filters)
        return pd.DataFrame(response.json())

    def get_facilities(self, filters: Optional[Dict] = None) -> pd.DataFrame:
        """Hent anleggsdata med valgfrie filtre"""
        endpoint = f"{self.base_url}/facilities"
        response = requests.get(endpoint, headers=self.headers, params=filters)
        return pd.DataFrame(response.json())

    def analyze_supplier_distribution(self) -> pd.DataFrame:
        """Analyser geografisk fordeling av leverandører"""
        suppliers = self.get_suppliers()
        return suppliers.groupby('poststed').size().sort_values(ascending=False)

    def get_supplier_details(self, supplier_id: str) -> Dict:
        """Hent detaljert informasjon om en leverandør"""
        endpoint = f"{self.base_url}/suppliers/{supplier_id}"
        response = requests.get(endpoint, headers=self.headers)
        return response.json()

    def get_orders(self, 
                  order_type: Optional[str] = None,
                  status: Optional[str] = None,
                  date_from: Optional[str] = None,
                  date_to: Optional[str] = None) -> pd.DataFrame:
        """
        Hent ordredata med filtre
        order_type: 'service', 'project', 'all'
        status: 'active', 'completed', 'cancelled'
        """
        endpoint = f"{self.base_url}/orders"
        params = {
            "type": order_type,
            "status": status,
            "date_from": date_from,
            "date_to": date_to
        }
        response = requests.get(endpoint, headers=self.headers, params=params)
        return pd.DataFrame(response.json())

    def get_service_orders(self, status: Optional[str] = None) -> pd.DataFrame:
        """Hent service-ordrer med status filter"""
        return self.get_orders(order_type="service", status=status)

    def analyze_order_statistics(self,
                               start_date: str,
                               end_date: str,
                               group_by: List[str] = ["type", "status"]) -> pd.DataFrame:
        """
        Analyser ordrestatistikk
        group_by: Liste av felter å gruppere på (f.eks. ["type", "status", "saksbehandler"])
        """
        orders = self.get_orders(date_from=start_date, date_to=end_date)
        return orders.groupby(group_by).agg({
            'beløp': ['sum', 'count', 'mean'],
            'fakt_beløp': ['sum', 'mean'],
            'gjenstår_beløp': 'sum'
        })

    def get_order_details(self, order_id: str) -> Dict:
        """Hent detaljert informasjon om en ordre"""
        endpoint = f"{self.base_url}/orders/{order_id}"
        response = requests.get(endpoint, headers=self.headers)
        return response.json() 