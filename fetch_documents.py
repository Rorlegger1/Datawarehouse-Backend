from cordel_api_client import CordelAPIClient
from datetime import datetime, timedelta
import pandas as pd

def main():
    # Initialize the API client
    client = CordelAPIClient()
    
    # Set up date range for last 30 days
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    print(f"Henter dokumenter fra {start_date} til {end_date}")
    
    try:
        # Try to get all documents first
        print("\nHenter alle dokumenter:")
        documents = client.get_documents(
            date_from=start_date,
            date_to=end_date,
            page_size=100
        )
        
        if not documents.empty:
            print("\nFunnet dokumenter:")
            print(f"Antall dokumenter: {len(documents)}")
            if 'type' in documents.columns:
                print("\nDokumenttyper:")
                print(documents['type'].value_counts())
            print("\nKolonner i datasettet:")
            print(documents.columns.tolist())
            print("\nFørste 5 dokumenter:")
            print(documents.head())
        else:
            print("Ingen dokumenter funnet med standard søk")
            
            # Try searching for specific document types
            print("\nPrøver å søke etter spesifikke dokumenttyper:")
            document_types = ["invoice", "order", "delivery", "quote", "contract"]
            
            for doc_type in document_types:
                print(f"\nSøker etter dokumenter av type: {doc_type}")
                type_docs = client.get_documents(
                    date_from=start_date,
                    date_to=end_date,
                    document_type=doc_type
                )
                
                if not type_docs.empty:
                    print(f"Funnet {len(type_docs)} dokumenter av type {doc_type}")
                    print("\nFørste dokument:")
                    print(type_docs.iloc[0])
            
            # Try free text search
            print("\nPrøver fritekst-søk:")
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