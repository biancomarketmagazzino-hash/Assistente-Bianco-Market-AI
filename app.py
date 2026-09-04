import os
import glob
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# ---------------------------------------------------------
# CONFIGURAZIONE PAGINA STREAMLIT
# ---------------------------------------------------------
st.set_page_config(
    page_title="Bianco Market - Assistant & Inventory AI",
    layout="wide"
)

# ---------------------------------------------------------
# MAPPATURA UFFICIALE CATEGORIE E FILIALI
# ---------------------------------------------------------
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

FILIALI_MAP = {
    '01': {'nome': 'Magazzino Centrale', 'col_c': 'C_01', 'col_s': 'S_01', 'cod_stor': '00'},
    '02': {'nome': 'Sciacca',            'col_c': 'C_02', 'col_s': 'S_02', 'cod_stor': '06'},
    '03': {'nome': 'Menfi',              'col_c': 'C_03', 'col_s': 'S_03', 'cod_stor': '01'},
    '04': {'nome': 'Marsala',            'col_c': 'C_04', 'col_s': 'S_04', 'cod_stor': '03'},
    '05': {'nome': 'Trapani',            'col_c': 'C_05', 'col_s': 'S_05', 'cod_stor': '09'},
    '06': {'nome': 'Ragusa',             'col_c': 'C_06', 'col_s': 'S_06', 'cod_stor': '07'},
    '07': {'nome': 'Sabella',            'col_c': 'C_07', 'col_s': 'S_07', 'cod_stor': '05'},
    '08': {'nome': 'Mazara del Vallo',   'col_c': 'C_08', 'col_s': 'S_08', 'cod_stor': '02'},
    '09': {'nome': 'Casa Market',        'col_c': 'C_09', 'col_s': 'S_09', 'cod_stor': '04'},
    '10': {'nome': 'Sport Market',       'col_c': 'C_10', 'col_s': 'S_10', 'cod_stor': '08'}
}

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
# FUNZIONI CARICAMENTO DATI CACHATE (DA FILE CSV)
# ---------------------------------------------------------

@st.cache_data(ttl=3600)
def load_articoli():
    path = find_file("ARTICOLI.csv")
    if not path:
        return pd.DataFrame()
    
    df = pd.read_csv(
        path, 
        encoding='latin1', 
        on_bad_lines='skip',
        dtype=str
    )
    
    rename_dict = {
        'CODICE_CAT': 'CAT_L1_REPARTO',
        'GRUPPO': 'CAT_L2_ARTICOLO',
        'SOTTOGRUPPO': 'CAT_L3_GENERE',
        'CAT_LEVEL_4': 'CAT_L4_TESSUTO'
    }
    df = df.rename(columns=rename_dict)
    
    text_cols = ['DESCRIZION', 'CAT_L1_REPARTO', 'CODICE_FOR', 'CODICE_MAR', 'CAT_L2_ARTICOLO', 'CAT_L3_GENERE', 'CAT_L4_TESSUTO']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna('NON DEFINITO').str.strip()
            
    if 'PRZ_ACQ' in df.columns:
        df['PRZ_ACQ'] = pd.to_numeric(df['PRZ_ACQ'].str.replace(',', '.'), errors='coerce').fillna(0.0)
        
    return df

@st.cache_data(ttl=3600)
def load_giacenze():
    path = find_file("Sit_filiali.csv")
    if not path:
        return pd.DataFrame()
    
    df = pd.read_csv(
        path, 
        encoding='latin1', 
        on_bad_lines='skip',
        dtype=str
    )
    
    num_cols = [c for c in df.columns if c != 'CODICE_ART']
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
    return df

@st.cache_data(ttl=3600)
def load_storico_vendite():
    path = find_file("STOR_CAR.csv")
    if not path:
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(path, encoding='latin1', on_bad_lines='skip', dtype=str)
        
        col_map = {
            'TIPO': 'Tipo_Movimento',
            'DATA': 'Data',
            'CODICE_ART': 'CODICE_ART',
            'FILIALE': 'Cod_Filiale_Stor',
            'PRZ_ACQ': 'Prezzo',
            'QTA': 'Quantita'
        }
        df = df.rename(columns=col_map)
        
        if 'Quantita' in df.columns:
            df['Quantita'] = pd.to_numeric(df['Quantita'].str.replace(',', '.'), errors='coerce').fillna(0)
        if 'Prezzo' in df.columns:
            df['Prezzo'] = pd.to_numeric(df['Prezzo'].str.replace(',', '.'), errors='coerce').fillna(0.0)
        if 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
            
        reverse_map = {v['cod_stor']: key for key, v in FILIALI_MAP.items()}
        if 'Cod_Filiale_Stor' in df.columns:
            df['Cod_Filiale_Key'] = df['Cod_Filiale_Stor'].str.zfill(2).map(reverse_map)
            
        return df
    except Exception:
        return pd.DataFrame()

# ---------------------------------------------------------
# INTERFACCIA E LOGICA PRINCIPALE
# ---------------------------------------------------------

st.title("🛍️ Bianco Market - Assistant & Inventory AI")
st.markdown("Sistema integrato per la gestione esistenze, analisi vendite e riassortimento automatizzato.")

df_art = load_articoli()
df_giac = load_giacenze()

if df_art.empty or df_giac.empty:
    st.warning("⚠️ File CSV non trovati. Verifica di aver caricato `ARTICOLI.csv` e `Sit_filiali.csv` nel progetto.")
    st.stop()

# Join Master Data
df_master = pd.merge(df_art, df_giac, on='CODICE_ART', how='left')

# ---------------------------------------------------------
# SIDEBAR - FILTRI CATALOGO
# ---------------------------------------------------------
st.sidebar.header("🔍 Filtri Avanzati Catalogo")

# 1. PRIMO FILTRO: Ricerca Avanzata Multiparola
search_term = st.sidebar.text_input(
    "🔎 Ricerca per Descrizione o Codice ART", 
    "", 
    placeholder="Es: ACCAPP DESID"
)

# 2. FILTRI CATEGORIA PER LIVELLO (1, 2, 3, 4)
sel_l1 = st.sidebar.multiselect("Livello 1: Reparto / Macro Cat.", CATEGORIE_L1)
sel_l2 = st.sidebar.multiselect("Livello 2: Tipologia Articolo", CATEGORIE_L2)
sel_l3 = st.sidebar.multiselect("Livello 3: Genere / Misura", CATEGORIE_L3)
sel_l4 = st.sidebar.multiselect("Livello 4: Materiale / Tessuto", CATEGORIE_L4)

fornitori = sorted([f for f in df_master['CODICE_FOR'].dropna().unique() if f]) if 'CODICE_FOR' in df_master.columns else []
sel_fornitore = st.sidebar.multiselect("Fornitore", fornitori)

marche = sorted([m for m in df_master['CODICE_MAR'].dropna().unique() if m]) if 'CODICE_MAR' in df_master.columns else []
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
# TABS SCHERMATE PRINCIPALI
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📦 Esistenze & Giacenze", 
    "📈 Analisi Vendite", 
    "💡 Algoritmo Riassortimento", 
    "🖨️ Reportistica & Export"
])

# TAB 1: ESISTENZE
with tab1:
    st.subheader("Consultazione Giacenze per Filiale")
    
    filiali_scelte = st.multiselect(
        "Seleziona le Filiali da visualizzare:",
        options=list(FILIALI_MAP.keys()),
        format_func=lambda x: f"{x} - {FILIALI_MAP[x]['nome']}",
        default=list(FILIALI_MAP.keys())
    )
    
    if filiali_scelte:
        c_cols = [FILIALI_MAP[f]['col_c'] for f in filiali_scelte if FILIALI_MAP[f]['col_c'] in df_filtered.columns]
        df_filtered['Totale_Giacenza_Selezionata'] = df_filtered[c_cols].sum(axis=1) if c_cols else 0
        
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Articoli Filtrati", f"{len(df_filtered):,}")
        kpi2.metric("Pezzi Totali in Giacenza", f"{df_filtered['Totale_Giacenza_Selezionata'].sum():,}")
        kpi3.metric("Filiali Incluse", len(filiali_scelte))
        
        cols_base = ['CODICE_ART', 'DESCRIZION', 'CAT_L1_REPARTO', 'CAT_L2_ARTICOLO', 'CAT_L3_GENERE', 'CAT_L4_TESSUTO', 'CODICE_FOR', 'CODICE_MAR']
        cols_presenti = [c for c in cols_base if c in df_filtered.columns]
        cols_to_show = cols_presenti + c_cols + ['Totale_Giacenza_Selezionata']
        
        st.dataframe(df_filtered[cols_to_show], use_container_width=True, height=400)
        
        st.subheader("📊 Ripartizione Giacenze per Punto Vendita")
        giac_totali = {
            FILIALI_MAP[f]['nome']: df_filtered[FILIALI_MAP[f]['col_c']].sum() 
            for f in filiali_scelte if FILIALI_MAP[f]['col_c'] in df_filtered.columns
        }
        
        if giac_totali:
            fig = px.bar(
                x=list(giac_totali.keys()), 
                y=list(giac_totali.values()),
                labels={'x': 'Punto Vendita', 'y': 'Giacenza (Pezzi)'},
                title="Distribuzione Pezzi tra le Filiali",
                color_discrete_sequence=['#0056b3']
            )
            st.plotly_chart(fig, use_container_width=True)

# TAB 2: VENDITE
with tab2:
    st.subheader("Analisi Storico Movimenti")
    
    tipi_mov = st.multiselect("Tipi Movimento:", ['S', 'F', 'C', 'T'], default=['S', 'F'])
    
    df_stor = load_storico_vendite()
    if not df_stor.empty:
        if 'Tipo_Movimento' in df_stor.columns:
            df_stor = df_stor[df_stor['Tipo_Movimento'].isin(tipi_mov)]
        
        art_validi = set(df_filtered['CODICE_ART'])
        df_stor_filt = df_stor[df_stor['CODICE_ART'].isin(art_validi)]
        
        st.markdown("---")
        k1, k2, k3 = st.columns(3)
        tot_pezzi = df_stor_filt['Quantita'].sum() if 'Quantita' in df_stor_filt.columns else 0
        tot_valore = (df_stor_filt['Quantita'] * df_stor_filt['Prezzo']).sum() if ('Quantita' in df_stor_filt.columns and 'Prezzo' in df_stor_filt.columns) else 0
        
        k1.metric("Pezzi Movimentati", f"{int(tot_pezzi):,}")
        k2.metric("Valore Stimato", f"€ {tot_valore:,.2f}")
        k3.metric("Numero Movimenti", f"{len(df_stor_filt):,}")
        
        if not df_stor_filt.empty and 'Data' in df_stor_filt.columns:
            df_trend = df_stor_filt.dropna(subset=['Data']).set_index('Data').groupby(pd.Grouper(freq='M'))['Quantita'].sum().reset_index()
            fig_trend = px.line(
                df_trend, 
                x='Data', 
                y='Quantita', 
                title="Andamento Mensile Movimenti (Pezzi)",
                markers=True
            )
            st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("Nessun dato trovato nel file STOR_CAR.csv.")

# TAB 3: RIASSORTIMENTO
with tab3:
    st.subheader("💡 Consigli Automatici di Riassortimento")
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        filiale_target = st.selectbox(
            "Seleziona la Filiale per cui generare il riassortimento:",
            options=list(FILIALI_MAP.keys()),
            format_func=lambda x: f"{x} - {FILIALI_MAP[x]['nome']}"
        )
    with col_r2:
        percentuale_scorta = st.slider("Incremento Scorta di Sicurezza (%)", 0, 50, 10)
        
    col_c = FILIALI_MAP[filiale_target]['col_c']
    col_s = FILIALI_MAP[filiale_target]['col_s']
    
    df_reorder = df_filtered.copy()
    if col_c in df_reorder.columns and col_s in df_reorder.columns:
        df_reorder['Giacenza_Attuale'] = df_reorder[col_c]
        df_reorder['Scorta_Minima_Base'] = df_reorder[col_s]
        df_reorder['Scorta_Calcolata'] = (df_reorder['Scorta_Minima_Base'] * (1 + percentuale_scorta/100)).astype(int)
        df_reorder['Proposta_Ordine'] = (df_reorder['Scorta_Calcolata'] - df_reorder['Giacenza_Attuale']).clip(lower=0)
        
        df_da_ordinare = df_reorder[df_reorder['Proposta_Ordine'] > 0]
        
        st.warning(f"⚠️ Trovati **{len(df_da_ordinare)}** articoli da riassortire per **{FILIALI_MAP[filiale_target]['nome']}**")
        
        cols_ordine_base = ['CODICE_ART', 'DESCRIZION', 'CAT_L1_REPARTO', 'CAT_L2_ARTICOLO', 'CODICE_FOR', 'CODICE_MAR', 'Giacenza_Attuale', 'Scorta_Minima_Base', 'Proposta_Ordine']
        cols_ordine = [c for c in cols_ordine_base if c in df_da_ordinare.columns]
        st.dataframe(df_da_ordinare[cols_ordine], use_container_width=True)

# TAB 4: REPORTISTICA
with tab4:
    st.subheader("🖨️ Generazione e Download Report")
    
    scelta_report = st.radio("Scegli il tipo di file da esportare:", [
        "Report Giacenze Completo (Articoli Filtrati)", 
        "Piano Ordine Riassortimento Fornitore"
    ])
    
    if scelta_report == "Report Giacenze Completo (Articoli Filtrati)":
        csv_full = df_filtered.to_csv(index=False).encode('latin1')
        st.download_button(
            label="📥 Scarica Report Giacenze in CSV",
            data=csv_full,
            file_name="Bianco_Market_Giacenze.csv",
            mime="text/csv"
        )
    else:
        if 'df_da_ordinare' in locals() and not df_da_ordinare.empty:
            csv_ord = df_da_ordinare[cols_ordine].to_csv(index=False).encode('latin1')
            st.download_button(
                label="📥 Scarica Ordine Suggerito in CSV",
                data=csv_ord,
                file_name=f"Ordine_Riassortimento_{FILIALI_MAP[filiale_target]['nome']}.csv",
                mime="text/csv"
            )
        else:
            st.info("Nessun ordine suggerito presente da esportare per la filiale selezionata.")