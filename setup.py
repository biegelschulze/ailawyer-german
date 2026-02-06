import argparse
from src.parser import parse_all_laws
from src.indexer import create_index, create_sqlite_index

def setup():
    parser = argparse.ArgumentParser(description="Setup AI Lawyer DB")
    parser.add_argument("--target", choices=["pickle", "sqlite", "all"], default="pickle", help="Ziel-Datenbank (pickle, sqlite oder all)")
    parser.add_argument("--skip-parse", action="store_true", help="XML-Parsing überspringen")
    args = parser.parse_args()

    if not args.skip_parse:
        print("--- Schritt 1: XML Parsen ---")
        parse_all_laws()
    
    print("\n--- Schritt 2: Index erstellen ---")
    
    if args.target in ["pickle", "all"]:
        print("Erstelle Pickle Index...")
        create_index()
        
    if args.target in ["sqlite", "all"]:
        print("Erstelle SQLite Index...")
        create_sqlite_index()

    print("\nSetup abgeschlossen!")

if __name__ == "__main__":
    setup()