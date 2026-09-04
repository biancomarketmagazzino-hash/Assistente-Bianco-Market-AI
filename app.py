import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai

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
    try:
        return pd.read_csv("dati_inventario.csv")
    except FileNotFoundError:
        # Dati demo se il file non è presente
        return pd.DataFrame({
            "Filiale": ["Ragusa", "Modica"],
            "Fornitore": ["Caleffi", "Cotonella"],
            "Marca": ["Caleffi", "Cotonella"],
            "Categoria": ["Tessile Casa", "Intimo"],
            "Tipo_Articolo": ["Lenzuolo Matrimoniale", "Pigiama Uomo C/cot"],
            "Taglia": ["Unica", "L"],
            "Esistenza": [12, 2],
            "Venduto_30gg": [10, 15],
            "Scorta_Minima": [5, 5]
        })

df = load_data()

# ---------------------------------------------------------
# CONFIGURAZIONE API GEMINI (Libreria Stabile)
# ---------------------------------------------------------
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else st.sidebar.text_input("Inserisci Gemini API Key:", type="password")

if not api_key:
    st.warning("Inserisci la chiave API Gemini per attivare l'assistente.")
    st.stop()

genai.configure(api_key=api_key)

# ---------------------------------------------------------
# BARRA LATERALE E FILTRI
# ---------------------------------------------------------
st.sidebar.header("🔍 Filtri Magazzino")
filiale_selected = st.sidebar.multiselect("Filiale:", options=df["Filiale"].unique(), default=df["Filiale"].unique())
df_filtered = df[df["Filiale"].isin(filiale_selected)]

st.sidebar.metric("Totale Giacenza", df_filtered["Esistenza"].sum())
st.sidebar.metric("Totale Venduto", df_filtered["Venduto_30gg"].sum())

# ---------------------------------------------------------
# CHATBOT AI (Modello Stabile gemini-1.5-flash)
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Ciao! Sono pronto. Chiedimi pure giacenze, vendite o consigli di riassortimento per Bianco Market."}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Es: Quanti pezzi abbiamo di Pigiama Uomo C/cot a Modica?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Preparazione del contesto dati per l'IA
    system_prompt = f"""
    Sei l'assistente intelligente per l'azienda Bianco Market.
    Usa ESCLUSIVAMENTE questi dati di inventario per rispondere alle domande:
    
    {df_filtered.to_string(index=False)}
    
    Rispondi in modo preciso, professionale e sintetico.
    """

    try:
        # Inizializzazione del modello stabile
        generation_config = {"temperature": 0.2}
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_prompt,
            generation_config=generation_config
        )
        
        response = model.generate_content(prompt)
        reply = response.text
        
    except Exception as e:
        reply = f"Errore di connessione: {e}. Riprova tra un istante."

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").write(reply)

# ---------------------------------------------------------
# SEZIONE GRAFICI
# ---------------------------------------------------------
st.divider()
st.subheader("📊 Grafici e Analisi")
if not df_filtered.empty:
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.bar(df_filtered, x="Tipo_Articolo", y="Esistenza", color="Filiale", title="Giacenze per Articolo")
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = px.pie(df_filtered, values="Venduto_30gg", names="Categoria", title="Vendite per Categoria")
        st.plotly_chart(fig2, use_container_width=True)
