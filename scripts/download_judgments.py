import os
import requests
import xml.etree.ElementTree as ET
from tqdm import tqdm

TOC_URL = "https://www.rechtsprechung-im-internet.de/rii-toc.xml"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, 'data', 'urteile')
LIMIT = 50  # Vorerst nur 50 Urteile zum Testen

def download_judgments():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print(f"Lade Inhaltsverzeichnis von {TOC_URL}...")
    try:
        response = requests.get(TOC_URL)
        if response.status_code != 200:
            print(f"Fehler beim Laden des TOC: {response.status_code}")
            return
    except Exception as e:
        print(f"Verbindungsfehler: {e}")
        return

    # XML parsen
    root = ET.fromstring(response.content)
    
    items = root.findall('.//item')
    print(f"Gefunden: {len(items)} Urteile im Inhaltsverzeichnis.")
    print(f"Lade die ersten {LIMIT} Urteile herunter...")

    count = 0
    for item in tqdm(items[:LIMIT]):
        link = item.find('link')
        if link is not None:
            url = link.text
            # Dateiname aus URL ableiten (meist am Ende)
            filename = url.split('/')[-1]
            target_path = os.path.join(OUTPUT_DIR, filename)
            
            if not os.path.exists(target_path):
                try:
                    r = requests.get(url)
                    if r.status_code == 200:
                        with open(target_path, 'wb') as f:
                            f.write(r.content)
                        count += 1
                except Exception as e:
                    print(f"Fehler bei {url}: {e}")
            else:
                # Überspringen, wenn schon da
                count += 1

    print(f"
Fertig. {count} Urteile in '{OUTPUT_DIR}' gespeichert.")

if __name__ == "__main__":
    download_judgments()
