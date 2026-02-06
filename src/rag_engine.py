import pickle
from google import genai
from google.genai import types
import numpy as np
from src.vector_db import SimpleVectorDB
from sklearn.metrics.pairwise import cosine_similarity
from src.config import DB_FILE, API_KEY, EMBEDDING_MODEL, GENERATION_MODEL, VECTOR_DB_FILE

def get_answer(query_text, chat_history=None, n_results=5, db_type="pickle"):
    if chat_history is None:
        chat_history = []
    
    # 2. Setup Client for Embedding (needed for both)
    client = genai.Client(api_key=API_KEY)
    
    retrieved_docs = []
    sources = []

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
        try:
            vdb = SimpleVectorDB(VECTOR_DB_FILE)
            
            results = vdb.query(
                query_embedding=query_embedding,
                n_results=n_results
            )
            
            # SimpleVectorDB returns lists of lists
            for i in range(len(results['ids'][0])):
                doc_text = results['documents'][0][i]
                meta = results['metadatas'][0][i]
                score = results['distances'][0][i]
                
                doc_header = f"{meta.get('id', '?')} - {meta.get('title', '?')}"
                retrieved_docs.append(doc_text)
                sources.append(f"{doc_header} (L2-Dist: {score:.4f})")
                
        except Exception as e:
            return f"Fehler mit SQLite DB: {e}. Haben Sie 'python setup.py --target sqlite' ausgeführt?", [], "", ""

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
            doc_header = f"{meta['id']} - {meta['title']}"
            retrieved_docs.append(f"{doc_header}\n{meta['text']}")
            sources.append(f"{doc_header} (Score: {score:.4f})")

    context_str = "\n\n".join(retrieved_docs)
    
    # Verlauf formatieren
    history_str = ""
    for msg in chat_history:
        role = "Nutzer" if msg['role'] == 'user' else "Assistent"
        history_str += f"{role}: {msg['content']}\n"

    # 4. Prompt Engineering
    prompt = f"""Du bist ein juristischer Assistent für das deutsche Recht.

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
