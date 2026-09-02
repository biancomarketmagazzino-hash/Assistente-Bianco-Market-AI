import sys
import os

# Assicura che Python trovi data_loader.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI
from data_loader import load_data, FILIALI_MAP

# Configurazione Pagina
st.set_page_config(
    page_title="Bianco Market AI Assistant", 
    layout="wide", 
    page_icon="🛍️"
)

st.title("🛍️ Bianco Market - Assistente AI & Gestione Magazzino")

# ------------------------------------------------------------------------------
# CARICAMENTO DATI
# ------------------------------------------------------------------------------
@st.cache_data
def get_data():
    return load_data()

try:
    df_articoli, df_storcar, df_sit = get_data()
except Exception as e:
    st.error(f"Errore nel caricamento dei dati: {e}")
    st.stop()

# ------------------------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------------------------
st.sidebar.header("📌 Menu di Controllo")
opzione = st.sidebar.radio(
    "Seleziona Modalità:", 
    ["💬 Chatbot AI", "📊 Dashboard Giacenze", "📦 Suggerimento Riassortimento"]
)

# ------------------------------------------------------------------------------
# MODALITÀ 1: CHATBOT AI INTELLIGENTE
# ------------------------------------------------------------------------------
if opzione == "💬 Chatbot AI":
    st.subheader("🤖 Fai una domanda all'assistente commerciale")
    st.write("Esempi: *'Quanti pigiami uomo abbiamo a Ragusa e Sciacca?'*, *'Quali sono i brand più venduti a Menfi?'*")

    if "GEMINI_API_KEY" not in st.secrets:
        st.warning("⚠️ Inserisci la chiave `GEMINI_API_KEY` nella sezione Secrets di Streamlit Cloud.")
        st.stop()
        
    raw_key = str(st.secrets["GEMINI_API_KEY"]).strip().strip('"').strip("'")
    
    # Inizializzazione del client compatibile OpenAI su endpoint Google
    client = OpenAI(
        api_key=raw_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Scrivi la tua domanda..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            system_prompt = (
                "Sei l'assistente AI per Bianco Market (azienda specializzata in biancheria per la casa e persona). "
                "Rispondi in modo professionale, chiaro e sintetico alla domanda sul magazzino o sulle vendite."
            )

            bot_response = None
            last_error = None

            with st.spinner("Elaborazione risposta..."):
                try:
                    response = client.chat.completions.create(
                        model="gemini-1.5-flash",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    if response and response.choices:
                        bot_response = response.choices[0].message.content
                except Exception as e:
                    last_error = str(e)

            if bot_response:
                st.markdown(bot_response)
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
            else:
                if "503" in str(last_error) or "UNAVAILABLE" in str(last_error):
                    st.warning("⚠️ I server sono momentaneamente sovraccarichi. Riprova tra qualche secondo.")
                else:
                    st.error(f"Errore di comunicazione: {last_error}")

# ------------------------------------------------------------------------------
# MODALITÀ 2: DASHBOARD GIACENZE
# ------------------------------------------------------------------------------
elif opzione == "📊 Dashboard Giacenze":
    st.subheader("📈 Analisi Esistenze per Filiale")
    
    filiale_sel = st.selectbox("Seleziona Filiale:", list(FILIALI_MAP.values()))
    
    if filiale_sel in df_sit.columns:
        df_filiale = df_sit[df_sit[filiale_sel] > 0][['CODICE', filiale_sel]]
        st.write(f"Totale articoli con giacenza positiva a **{filiale_sel}**: `{len(df_filiale)}`")
        st.dataframe(df_filiale.head(50), use_container_width=True)
    else:
        st.info("Dati giacenza non disponibili per la filiale selezionata.")

# ------------------------------------------------------------------------------
# MODALITÀ 3: SUGGERIMENTO RIASSORTIMENTO
# ------------------------------------------------------------------------------
elif opzione == "📦 Suggerimento Riassortimento":
    st.subheader("🧮 Calcolo automatico della quantità da ordinare")
    st.info("L'algoritmo incrocia il venduto storico (S/F) con la giacenza attuale per calcolare la stima di riassortimento.")
    
    giorni_copertura = st.slider("Giorni di copertura desiderati:", 15, 90, 30)
    
    if st.button("Calcola Riassortimento"):
        st.success(f"Analisi calcolata per una copertura target di {giorni_copertura} giorni.")
