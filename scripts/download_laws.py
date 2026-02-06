import os
import requests
import zipfile
import io
from urllib.parse import urljoin

# Die Liste der Gesetzeskürzel
LAWS = [
    "gg", "bgb", "zpo", "stgb", "stpo", "hgb", 
    "sgb_5", "vwgo", "gvg", "bgbeg", "stpoeg", "gvgeg"
]

BASE_URL_TEMPLATE = "https://www.gesetze-im-internet.de/{}/xml.zip"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

def download_and_extract():
    print(f"Starte Download von {len(LAWS)} Gesetzesbüchern...")
    
    for law in LAWS:
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
        except Exception as e:
            print(f"  !!! Fehler bei {law}: {e}")

    print("\nDownload abgeschlossen.")

if __name__ == "__main__":
    download_and_extract()