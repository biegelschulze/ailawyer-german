import json
from google import genai
from google.genai import types
import pickle
import time
from tqdm import tqdm
from src.config import JSON_FILE, DB_FILE, API_KEY, EMBEDDING_MODEL

def create_index():
    print("Initialisiere Gemini API Client (V1)...")
    client = genai.Client(api_key=API_KEY)
    
    print(f"Lade Daten aus {JSON_FILE}...")
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Datei nicht gefunden: {JSON_FILE}")
        return

    documents = []
    metadatas = []

    print("Bereite Texte vor...")
    for entry in data:
        doc_text = f"{entry['id']} {entry['title']}\n{entry['text']}"
        documents.append(doc_text)
        metadatas.append(entry)

    print(f"Erstelle Embeddings für {len(documents)} Dokumente...")
    
    embeddings = []
    batch_size = 50 
    
    for i in tqdm(range(0, len(documents), batch_size)):
        batch_docs = documents[i:i + batch_size]
        try:
            # Neuer API Aufruf
            result = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=batch_docs,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",
                    title="Gesetzestext"
                )
            )
            # Im neuen SDK ist embeddings ein Attribut des Objekts, nicht mehr ein Dict-Key
            if result.embeddings:
                # result.embeddings ist eine Liste von Embedding-Objekten, wir brauchen die 'values'
                batch_embeddings = [e.values for e in result.embeddings]
                embeddings.extend(batch_embeddings)
                
        except Exception as e:
            print(f"\nFehler bei Batch {i}: {e}")
            time.sleep(5)
            try:
                # Retry
                result = client.models.embed_content(
                    model=EMBEDDING_MODEL,
                    contents=batch_docs,
                    config=types.EmbedContentConfig(
                        task_type="RETRIEVAL_DOCUMENT"
                    )
                )
                if result.embeddings:
                    batch_embeddings = [e.values for e in result.embeddings]
                    embeddings.extend(batch_embeddings)
            except Exception as e2:
                print(f"Retry failed ({e2}), überspringe Batch.")
                # Leere Embeddings als Fallback um Index-Verschiebung zu vermeiden
                # (Hier vereinfacht: wir füllen mit Nullen auf oder brechen ab)
                return 

        time.sleep(1)

    print("Speichere Datenbank...")
    with open(DB_FILE, 'wb') as f:
        pickle.dump({
            "embeddings": embeddings,
            "metadatas": metadatas
        }, f)
        
    print(f"Fertig! Datenbank: {DB_FILE}")

if __name__ == "__main__":
    create_index()
