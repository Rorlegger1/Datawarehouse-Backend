from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from datetime import datetime
import os
from cordel_api_client import CordelAPIClient
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)

# Models
class TimeRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_number = db.Column(db.String(50))
    employee_name = db.Column(db.String(100))
    project_number = db.Column(db.String(50))
    project_name = db.Column(db.String(100))
    hours = db.Column(db.Float)
    cost = db.Column(db.Float)
    date = db.Column(db.DateTime)
    description = db.Column(db.Text)

@app.route('/')
def index():
    # Get summary statistics
    total_hours = db.session.query(db.func.sum(TimeRegistration.hours)).scalar() or 0
    total_cost = db.session.query(db.func.sum(TimeRegistration.cost)).scalar() or 0
    employee_count = db.session.query(TimeRegistration.employee_name.distinct()).count()
    project_count = db.session.query(TimeRegistration.project_number.distinct()).count()

    # Get top 5 projects by hours
    top_projects = db.session.query(
        TimeRegistration.project_number,
        TimeRegistration.project_name,
        db.func.sum(TimeRegistration.hours).label('total_hours')
    ).group_by(TimeRegistration.project_number, TimeRegistration.project_name)\
     .order_by(db.text('total_hours DESC')).limit(5).all()

    # Get latest registrations
    latest_registrations = TimeRegistration.query.order_by(TimeRegistration.date.desc()).limit(10).all()

    return render_template('index.html',
                         total_hours=total_hours,
                         total_cost=total_cost,
                         employee_count=employee_count,
                         project_count=project_count,
                         top_projects=top_projects,
                         latest_registrations=latest_registrations)

@app.route('/sync_data')
def sync_data():
    try:
        client = CordelAPIClient()
        time_data = client.get_time_registrations()
        
        if not time_data.empty:
            # Clear existing data
            TimeRegistration.query.delete()
            
            # Insert new data
            for _, row in time_data.iterrows():
                registration = TimeRegistration(
                    employee_number=row.get('employeeNumber'),
                    employee_name=row.get('employeeName'),
                    project_number=row.get('projectNumber'),
                    project_name=row.get('projectName'),
                    hours=float(row.get('quantity', 0)),
                    cost=float(row.get('cost', 0)),
                    date=pd.to_datetime(row.get('date')),
                    description=row.get('comment', '')
                )
                db.session.add(registration)
            
            db.session.commit()
            return jsonify({'status': 'success', 'message': f'Synced {len(time_data)} records'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/projects')
def projects():
    projects = db.session.query(
        TimeRegistration.project_number,
        TimeRegistration.project_name,
        db.func.sum(TimeRegistration.hours).label('total_hours'),
        db.func.sum(TimeRegistration.cost).label('total_cost')
    ).group_by(TimeRegistration.project_number, TimeRegistration.project_name)\
     .order_by(db.text('total_hours DESC')).all()
    
    return render_template('projects.html', projects=projects)

@app.route('/employees')
def employees():
    employees = db.session.query(
        TimeRegistration.employee_name,
        db.func.sum(TimeRegistration.hours).label('total_hours'),
        db.func.sum(TimeRegistration.cost).label('total_cost')
    ).group_by(TimeRegistration.employee_name)\
     .order_by(db.text('total_hours DESC')).all()
    
    return render_template('employees.html', employees=employees)

@app.route('/time_analysis')
def time_analysis():
    try:
        client = CordelAPIClient()
        print("Fetching time registrations for project 50...")
        time_data = client.get_time_registrations(project_number='50')
        
        print("Time data received:", time_data is not None)
        if time_data is not None and not time_data.empty:
            print("Number of records:", len(time_data))
            print("Columns:", time_data.columns.tolist())
            print("First row:", time_data.iloc[0] if len(time_data) > 0 else "No rows")
            
            # Convert to DataFrame if not already
            df = pd.DataFrame(time_data)
            
            # Add project number and name if not present
            if 'projectNumber' not in df.columns:
                df['projectNumber'] = '50'
            if 'projectName' not in df.columns:
                df['projectName'] = 'Project 50'
            
            # Ensure we have the required columns
            required_columns = ['employeeNumber', 'employeeName', 'quantity', 'cost', 'date']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                print(f"Missing required columns: {missing_columns}")
                return f"Data structure is incomplete. Missing columns: {missing_columns}", 500
            
            # Rename columns for consistency
            column_mapping = {
                'employeeNumber': 'employee_number',
                'employeeName': 'employee_name',
                'projectNumber': 'project_number',
                'projectName': 'project_name',
                'quantity': 'hours',
                'cost': 'cost',
                'comment': 'description'
            }
            
            # Only rename columns that exist
            rename_cols = {k: v for k, v in column_mapping.items() if k in df.columns}
            df = df.rename(columns=rename_cols)
            
            print("Columns after renaming:", df.columns.tolist())
            
            # Convert date column to datetime
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            
            # Create visualizations
            # Project hours chart
            project_hours = df.groupby(['project_number', 'project_name', 'employee_name'])['hours'].sum().reset_index()
            fig_projects = px.bar(
                project_hours,
                x='project_name',
                y='hours',
                color='employee_name',
                title='Project 50 Hours by Employee',
                template='plotly_white',
                barmode='stack'
            )
            
            # Monthly trend chart
            df['month'] = df['date'].dt.strftime('%Y-%m')
            monthly_hours = df.groupby('month')['hours'].sum().reset_index()
            fig_trend = px.line(
                monthly_hours,
                x='month',
                y='hours',
                title='Monthly Hours Trend',
                template='plotly_white'
            )
            
            # Employee distribution chart
            employee_hours = df.groupby('employee_name')['hours'].sum()
            top_employees = employee_hours.nlargest(10)
            other_hours = employee_hours[~employee_hours.index.isin(top_employees.index)].sum()
            plot_data = pd.concat([top_employees, pd.Series({'Others': other_hours})])
            
            fig_employees = go.Figure(data=[go.Pie(
                labels=plot_data.index,
                values=plot_data.values,
                hole=.3
            )])
            
            # Convert plots to JSON
            graphJSON = {
                'projects': json.dumps(fig_projects, cls=plotly.utils.PlotlyJSONEncoder),
                'trend': json.dumps(fig_trend, cls=plotly.utils.PlotlyJSONEncoder),
                'employees': json.dumps(fig_employees, cls=plotly.utils.PlotlyJSONEncoder)
            }
            
            # Calculate summary statistics
            total_hours = df['hours'].sum()
            total_employees = df['employee_name'].nunique()
            total_projects = df['project_number'].nunique()
            avg_hours_per_project = total_hours / total_projects if total_projects > 0 else 0
            
            return render_template(
                'time_analysis.html',
                plots=graphJSON,
                stats={
                    'total_hours': f"{total_hours:,.1f}",
                    'total_employees': total_employees,
                    'total_projects': total_projects,
                    'avg_hours_per_project': f"{avg_hours_per_project:,.1f}"
                }
            )
        else:
            print("No data received from API")
            return "No data available from the API", 404
            
    except Exception as e:
        print(f"Error in time_analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error processing data: {str(e)}", 500

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully")

# Initialize database before running the app
init_db()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') 