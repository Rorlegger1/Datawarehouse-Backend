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
    

## Reflection

This was a 4 month project, and is a part of a system made in collaboration with Cordel Norge, as a bachelorproject. The goad for this applicaiton is a system for handling the incoming data, store it, and make it accessible for other parts of the project.

It has been challenging working with alot of new software, and therefore posing as a very good learning experience.



