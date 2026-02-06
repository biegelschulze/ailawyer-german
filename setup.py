from src.parser import parse_all_laws
from src.indexer import create_index

def setup():
    print("--- Schritt 1: XML Parsen ---")
    parse_all_laws()
    print("\n--- Schritt 2: Index erstellen ---")
    create_index()
    print("\nSetup abgeschlossen!")

if __name__ == "__main__":
    setup()