import os
import requests
import zipfile
import io
import argparse
from urllib.parse import urljoin

# Standard-Liste der Gesetzeskürzel
DEFAULT_LAWS = [
    "gg", "bgb", "zpo", "stgb", "stpo", "hgb", 
    "sgb_5", "vwgo", "gvg", "bgbeg", "stpoeg", "gvgeg"
]

BASE_URL_TEMPLATE = "https://www.gesetze-im-internet.de/{}/xml.zip"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

def download_and_extract(laws):
    print(f"Starte Download von {len(laws)} Gesetzesbüchern...")
    
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    for law in laws:
        law = law.lower().strip()
        url = BASE_URL_TEMPLATE.format(law)
        print(f"Lade {law.upper()}... ({url})")
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    for filename in z.namelist():
                        if filename.endswith('.xml'):
                            xml_content = z.read(filename)
                            target_path = os.path.join(DATA_DIR, f"{law}.xml")
                            
                            with open(target_path, 'wb') as f:
                                f.write(xml_content)
                            print(f"  -> Gespeichert als data/{law}.xml")
                            break 
            else:
                print(f"  !!! Fehler beim Download von {law}: Status {response.status_code}")
                print(f"      Hinweis: Stellen Sie sicher, dass '{law}' das korrekte Kürzel ist (siehe https://www.gesetze-im-internet.de/aktuell.html)")
        except Exception as e:
            print(f"  !!! Fehler bei {law}: {e}")

    print("\nDownload abgeschlossen.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lade Gesetze von gesetze-im-internet.de herunter")
    parser.add_argument("laws", nargs="*", help="Liste der Gesetzeskürzel (z.B. bgb stgb). Wenn leer, wird die Standard-Liste geladen.")
    
    args = parser.parse_args()
    
    target_laws = args.laws if args.laws else DEFAULT_LAWS
    download_and_extract(target_laws)