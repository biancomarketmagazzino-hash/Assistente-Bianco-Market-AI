import os
import pandas as pd
import streamlit as st

# ---------------------------------------------------------
# CONFIGURAZIONE PAGINA STREAMLIT
# ---------------------------------------------------------
st.set_page_config(
    page_title="Bianco Market - Assistant & Inventory AI",
    layout="wide"
)

# ---------------------------------------------------------
# CSS PERSONALIZZATO PER LA STAMPA INTEGRALE
# ---------------------------------------------------------
st.markdown("""
    <style>
    @media print {
        section[data-testid="stSidebar"], 
        .stButton, 
        .stDownloadButton, 
        iframe,
        footer, 
        header {
            display: none !important;
        }
        
        .main .block-container {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
        }

        [data-testid="stDataFrame"], 
        [data-testid="stTable"], 
        div[data-baseweb="data-table"],
        div[role="grid"] {
            overflow: visible !important;
            height: auto !important;
            max-height: none !important;
        }

        tr {
            page-break-inside: avoid !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# MAPPATURA UFFICIALE FILIALI E CATEGORIE
# ---------------------------------------------------------
MAPPA_FILIALI = {
    'C_01': 'Magazzino',
    'C_02': 'Sciacca',
    'C_03': 'Menfi',
    'C_04': 'Marsala',
    'C_05': 'Trapani',
    'C_06': 'Ragusa',
    'C_07': 'Sabella',
    'C_08': 'Mazara',
    'C_09': 'Casa Market',
    'C_10': 'Sport Market'
}

CATEGORIE_L1 = [
    "ACCESSORI", "ARREDO BAGNO", "ARREDO CASA", "ARREDO GIARDINO", "ARTICOLI DA REGALO",
    "BIANCHERIA BAGNO", "BIANCHERIA CASA", "BIANCHERIA INTIMA", "BIANCHERIA LETTO",
    "CERAMICA", "CERE", "COLLANTERIA", "CONFEZIONE", "CORSETTERIA", "CUCINA",
    "ELETTRODOMESTICI", "ESENTE IVA", "GIOCATTOLI", "IGIENE CASA", "IGIENE PERSONA",
    "INFANZIA", "IVA 10", "IVA 5", "MAGLIERIA", "MARE", "MATERASSI", "MUTANDERIA",
    "NATALIZIO", "PARTY", "PENTOLAME", "PIGIAMERIA", "PLASTICA", "PRODOTTI PER ANIMALI",
    "REPARTO ANIMALI", "REPARTO22", "REPARTO37", "SCUOLA", "TAPPETI", "TEMPO LIBERO", "TENDE"
]

CATEGORIE_L2 = [
    "ABITO", "ACCAPPATOIO", "ASCIUGAMANI", "BARATTOLO", "BASTONE TENDA", "BAVETTE",
    "BERRETTO", "BODY", "BORRACCE", "BORSA MARE", "BORSONE", "BOXER", "BRALETTE",
    "BRASILIANA", "CALCIO", "CALZA CORTA", "CALZA LUNGA", "CAMICE LAVORO", "CAMICIA",
    "CAMICIA DA NOTTE", "CANOTTA", "CAPPELLO", "CARTA REGALO", "CENTRI 3 PEZZI",
    "CENTROTAVOLA", "CERATA AL METRO", "CIABATTA", "CIOTOLA", "COLLANT",
    "COMPLETINO CALCIO", "COMPLETO", "COMPLETO LENZUOLA", "COORDINATO", "COPERTA",
    "COPERTINA", "COPPIA ASCIUGAMANI", "COPRIABITO", "COPRIASSE", "COPRICOSTUMI",
    "COPRICUSCINO", "COPRIDIVANO", "COPRIFORNELLI", "COPRIFORNO", "COPRILAVATRICE",
    "COPRILETTI", "COPRIMACCHIA", "COPRIMATERASSO", "COPRIPIUMINO", "COPRIPOLTRONA",
    "COPRIRETE", "COPRISEDIE", "COPRISEDUTE", "COPRITAVOLA", "COPRITUTTO", "COSTUMI",
    "CUFFIA", "CULOTTA", "CUSCINO", "DIETROVETRI", "FANTASMINI", "FASCIA", "FAZZOLETTI",
    "FEDERE", "FELPE", "FERMAPORTA", "FERMATENDA", "GIACCA", "GIACCA A VENTO",
    "GIUBBOTTI", "GONNA", "GREMBIULE", "GUAINA", "GUANCIALE", "GUANTI", "GUANTO DA FORNO",
    "HOTEL", "IMBOTTITURA", "INFRADITO", "JEANS", "JOGGER", "KIMONO", "LANTERNE",
    "LAVETTE", "LEGGINGS", "LENZUOLO", "LONETA", "LUPETTO", "MAGLIA", "MAGLIONE",
    "MATERASSO", "MINICALZA", "MUTANDONE", "OSPITE", "PALLONE", "PANCA", "PANCERA",
    "PANTALONI", "PANTOFOLE", "PARURE BAGNO", "PASSATOIA", "PIGIAMA", "PIUMINO",
    "PLAID", "POLO", "PONCHO", "PORTABIANCHERIA", "POUF", "PRESINE", "QUADRATO NEONATO",
    "QUARTER", "REGGISENO", "RETE", "SALVAPIEDE", "SCALDASONNO", "SCALDOTTO", "SCARPE",
    "SCIARPE", "SET ASCIUGAMANI", "SHORT", "SLIP", "SLIP MAXI", "SLIP MIDI", "SLIP PIZZO",
    "SLIP VITA ALTA", "SLIP VITA BASSA", "SMANICATO", "SNEAKERS", "SOTTOGONNA",
    "SOTTOVESTE", "SPEZZATO", "STROFINACCI", "T-SHIRT", "TAPPETO", "TAZZE", "TELO",
    "TENDA DOCCIA", "TENNIS", "TOP", "TOPPER", "TOVAGLIA", "TRAPUNTE", "TRAPUNTINI",
    "TRIS SPUGNA", "TUTE", "TUTINA", "VESTAGLIA", "VESTITINO", "ZANZARIERE"
]

CATEGORIE_L3 = [
    "1 PIAZZA E MEZZO", "1 POSTO", "2 POSTI", "3 POSTI", "4 POSTI", "BAMBINI",
    "BIMBA", "BIMBO", "CULLA", "DONNA", "DONNA CAL", "KING SIZE", "MATRIMONIALE",
    "NEONATA", "NEONATI", "NEONATO", "RAGAZZA", "RAGAZZI", "RAGAZZO", "ROTONDO",
    "SINGOLO", "UNISEX", "UOMO", "UOMO CAL", "X12", "X18", "X24", "X4", "X6", "X8"
]

CATEGORIE_L4 = [
    "ALOE VERA", "BIELASTICO", "C/COTONE", "CINIGLIA", "CORAL", "COTONE", "COTONE U/T",
    "CUSCINO ARREDO", "DAMASCO", "FELPATA", "FIBRA", "FILO DI SCOZIA", "FIOCCO MEMORY",
    "FLANELLA", "GARZA", "GOBELIN", "HOTELLERIA", "LANA", "LINO", "MEMORY",
    "MICROFIBRA", "NIDO APE", "P.MILANO", "PELLICCIA", "PERCALLE", "PILE", "POP CORN",
    "PVC", "RASO", "SEAMLESS", "SETA", "SPUGNA", "TRAPUNTATO", "TRIACETATO", "VELVET", "VISCOSA"
]

# ---------------------------------------------------------
# UTILITY PER RICERCA FILE CSV
# ---------------------------------------------------------
def find_file(filename, possible_dirs=None):
    if possible_dirs is None:
        possible_dirs = ["data/current", "data", "."]
        
    for d in possible_dirs:
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.lower() == filename.lower():
                    return os.path.join(d, f)
    return None

# ---------------------------------------------------------
# CARICAMENTO DATI CACHATO
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def load_articoli():
    path = find_file("ARTICOLI.csv")
    if not path:
        return pd.DataFrame()
    
    df = pd.read_csv(path, encoding='latin1', on_bad_lines='skip', dtype=str)
    
    rename_dict = {
        'CODICE_CAT': 'CAT_L1_REPARTO',
        'GRUPPO': 'CAT_L2_ARTICOLO',
        'SOTTOGRUPPO': 'CAT_L3_GENERE',
        'CAT_LEVEL_4': 'CAT_L4_TESSUTO'
    }
    df = df.rename(columns=rename_dict)
    
    text_cols = ['DESCRIZION', 'CODICE_FOR', 'CODICE_MAR', 'CAT_L1_REPARTO', 'CAT_L2_ARTICOLO', 'CAT_L3_GENERE', 'CAT_L4_TESSUTO']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna('-').str.strip()
            
    return df

@st.cache_data(ttl=3600)
def load_giacenze():
    path = find_file("Sit_filiali.csv")
    if not path:
        return pd.DataFrame()
    
    df = pd.read_csv(path, encoding='latin1', on_bad_lines='skip', dtype=str)
    
    num_cols = [c for c in df.columns if c != 'CODICE_ART']
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
    return df

# ---------------------------------------------------------
# CARICAMENTO E PREPARAZIONE DATI
# ---------------------------------------------------------
st.title("🛍️ Bianco Market - Gestione Esistenze & Giacenze")

df_art = load_articoli()
df_giac = load_giacenze()

if df_art.empty or df_giac.empty:
    st.warning("⚠️ Impossibile caricare `ARTICOLI.csv` o `Sit_filiali.csv`.")
    st.stop()

df_master = pd.merge(df_art, df_giac, on='CODICE_ART', how='left')

# ---------------------------------------------------------
# SIDEBAR - FILTRI CATALOGO
# ---------------------------------------------------------
st.sidebar.header("🔍 Filtri Catalogo")

search_term = st.sidebar.text_input("🔎 Ricerca per Descrizione o Codice ART", "", placeholder="Es: STROFINACCI")

sel_l1 = st.sidebar.multiselect("Livello 1: Reparto", CATEGORIE_L1)
sel_l2 = st.sidebar.multiselect("Livello 2: Tipologia Articolo", CATEGORIE_L2)
sel_l3 = st.sidebar.multiselect("Livello 3: Genere / Misura", CATEGORIE_L3)
sel_l4 = st.sidebar.multiselect("Livello 4: Materiale / Tessuto", CATEGORIE_L4)

fornitori = sorted([f for f in df_master['CODICE_FOR'].unique() if f != '-']) if 'CODICE_FOR' in df_master.columns else []
sel_fornitore = st.sidebar.multiselect("Fornitore", fornitori)

marche = sorted([m for m in df_master['CODICE_MAR'].unique() if m != '-']) if 'CODICE_MAR' in df_master.columns else []
sel_marca = st.sidebar.multiselect("Marca", marche)

# APPLICAZIONE FILTRI
df_filtered = df_master.copy()

if search_term.strip():
    words = search_term.strip().split()
    combined_text = df_filtered['DESCRIZION'].fillna('') + ' ' + df_filtered['CODICE_ART'].fillna('')
    mask = pd.Series(True, index=df_filtered.index)
    for word in words:
        mask = mask & combined_text.str.contains(word, case=False, regex=False)
    df_filtered = df_filtered[mask]

if sel_l1 and 'CAT_L1_REPARTO' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['CAT_L1_REPARTO'].isin(sel_l1)]
if sel_l2 and 'CAT_L2_ARTICOLO' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['CAT_L2_ARTICOLO'].isin(sel_l2)]
if sel_l3 and 'CAT_L3_GENERE' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['CAT_L3_GENERE'].isin(sel_l3)]
if sel_l4 and 'CAT_L4_TESSUTO' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['CAT_L4_TESSUTO'].isin(sel_l4)]
if sel_fornitore and 'CODICE_FOR' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['CODICE_FOR'].isin(sel_fornitore)]
if sel_marca and 'CODICE_MAR' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['CODICE_MAR'].isin(sel_marca)]

# ---------------------------------------------------------
# SELEZIONE FILIALI DA MOSTRARE
# ---------------------------------------------------------
filiali_scelte_keys = st.multiselect(
    "Seleziona le Filiali da includere in tabella:",
    options=list(MAPPA_FILIALI.keys()),
    format_func=lambda x: MAPPA_FILIALI[x],
    default=list(MAPPA_FILIALI.keys())
)

if not filiali_scelte_keys:
    st.info("Seleziona almeno una filiale per visualizzare i dati.")
    st.stop()

# Calcolo totale quantità selezionata
df_filtered['Quantità Totale Selezionata'] = df_filtered[filiali_scelte_keys].sum(axis=1)

# Preparazione colonne della tabella
colonne_mappate = {k: MAPPA_FILIALI[k] for k in filiali_scelte_keys}
nomi_filiali_selezionate = list(colonne_mappate.values())

df_display = df_filtered[[
    'CODICE_ART', 
    'DESCRIZION', 
    'CODICE_FOR', 
    'CODICE_MAR'
] + filiali_scelte_keys + ['Quantità Totale Selezionata']].copy()

df_display = df_display.rename(columns={
    'CODICE_ART': 'Codice Articolo',
    'DESCRIZION': 'Descrizione',
    'CODICE_FOR': 'Fornitore',
    'CODICE_MAR': 'Marca',
    **colonne_mappate
})

# ---------------------------------------------------------
# FUNZIONE STYLING / COLORAZIONE CONDIZIONALE
# ---------------------------------------------------------
def applica_colori_giacenza(df, colonne_numeric):
    v_max = df[colonne_numeric].max().max()
    if pd.isna(v_max) or v_max <= 0:
        v_max = 1

    def colora_cella(val):
        if not isinstance(val, (int, float)) or val <= 0:
            return ''
        
        ratio = 0.15 + 0.70 * (val / v_max)
        r = int(225 - (185 * ratio))
        g = int(238 - (150 * ratio))
        b = int(250 - (70 * ratio))
        
        text_color = "white" if ratio > 0.55 else "black"
        
        return f'background-color: rgb({r}, {g}, {b}); color: {text_color}; font-weight: bold;'

    # Applica lo stile e nasconde l'indice di riga direttamente nello Styler
    styler = df.style.map(colora_cella, subset=colonne_numeric)
    return styler.hide(axis='index')

# ---------------------------------------------------------
# METRICHE E TABELLA FORMATTATA
# ---------------------------------------------------------
k1, k2 = st.columns(2)
k1.metric("Totale Articoli Trovati", f"{len(df_display):,}")
k2.metric("Quantità Totale Giacenza", f"{df_display['Quantità Totale Selezionata'].sum():,}")

# Creazione dell'oggetto Styler
styled_df = applica_colori_giacenza(df_display, nomi_filiali_selezionate)

# Visualizzazione dataframe (senza passare hide_index)
st.dataframe(
    styled_df, 
    use_container_width=True, 
    height=550
)

# ---------------------------------------------------------
# PULSANTI D'AZIONE: DOWNLOAD ED STAMPA
# ---------------------------------------------------------
col_btn1, col_btn2 = st.columns([1, 4])

with col_btn1:
    csv_data = df_display.to_csv(index=False).encode('latin1')
    st.download_button(
        label="📥 Scarica CSV",
        data=csv_data,
        file_name="Giacenze_Filiali_Bianco_Market.csv",
        mime="text/csv"
    )

with col_btn2:
    st.components.v1.html(
        """
        <button onclick="window.parent.print()" style="
            background-color: #0056b3;
            color: white;
            border: none;
            padding: 9px 18px;
            font-size: 14px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
        ">🖨️ Stampa Rapida Tabella</button>
        """,
        height=45
    )