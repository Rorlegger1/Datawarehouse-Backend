# Cordel Data Analysis System

## System Overview
Cordel er et omfattende forretningssystem med følgende hovedmoduler:

### 1. Salg/Kalkyler
- Kunder/Marked
- Kalkylasjon/Tilbud
- Prosjektanbud
- Direkt mail
- Varer/Prislok
- Favorittleverandører
- Pakker
- Kampanjer
- Anlegg

### 2. Ordre
- Ordrer (Alle)
- Serviceordrer
- Prosjektordrer
- Serviceavtaler
- Avvik
- Dokumenter til signering

### 3. Økonomi
- Faktura/Kundereskontro
- Leverandørreskontro
- Regnskap

### 4. Lager/Innkjøp
- Butikksalg
- Lager
- Innkjøp
- Pakker med standardpriser og beskrivelser

## Data Structure
Systemet inneholder følgende hovedentiteter:

1. **Kunder**
   - Kundenummer
   - Navn
   - Adresse
   - Postnr/Sted
   - Kontaktinformasjon
   - Omsetning

2. **Tilbud/Anbud**
   - Tilbudsnummer
   - Prosjekt
   - Kunde
   - Prosjektbeskrivelse
   - Beløp
   - Status
   - Datoer
   - Saksbehandler

3. **Pakker/Produkter**
   - Produktnummer
   - Beskrivelse
   - Enhet
   - Pris u/arbeid
   - Pris inkl. arbeid
   - Kategori
   - Standardpriser

# Datawarehouse-Backend

## Project Name & Pitch

Backend for Cordel Norge

An application used for handling and storing data from Cordel Norge's tenants. Built with .Net and C#

## Project Status

This project is a finished MVP. The project will be further developeloped by Cordel.

## Installation and Setup Instructions

To setup this application, open the Terminal and write the following code:

This command builds the project and its dependencies

    - dotnet build
    
Starts the application

    - dotnet run
    

## API Integration

The system integrates with Cordel's API for data synchronization. The following features are supported:

### API Endpoints
- Customers data
- Offers and calculations
- Orders (Service and Project)
- Products and packages
- Invoices
- Time registration

### Authentication
API access requires authentication using a Bearer token. Contact Cordel support for API credentials.

### Data Synchronization
The system automatically synchronizes data with the following parameters:
- Default limit: 100 records per request
- Date filtering support (YYYY-MM-DD format)
- Status filtering (active/completed/cancelled)

### Required Permissions
The following API permissions are required:
- read:customers
- read:offers
- read:orders
- read:invoices
- read:products
- read:service_orders

For detailed API documentation, refer to the internal documentation or contact Cordel support.

## Reflection

This was a 4 month project, and is a part of a system made in collaboration with Cordel Norge, as a bachelorproject. The goad for this applicaiton is a system for handling the incoming data, store it, and make it accessible for other parts of the project.

It has been challenging working with alot of new software, and therefore posing as a very good learning experience.

## Time Registration Data

The DataWarehouse API provides access to time registration data through the projects endpoint. Here's how to work with time registrations:

### Accessing Time Registrations

Time registrations are available through the `/api/Projects` endpoint. Each project contains a `usedWork` array with detailed time registration entries.

### Data Structure

Each time registration entry includes:
- Employee information (number and name)
- Hours worked
- Cost information
- Date
- Job/task information
- Comments

### Aggregation Options

The API supports various aggregation levels:
- By employee
- By month
- By project

### Query Parameters

When fetching time registrations, you can use these parameters:
- `pageSize`: Number of records per page (default: 100)
- `pageNumber`: Page number for pagination
- `submittedAfter`: Start date filter (YYYY-MM-DD)
- `submittedBefore`: End date filter (YYYY-MM-DD)

### Example Usage

```python
# Fetch time registrations for a specific project
project_id = "1000"
start_date = "2023-01-01"
end_date = "2023-12-31"

# The data will be returned in the project's usedWork array
response = api.get_project_time_registrations(
    project_id,
    start_date=start_date,
    end_date=end_date
)
```

### Data Processing

The API returns time registration data that can be aggregated and analyzed in various ways:
- Total hours and costs per project
- Monthly distribution of work
- Employee-wise breakdown of hours
- Cost analysis and reporting

For detailed implementation examples, refer to the `fetch_project_hours.py` script in this repository.



