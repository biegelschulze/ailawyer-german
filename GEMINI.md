# AI Lawyer German - Project Context

## Project Overview
**AI Lawyer German** is a command-line interface (CLI) based legal assistant specialized in German law. It utilizes Retrieval-Augmented Generation (RAG) to provide accurate legal information by referencing specific German laws (BGB, StGB, GG, etc.).

The system leverages:
*   **Google Gemini API:** For text generation (`gemini-3-flash-preview`) and embeddings (`gemini-embedding-001`).
*   **Local Vector Database:** Uses `numpy` and `scikit-learn` for efficient similarity search on pre-processed legal texts.
*   **Rich CLI:** Provides a user-friendly terminal interface.

## Key Files & Directories

*   `main.py`: The entry point for the application. Handles CLI arguments and the chat loop.
*   `setup.py`: Script to initialize the project by parsing XML laws and generating embeddings.
*   `src/`: Core source code.
    *   `config.py`: Configuration settings (paths, API keys, model names). **Important:** Uses `python-dotenv` to load credentials.
    *   `rag_engine.py`: Implements the RAG logic: embedding queries, searching the vector DB, and generating responses.
    *   `parser.py`: Parses raw XML law files into structured JSON.
    *   `indexer.py`: Generates embeddings for the parsed laws and saves them to a pickle file.
*   `data/`: Storage for raw XML laws, parsed JSON data (`all_laws_parsed.json`), and the vector index (`legal_embeddings.pkl`).
*   `docs/`: Documentation files, including architecture diagrams.

## Setup & Configuration

1.  **Environment Variables:**
    The project uses a `.env` file to manage sensitive credentials. Ensure a `.env` file exists in the root directory with the following content:
    ```bash
    GEMINI_API_KEY=your_actual_api_key_here
    ```

2.  **Dependencies:**
    Managed via `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Data Acquisition:**
    Laws are sourced from [gesetze-im-internet.de](https://www.gesetze-im-internet.de/aktuell.html).
    To download specific laws (using their abbreviations):
    ```bash
    python scripts/download_laws.py bgb stgb aktg
    ```

4.  **Initialization:**
    Before running the agent, the database must be built:
    ```bash
    python setup.py
    ```
    This script parses XML files in `data/` and creates the vector embeddings. Use `--target chroma` to use ChromaDB instead of the default Pickle index.

## Usage Commands

*   **Interactive Chat:**
    ```bash
    python main.py -i
    ```
*   **Single Query:**
    ```bash
    python main.py "Was ist Diebstahl?"
    ```
*   **Session Management:**
    To save/load a specific chat history:
    ```bash
    python main.py -i --session my-session-id
    ```

## Development Notes

*   **Model Selection:** The models are defined in `src/config.py`. Currently configured to use `models/gemini-3-flash-preview` for generation.
*   **SDK:** The project uses the `google-genai` library (v1.0.0+).
*   **Style:** Follows standard Python conventions. The UI is built with the `rich` library, so output formatting is handled there.
