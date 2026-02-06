import json
import os
import time
from src.config import DATA_DIR

SESSION_DIR = os.path.join(DATA_DIR, 'sessions')

def ensure_session_dir():
    if not os.path.exists(SESSION_DIR):
        os.makedirs(SESSION_DIR)

def get_session_file(session_id):
    ensure_session_dir()
    return os.path.join(SESSION_DIR, f"{session_id}.json")

def load_history(session_id):
    """Lädt den Chatverlauf oder gibt eine leere Liste zurück."""
    filepath = get_session_file(session_id)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Fehler beim Laden der Session: {e}")
            return []
    return []

def save_history(session_id, history):
    """Speichert den Chatverlauf."""
    filepath = get_session_file(session_id)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def generate_session_id():
    """Erzeugt eine einfache Zeitstempel-ID."""
    return f"chat_{int(time.time())}"
