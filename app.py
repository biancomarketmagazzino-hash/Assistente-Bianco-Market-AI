import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai
from google.genai import types

# ---------------------------------------------------------
# CONFIGURAZIONE PAGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Bianco Market - AI Assistant",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Assistant Bianco Market")
st.caption("Gestionale Intelligente per Giacenze, Vendite e Riassortimenti")

# ---------------------------------------------------------
# CARICAMENTO DATI
# ---------------------------------------------------------
@st.cache_data
def load_data():
    # Sostituisci con il percorso del tuo file o database
    try:
        df = pd.read_csv("dati_inventario.csv")
        return df
    except FileNotFoundError:
        # Dati demo se il file non esiste ancora
        data = {
            "Filiale": ["Ragusa", "Ragusa", "Modica", "Modica"],
            "Fornitore": ["Caleffi", "Cotonella", "Caleffi", "Cotonella"],
            "Marca": ["Caleffi", "Cotonella", "Caleffi", "Cotonella"],
            "Categoria": ["Tessile Casa", "Intimo", "Tessile Casa", "Intimo"],
            "Tipo_Articolo": ["Lenzuolo Matrimoniale", "Pigiama Uomo C/cot", "Lenzuolo Matrimoniale", "Pigiama Uomo C/cot"],
            "Taglia": ["Unica", "L", "Unica", "M"],
            "Esistenza": [12, 2, 5, 0],
            "Venduto_30gg": [10, 15, 8, 12],
            "Scorta_Minima": [5, 5, 5, 5]
        }
        return pd.DataFrame(data)

df = load_data()

# ---------------------------------------------------------
# CONFIGURAZIONE GEMINI API
# ---------------------------------------------------------
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else st.sidebar.text_input("Inserisci Gemini API Key:", type="password")

if not api_key:
    st.warning("Inserisci la tua chiave API Gemini nei Secrets di Streamlit o nella barra laterale per proseguire.")
    st.stop()

client = genai.Client(api_key=api_key)

# ---------------------------------------------------------
# BARRA LATERALE: STATISTICHE E FILTRI RAPIDI
# ---------------------------------------------------------
st.sidebar.header("🔍 Vista Rapida Magazzino")
filiale_selected = st.sidebar.multiselect("Filtra per Filiale:", options=df["Filiale"].unique(), default=df["Filiale"].unique())
df_filtered = df[df["Filiale"].isin(filiale_selected)]

st.sidebar.metric("Totale Pezzi in Giacenza", df_filtered["Esistenza"].sum())
st.sidebar.metric("Totale Venduto (30gg)", df_filtered["Venduto_30gg"].sum())

# Calcolo articoli da riassortire (Giacenza < Scorta Minima)
da_riassortire = df_filtered[df_filtered["Esistenza"] < df_filtered["Scorta_Minima"]]
st.sidebar.error(f"Articoli sotto Scorta Minima: {len(da_riassortire)}")

# Export Report rapido
st.sidebar.subheader("📄 Reportistica")
csv_data = df_filtered.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="📥 Scarica Report Filiali (CSV)",
    data=csv_data,
    file_name="report_bianco_market.csv",
    mime="text/csv"
)

# ---------------------------------------------------------
# CHATBOT AI CON GEMINI
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Ciao! Sono l'assistente di **Bianco Market**. Chiedimi pure giacenze, vendite o consigli sugli ordini di riassortimento per le tue filiali."}
    ]

# Visualizzazione della cronologia chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Input dell'utente
if prompt := st.chat_input("Es: Quante giacenze abbiamo di Pigiama Uomo C/cot a Ragusa?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Contesto fornito all'IA per la query
    system_instruction = f"""
    Sei l'assistente intelligente per l'azienda Bianco Market.
    Hai accesso immediato ai seguenti dati di inventario e vendite aggiornati:
    
    {df_filtered.to_string(index=False)}
    
    Istruzioni operative:
    1. Rispondi in modo preciso basandoti ESCLUSIVAMENTE sui dati sopra riportati.
    2. Se l'utente chiede il calcolo per il riassortimento, consiglia di ordinare la quantità necessaria per coprire le vendite stimate mantenendo la scorta minima.
    3. Rispondi sempre in modo professionale, sintetico e chiaro.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2 # Bassa temperatura per risposte precise sui dati
            )
        )
        
        reply = response.text
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.chat_message("assistant").write(reply)

    except Exception as e:
        st.error(f"Errore nella generazione della risposta: {e}")

# ---------------------------------------------------------
# SEZIONE GRAFICI E ANALISI
# ---------------------------------------------------------
st.divider()
st.subheader("📊 Analisi Grafica")

col1, col2 = st.columns(2)

with col1:
    fig_giacenze = px.bar(
        df_filtered, 
        x="Tipo_Articolo", 
        y="Esistenza", 
        color="Filiale", 
        barmode="group",
        title="Giacenze per Articolo e Filiale"
    )
    st.plotly_chart(fig_giacenze, use_container_width=True)

with col2:
    fig_vendite = px.pie(
        df_filtered, 
        values="Venduto_30gg", 
        names="Categoria", 
        title="Distribuzione Vendite (30gg) per Categoria"
    )
    st.plotly_chart(fig_vendite, use_container_width=True)
