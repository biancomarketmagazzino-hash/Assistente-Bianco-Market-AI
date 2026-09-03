import streamlit as st
import pandas as pd
import plotly.express as px
from db_engine import load_data
from ai_helper import get_sql_query, explain_results

st.set_page_config(page_title="Bianco Market AI", page_icon="🛍️", layout="wide")

st.title("🛍️ Bianco Market - Assistente Gestionale AI")
st.caption("Interroga giacenze, vendite, trasferimenti e pianifica il riassortimento in tempo reale.")

# Recupera la chiave API da Streamlit Secrets o Input Utente
api_key = st.sidebar.text_input("Groq API Key (Gratuita)", type="password")
if not api_key:
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
    else:
        st.info("Inserisci la tua API Key gratuita di Groq nella barra laterale per attivare l'AI.")
        st.stop()

@st.cache_resource
def init_db():
    return load_data()

with st.spinner("Caricamento archivi Bianco Market..."):
    con = init_db()

# Inizializza cronologia chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostra messaggi precedenti
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "data" in msg:
            st.dataframe(msg["data"])

# Input Chat
user_prompt = st.chat_input("Es: Quali sono i 5 articoli più venduti a Sabella e quanta giacenza abbiamo a Magazzino?")

if user_prompt:
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.write(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("L'AI sta analizzando i dati..."):
            try:
                # 1. Genera SQL
                sql = get_sql_query(user_prompt, api_key)
                
                # 2. Esegui Query
                df_res = con.execute(sql).fetchdf()
                
                # 3. Spiegazione e Sintesi
                risposta = explain_results(user_prompt, df_res, api_key)
                st.write(risposta)
                
                # 4. Tabella Dati
                if not df_res.empty:
                    st.dataframe(df_res, use_container_width=True)
                    
                    # Grafico automatico se ci sono colonne adatte
                    num_cols = df_res.select_dtypes(include=['number']).columns
                    cat_cols = df_res.select_dtypes(include=['object']).columns
                    
                    if len(num_cols) >= 1 and len(cat_cols) >= 1:
                        fig = px.bar(df_res.head(15), x=cat_cols[0], y=num_cols[0], 
                                     title=f"Grafico: {cat_cols[0]} vs {num_cols[0]}",
                                     color=num_cols[0], color_continuous_scale="Blues")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Download Report Excel
                    excel_data = df_res.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Scarica Report (CSV/Excel)",
                        data=excel_data,
                        file_name="Report_Bianco_Market.csv",
                        mime="text/csv"
                    )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": risposta,
                    "data": df_res if not df_res.empty else None
                })
                
            except Exception as e:
                st.error(f"Errore durante l'elaborazione: {e}")
