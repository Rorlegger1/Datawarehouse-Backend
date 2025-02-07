from cordel_api_client import CordelAPIClient
from datetime import datetime, timedelta
import pandas as pd

def main():
    # Initialize the API client
    client = CordelAPIClient()
    
    # Set up date range for last 30 days
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    # Project number to search for
    project_number = "P1000"  # Åsgard skole
    
    print(f"Henter dokumenter for prosjekt {project_number}")
    print(f"Periode: {start_date} til {end_date}")
    
    try:
        # Get project documents
        documents = client.get_project_documents(
            project_number=project_number,
            date_from=start_date,
            date_to=end_date
        )
        
        if not documents.empty:
            print("\nFunnet dokumenter:")
            print(f"Antall dokumenter: {len(documents)}")
            
            # Display document types if available
            if 'type' in documents.columns:
                print("\nDokumenttyper:")
                print(documents['type'].value_counts())
            
            # Display available columns
            print("\nTilgjengelige kolonner:")
            print(documents.columns.tolist())
            
            # Display first few documents
            print("\nFørste 5 dokumenter:")
            print(documents.head())
            
            # If we have document IDs, try to fetch a specific document
            if 'id' in documents.columns and not documents['id'].empty:
                first_doc_id = documents['id'].iloc[0]
                print(f"\nHenter detaljer for dokument {first_doc_id}:")
                doc_details = client.get_project_document_by_id(
                    project_number=project_number,
                    document_id=first_doc_id
                )
                print("Dokumentdetaljer:")
                print(doc_details)
        else:
            print("Ingen dokumenter funnet for prosjektet")
            
            # Try searching for documents
            print("\nPrøver å søke etter dokumenter:")
            search_terms = ["faktura", "ordre", "tilbud", "kontrakt", "avtale"]
            
            for term in search_terms:
                print(f"\nSøker etter dokumenter med tekst: {term}")
                search_docs = client.search_documents(
                    search_text=term,
                    date_from=start_date,
                    date_to=end_date
                )
                
                if not search_docs.empty:
                    print(f"Funnet {len(search_docs)} dokumenter med søkeord '{term}'")
                    print("\nFørste dokument:")
                    print(search_docs.iloc[0])
        
    except Exception as e:
        print(f"En feil oppstod: {str(e)}")

if __name__ == "__main__":
    main() 