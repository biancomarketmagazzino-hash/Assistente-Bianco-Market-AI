import streamlit as st
import pandas as pd
import plotly.express as px
from db_engine import load_data, load_data_from_uploads
from ai_helper import get_sql_query, explain_results

st.set_page_config(page_title="Bianco Market AI", page_icon="🛍️", layout="wide")

st.title("🛍️ Bianco Market - Assistente Gestionale AI")
st.caption("Interroga giacenze, vendite, trasferimenti e pianifica il riassortimento in tempo reale.")

# Recupera la chiave API
api_key = st.sidebar.text_input("Groq API Key (Gratuita)", type="password")
if not api_key:
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
    else:
        st.info("💡 Inserisci la tua API Key gratuita di Groq nella barra laterale per procedere.")
        st.stop()

# Connessione al Database
con = None

try:
    con = load_data()
    st.sidebar.success("✅ Dati caricati dalla repository")
except Exception:
    st.sidebar.warning("⚠️ File locali non trovati. Caricali manualmente:")
    up_art = st.sidebar.file_uploader("1. File ARTICOLI (.txt)", type=["txt"])
    up_sit = st.sidebar.file_uploader("2. File Sit_filiali (.txt)", type=["txt"])
    up_stor = st.sidebar.file_uploader("3. File STOR_CAR (.txt)", type=["txt"])
    
    if up_art and up_sit and up_stor:
        with st.spinner("Caricamento archivi in corso..."):
            con = load_data_from_uploads(up_art, up_sit, up_stor)
            st.sidebar.success("✅ File caricati con successo!")
    else:
        st.info("📥 Carica i 3 file dal menu laterale a sinistra per iniziare.")
        st.stop()

# Cronologia Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "data" in msg and msg["data"] is not None:
            st.dataframe(msg["data"])

# Input Chat
user_prompt = st.chat_input("Es: Mostrami i 10 prodotti più venduti a Sabella con le giacenze attuali a Magazzino")

if user_prompt and con is not None:
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.write(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("L'AI sta analizzando i dati di Bianco Market..."):
            try:
                # 1. Genera SQL
                sql = get_sql_query(user_prompt, api_key)
                
                # 2. Esegui Query
                df_res = con.execute(sql).fetchdf()
                
                # 3. Spiegazione AI
                risposta = explain_results(user_prompt, df_res, api_key)
                st.write(risposta)
                
                # 4. Tabella e Grafici
                if not df_res.empty:
                    st.dataframe(df_res, use_container_width=True)
                    
                    num_cols = df_res.select_dtypes(include=['number']).columns
                    cat_cols = df_res.select_dtypes(include=['object']).columns
                    
                    if len(num_cols) >= 1 and len(cat_cols) >= 1:
                        fig = px.bar(
                            df_res.head(15), 
                            x=cat_cols[0], 
                            y=num_cols[0], 
                            title=f"Analisi: {cat_cols[0]} vs {num_cols[0]}",
                            color=num_cols[0], 
                            color_continuous_scale="Blues"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Download CSV
                    csv_data = df_res.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Scarica Report (CSV)",
                        data=csv_data,
                        file_name="Report_Bianco_Market.csv",
                        mime="text/csv"
                    )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": risposta,
                    "data": df_res if not df_res.empty else None
                })
                
            except Exception as e:
                st.error(f"Errore durante l'interrogazione: {e}")
