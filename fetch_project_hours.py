from cordel_api_client import CordelAPIClient
from datetime import datetime
import pandas as pd

def main():
    # Initialize the API client
    client = CordelAPIClient()
    
    # Set up the date range for 2023
    date_from = "2023-01-01"
    date_to = "2023-12-31"
    project_number = "1000"  # Remove 'P' prefix
    
    print(f"Henter timeregistreringer for prosjekt {project_number}...")
    print(f"Periode: {date_from} til {date_to}")
    
    try:
        # Get the total hours
        result = client.get_project_total_hours(
            project_number=project_number,
            date_from=date_from,
            date_to=date_to
        )
        
        print("\nResultat:")
        print(f"Totalt antall timer: {result['total_hours']:.2f}")
        print(f"Total kostnad: {result['total_cost']:.2f} NOK")
        
        # Get detailed time registrations for analysis
        time_data = client.get_time_registrations(
            project_number=project_number,
            date_from=date_from,
            date_to=date_to
        )
        
        if not time_data.empty:
            print("\nMånedlig fordeling:")
            time_data['date'] = pd.to_datetime(time_data['date'])
            monthly_hours = time_data.groupby(time_data['date'].dt.strftime('%Y-%m')).agg({
                'quantity': 'sum',
                'cost': 'sum'
            }).rename(columns={'quantity': 'hours', 'cost': 'cost'})
            print(monthly_hours)
            
            print("\nFordeling per ansatt:")
            employee_hours = time_data.groupby('employeeName').agg({
                'quantity': 'sum',
                'cost': 'sum'
            }).rename(columns={'quantity': 'hours', 'cost': 'cost'})
            print(employee_hours)
            
    except Exception as e:
        print(f"En feil oppstod: {str(e)}")

if __name__ == "__main__":
    main() 