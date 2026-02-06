import streamlit as st
import pickle
import numpy as np
import pandas as pd
import umap
import plotly.express as px
import os
import sys

# Pfad zur Datenbank anpassen, falls das Skript aus dem Root oder scripts ordner gestartet wird
# Wir gehen davon aus, dass wir im Root starten oder das Skript den Pfad findet
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "legal_embeddings.pkl")

st.set_page_config(page_title="Legal Vector Explorer", layout="wide")

@st.cache_data
def load_data(path):
    if not os.path.exists(path):
        st.error(f"Datenbank nicht gefunden unter: {path}")
        return None, None
    
    with open(path, "rb") as f:
        data = pickle.load(f)
    
    embeddings = np.array(data["embeddings"])
    metadatas = data["metadatas"]
    
    # Metadaten in DataFrame umwandeln
    df_meta = pd.DataFrame(metadatas)
    
    # Falls 'law' noch nicht in den Metadaten ist (alte Version), extrahieren wir es aus der ID
    if 'law' not in df_meta.columns:
        df_meta['law'] = df_meta['id'].apply(lambda x: x.split()[0] if " " in x else "Unknown")
        
    return embeddings, df_meta

@st.cache_data
def run_umap(embeddings, n_neighbors=15, min_dist=0.1):
    reducer = umap.UMAP(n_neighbors=n_neighbors, min_dist=min_dist, random_state=42)
    coords = reducer.fit_transform(embeddings)
    return coords

def main():
    st.title("§ Juristischer Vektor-Raum Explorer")
    st.markdown("Erkunde die semantische Nähe von Gesetzen im 2D-Raum.")

    # 1. Daten laden
    with st.spinner("Lade Vektordaten..."):
        embeddings, df = load_data(DB_PATH)

    if embeddings is None:
        return

    st.sidebar.header("Einstellungen")
    
    # 2. Filter
    all_laws = sorted(df['law'].unique())
    selected_laws = st.sidebar.multiselect("Gesetze filtern", all_laws, default=all_laws)
    
    if not selected_laws:
        st.warning("Bitte wähle mindestens ein Gesetz aus.")
        return

    # Filtern
    mask = df['law'].isin(selected_laws)
    filtered_embeddings = embeddings[mask]
    filtered_df = df[mask].reset_index(drop=True)

    st.write(f"Zeige {len(filtered_df)} Normen an.")

    # 3. UMAP Berechnung (nur wenn nötig)
    # Achtung: UMAP neu zu berechnen dauert bei vielen Punkten etwas.
    # Wir cachen das Ergebnis basierend auf den Embeddings.
    if len(filtered_df) > 0:
        with st.spinner("Berechne 2D-Projektion (UMAP)..."):
            # UMAP Parameter in Sidebar
            n_neighbors = st.sidebar.slider("UMAP Neighbors (Lokale vs. Globale Struktur)", 2, 100, 15)
            min_dist = st.sidebar.slider("UMAP Min Dist (Cluster-Dichte)", 0.0, 1.0, 0.1)
            
            coords = run_umap(filtered_embeddings, n_neighbors, min_dist)
            
            filtered_df["x"] = coords[:, 0]
            filtered_df["y"] = coords[:, 1]

        # 4. Plotten
        fig = px.scatter(
            filtered_df,
            x="x",
            y="y",
            color="law",
            hover_data=["id", "title"],
            title="Semantische Landkarte der Gesetze",
            template="plotly_dark",
            height=800
        )
        
        # Tooltip verbessern
        fig.update_traces(marker=dict(size=5), selector=dict(mode='markers'))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 5. Suche / Detailansicht
        st.subheader("Detail-Suche")
        search_term = st.text_input("Suche nach Norm (z.B. 'Mord')", "")
        if search_term:
            hits = filtered_df[filtered_df['text'].str.contains(search_term, case=False, na=False) | 
                               filtered_df['title'].str.contains(search_term, case=False, na=False)]
            st.dataframe(hits[['id', 'title', 'text']])

if __name__ == "__main__":
    main()
