import sqlite3
import numpy as np
import json
import os

class SimpleVectorDB:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS embeddings (
                id TEXT PRIMARY KEY,
                embedding BLOB,
                metadata TEXT,
                document TEXT
            )
        ''')
        self.conn.commit()

    def add(self, ids, embeddings, metadatas, documents):
        cursor = self.conn.cursor()
        for i, emb, meta, doc in zip(ids, embeddings, metadatas, documents):
            cursor.execute(
                "INSERT OR REPLACE INTO embeddings (id, embedding, metadata, document) VALUES (?, ?, ?, ?)",
                (i, np.array(emb, dtype=np.float32).tobytes(), json.dumps(meta), doc)
            )
        self.conn.commit()

    def query(self, query_embedding, n_results=5):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, embedding, metadata, document FROM embeddings")
        rows = cursor.fetchall()
        
        results = {
            'ids': [[]],
            'documents': [[]],
            'metadatas': [[]],
            'distances': [[]]
        }
        
        if not rows:
            return results

        db_ids = []
        db_embs = []
        db_metas = []
        db_docs = []
        
        for row in rows:
            db_ids.append(row[0])
            db_embs.append(np.frombuffer(row[1], dtype=np.float32))
            db_metas.append(json.loads(row[2]))
            db_docs.append(row[3])
        
        db_embs = np.array(db_embs)
        query_embedding = np.array(query_embedding, dtype=np.float32)
        
        # Simple L2 distance for "benchmark"
        distances = np.linalg.norm(db_embs - query_embedding, axis=1)
        top_indices = distances.argsort()[:n_results]
        
        for idx in top_indices:
            results['ids'][0].append(db_ids[idx])
            results['documents'][0].append(db_docs[idx])
            results['metadatas'][0].append(db_metas[idx])
            results['distances'][0].append(float(distances[idx]))
            
        return results
