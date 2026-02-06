import os
import glob
from dotenv import load_dotenv

# Lade Umgebungsvariablen aus .env Datei
load_dotenv()

# Basis-Pfad des Projekts
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Pfade zu den Daten
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Automatisch alle XML-Dateien im data-Ordner finden
XML_FILES = glob.glob(os.path.join(DATA_DIR, '*.xml'))

JSON_FILE = os.path.join(DATA_DIR, 'all_laws_parsed.json')
DB_FILE = os.path.join(DATA_DIR, 'legal_embeddings.pkl')
CHROMA_DB_DIR = os.path.join(DATA_DIR, 'chroma_db')

# API Konfiguration
API_KEY = os.getenv("GEMINI_API_KEY")
EMBEDDING_MODEL = "models/gemini-embedding-001"
GENERATION_MODEL = "models/gemini-3-flash-preview"