import pickle
from google import genai
from google.genai import types
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from src.config import DB_FILE, API_KEY, EMBEDDING_MODEL, GENERATION_MODEL

def get_answer(query_text, chat_history=None, n_results=5):
    if chat_history is None:
        chat_history = []

    # 1. Datenbank laden
    try:
        with open(DB_FILE, 'rb') as f:
            data = pickle.load(f)
    except FileNotFoundError:
        return "Fehler: Datenbank nicht gefunden. Bitte zuerst setup.py ausführen.", [], "", ""

    embeddings = np.array(data["embeddings"])
    metadatas = data["metadatas"]
    
    # 2. Setup Client
    client = genai.Client(api_key=API_KEY)
    
    # 3. Retrieval (Suche)
    try:
        # Embedding für die Query
        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=query_text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY"
            )
        )
        # Einzelnes Embedding extrahieren
        query_embedding = np.array([result.embeddings[0].values])
        
    except Exception as e:
        return f"API Fehler (Embedding): {e}", [], "", ""
    
    similarities = cosine_similarity(query_embedding, embeddings)[0]
    top_indices = similarities.argsort()[-n_results:][::-1]
    
    retrieved_docs = []
    sources = []
    
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
