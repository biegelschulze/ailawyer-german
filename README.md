# AI Lawyer German (Juristischer AI Agent)

Ein juristischer KI-Assistent für deutsches Recht, basierend auf Google Gemini und RAG (Retrieval-Augmented Generation). Das System nutzt deutsche Gesetzestexte (BGB, StGB, GG, etc.) als Faktenbasis, um präzise Antworten auf Rechtsfragen zu geben und Paragraphen zu zitieren.

## Features

- **RAG-Engine:** Sucht relevante Gesetze in einer lokalen Vektor-Datenbank (Pickle/Numpy).
- **Gemini Integration:** Nutzt `gemini-1.5-flash` für die Antwortgenerierung und `gemini-embedding-001` für Embeddings.
- **Gesetzes-Parser:** Automatisiertes Einlesen von Gesetzen im XML-Format (bereitgestellt durch gesetze-im-internet.de).
- **Session-Management:** Speichert Chatverläufe lokal ab, um Kontext über mehrere Fragen hinweg zu bewahren.
- **Interaktiver Modus:** Ein CLI-Chat-Interface mit farbiger Ausgabe (Rich).

## Projektstruktur

- `main.py`: Haupteinstiegspunkt für den CLI-Agenten.
- `setup.py`: Initialisiert die Datenbank (Parsing & Indexing).
- `src/`: Quellcode der Module.
  - `parser.py`: Extrahiert Normen und Texte aus XML-Dateien.
  - `indexer.py`: Erstellt Vektor-Embeddings via Gemini API.
  - `rag_engine.py`: Logik für Suche und Antwortgenerierung.
  - `config.py`: Zentrale Konfiguration und Pfade.
- `data/`: Enthält XML-Gesetze, die generierte JSON-Datenbank und Vektor-Indizes.
- `scripts/`: Hilfsskripte zum Herunterladen von Daten oder Visualisieren.

## Installation

1. **Repository klonen:**
   ```bash
   git clone https://github.com/biegelschulze/ailawyer-german.git
   cd ailawyer-german
   ```

2. **Virtuelle Umgebung erstellen & aktivieren:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   # oder: .venv\Scripts\activate  # Windows
   ```

3. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```

4. **API Key konfigurieren:**
   Trage deinen Google Gemini API Key in `src/config.py` ein:
   ```python
   API_KEY = "DEIN_API_KEY"
   ```

## Setup (Datenbank initialisieren)

Bevor der Agent genutzt werden kann, müssen die Gesetze geparst und der Vektor-Index erstellt werden:

```bash
python setup.py
```
*Hinweis: Dies erfordert einen aktiven API-Key für die Erstellung der Embeddings.*

## Nutzung

### Interaktiver Chat
Starte den Agenten im interaktiven Modus:
```bash
python main.py -i
```

### Einzelne Abfrage
```bash
python main.py "Was steht in § 823 BGB?"
```

### Mit Session-Management
Lade oder speichere eine spezifische Session:
```bash
python main.py -i --session meine-beratung
```

### Optionen
- `-i`, `--interactive`: Startet den Chat-Modus.
- `--session ID`: Lädt/Speichert den Verlauf in `data/sessions/ID.json`.
- `-q`, `--quiet`: Unterdrückt die Anzeige von Kontext und Prompts (nur die Antwort wird gezeigt).

## Datenquellen
Die XML-Dateien stammen von [gesetze-im-internet.de](https://www.gesetze-im-internet.de/), einem Service des Bundesamts für Justiz.
