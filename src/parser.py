import xml.etree.ElementTree as ET
import json
import re
import os
from src.config import XML_FILES, JSON_FILE

def parse_all_laws():
    print(f"Starte Parsing von {len(XML_FILES)} Gesetzesdateien...")
    
    all_parsed_data = []
    
    for xml_file in XML_FILES:
        # Gesetzesnamen aus Dateinamen ableiten (z.B. "data/bgb.xml" -> "BGB")
        law_name = os.path.basename(xml_file).replace('.xml', '').upper()
        print(f"Verarbeite {law_name}...")
        
        try:
            with open(xml_file, 'r', encoding='utf-8') as f:
                xml_content = f.read()
        except Exception as e:
            print(f"Fehler beim Lesen von {xml_file}: {e}")
            continue

        xml_content = re.sub(r'<!DOCTYPE.*?>', '', xml_content, flags=re.DOTALL)

        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            print(f"Fehler beim XML-Parsen von {xml_file}: {e}")
            continue

        count = 0
        for norm in root.findall('norm'):
            metadaten = norm.find('metadaten')
            textdaten = norm.find('textdaten')
            
            if metadaten is None:
                continue

            enbez = metadaten.find('enbez')
            titel = metadaten.find('titel')
            
            # Nur echte Paragraphen oder Artikel
            if enbez is not None and enbez.text:
                norm_id = enbez.text.strip()
                # Einfacher Filter: Muss mit § oder Art beginnen (für GG, EGBGB)
                if not (norm_id.startswith("§") or norm_id.startswith("Art")):
                    continue
                    
                norm_title = titel.text.strip() if (titel is not None and titel.text) else ""
                
                text_content = []
                if textdaten is not None:
                    text_elem = textdaten.find('text')
                    if text_elem is not None:
                        content_elem = text_elem.find('Content')
                        if content_elem is not None:
                            for p in content_elem.findall('.//P'):
                                p_text = "".join(p.itertext()).strip()
                                if p_text:
                                    text_content.append(p_text)
                
                full_text = "\n".join(text_content)
                
                if full_text:
                    # Wir speichern jetzt auch den Gesetzesnamen
                    # Die ID wird eindeutig gemacht: "StGB § 211"
                    unique_id = f"{law_name} {norm_id}"
                    
                    entry = {
                        "id": unique_id,          # Eindeutige ID für den Vektor-Index
                        "law": law_name,          # Gesetz (z.B. BGB)
                        "norm": norm_id,          # Paragraph (z.B. § 823)
                        "title": norm_title,
                        "text": full_text
                    }
                    all_parsed_data.append(entry)
                    count += 1
        
        print(f"  -> {count} Normen extrahiert.")

    print(f"Gesamt: {len(all_parsed_data)} Normen aus allen Gesetzen.")

    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_parsed_data, f, ensure_ascii=False, indent=2)
    
    print(f"Datenbank gespeichert in: {JSON_FILE}")

if __name__ == "__main__":
    parse_all_laws()