import os
import io
import datetime
import pandas as pd
import streamlit as st

# ---------------------------------------------------------
# CONFIGURAZIONE PAGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Bianco Market - Gestione Giacenze & Ordini",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    "COPRIDIVANO", "COPRIFORNELLI", "COPRIFORNO", "COPRILAVATRICE",
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
# FUNZIONI DI UTILITÀ E PARSING
# ---------------------------------------------------------
def clean_code(series):
    return series.astype(str).str.strip().str.upper()

def parse_date_it(series):
    return pd.to_datetime(series, format='%d/%m/%Y', errors='coerce', dayfirst=True)

def parse_numeric_quantity(series):
    """Pulisce e converte correttamente i numeri gestendo virgole e punti italiani"""
    s_clean = series.astype(str).str.strip().str.replace(',', '.', regex=False)
    return pd.to_numeric(s_clean, errors='coerce').fillna(0).round().astype(int)

def find_file(filename, base_dir="data"):
    search_dirs = [base_dir, "data/current", "."]
    for d in search_dirs:
        if os.path.exists(d):
            for root, dirs, files in os.walk(d):
                for f in files:
                    if f.lower().startswith(filename.lower()):
                        return os.path.join(root, f)
    return None

def find_2026_storici_files(base_dir="data"):
    matched_files = []
    search_dirs = [os.path.join(base_dir, "storici"), base_dir, "."]
    
    for d in search_dirs:
        if os.path.exists(d):
            for root, dirs, files in os.walk(d):
                for f in files:
                    f_upper = f.upper()
                    if ("STOR_CAR" in f_upper or "VENDITE" in f_upper or "VENDUTO" in f_upper) and f_upper.endswith(".CSV"):
                        full_path = os.path.join(root, f)
                        if full_path not in matched_files:
                            matched_files.append(full_path)
    return matched_files

def safe_read_csv(path):
    if not path or not os.path.exists(path):
        return pd.DataFrame()

    for encoding in ['latin1', 'utf-8-sig', 'utf-8', 'cp1252']:
        for sep in [',', ';', '\t', '|']:
            try:
                df = pd.read_csv(path, encoding=encoding, sep=sep, on_bad_lines='skip', dtype=str)
                if len(df.columns) > 1:
                    return df
            except Exception:
                continue
    return pd.DataFrame()

# ---------------------------------------------------------
# CARICAMENTO DATI
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def load_articoli():
    path = find_file("ARTICOLI")
    df = safe_read_csv(path)
    if df.empty:
        return pd.DataFrame()
    
    rename_dict = {
        'CODICE_CAT': 'CAT_L1_REPARTO',
        'GRUPPO': 'CAT_L2_ARTICOLO',
        'SOTTOGRUPPO': 'CAT_L3_GENERE',
        'CAT_LEVEL_4': 'CAT_L4_TESSUTO'
    }
    df = df.rename(columns=rename_dict)
    if 'CODICE_ART' in df.columns:
        df['CODICE_ART'] = clean_code(df['CODICE_ART'])
    
    text_cols = ['DESCRIZION', 'CODICE_FOR', 'CODICE_MAR', 'CAT_L1_REPARTO', 'CAT_L2_ARTICOLO', 'CAT_L3_GENERE', 'CAT_L4_TESSUTO']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna('-').str.strip()
            
    return df

@st.cache_data(ttl=3600)
def load_giacenze():
    path = find_file("Sit_filiali")
    df = safe_read_csv(path)
    if df.empty:
        return pd.DataFrame()
    
    if 'CODICE_ART' in df.columns:
        df['CODICE_ART'] = clean_code(df['CODICE_ART'])
        
    cols_filiali = [c for c in df.columns if c in MAPPA_FILIALI.keys()]
    for col in cols_filiali:
        df[col] = parse_numeric_quantity(df[col])
        
    return df

@st.cache_data(ttl=3600)
def load_stor_car_multianno():
    file_list = find_2026_storici_files("data")
    if not file_list:
        return pd.DataFrame(), []

    dfs = []
    loaded_paths = []

    for path in file_list:
        df_temp = safe_read_csv(path)
        if df_temp.empty:
            continue

        cols_upper = {c: str(c).upper().strip().replace('"', '') for c in df_temp.columns}
        df_temp = df_temp.rename(columns=cols_upper)

        col_art = next((c for c in ['CODICE_ART', 'CODICE', 'ARTICOLO', 'COD_ART'] if c in df_temp.columns), None)
        col_qta = next((c for c in ['QT_CAR', 'QUANTITA', 'QTA', 'PZ_VENDUTI', 'PEZZI', 'VENDUTO'] if c in df_temp.columns and "IMP" not in c and "PREZZO" not in c), None)
        col_data = next((c for c in ['DATA', 'DATA_VENDITA', 'DATAVENDITA', 'DATA_MOV'] if c in df_temp.columns), None)
        col_pv = next((c for c in ['CODICE_PV', 'PV', 'PUNTO_VENDITA', 'FILIALE', 'COD_FILIALE'] if c in df_temp.columns), None)

        if not col_art or not col_qta or not col_data:
            continue

        df_temp['CODICE_ART'] = clean_code(df_temp[col_art])
        df_temp['QUANTITA'] = parse_numeric_quantity(df_temp[col_qta])
        df_temp['DATA_PARSED'] = parse_date_it(df_temp[col_data])

        if col_pv:
            df_temp['CODICE_PV'] = df_temp[col_pv].astype(str).str.strip()
        else:
            df_temp['CODICE_PV'] = 'TUTTI'

        df_temp = df_temp.dropna(subset=['DATA_PARSED'])
        df_temp['FILE_ORIGINE'] = os.path.basename(path)

        dfs.append(df_temp[['CODICE_ART', 'QUANTITA', 'DATA_PARSED', 'CODICE_PV', 'FILE_ORIGINE']])
        loaded_paths.append(path)

    if not dfs:
        return pd.DataFrame(), []

    df_stor_combined = pd.concat(dfs, ignore_index=True)
    return df_stor_combined, loaded_paths

def convert_df_to_excel(df, sheet_name='Data'):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()

# ---------------------------------------------------------
# INIZIALIZZAZIONE DATI MASTER
# ---------------------------------------------------------
st.title("🛍️ Bianco Market - Gestione Giacenze & Ordini")

df_art = load_articoli()
df_giac = load_giacenze()
df_stor, file_caricati = load_stor_car_multianno()

if df_art.empty or df_giac.empty:
    st.error("❌ Impossibile caricare i file 'ARTICOLI.csv' o 'Sit_filiali.csv'. Verificare la cartella data/.")
    st.stop()

df_master = pd.merge(df_art, df_giac, on='CODICE_ART', how='left')

def applica_filtri_catalogo(df, search, l1, l2, l3, l4, forn, marca):
    df_f = df.copy()
    if search and search.strip():
        words = search.strip().split()
        combined_text = df_f['DESCRIZION'].fillna('') + ' ' + df_f['CODICE_ART'].fillna('')
        mask = pd.Series(True, index=df_f.index)
        for word in words:
            mask = mask & combined_text.str.contains(word, case=False, regex=False)
        df_f = df_f[mask]

    if l1 and 'CAT_L1_REPARTO' in df_f.columns:
        df_f = df_f[df_f['CAT_L1_REPARTO'].isin(l1)]
    if l2 and 'CAT_L2_ARTICOLO' in df_f.columns:
        df_f = df_f[df_f['CAT_L2_ARTICOLO'].isin(l2)]
    if l3 and 'CAT_L3_GENERE' in df_f.columns:
        df_f = df_f[df_f['CAT_L3_GENERE'].isin(l3)]
    if l4 and 'CAT_L4_TESSUTO' in df_f.columns:
        df_f = df_f[df_f['CAT_L4_TESSUTO'].isin(l4)]
    if forn and 'CODICE_FOR' in df_f.columns:
        df_f = df_f[df_f['CODICE_FOR'].isin(forn)]
    if marca and 'CODICE_MAR' in df_f.columns:
        df_f = df_f[df_f['CODICE_MAR'].isin(marca)]
    return df_f

# ---------------------------------------------------------
# SCHEDE APPLICAZIONE (TABS)
# ---------------------------------------------------------
tab_giacenze, tab_ordini, tab_dettaglio_pv, tab_diagnostica = st.tabs([
    "📦 Giacenze & Catalogo", 
    "🛒 Gestione Ordini & Reintegri", 
    "🏬 Venduto per Singola Filiale",
    "🔧 Diagnostica"
])

# =========================================================
# TAB 1: GIACENZE E CATALOGO COMPLETO
# =========================================================
with tab_giacenze:
    st.sidebar.header("🔍 Filtri Catalogo")

    search_term = st.sidebar.text_input("🔎 Ricerca Descrizione / Codice", "", key="g_search")
    sel_l1 = st.sidebar.multiselect("Reparto (L1)", CATEGORIE_L1, key="g_l1")
    sel_l2 = st.sidebar.multiselect("Tipologia (L2)", CATEGORIE_L2, key="g_l2")
    sel_l3 = st.sidebar.multiselect("Genere/Misura (L3)", CATEGORIE_L3, key="g_l3")
    sel_l4 = st.sidebar.multiselect("Materiale/Tessuto (L4)", CATEGORIE_L4, key="g_l4")

    fornitori = sorted([f for f in df_master['CODICE_FOR'].unique() if f != '-']) if 'CODICE_FOR' in df_master.columns else []
    sel_fornitore = st.sidebar.multiselect("Fornitore", fornitori, key="g_forn")

    marche = sorted([m for m in df_master['CODICE_MAR'].unique() if m != '-']) if 'CODICE_MAR' in df_master.columns else []
    sel_marca = st.sidebar.multiselect("Marca", marche, key="g_marca")

    df_filtered = applica_filtri_catalogo(df_master, search_term, sel_l1, sel_l2, sel_l3, sel_l4, sel_fornitore, sel_marca)

    nomi_filiali = list(MAPPA_FILIALI.values())
    filiali_selezionate_nomi = st.multiselect(
        "Seleziona i Punti Vendita da includere nella Giacenza Totale:",
        options=nomi_filiali,
        default=nomi_filiali,
        key="g_filiali"
    )

    keys_selezionate = [k for k, v in MAPPA_FILIALI.items() if v in filiali_selezionate_nomi]

    if keys_selezionate:
        df_filtered['Giacenza Totale (Pz)'] = df_filtered[keys_selezionate].sum(axis=1)
        colonne_mappate = {k: MAPPA_FILIALI[k] for k in keys_selezionate}
        cols_display = ['CODICE_ART', 'DESCRIZION', 'CODICE_FOR', 'CODICE_MAR'] + keys_selezionate + ['Giacenza Totale (Pz)']
        
        df_display = df_filtered[cols_display].copy()
        df_display = df_display.rename(columns={
            'CODICE_ART': 'Codice Articolo', 
            'DESCRIZION': 'Descrizione', 
            'CODICE_FOR': 'Fornitore', 
            'CODICE_MAR': 'Marca', 
            **colonne_mappate
        })
        
        st.dataframe(df_display.set_index('Codice Articolo'), width="stretch", height=550)

# =========================================================
# TAB 2: GESTIONE ORDINI, VENDITE E REINTEGRI
# =========================================================
with tab_ordini:
    st.header("🛒 Calcolo Vendite e Suggerimento Reintegro")

    with st.form(key="form_ordini_main"):
        st.subheader("📅 Intervallo Temporale (Formato GG/MM/AAAA)")
        
        c1, c2, c3 = st.columns([1.5, 1.5, 1])
        with c1:
            data_inizio = st.date_input("Data Inizio:", datetime.date(2026, 6, 1), format="DD/MM/YYYY")
        with c2:
            data_fine = st.date_input("Data Fine:", datetime.date(2026, 9, 4), format="DD/MM/YYYY")
        with c3:
            solo_venduti = st.checkbox("Mostra solo articoli venduti (>0)", value=False)

        st.subheader("⚙️ Parametri Reintegro")
        p1, p2 = st.columns(2)
        with p1:
            scorta_minima = st.number_input("Scorta Minima Desiderata (Totale Punti Vendita):", min_value=0, value=2)
        with p2:
            moltiplicatore_reintegro = st.number_input("Coefficiente Reintegro sul Venduto:", min_value=0.0, value=1.0, step=0.1)

        o_search = st.text_input("🔎 Ricerca mirata (es. Codice 83909924 o Descrizione):", "", key="o_search")
        btn_calcola = st.form_submit_button("🔥 CALCOLA VENDUTO E REINTEGRO", width="stretch")

    df_ord_base = applica_filtri_catalogo(df_master, o_search, sel_l1, sel_l2, sel_l3, sel_l4, sel_fornitore, sel_marca)

    tutte_filiali = list(MAPPA_FILIALI.keys())
    df_ord_base['Giacenza Totale (Tutti i PV)'] = df_ord_base[tutte_filiali].sum(axis=1)

    if not df_stor.empty and data_inizio and data_fine:
        d_start = pd.Timestamp(data_inizio)
        d_end = pd.Timestamp(data_fine)

        mask_periodo = (df_stor['DATA_PARSED'] >= d_start) & (df_stor['DATA_PARSED'] <= d_end)
        df_venduto_filtrato = df_stor[mask_periodo]

        venduto_agg = df_venduto_filtrato.groupby('CODICE_ART')['QUANTITA'].sum().reset_index()
        venduto_agg.columns = ['CODICE_ART', 'Quantità Venduta (Periodo)']

        df_ord_base = pd.merge(df_ord_base, venduto_agg, on='CODICE_ART', how='left')
        df_ord_base['Quantità Venduta (Periodo)'] = df_ord_base['Quantità Venduta (Periodo)'].fillna(0).astype(int)
    else:
        df_ord_base['Quantità Venduta (Periodo)'] = 0

    df_ord_base['Fabbisogno'] = (df_ord_base['Quantità Venduta (Periodo)'] * moltiplicatore_reintegro) + scorta_minima
    df_ord_base['Proposta Reintegro (Pz)'] = df_ord_base['Fabbisogno'] - df_ord_base['Giacenza Totale (Tutti i PV)']
    df_ord_base['Proposta Reintegro (Pz)'] = df_ord_base['Proposta Reintegro (Pz)'].apply(lambda x: max(0, int(round(x))))

    if solo_venduti:
        df_ord_base = df_ord_base[df_ord_base['Quantità Venduta (Periodo)'] > 0]

    df_risultato = df_ord_base[[
        'CODICE_ART', 'DESCRIZION', 'CODICE_FOR', 'CODICE_MAR', 
        'Giacenza Totale (Tutti i PV)', 'Quantità Venduta (Periodo)', 'Proposta Reintegro (Pz)'
    ]].copy()

    df_risultato.columns = [
        'Codice Articolo', 'Descrizione', 'Fornitore', 'Marca', 
        'Giacenza Totale (Tutti i PV)', 'Quantità Venduta (Periodo)', 'Proposta Reintegro (Pz)'
    ]

    m1, m2, m3 = st.columns(3)
    m1.metric("Totale Giacenza Attuale", f"{df_risultato['Giacenza Totale (Tutti i PV)'].sum():,} pz")
    m2.metric("Totale Venduto Nel Periodo", f"{df_risultato['Quantità Venduta (Periodo)'].sum():,} pz")
    m3.metric("Totale Pezzi da Riordinare", f"{df_risultato['Proposta Reintegro (Pz)'].sum():,} pz")

    st.dataframe(df_risultato.set_index('Codice Articolo'), width="stretch", height=500)

    # ---------------------------------------------------------
    # VERIFICA TRACCIABILITÀ SINGOLO ARTICOLO
    # ---------------------------------------------------------
    if o_search.strip() and not df_stor.empty:
        st.subheader("🔍 Tracciabilità e Controllo Righe Storico")
        art_cod = o_search.strip().upper()
        df_check = df_stor[(df_stor['CODICE_ART'] == art_cod) & 
                           (df_stor['DATA_PARSED'] >= pd.Timestamp(data_inizio)) & 
                           (df_stor['DATA_PARSED'] <= pd.Timestamp(data_fine))]
        if not df_check.empty:
            st.write(f"Movimenti trovati per `{art_cod}` tra {data_inizio.strftime('%d/%m/%Y')} e {data_fine.strftime('%d/%m/%Y')}:")
            st.dataframe(df_check[['CODICE_ART', 'QUANTITA', 'DATA_PARSED', 'CODICE_PV', 'FILE_ORIGINE']])
            st.info(f"Somma Totale Righe lette per {art_cod}: **{df_check['QUANTITA'].sum()} pz**")
        else:
            st.warning("Nessuna riga trovata nello storico per il codice cercato nell'intervallo selezionato.")

    exp_c1, exp_c2 = st.columns(2)
    with exp_c1:
        csv_data = df_risultato.to_csv(index=False, sep=';').encode('utf-8-sig')
        st.download_button("📥 Esporta Report CSV", csv_data, "Report_Vendite_Giacenze.csv", "text/csv", width="stretch")
    with exp_c2:
        excel_data = convert_df_to_excel(df_risultato, sheet_name='Report Reintegro')
        st.download_button("📊 Esporta Report Excel", excel_data, "Report_Vendite_Giacenze.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")

# =========================================================
# TAB 3: DETTAGLIO VENDUTO PER SINGOLA FILIALE
# =========================================================
with tab_dettaglio_pv:
    st.header("🏬 Analisi Dettagliata per Punto Vendita")

    art_ricercato = st.text_input("Inserisci il Codice Articolo (es. 83909924):", "83909924")

    if art_ricercato.strip():
        cod_clean = art_ricercato.strip().upper()
        row_art = df_master[df_master['CODICE_ART'] == cod_clean]

        if not row_art.empty:
            info = row_art.iloc[0]
            st.success(f"**Articolo:** {info['CODICE_ART']} - {info.get('DESCRIZION', '')} | Marca: {info.get('CODICE_MAR', '-')} | Fornitore: {info.get('CODICE_FOR', '-')}")

            giacenze_pv = []
            for k, v in MAPPA_FILIALI.items():
                val = pd.to_numeric(info.get(k, 0), errors='coerce')
                giacenze_pv.append({'Punto Vendita': v, 'Giacenza Attuale (Pz)': int(val) if pd.notna(val) else 0, 'Codice_PV_Internal': k})

            df_pv_giac = pd.DataFrame(giacenze_pv)

            if not df_stor.empty and 'CODICE_PV' in df_stor.columns:
                mask_art = df_stor['CODICE_ART'] == cod_clean
                mask_dates = (df_stor['DATA_PARSED'] >= pd.Timestamp(data_inizio)) & (df_stor['DATA_PARSED'] <= pd.Timestamp(data_fine))
                df_stor_art = df_stor[mask_art & mask_dates]

                venduto_pv = df_stor_art.groupby('CODICE_PV')['QUANTITA'].sum().reset_index()
                venduto_pv.columns = ['Codice_PV_Internal', 'Quantità Venduta (Periodo)']

                df_pv_giac = pd.merge(df_pv_giac, venduto_pv, on='Codice_PV_Internal', how='left')
                df_pv_giac['Quantità Venduta (Periodo)'] = df_pv_giac['Quantità Venduta (Periodo)'].fillna(0).astype(int)

            df_pv_giac = df_pv_giac[['Punto Vendita', 'Giacenza Attuale (Pz)', 'Quantità Venduta (Periodo)']]
            st.table(df_pv_giac.set_index('Punto Vendita'))
        else:
            st.warning(f"⚠️ Nessun articolo trovato con codice {cod_clean}.")

# =========================================================
# TAB 4: DIAGNOSTICA
# =========================================================
with tab_diagnostica:
    st.header("🔧 Diagnostica Dati e Integrità Files")
    
    st.write("**File di Storico Rilevati:**")
    if file_caricati:
        for f in file_caricati:
            st.code(f)
    else:
        st.warning("Nessun file STOR_CAR trovato nella cartella data/")

    if not df_stor.empty:
        st.subheader("Anteprima Dati Caricati:")
        st.write(f"Totale movimenti rilevati: **{len(df_stor):,}**")
        
        date_valide = df_stor['DATA_PARSED'].dropna()
        if not date_valide.empty:
            st.info(f"📅 Data Inizio Storico: **{date_valide.min().strftime('%d/%m/%Y')}** | Data Fine Storico: **{date_valide.max().strftime('%d/%m/%Y')}**")
        
        df_preview = df_stor.head(20).copy()
        df_preview.columns = ['Codice Articolo', 'Quantità', 'Data Formattata', 'Codice PV', 'File Origine']
        st.dataframe(df_preview, width="stretch")