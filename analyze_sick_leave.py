from cordel_api_client import CordelAPIClient
import pandas as pd
from datetime import datetime, timedelta

def main():
    print("Analyzing sick leave patterns for January 2025...")
    
    # Initialize API client
    client = CordelAPIClient()
    
    # Set date range for January 2025
    date_from = "2025-01-01"
    date_to = "2025-01-31"
    
    print(f"\nFetching time registrations for period: {date_from} to {date_to}")
    time_data = client.get_time_registrations(date_from=date_from, date_to=date_to)
    
    if time_data.empty:
        print("No time registration data found")
        return
        
    # Convert date column to datetime
    time_data['date'] = pd.to_datetime(time_data['date'])
    
    # Sort by employee and date
    time_data = time_data.sort_values(['employeeNumber', 'date'])
    
    # Identify sick leave entries
    sick_pattern = r'syk|sick|sykemelding|sykmelding'
    sick_leaves = time_data[time_data['comment'].str.contains(sick_pattern, case=False, na=False)].copy()
    
    if sick_leaves.empty:
        print("No sick leave entries found for January 2025")
        return
    
    # Calculate summary statistics
    total_sick_hours = sick_leaves['quantity'].sum()
    total_employees = sick_leaves['employeeNumber'].nunique()
    
    print("\nSick Leave Summary for January 2025:")
    print("-" * 80)
    print(f"Total Sick Leave Hours: {total_sick_hours:.2f} ({total_sick_hours/8:.2f} work days)")
    print(f"Number of Employees on Sick Leave: {total_employees}")
    print("-" * 80)
    
    # Group by employee
    employee_stats = sick_leaves.groupby(['employeeNumber', 'employeeName'])['quantity'].agg(['sum', 'count']).reset_index()
    employee_stats.columns = ['Employee Number', 'Employee Name', 'Total Hours', 'Number of Days']
    
    print("\nBreakdown by Employee:")
    for _, row in employee_stats.iterrows():
        print(f"\n{row['Employee Name']} (ID: {row['Employee Number']})")
        print(f"Total Sick Hours: {row['Total Hours']:.2f} ({row['Total Hours']/8:.2f} work days)")
        print(f"Number of Sick Days: {row['Number of Days']}")

if __name__ == "__main__":
    main() 