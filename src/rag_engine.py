import pickle
from google import genai
from google.genai import types
import numpy as np
import chromadb
from sklearn.metrics.pairwise import cosine_similarity
from src.config import DB_FILE, API_KEY, EMBEDDING_MODEL, GENERATION_MODEL, CHROMA_DB_DIR

def get_answer(query_text, chat_history=None, n_results=5, db_type="pickle"):
    if chat_history is None:
        chat_history = []
    
    # 2. Setup Client for Embedding (needed for both)
    client = genai.Client(api_key=API_KEY)
    
    retrieved_docs = []
    sources = []
    found_laws = set()

    try:
        # Embedding für die Query
        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=query_text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY"
            )
        )
        query_embedding = result.embeddings[0].values
        
    except Exception as e:
        return f"API Fehler (Embedding): {e}", [], "", ""

    if db_type == "sqlite":
        # ... (removed for this specific replacement context, but logically handled)
        pass 

    if db_type == "chroma":
        try:
            chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
            collection = chroma_client.get_collection(name="german_law")
            
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            for i in range(len(results['ids'][0])):
                doc_text = results['documents'][0][i]
                meta = results['metadatas'][0][i]
                score = results['distances'][0][i]
                
                # Sammle Gesetzesnamen
                if 'law' in meta:
                    found_laws.add(meta['law'])
                
                doc_header = f"{meta.get('id', '?')} - {meta.get('title', '?')}"
                retrieved_docs.append(doc_text)
                sources.append(f"{doc_header} (Distance: {score:.4f})")
                
        except Exception as e:
            return f"Fehler mit ChromaDB: {e}. Haben Sie 'python setup.py --target chroma' ausgeführt?", [], "", ""

    else: # Default: Pickle
        # 1. Datenbank laden
        try:
            with open(DB_FILE, 'rb') as f:
                data = pickle.load(f)
        except FileNotFoundError:
            return "Fehler: Datenbank nicht gefunden. Bitte zuerst setup.py ausführen.", [], "", ""

        embeddings = np.array(data["embeddings"])
        metadatas = data["metadatas"]
        
        query_embedding_np = np.array([query_embedding])
        
        similarities = cosine_similarity(query_embedding_np, embeddings)[0]
        top_indices = similarities.argsort()[-n_results:][::-1]
        
        for idx in top_indices:
            meta = metadatas[idx]
            score = similarities[idx]
            
            # Sammle Gesetzesnamen
            if 'law' in meta:
                found_laws.add(meta['law'])
                
            doc_header = f"{meta['id']} - {meta['title']}"
            retrieved_docs.append(f"{doc_header}\n{meta['text']}")
            sources.append(f"{doc_header} (Score: {score:.4f})")

    context_str = "\n\n".join(retrieved_docs)
    
    # Dynamische Rollen-Beschreibung
    if found_laws:
        laws_str = " und ".join(sorted(found_laws))
        role_description = f"Du bist ein spezialisierter Anwalt für {laws_str}."
    else:
        role_description = "Du bist ein juristischer Assistent für das deutsche Recht."

    # Verlauf formatieren
    history_str = ""
    for msg in chat_history:
        role = "Nutzer" if msg['role'] == 'user' else "Assistent"
        history_str += f"{role}: {msg['content']}\n"

    # 4. Prompt Engineering
    prompt = f"""{role_description}

Hintergrundwissen (Gesetze):
{context_str}

Bisheriger Gesprächsverlauf:
{history_str}

Neue Frage des Nutzers: {query_text}

Aufgabe:
Beantworte die neue Frage. Beziehe dich auf den bisherigen Verlauf, falls nötig.
Nutze die bereitgestellten Gesetze als Faktenbasis. Zitiere Paragraphen.
"""

    # 5. Generierung
    try:
        response = client.models.generate_content(
            model=GENERATION_MODEL,
            contents=prompt
        )
        return response.text, sources, prompt, context_str
    except Exception as e:
        return f"Generierungs-Fehler: {e}", sources, prompt, context_str
