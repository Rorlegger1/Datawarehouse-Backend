from cordel_api_client import CordelAPIClient
import pandas as pd
from datetime import datetime, timedelta

def main():
    print("Analyzing sick leave patterns by previous project assignments...")
    
    # Initialize API client
    client = CordelAPIClient()
    
    # Get all time registrations
    print("\nFetching time registrations...")
    time_data = client.get_time_registrations()
    
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
        print("No sick leave entries found")
        return
    
    # For each sick leave entry, find the project the employee was working on the day before
    results = []
    for _, sick_entry in sick_leaves.iterrows():
        # Get entries from the day before
        prev_day = sick_entry['date'] - timedelta(days=1)
        prev_entries = time_data[
            (time_data['employeeNumber'] == sick_entry['employeeNumber']) & 
            (time_data['date'] == prev_day)
        ]
        
        # If found previous day entries, use that project
        if not prev_entries.empty:
            project_number = prev_entries.iloc[0]['projectNumber']
            project_name = prev_entries.iloc[0]['projectName']
        else:
            # If no previous day entry, use the project from the sick leave entry
            project_number = sick_entry['projectNumber']
            project_name = sick_entry['projectName']
        
        results.append({
            'date': sick_entry['date'],
            'employee_number': sick_entry['employeeNumber'],
            'employee_name': sick_entry['employeeName'],
            'project_number': project_number,
            'project_name': project_name,
            'hours': sick_entry['quantity'],
            'comment': sick_entry['comment']
        })
    
    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    
    # Group by project and calculate statistics
    project_stats = results_df.groupby(['project_number', 'project_name']).agg({
        'hours': ['sum', 'count'],
        'employee_number': 'nunique'
    }).reset_index()
    
    # Flatten column names
    project_stats.columns = ['project_number', 'project_name', 'total_hours', 'num_incidents', 'num_employees']
    
    # Calculate total sick leave hours
    total_sick_hours = project_stats['total_hours'].sum()
    
    print("\nSick Leave Analysis by Project:")
    print("-" * 80)
    print(f"Total Sick Leave Hours: {total_sick_hours:.2f} ({total_sick_hours/8:.2f} work days)")
    print("-" * 80)
    
    # Sort by total hours descending
    project_stats = project_stats.sort_values('total_hours', ascending=False)
    
    # Print project statistics
    for _, row in project_stats.iterrows():
        print(f"\nProject {row['project_number']}: {row['project_name']}")
        print(f"Total Sick Hours: {row['total_hours']:.2f} ({row['total_hours']/8:.2f} work days)")
        print(f"Number of Incidents: {row['num_incidents']}")
        print(f"Number of Employees: {row['num_employees']}")
        print(f"Percentage of Total: {(row['total_hours']/total_sick_hours)*100:.1f}%")
    
    # Monthly distribution
    print("\nMonthly Distribution of Sick Leave:")
    monthly_stats = results_df.groupby(results_df['date'].dt.strftime('%Y-%m'))['hours'].sum().sort_index()
    print(monthly_stats)

if __name__ == "__main__":
    main() 